import socket
import threading

from file_manager import (
    format_http_time,
    get_file_details,
    is_not_modified,
    map_url_to_file,
    read_binary_file,
)
from logger import log_connection_end, log_connection_start, log_request
from request_parse import parse_http_request, read_http_request, should_keep_alive
from response_gen import STATUS_TEXTS, build_error_response, build_http_response

KEEP_ALIVE_TIMEOUT = 5
connection_id_lock = threading.Lock()
next_connection_id = 0


def allocate_connection_id():
    global next_connection_id
    with connection_id_lock:
        next_connection_id = next_connection_id + 1
        return next_connection_id


def start_client_thread(connection_socket, client_address, web_root, log_file_path):
    connection_id = allocate_connection_id()
    thread_name = "client-" + str(connection_id)

    client_thread = threading.Thread(
        target=handle_client_connection,
        args=(connection_socket, client_address, web_root, log_file_path, connection_id),
        name=thread_name,
    )
    client_thread.daemon = True
    client_thread.start()


def process_request(parsed_request, web_root):
    method = parsed_request["method"]
    request_target = parsed_request["target"]
    version = parsed_request["version"]
    headers = parsed_request["headers"]

    requested_file = request_target

    if version not in ("HTTP/1.0", "HTTP/1.1"):
        return 400, requested_file, {}, b""

    if method not in ("GET", "HEAD"):
        return 400, requested_file, {}, b""

    status_code, requested_file, file_path = map_url_to_file(request_target, web_root)
    if status_code != 200:
        return status_code, requested_file, {}, b""

    file_details = get_file_details(file_path)
    last_modified_header = format_http_time(file_details["last_modified"])

    # cache validation for If-Modified-Since
    if_modified_since = headers.get("if-modified-since")
    if if_modified_since and is_not_modified(if_modified_since, file_details["last_modified"]):
        response_headers = {
            "Last-Modified": last_modified_header,
            "Content-Length": "0",
        }
        return 304, requested_file, response_headers, b""

    response_headers = {
        "Content-Type": file_details["content_type"],
        "Content-Length": str(file_details["content_length"]),
        "Last-Modified": last_modified_header,
    }

    if method == "GET":
        try:
            response_body = read_binary_file(file_path)
        except PermissionError:
            return 403, requested_file, {}, b""
    else:
        response_body = b""

    return 200, requested_file, response_headers, response_body


def handle_client_connection(
    connection_socket,
    client_address,
    web_root,
    log_file_path,
    connection_id,
):
    connection_socket.settimeout(KEEP_ALIVE_TIMEOUT)
    thread_name = threading.current_thread().name
    request_count = 0
    end_reason = "client_closed_connection"

    log_connection_start(
        log_file_path,
        connection_id,
        client_address,
        thread_name,
        threading.active_count(),
    )

    while True:
        requested_file = "-"
        try:
            client_request = read_http_request(connection_socket)
            if not client_request:
                end_reason = "client_closed_connection"
                break

            parsed_request = parse_http_request(client_request)
            if parsed_request is None:
                response_bytes = build_error_response("HTTP/1.1", 400, "GET", False)
                connection_socket.sendall(response_bytes)
                log_request(
                    log_file_path,
                    connection_id,
                    thread_name,
                    client_address,
                    "INVALID",
                    requested_file,
                    "HTTP/1.1",
                    400,
                    STATUS_TEXTS[400],
                    False,
                )
                request_count = request_count + 1
                end_reason = "bad_request_parsing_failed"
                break

            method = parsed_request["method"]
            version = parsed_request["version"]
            headers = parsed_request["headers"]
            keep_alive = should_keep_alive(version, headers)

            status_code, requested_file, response_headers, response_body = process_request(
                parsed_request,
                web_root,
            )

            if status_code == 400:
                keep_alive = False

            if status_code in (400, 403, 404):
                response_bytes = build_error_response(version, status_code, method, keep_alive)
            else:
                response_bytes = build_http_response(
                    version,
                    status_code,
                    response_headers,
                    response_body,
                    keep_alive,
                )

            connection_socket.sendall(response_bytes)

            log_request(
                log_file_path,
                connection_id,
                thread_name,
                client_address,
                method,
                requested_file,
                version,
                status_code,
                STATUS_TEXTS[status_code],
                keep_alive,
            )
            request_count = request_count + 1

            if not keep_alive:
                end_reason = "connection_header_close"
                break

        except socket.timeout:
            end_reason = "keep_alive_timeout"
            break
        except Exception:
            response_bytes = build_error_response("HTTP/1.1", 400, "GET", False)
            try:
                connection_socket.sendall(response_bytes)
            except Exception:
                pass

            log_request(
                log_file_path,
                connection_id,
                thread_name,
                client_address,
                "EXCEPTION",
                requested_file,
                "HTTP/1.1",
                400,
                STATUS_TEXTS[400],
                False,
            )
            request_count = request_count + 1
            end_reason = "server_exception"
            break

    log_connection_end(
        log_file_path,
        connection_id,
        client_address,
        thread_name,
        request_count,
        end_reason,
    )
    connection_socket.close()
