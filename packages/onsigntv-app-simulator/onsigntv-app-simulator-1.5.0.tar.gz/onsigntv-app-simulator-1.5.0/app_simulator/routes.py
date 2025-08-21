import asyncio
import json
import logging
import mimetypes
import random
import urllib
from datetime import datetime, timedelta

from aiohttp.web import FileResponse, HTTPNotFound, Response
from aiohttp_sse import sse_response
from jinja2 import Environment, PackageLoader, select_autoescape
from multidict import MultiDict
from wtforms import DateTimeField

from .app_config import SDK_TAG, extract_app_config, render_app_html
from .fields import ContentFile, ContentList
from .form import ALLOWED_FILE_TYPES, build_form
from .samples import AIRPORT_DATA, INSTAGRAM_FEED, PLAYBACK_LOOP, TWITTER_FEED
from .storage import get_file, save_file
from .utils import (
    formdata_to_json,
    get_resource_string,
    inject_datasource_script,
    inject_script_into_html,
)

jinja_env = Environment(
    loader=PackageLoader("app_simulator", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

logger = logging.getLogger("onsigntv.routes")


tracked_files = {}


def get_app_kind(config):
    if config.get("automation"):
        return "Automation App"
    elif config.get("plugin"):
        return "Plugin App"
    elif config.get("audio"):
        return "Audio App"


def build_playback_loops(config):
    pb_loops = json.loads(PLAYBACK_LOOP)

    loop = pb_loops["loops"][0]
    if config.get("audio"):
        loop["name"] = "AUDIO"
    elif config.get("automation") or config.get("plugin"):
        loop["name"] = "AUTOMATION"

    loop["content"]["name"] = config["title"]

    return json.dumps(pb_loops)


def handle_widget_exception(exp, formdata=None):
    logger.info("handling rendering exception: %s", exp)

    context = {"exceptions": [exp]}
    if formdata:
        context["formdata"] = formdata_to_json(formdata)

    return Response(
        text=jinja_env.get_template("widget_exceptions.html").render(context),
        content_type="text/html",
    )


def track_file(x):
    tracked_files[x] = 0


async def list_form_file(request):
    name = request.match_info.get("file_name", "")
    path = request.app["base_path"]
    if name:
        path = path / name

    if path.is_file() and path.name.endswith(".html"):
        logger.debug("open a html file: %s", name)

        try:
            config = extract_app_config(path.read_text("utf-8"))

            tracked_files.clear()
            logger.debug("add %s to tracked files list", name)
            track_file(path)

            form = build_form(config)
            form.process()

        except Exception as exp:
            return handle_widget_exception(exp)

        return Response(
            text=jinja_env.get_template("widget_form.html").render(
                {
                    "form": form,
                    "title": config["title"],
                    "description": config.get("description"),
                    "kind": get_app_kind(config),
                    "has_attributes": any(config["attrs"]),
                    "file_name": f"/.preview/{urllib.parse.quote(name)}",
                    "warnings": config["warnings"],
                },
            ),
            content_type="text/html",
        )
    elif path.is_file():
        if ".preview/" in request.headers.get("referer", ""):
            return HTTPNotFound()
        elif path.suffix in ALLOWED_FILE_TYPES:
            logger.debug("serving file: %s", name)
            return FileResponse(path)
        else:
            return HTTPNotFound()
    elif path.is_dir():
        logger.debug("opening directory")

        folder_or_files = []
        if name:
            link = str(path.parent.relative_to(request.app["base_path"]))
            if link == ".":
                link = "/"
            else:
                link = f"/{link}/"

            folder_or_files.append(
                {
                    "name": "Up...",
                    "link": link,
                    "is_up": True,
                }
            )

        for element in sorted(
            path.iterdir(), key=lambda f: (not f.is_dir(), f.name.lower())
        ):
            if element.is_file() and element.suffix not in ALLOWED_FILE_TYPES:
                continue

            if element.name.startswith("."):
                continue

            folder_or_files.append(
                {
                    "name": element.name + ("/" if element.is_dir() else ""),
                    "link": urllib.parse.quote(
                        element.name + ("/" if element.is_dir() else "")
                    ),
                    "is_file": element.is_file(),
                }
            )
        return Response(
            text=jinja_env.get_template("list_files.html").render(
                {
                    "files": folder_or_files,
                    "path": path.absolute(),
                }
            ),
            content_type="text/html",
        )
    else:
        return HTTPNotFound()


async def preview_app(request):
    logger.debug("retrieve data")

    name = request.match_info["file_name"]
    path = request.app["base_path"] / name

    if path not in tracked_files:
        logger.debug("add %s to tracked files list before preview", name)
        track_file(path)

    formdata = MultiDict()

    request_reader = await request.multipart()

    while True:
        part = await request_reader.next()
        if part is None:
            break

        field_name = part.name
        if part.filename:
            logger.debug("field name %s is a file", field_name)
            file_byte = await part.read(decode=True)
            formdata.add(field_name, save_file(part.filename, file_byte))
        else:
            metadata = await part.text()
            logger.debug("field name %s has value %s", field_name, metadata)
            formdata.add(field_name, metadata)

    try:
        config = extract_app_config(path.read_text("utf-8"))
    except Exception as exp:
        return handle_widget_exception(exp, formdata)

    form = build_form(config)
    form.process(formdata=formdata)

    if form.validate():
        logger.debug("form data valid")
        data = {}
        attrs_info = {}
        js_app_config = {}
        has_datafeed = False
        for field in form:
            if callable(getattr(field, "adapt", None)):
                try:
                    field.adapt()
                except Exception as exp:
                    return handle_widget_exception(exp)
                
            if getattr(field, "is_datafeed", False):
                has_datafeed = True

            if getattr(field, "is_attribute", None):
                default = None
                if field.data not in (None, ""):
                    default = field.data
                    if field.attr_type in {"numberarray", "stringarray"}:
                        try:
                            default = json.loads(default)
                            if not isinstance(default, list):
                                raise ValueError()
                        except ValueError:
                            return handle_widget_exception(
                                f'Invalid value "{default}" for attribute "{field.player_name}" of type "{field.attr_type}". Value must be a JSON array.'
                            )

                attrs_info[field.name] = {
                    "type": field.attr_type,
                    "mode": field.mode,
                    "playerName": field.player_name,
                    "default": default,
                }
            else:
                data[field.name] = field.data

            if field.name in config.get("js_app_config", []) and field.data not in (
                "",
                None,
            ):
                field_data = field.data

                if isinstance(field, DateTimeField):
                    js_app_config[field.name] = field.data.isoformat()
                elif isinstance(field_data, ContentFile):
                    js_app_config[field.name] = field_data._serialize()
                elif isinstance(field_data, ContentList):
                    js_app_config[field.name] = [c._serialize() for c in field_data]
                else:
                    js_app_config[field.name] = field_data

        app_global_objects = {
            "__appFormData": formdata_to_json(formdata),
        }

        if attrs_info:
            app_global_objects["__appAttrs"] = json.dumps(attrs_info)

        if js_app_config:
            js_app_config["__lang__"] = "en"
            app_global_objects["appConfig"] = json.dumps(js_app_config)

        if data["_serial_port_config"]:
            app_global_objects["__serialPorts"] = data["_serial_port_config"]

        app_global_objects["__playbackLoops"] = build_playback_loops(config)

        html, exp = render_app_html(data, path, track_file)
        if html is None:
            return handle_widget_exception(exp, formdata)

        html = inject_script_into_html(html, SDK_TAG, app_global_objects)
        
        if has_datafeed:
            html = inject_datasource_script(html)

        return Response(text=html, content_type="text/html")
    else:
        logger.debug("invalid data")

        for field in form:
            for error in field.errors:
                logger.info("Field %s: %s", field.name, error)

        return Response(
            text=jinja_env.get_template("widget_form.html").render(
                {
                    "form": form,
                    "title": config["title"],
                    "description": config.get("description"),
                    "kind": get_app_kind(config),
                    "has_attributes": any(config["attrs"]),
                    "file_name": f"/.preview/{urllib.parse.quote(name)}",
                    "warnings": config["warnings"],
                },
            ),
            content_type="text/html",
        )


async def change_notification_sse(request):
    async with sse_response(request) as resp:
        while resp.is_connected():
            if not tracked_files:
                await resp.send("refresh")
                return resp

            for path, last_modification in tracked_files.items():
                if path.is_file():
                    actual_modification = path.stat().st_ctime
                    logger.debug("Checking m_time %s", path)

                    if last_modification == 0:
                        tracked_files[path] = actual_modification
                    else:
                        if actual_modification > last_modification:
                            logger.info("Reloading due to change on %s", path)
                            await resp.send("refresh")
                            tracked_files[path] = actual_modification
                else:
                    logger.info("File not found: %s", path)
            await asyncio.sleep(1)

    return resp


async def proxy_request(request):
    import aiohttp
    from multidict import CIMultiDict

    hop_by_hop_headers = (
        "Accept-Encoding",
        "Connection",
        "Keep-Alive",
        "TE",
        "Trailer",
        "Transfer-Encoding",
        "Upgrade",
    )

    async with aiohttp.ClientSession() as session:
        # Clean hop-by-hop headers
        req_headers = CIMultiDict(request.headers)
        for header_name in hop_by_hop_headers + ("Host",):
            req_headers.pop(header_name, 0)

        req_data = None
        if request.body_exists:
            req_data = await request.read()

        async with session.request(
            request.method, request.query.get("url"), headers=req_headers, data=req_data
        ) as resp:
            # Clean hop-by-hop headers
            resp_headers = CIMultiDict(resp.headers)
            for header_name in hop_by_hop_headers + (
                "Content-Encoding",
                "Content-Length",
            ):
                resp_headers.pop(header_name, 0)

            resp_data = await resp.read()
            return Response(
                body=resp_data,
                status=resp.status,
                headers=resp_headers,
            )


async def serve_preview_asset(request):
    name = request.match_info.get("file_name", "")

    path = request.app["base_path"]
    if name:
        path = path / name

    if (
        path.is_file()
        and path.suffix in ALLOWED_FILE_TYPES
        and request.query.get("tracked")
    ):
        logger.debug("serving file: %s", name)
        return FileResponse(path)

    return HTTPNotFound()


async def serve_file_from_uploads(request):
    return FileResponse(get_file(request.match_info["file_name"]))


async def serve_twitter_data(request):
    import json

    from aiohttp import web

    return web.json_response(json.loads(TWITTER_FEED))


async def serve_instagram_data(request):
    import json

    from aiohttp import web

    return web.json_response(json.loads(INSTAGRAM_FEED))


async def serve_airport_data(request):
    import json

    from aiohttp import web

    def populate_flight_times(flights):
        dt = datetime.now()
        for flight in flights:
            random_min = random.randint(10, 40)
            dt += timedelta(minutes=random_min)

            flight["time"] = flight["estimated-time"] = dt.strftime(
                "%Y-%m-%dT%H:%M:%S+00:00"
            )

    airport = request.match_info.get("airport_name", "")
    flight_kinds = request.match_info.get("flight_kinds", "")

    data = json.loads(AIRPORT_DATA)
    data["name"] = airport
    data["localtime"] = data["updated_at"] = datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S+00:00"
    )

    for kind in ("departures", "arrivals"):
        if kind in flight_kinds:
            populate_flight_times(data[kind])
        else:
            data.pop(kind, None)

    return web.json_response(data)


async def serve_font(request):
    font_path = request.match_info["blob_path"]

    font_file = get_file(font_path.replace("/", ""))

    if font_file:
        return FileResponse(font_file)
    else:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://signagewidgets.net/app-media/" + font_path
            ) as resp:
                data = await resp.read()

        filename = save_file(font_path, data)

        return FileResponse(get_file(filename))


async def serve_static_asset(request):
    file_path = request.match_info.get("path", "")

    try:
        file_content = get_resource_string("/static/" + file_path)

        return Response(
            content_type=mimetypes.guess_type(file_path)[0], body=file_content
        )
    except FileNotFoundError:
        return HTTPNotFound()
