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

import os
import socket
import sys
import traceback
from argparse import ArgumentParser, Namespace

import numpy as np
import PIL.Image

from .. import vicpy as vp
from .extension_socket import *
from .line_data import *
from .point_data import *


class VicExtension(object):
    """
    Base class for Vic extensions. Provides argument parsing.
    """

    def __init__(self):
        self.options = Namespace()
        self.arg_parser = ArgumentParser(description=self.__doc__)

        self.arg_parser.add_argument(
            '--port', '-p', type=int, default=-1, help='Port for communicating with Vic.'
        )

        self.add_arguments(self.arg_parser)
        # Call super().__init__() last so that the arg parser is set up for
        # mixins. As long as the mixin calls super().__init__() first, the
        # order of inheritance does not matter.
        super().__init__()

    def add_arguments(self, parser):
        """
        Add extra arguments to the extension. For instance, use

        def add_arguments(self, pars):
            pars.add_argument('--radius', help='Circle radius', type=float, default=2.0)

        The radius will be available as self.options.radius.
        """
        # nothing to do here

    def run(self, args=None):
        """Run the extension"""
        try:
            if args is None:
                args = sys.argv[1:]
            self.options = self.arg_parser.parse_args(args)

            self.process()

        except Exception as err:
            tb = traceback.format_exception(type(err), err, err.__traceback__)
            start = max(len(tb) - 2, 0)
            for line in tb[start:]:
                print(line.strip())

    def process(self):
        raise NotImplementedError(f"self.process not implemented for {self.__class__.__name__}")


class DataSet(vp.VicDataSet):
    def __init__(self):
        self.port = None
        super().__init__()

    def set_port(self, port):
        self.port = port

    def load(self, filename):
        if self.port >= 0:
            sock = ExtensionSocket(self.port)
            req = 'GETOUTFILE: {}\r\n\r\n'.format(filename).encode('utf-8')
            c_type, data, _ = sock.get_data(req)
            if c_type == 'OUTFILE' and len(data):
                self.load_from_data(data, filename)
        else:
            super().load(filename)

    def save(self, filename=None):
        if not filename:
            filename = self.file_name()
        if self.port >= 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', self.port))
            data = bytes()
            data += 'PUTOUTFILE: {}\r\n'.format(filename).encode('utf-8')
            out_data = self.export_raw()
            data += 'CONTENT-LENGTH: {}\r\n\r\n'.format(len(out_data)).encode('utf-8')
            data += out_data
            sock.send(data)
            sock.close()
        else:
            super().save(filename)


class FullFieldProcessor(VicExtension):
    """
    Extension for processing full-field data, one output file at a time.
    """

    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument('--input', '-i', type=str, help='Input file.', required=True)
        self.arg_parser.add_argument(
            '--output', '-o', type=str, help='Output file. If not given, defaults to input.'
        )

    def process(self):
        output = self.options.input
        if self.options.output:
            output = self.options.output
        data = DataSet()
        data.set_port(self.options.port)
        try:
            data.load(self.options.input)
        except:
            print('Could not load data {}'.format(self.options.input), file=sys.stderr)
            sys.exit(-1)

        # set output file name so extension can call data.save()
        data.set_file_name(output)
        # Process the data file
        self.process_data(data)

    def process_data(self, data):
        raise NotImplementedError(f"self.processData not implemented for {self.__class__.__name__}")


class FullFieldExporter(VicExtension):
    """
    Extension for exporting full-field data, one output file at a time.
    """

    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument('--input', '-i', type=str, help='Input file.', required=True)

    def process(self):
        data = DataSet()
        data.set_port(self.options.port)
        try:
            data.load(self.options.input)
        except:
            print('Could not load data {}'.format(self.options.input), file=sys.stderr)
            sys.exit(-1)

        # Process the data file
        self.process_data(data)

    def process_data(self, data):
        raise NotImplementedError(f"self.processData not implemented for {self.__class__.__name__}")


class LineSliceGenerator(VicExtension):
    """
    Extension for generating line (slice) data from Vic output files.
    """

    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument('--input', '-i', type=str, help='Input file.', required=True)
        self.arg_parser.add_argument(
            '--output',
            '-o',
            type=str,
            help='Output file. If not given, defaults to input with suffix ".csv".',
        )

    def process(self):
        output = self.options.input
        if self.options.port < 0:
            output = os.path.splitext(output)[0] + '.csv'
        if self.options.output:
            output = self.options.output
        data = DataSet()
        data.set_port(self.options.port)
        try:
            data.load(self.options.input)
        except:
            print('Could not load data {}'.format(self.options.input), file=sys.stderr)
            sys.exit(-1)

        # set output file name so extension can call data.save()
        data.set_file_name(output)

        # set up line data
        line_data = LineDataSet()
        line_data.set_port(self.options.port)
        line_data.set_file_name(output)
        # Process the data file
        self.process_data(data, line_data)

    def process_data(self, data, line_data):
        raise NotImplementedError(f"self.processData not implemented for {self.__class__.__name__}")


