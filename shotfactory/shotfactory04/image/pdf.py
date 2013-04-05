#!/usr/bin/env python
# pdf.py - Convert simple PDF screenshots to PPM in pure Python
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Changelog (recent first):
# 2007-06-03 Johann: Very simple prototype PDF reader.

"""
This is a quick hack to extract image data from PDF screenshots as
produced by the screencapture tool on Mac OS X 10.3 Panther.
"""

__revision__ = "$Rev: 2010 $"
__date__ = "$Date: 2007-08-19 22:55:43 -0300 (dom, 19 ago 2007) $"
__author__ = "$Author: johann $"

import sys
import re
import zlib

obj_match = re.compile(r'^(\d+)\s+(\d+)\s+obj$').match
size_match = re.compile(r' /Width (\d+) /Height (\d+) ').search
filter_match = re.compile(r' /Filter /(\S+) ').search


def find_objects(lines):
    """
    Find objects in PDF file.
    """
    for index, line in enumerate(lines):
        match = obj_match(line)
        if match is not None:
            start = index
            a = int(match.group(1))
            b = int(match.group(2))
        if line.strip() == 'endobj':
            yield start, a, b, index


def object_header(lines, start):
    """
    Get the object header at a specified line.
    """
    index = start + 1
    result = lines[index].strip()
    while result.count('<<') > result.count('>>'):
        index += 1
        result += ' ' + lines[index].strip()
    return result, index


def flate_decode(lines, start, stop):
    """
    Decompress a data block.
    """
    assert lines[start].strip() == 'stream'
    assert lines[stop].strip() == 'endstream'
    start += 1
    data = ''.join(lines[start:stop])
    return zlib.decompress(data)


def read_pdf(filename):
    """
    Read an image from a PDF file.
    """
    lines = file(filename, 'rb').readlines()
    for start, a, b, stop in find_objects(lines):
        # print 'found obj %d: lines %d to %d' % (a, start, stop)
        header, header_index = object_header(lines, start)
        # print '   ', header
        if not header.count(' /Type /XObject '):
            continue
        # print '    XObject'
        if not header.count(' /Subtype /Image '):
            continue
        # print '    Image'
        match = size_match(header)
        if match is None:
            continue
        width = int(match.group(1))
        height = int(match.group(2))
        # print '   ', width, height
        match = filter_match(header)
        if match is None:
            continue
        filter_name = match.group(1)
        # print '   ', filter_name
        if filter_name == 'FlateDecode':
            image = flate_decode(lines, header_index + 1, stop - 1)
            return width, height, image
    raise NotImplementedError


def write_ppm(width, height, image, filename=None):
    """
    Output image as PPM file.
    """
    if filename is None:
        outfile = sys.stdout
    else:
        outfile = open(filename, 'wb')
    outfile.write('P6 %d %d 255\n' % (width, height))
    outfile.write(image)


def _main():
    """
    Convert PDF file specified on command line to PPM.
    """
    assert len(sys.argv) == 2
    filename = sys.argv[1]
    width, height, image = read_pdf(filename)
    write_ppm(width, height, image)


if __name__ == '__main__':
    _main()
