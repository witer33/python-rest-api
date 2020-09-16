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


from .types import HttpRequest, HttpResponse, Filter, ApiConnection
from .parser import Parser
from .server import Server
from typing import List
import threading
import time

class Api:

    def __init__(self, port: int, localhost: bool = False, workers:int = 4, rate_limit: int = 20):
        self.port = port
        self.localhost = localhost
        self.workers = workers
        self.rate_limit = rate_limit
        self.handlers = []

    def _requests_handler(self):
        while True:
            try:
                conn, request, addr = tuple(self.server.queue.get())
                request = Parser(request.decode()).parse()
                breaked = False
                reply = False
                for handler in self.handlers:
                    for match_filter in handler[0]:
                        if not match_filter.match(request):
                            breaked = True
                            break
                    if not breaked:
                        conn = ApiConnection(conn, request)
                        try:
                            reply = True
                            handler[1](conn, request)
                            if conn.conn.fileno() != -1:
                                conn.conn.close()
                            break
                        except Exception as e:
                            reply = True
                            conn.reply("<h1 align=\"center\">Internal Server Error</h1>", status_code="500 Internal Server Error")
                            break
                if not reply:
                    conn = ApiConnection(conn, request)
                    conn.reply("<h1 align=\"center\">Not Found</h1>", status_code="404 Not Found")
            except Exception as e:
                print(e)
                continue

    def add_handler(self, match_function, *filters):
        self.handlers.append([filters, match_function])

    def on_request(self, *filters):
        def add_handler(func):
            self.add_handler(func, *filters)
            return None
        return add_handler

    def start(self):
        self.server = Server(self.port, self.localhost, 2, self.workers, self.rate_limit)
        self.server.start()
        for _ in range(self.workers):
            threading.Thread(target=self._requests_handler).start()
