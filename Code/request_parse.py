import re

REQUEST_LINE_PATTERN = re.compile(r"^([A-Z]+)\s+(\S+)\s+(HTTP/\d\.\d)$")
HEADER_LINE_PATTERN = re.compile(r"^([^:]+):\s*(.*)$")


def read_http_request(connection_socket):
    request_bytes = b""
    while b"\r\n\r\n" not in request_bytes and len(request_bytes) < 65536:
        chunk = connection_socket.recv(4096)
        if not chunk:
            break
        request_bytes += chunk
    return request_bytes


def parse_http_request(request_bytes):
    try:
        request_text = request_bytes.decode("iso-8859-1")
    except UnicodeDecodeError:
        return None

    header_text = request_text.split("\r\n\r\n", 1)[0]
    lines = header_text.split("\r\n")
    if len(lines) == 0 or lines[0].strip() == "":
        return None

    request_line_match = REQUEST_LINE_PATTERN.match(lines[0].strip())
    if request_line_match is None:
        return None

    method, target, version = request_line_match.groups()

    headers = {}
    for line in lines[1:]:
        if line == "":
            continue
        header_match = HEADER_LINE_PATTERN.match(line)
        if header_match is None:
            return None
        key, value = header_match.groups()
        headers[key.strip().lower()] = value.strip()

    return {
        "method": method,
        "target": target,
        "version": version,
        "headers": headers,
    }


def should_keep_alive(version, headers):
    connection_header = headers.get("connection", "").lower()

    if version == "HTTP/1.1":
        return connection_header != "close"

    if version == "HTTP/1.0":
        return connection_header == "keep-alive"

    return False