class PointDataGenerator(VicExtension):
    """
    Extension for generating point data from Vic output files.
    """

    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument('--input', '-i', type=str, help='Input file.', required=True)
        self.arg_parser.add_argument(
            '--output',
            '-o',
            type=str,
            help='Output file. If not given, defaults to input with suffix ".csv".',
        )

    def process(self):
        output = self.options.input
        if self.options.port < 0:
            output = os.path.splitext(output)[0] + '.csv'
        if self.options.output:
            output = self.options.output
        data = DataSet()
        data.set_port(self.options.port)
        try:
            data.load(self.options.input)
        except:
            print('Could not load data {}'.format(self.options.input), file=sys.stderr)
            sys.exit(-1)

        # set output file name so extension can call data.save()
        data.set_file_name(output)

        # set up point data
        point_data_set = PointDataSet()
        point_data_set.set_port(self.options.port)
        point_data_set.set_file_name(output)
        # Process the data file
        self.process_data(data, point_data_set)

    def process_data(self, data, point_data_set):
        raise NotImplementedError(f"self.processData not implemented for {self.__class__.__name__}")


class SubsetSizeMixin:
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument('--subset-size', type=int, help='Subset size used for analysis.')


class VariableListMixin:
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument(
            '--variable-list',
            type=self.read_variable_list,
            help='Colon-separated list of variable names.',
            required=True,
        )

    def read_variable_list(self, vars):
        return vars.split(':')


class InspectorLineMixin:
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument(
            '--inspector-line',
            type=self.read_inspector_line,
            help='Colon-separated list with name followed by x/y coordinates',
            required=False,
            action='append',
            default=[],
        )

    def read_inspector_line(self, obj):
        l = obj.split(':')
        if len(l) & 1 != 1:
            raise ValueError('Invalid line data.')
        return {'name': l[0], 'points': [float(x) for x in l[1:]]}


class InspectorRectangleMixin:
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument(
            '--inspector-rect',
            type=self.read_inspector_rect,
            help='Colon-separated list with name:tlx:tly:brx:bry',
            required=False,
            action='append',
            default=[],
        )

    def read_inspector_rect(self, obj):
        l = obj.split(':')
        if len(l) != 5:
            raise ValueError('Invalid rect data.')
        return {'name': l[0], 'points': [float(x) for x in l[1:]]}


class InspectorCircleMixin:
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument(
            '--inspector-circle',
            type=self.read_inspector_circle,
            help='Colon-separated list with name:cx:cy:r',
            required=False,
            action='append',
            default=[],
        )

    def read_inspector_circle(self, obj):
        l = obj.split(':')
        if len(l) != 4:
            raise ValueError('Invalid circle data.')
        return {'name': l[0], 'center': [float(l[1]), float(l[2])], "radius": float(l[3])}


class AoiMaskMixin:
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument(
            '--aoi-mask', type=self.read_aoi_mask, help='Aoi mask image file name.', required=True
        )

    def read_aoi_mask(self, source):
        q = source.split(':')
        if len(q) == 2 and q[0] == "port":
            port = int(q[1])
            sock = ExtensionSocket(port)
            req = 'GETAOIMASK\r\n\r\n'.encode('utf-8')
            c_type, mask_data, headers = sock.get_data(req)
            if c_type == 'AOIMASK' and len(mask_data):
                w = 0
                h = 0
                for key, value in headers.items():
                    if key == 'WIDTH':
                        w = int(value)
                    elif key == 'HEIGHT':
                        h = int(value)
                    else:
                        print('Unknown key {}'.format(key), file=sys.stderr)
            # print('Got aoi mask {}x{} with {} bytes'.format(w, h, len(mask_data)), file=sys.stderr)
            aoi_mask = np.frombuffer(mask_data, dtype=np.uint8)
            aoi_mask = aoi_mask.reshape([h, w])
            return aoi_mask
        else:
            # print('should read mask from file {}'.format(source), file=sys.stderr)
            return np.asarray(PIL.Image.open(source))


class ReferenceDataMixin:
    def __init__(self):
        super().__init__()
        self.arg_parser.add_argument(
            '--reference-data', type=self.read_ref_data, help='Reference data file name.', required=True
        )

    def read_ref_data(self, source):
        q = source.split(':')
        if len(q) == 2 and q[0] == "port":
            port = int(q[1])
            sock = ExtensionSocket(port)
            req = 'GETREFERENCEDATA\r\n\r\n'.encode('utf8')
            c_type, data, _ = sock.get_data(req)
            if c_type == 'OUTFILE' and len(data):
                d = vp.VicDataSet()
                d.load_from_data(data, '')
                return d
            raise ValueError('Could not load reference data.')
        else:
            data = vp.VicDataSet()
            data.load(source)
            return data
