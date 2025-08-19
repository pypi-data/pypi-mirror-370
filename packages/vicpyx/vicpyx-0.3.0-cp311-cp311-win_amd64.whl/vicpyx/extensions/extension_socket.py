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
import sys


class ExtensionSocket:
    def __init__(self, port):
        self.port = port

    def get_data(self, req):
        # print('Sending request {}'.format(req), file=sys.stderr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', self.port))
        sock.send(req)
        c_len = 0
        c_type = None
        c_dict = dict()
        all_data = sock.recv(100000000)
        if len(all_data) == 0:
            raise RuntimeError('Socket disconnected')
        while True:
            ix = all_data.find(b'\r\n\r\n')
            if ix < 0:
                q = sock.recv(100000000)
                if len(q) == 0:
                    raise RuntimeError('Socket disconnected')
                else:
                    all_data += q
            else:
                headers = all_data[0:ix].decode('utf-8').split('\r\n')
                if len(all_data) > ix + 4:
                    all_data = all_data[ix + 4 :]
                else:
                    all_data = bytes()
                break
        # parse headers
        for l in headers:
            # print('analyzing header {}'.format(l), file=sys.stderr)
            if l.find('OUTFILE') == 0:
                c_type = 'OUTFILE'
            elif l.find('AOIMASK') == 0:
                c_type = 'AOIMASK'
            elif l.find('CONTENT-LENGTH:') == 0:
                try:
                    c_len = int(l[15:])
                except:
                    print('Could not read content length')
            else:
                q = l.split(':')
                if len(q) == 2:
                    c_dict[q[0]] = q[1]
                    # print('Added key {} with value {} to content dict.'.format(q[0], q[1]), file=sys.stderr)
                else:
                    print('Got unexpected header {}'.format(l), file=sys.stderr)

        if c_len == 0:
            return c_type, bytes(), c_dict

        n_tries = 10000
        while len(all_data) < c_len and n_tries > 0:
            all_data += sock.recv(c_len - len(all_data))
            n_tries -= 1
        sock.close()
        # print('Data length at end: {}'.format(len(all_data)), file=sys.stderr)
        if len(all_data) != c_len:
            print(
                '@@@@@@@@@@@@@@ mismatch in data length: {} {}'.format(len(all_data), c_len),
                file=sys.stderr,
            )
            c_type, bytes(), dict()

        return c_type, all_data, c_dict
