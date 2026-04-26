import os
from datetime import datetime, timezone

HTTP_DATE_FORMATS = [
    "%a, %d %b %Y %H:%M:%S GMT",
    "%A, %d-%b-%y %H:%M:%S GMT",
    "%a %b %d %H:%M:%S %Y",
]

MIME_TYPE_MAP = {
    ".html": "text/html",
    ".htm": "text/html",
    ".txt": "text/plain",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def ensure_project_folders():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_root = os.path.join(base_dir, "www")
    log_dir = os.path.join(base_dir, "logs")

    os.makedirs(web_root, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    default_index = os.path.join(web_root, "index.html")
    if not os.path.exists(default_index):
        with open(default_index, "w", encoding="utf-8") as file_object:
            file_object.write("<html><body><h1>Server is Live</h1></body></html>\n")

    return web_root, log_dir


def map_url_to_file(request_target, web_root):
    request_path = request_target

    if "?" in request_path:
        request_path = request_path.split("?", 1)[0]

    if "#" in request_path:
        request_path = request_path.split("#", 1)[0]

    if request_path == "":
        request_path = "/"

    if request_path == "/":
        request_path = "/index.html"

    safe_relative_path = os.path.normpath(request_path.lstrip("/"))
    file_path = os.path.abspath(os.path.normpath(os.path.join(web_root, safe_relative_path)))

    web_root_abs = os.path.abspath(web_root)
    if not file_path.startswith(web_root_abs + os.sep) and file_path != web_root_abs:
        return 403, request_path, None

    if os.path.isdir(file_path):
        file_path = os.path.abspath(os.path.join(file_path, "index.html"))

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return 404, request_path, None

    if not os.access(file_path, os.R_OK):
        return 403, request_path, None

    return 200, request_path, file_path


def detect_content_type(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    return MIME_TYPE_MAP.get(extension, "application/octet-stream")


def read_binary_file(file_path):
    with open(file_path, "rb") as file_object:
        return file_object.read()


def get_file_details(file_path):
    return {
        "content_type": detect_content_type(file_path),
        "content_length": os.path.getsize(file_path),
        "last_modified": int(os.path.getmtime(file_path)),
    }


def format_http_time(timestamp):
    utc_time = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    return utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")


def parse_http_time(date_text):
    if date_text is None:
        return None

    trimmed_date = date_text.strip()
    for format_string in HTTP_DATE_FORMATS:
        try:
            date_object = datetime.strptime(trimmed_date, format_string)
            date_object = date_object.replace(tzinfo=timezone.utc)
            return date_object.timestamp()
        except ValueError:
            continue

    return None


def is_not_modified(if_modified_since, file_timestamp):
    client_timestamp = parse_http_time(if_modified_since)
    if client_timestamp is None:
        return False
    return int(file_timestamp) <= int(client_timestamp)
