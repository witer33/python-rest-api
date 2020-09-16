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


from .types import HttpRequest

class Parser:

    def __init__(self, request: str):
        self.request = request
        self.pos = 0

    def advance(self):
        self.pos += 1
        if len(self.request) >= self.pos:
            return self.request[self.pos - 1]

    def parse(self):
        char = self.advance()
        line = 0
        headers = {}
        method_line = ""
        header_name = ""
        header_value = ""
        in_value = False
        in_content = False
        content = ""
        skip = False

        while char:
            if line != 0 and not in_content:
                if char == "\r":
                    self.advance()
                    if header_name != "":
                        header_name = header_name.lower()
                        line += 1
                        in_value = False
                        headers[header_name] = header_value.strip()
                        header_value = ""
                        header_name = ""
                    else:
                        in_content = True
                elif char == ":" and not in_value:
                    in_value = True
                elif in_value:
                    header_value += char
                else:
                    header_name += char
            elif in_content:
                content += char
            elif char == "\r":
                self.advance()
                line += 1
            else:
                method_line += char

            char = self.advance()

        if header_name != "" and not in_content:
            header_name = header_name.lower()
            headers[header_name] = header_value.strip()
        values = method_line.strip().split(" ", 2)
        method, path, http_version = tuple(values)
        params = path.split("?", 1)
        if len(params) == 2:
            path = params[0]
            get_params = params[1]
            get_params_parsed = {}
            for param in get_params.split("&"):
                name, value = tuple(param.split("="))
                get_params_parsed[name] = value
        else:
            get_params_parsed = {}
        http_version = float(http_version.split("/", 1)[1])

        return HttpRequest(method, path, http_version, headers, content, get_params_parsed)
