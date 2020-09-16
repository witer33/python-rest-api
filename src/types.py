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


from typing import Dict, List
from datetime import datetime
import time
import socket

class HttpRequest:

    def __init__(self, method: str, path: str, http_version: int, headers: Dict[str, str], content: str, get_params: Dict[str, str] = {}):
        self.headers = headers
        self.method = method
        self.path = path
        self.http_version = http_version
        self.content = content
        self.get_params = get_params
    
    def __getattr__(self, name):
        return self.headers.get(name.lower(), None)

    def __getitem__(self, name):
        return self.headers.get(name.lower(), None)
    
    def get(self, name):
        return self.get_params.get(name, "")

class HttpResponse:

    def __init__(self, status_code, http_version: int, headers: Dict[str, str] = {}, content: str = ""):
        self.http_version = http_version
        self.status_code = status_code
        self.headers = headers
        self.content = content

    def to_string(self):
        response = f"HTTP/{self.http_version} {self.status_code}\r\n"
        if isinstance(self.content, str):
            self.headers["Content-Length"] = len(self.content)
        else:
            self.headers["Content-Length"] = 0
        headers = []
        for name, value in self.headers.items():
            name = "-".join([i.capitalize() for i in name.split("-")])
            headers.append(f"{name}: {', '.join(value) if isinstance(value, list) else value}")
        response = response + "\r\n".join(headers)
        if self.content != "" and self.content:
            response = f"{response}\r\n\r\n{self.content}"
        return response

    def __getattr__(self, name):
        return self.headers.get(name.lower(), None)

    def __getitem__(self, name):
        return self.headers.get(name.lower(), None)

    def __setitem__(self, name, value):
        self.headers[name.lower()] = value

class Filter:

    def __init__(self, match_function):
        self.match_function = match_function

    def match(self, request: HttpRequest):
        return self.match_function(request)

class Filters:

    def path(*paths):
        return Filter(lambda request : request.path.split("/", 1)[1] in paths)

    def method(method):
        return Filter(lambda request : request.method.lower() == method.lower())

    def get(**params):
        def match(request):
            breaked = False
            for param, value in params.items():
                if isinstance(value, str):
                    if request.get(param) != value:
                        breaked = True
                        break
                elif isinstance(value, list) or isinstance(value, tuple):
                    if request.get(param) not in value:
                        breaked = True
                        break
            if not breaked:
                return True
        return Filter(match)

class ContentTypes:

    javascript = "application/javascript"
    json = "application/json"
    zip = "application/zip"
    ogg = "application/ogg"
    pdf = "application/pdf"
    mpeg = "audio/mpeg"
    wav = "audio/x-wav"
    gif = "image/gif"
    jpeg = "image/jpeg"
    png = "image/png"
    form_data = "multipart/form-data"
    css = "text/css"
    csv = "text/csv"
    html = "text/html"
    plain = "text/plain"
    xml = "text/xml"
    video_mpeg = "video/mpeg"
    mp4 = "video/mp4"
    quicktime = "video/quicktime"
    webm = "video/webm"

class ApiConnection:

    def __init__(self, conn: socket.socket, request: HttpRequest = None):
        self.conn = conn
        self.request = request

    def reply(self, content: str, content_type: str = "text/html", status_code: str = "200 OK", headers: dict = {}):
        if self.request:
            response = HttpResponse(status_code, self.request.http_version, headers)
        else:
            response = HttpResponse(status_code, 1.1, headers)
        response["Connection"] = "Closed"
        response["Server"] = "Python-API"
        response["Content-Type"] = content_type
        response["Date"] = datetime.fromtimestamp(time.time()).strftime("%a, %d %b %Y %I:%M:%S %p")
        response.content = content
        self.conn.sendall(response.to_string().encode())
        self.conn.close()
