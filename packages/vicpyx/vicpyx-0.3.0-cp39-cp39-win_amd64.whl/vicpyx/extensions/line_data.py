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

import base64
import socket
import numpy as np
import json


class LineData:
    def __init__(self):
        self.name = ''
        self.lines = []

    def add_line(self, var_name, var_desc, data):
        if var_name in self.variable_names():
            raise ValueError('Variable {} is already present.'.format(var_name))
        data = np.array(data)
        assert data.ndim == 1, 'Line data must be 1-dimensional'
        if len(self.lines):
            assert len(self.lines[0]['data']) == len(data), 'All lines must have the same length'
        d = data.astype(np.float32)
        self.lines.append({'name': var_name, 'desc': var_desc, 'data': d})

    def variable_names(self):
        l = []
        for line in self.lines:
            l.append(line['name'])
        return l


class LineDataSet:
    def __init__(self):
        self.line_sets = []
        self.port = -1
        self.filename = None

    def set_port(self, port):
        self.port = port

    def set_file_name(self, filename):
        self.filename = filename

    def append(self, line_data):
        self.line_sets.append(line_data)

    def save(self, filename=None):
        if not filename:
            filename = self.filename
        if self.port >= 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', self.port))
            data = bytes()
            data += 'PUTLINESLICE\r\n'.format(filename).encode('utf-8')
            line_data = json.dumps(self, cls=VicLineSliceEncoder, indent=4).encode('utf-8')
            data += 'CONTENT-LENGTH: {}\r\n\r\n'.format(len(line_data)).encode('utf-8')
            data += line_data
            sock.send(data)
            sock.close()

        else:
            raise NotImplementedError('Saving to file not implemented')


class VicLineSliceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LineDataSet):
            d = {'id': obj.filename, 'line_sets': []}
            for l in obj.line_sets:
                d['line_sets'].append(
                    {
                        'name': l.name,
                        'lines': [
                            {
                                'name': x['name'],
                                'desc': x['desc'],
                                'data': base64.b64encode(x['data'].tobytes()).decode('utf-8'),
                            }
                            for x in l.lines
                        ],
                    }
                )
            return d
        else:
            return super().default(obj)
