import socket

from file_manager import ensure_project_folders
from logger import ensure_log_file
from thread_manager import start_client_thread

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
BACKLOG_SIZE = 5


def start_server():
    web_root, log_dir = ensure_project_folders()
    log_file_path = ensure_log_file(log_dir)

    # create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("socket successfully created")

    # bind and listen
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    print("socket binded to %s" % SERVER_PORT)

    server_socket.listen(BACKLOG_SIZE)
    print("URL: http://%s:%s/" % (SERVER_HOST, SERVER_PORT))

    try:
        while True:
            connection_socket, client_address = server_socket.accept()

            start_client_thread(
                connection_socket,
                client_address,
                web_root,
                log_file_path,
            )
    except KeyboardInterrupt:
        print("\nserver stopped by user")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
