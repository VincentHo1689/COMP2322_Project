# Multi-Threaded HTTP Web Server

COMP2322 Project
Student Name: Ho Kwun Chung
Student ID: 22074679d

## 1. Reproduce

### Step 1: Clone the repo

git clone <https://github.com/VincentHo1689/COMP2322_Project.git>
cd Code

### Step 2: Start server

python3 server_main.py

---

## 2. Source Code Descriptions

The server is built using 6 Python files:

1. server_main.py: Initializes the server socket and listens for incoming TCP connections.
2. thread_manager.py: Manages thread creation and the persistent connection (Keep-Alive) logic.
3. request_parse.py: Uses regular expressions to parse HTTP methods, URLs, and headers.
4. file_manager.py: Validates file paths, detects MIME types, and retrieves file modification times.
5. response_gen.py: Generates compliant HTTP response messages (Status line, Headers, and Body).
6. logger.py: Provides thread-safe logging of server events to a local text file.

---

## 3. Project Hierarchy

Code/
├── server_main.py
├── thread_manager.py
├── request_parse.py
├── file_manager.py
├── response_gen.py
├── logger.py
├── logs/
│ └── logs.txt
└── www/
├── index.html
├── sample.txt
├── 403.txt
└── images/

---

## 4. Log File Format

Log file path:

- logs/logs.txt

Every connection and request is logged with detailed fields:

- CONNECTION_START: connection_id, thread name, client ip:port, active thread count
- REQUEST: connection_id, method (GET/HEAD/INVALID), target, HTTP version, status code/text, persistent=True/False
- CONNECTION_END: connection_id, total requests in the connection, end reason (close, timeout, parse error, exception)
