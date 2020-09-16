# Python Rest API - Pure-Python web server for Rest APIs.
# Copyright (C) 2020-2021 witer33 <https://github.com/witer33>
#
# This file is part of Python Rest API.
#
# Python Rest API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Python Rest API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Python Rest API.  If not, see <http://www.gnu.org/licenses/>.


from .types import HttpRequest, HttpResponse, ApiConnection
from .parser import Parser
import socket
import threading
import queue
import time

class Server:

    def __init__(self, port: int, localhost: bool = False, timeout: int = 2, workers: int = 4, rate_limit: int = 20):
        self.port = port
        self.localhost = localhost
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.timeout = timeout
        self.queue = queue.Queue()
        self.workers = workers
        self.rate_limit = rate_limit
        self.rate_limit_cache = {}
        self.max_headers_len = 16384

    def _request_handler(self):
        while True:
            try:
                step = 0
                conn, addr = self.sock.accept()
                addr = addr[0]
                conn.settimeout(self.timeout)
                if self.rate_limit_cache.get(addr, [0, 0])[0] == self.rate_limit and self.rate_limit_cache.get(addr, [0, 0])[1] == int(time.time()):
                    conn = ApiConnection(conn, None)
                    conn.reply("<h1 align=\"center\">Enhance your calm</h1>", status_code="420 Enhance your calm")
                    continue
                elif self.rate_limit_cache.get(addr, [0, 0])[1] != int(time.time()):
                    self.rate_limit_cache[addr] = [0, int(time.time())]
                self.rate_limit_cache[addr][0] = self.rate_limit_cache.get(addr, 0)[0] + 1
                char = conn.recv(1)
                request_headers = bytes()
                request_len = 1
                while True:
                    if char == "" or not char:
                        raise Exception("Connection closed.")
                    request_len += 1
                    if request_len > self.max_headers_len:
                        raise Exception("Max len reached.")
                    request_headers += char
                    if (step % 2) == 0 and char == b"\r":
                        step += 1
                    elif (step % 2) == 1 and char == b"\n":
                        step += 1
                    else:
                        step = 0
                    if step == 4:
                        break
                    try:
                        char = conn.recv(1)
                    except socket.timeout:
                        break
                request = request_headers
                request_headers = Parser(request_headers.decode()).parse()
                content_length = int(request_headers.headers.get("Content-Length", "0"))
                buffers = []
                for i in range(int(content_length / 1024)):
                    buffers.append(1024)
                buffers.append(content_length - (int(content_length / 1024) * 1024))
                content = bytes()
                for i in buffers:
                    content += conn.recv(i)
                self.queue.put([conn, request + content, addr[0]])
            except Exception as e:
                try:
                    conn.close()
                except:
                    pass
                continue

    def bind(self):
        self.sock.bind(("127.0.0.1" if self.localhost else "0.0.0.0", self.port))

    def start(self):
        self.bind()
        self.sock.listen()
        for _ in range(self.workers):
            threading.Thread(target=self._request_handler).start()
