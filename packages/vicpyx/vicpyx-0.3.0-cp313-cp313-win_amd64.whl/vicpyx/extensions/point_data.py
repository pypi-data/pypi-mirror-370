# -----------------------------------------------------------------------------
# Copyright (C) 2025 Correlated Solutions, Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# -----------------------------------------------------------------------------

import socket
import json


class PointData:
    def __init__(self):
        self.name = ''
        self.variables = []
        self.descriptions = []
        self.values = []

    def set_data(self, name, variables, descriptions, values):
        assert len(variables) == len(descriptions) and len(variables) == len(
            values
        ), 'mismatch in point data lengths'
        self.name = name
        self.variables = variables
        self.descriptions = descriptions
        self.values = values


class PointDataSet:
    def __init__(self):
        self.points = []
        self.port = -1
        self.filename = None

    def set_port(self, port):
        self.port = port

    def set_file_name(self, filename):
        self.filename = filename

    def append(self, point_data):
        self.points.append(point_data)

    def save(self, filename=None):
        if len(self.points) == 0:
            raise RuntimeError('No point data to save.')
        if not filename:
            filename = self.filename
        if self.port >= 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', self.port))
            data = bytes()
            data += 'PUTPOINTDATA\r\n'.format(filename).encode('utf-8')
            line_data = json.dumps(self, cls=VicPointDataEncoder, indent=4).encode('utf-8')
            data += 'CONTENT-LENGTH: {}\r\n\r\n'.format(len(line_data)).encode('utf-8')
            data += line_data
            sock.send(data)
            sock.close()

        else:
            raise NotImplementedError('Saving to file not implemented')


class VicPointDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PointDataSet):
            d = {'id': obj.filename, 'points': []}
            for l in obj.points:
                d['points'].append(
                    {'name': l.name, 'vars': l.variables, 'desc': l.descriptions, 'values': l.values}
                )
            return d
        else:
            return super().default(obj)
