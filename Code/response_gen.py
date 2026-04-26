from datetime import datetime, timezone

STATUS_TEXTS = {
    200: "OK",
    304: "Not Modified",
    400: "Bad Request",
    403: "Forbidden",
    404: "File Not Found",
}

SERVER_NAME = "22074679D-MultiThreadWebServer"


def build_http_now():
    current_utc_time = datetime.now(timezone.utc)
    return current_utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")


def build_error_body(status_code):
    status_text = STATUS_TEXTS[status_code]
    body_text = (
        "<html><head><title>"
        + str(status_code)
        + " "
        + status_text
        + "</title></head>"
        + "<body><h1>"
        + str(status_code)
        + " "
        + status_text
        + "</h1></body></html>"
    )
    return body_text.encode("utf-8")


def build_http_response(version, status_code, headers, body_bytes, keep_alive):
    status_text = STATUS_TEXTS[status_code]

    response_headers = {}
    if headers is not None:
        response_headers.update(headers)

    if "Content-Length" not in response_headers:
        response_headers["Content-Length"] = str(len(body_bytes))

    header_lines = [
        version + " " + str(status_code) + " " + status_text,
        "Date: " + build_http_now(),
        "Server: " + SERVER_NAME,
    ]

    if keep_alive:
        header_lines.append("Connection: keep-alive")
        header_lines.append("Keep-Alive: timeout=5, max=20")
    else:
        header_lines.append("Connection: close")

    for key, value in response_headers.items():
        header_lines.append(key + ": " + str(value))

    header_text = "\r\n".join(header_lines) + "\r\n\r\n"
    return header_text.encode("iso-8859-1") + body_bytes


def build_error_response(version, status_code, method, keep_alive):
    error_body = build_error_body(status_code)
    response_headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Length": str(len(error_body)),
    }

    if method == "HEAD":
        return build_http_response(version, status_code, response_headers, b"", keep_alive)

    return build_http_response(version, status_code, response_headers, error_body, keep_alive)
