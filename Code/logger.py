import os
import threading
from datetime import datetime

log_lock = threading.Lock()


def current_time_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_log_line(log_file_path, log_line):
    with log_lock:
        with open(log_file_path, "a", encoding="utf-8") as log_object:
            log_object.write(log_line + "\n")


def ensure_log_file(log_directory):
    os.makedirs(log_directory, exist_ok=True)
    log_file_path = os.path.join(log_directory, "logs.txt")

    if not os.path.exists(log_file_path):
        with open(log_file_path, "a", encoding="utf-8"):
            pass

    return log_file_path


def log_connection_start(log_file_path, connection_id, client_address, thread_name, active_threads):
    client_ip = client_address[0]
    client_port = client_address[1]

    log_line = (
        "EVENT=CONNECTION_START"
        + "\ttime="
        + current_time_text()
        + "\tconnection_id="
        + str(connection_id)
        + "\tthread="
        + thread_name
        + "\tclient="
        + client_ip
        + ":"
        + str(client_port)
        + "\tactive_threads="
        + str(active_threads)
    )
    write_log_line(log_file_path, log_line)


def log_request(
    log_file_path,
    connection_id,
    thread_name,
    client_address,
    method,
    requested_file,
    version,
    status_code,
    status_text,
    is_persistent,
):
    client_ip = client_address[0]
    client_port = client_address[1]

    log_line = (
        "EVENT=REQUEST"
        + "\ttime="
        + current_time_text()
        + "\tconnection_id="
        + str(connection_id)
        + "\tthread="
        + thread_name
        + "\tclient="
        + client_ip
        + ":"
        + str(client_port)
        + "\tmethod="
        + method
        + "\ttarget="
        + requested_file
        + "\tversion="
        + version
        + "\tstatus_code="
        + str(status_code)
        + "\tstatus_text="
        + status_text
        + "\tpersistent="
        + str(is_persistent)
    )
    write_log_line(log_file_path, log_line)


def log_connection_end(
    log_file_path,
    connection_id,
    client_address,
    thread_name,
    total_requests,
    end_reason,
):
    client_ip = client_address[0]
    client_port = client_address[1]

    log_line = (
        "EVENT=CONNECTION_END"
        + "\ttime="
        + current_time_text()
        + "\tconnection_id="
        + str(connection_id)
        + "\tthread="
        + thread_name
        + "\tclient="
        + client_ip
        + ":"
        + str(client_port)
        + "\ttotal_requests="
        + str(total_requests)
        + "\treason="
        + end_reason
    )
    write_log_line(log_file_path, log_line)
