# browsershots.org - Test your web design in different browsers
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# Browsershots is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Browsershots is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Managing screenshots as PNG files.
"""

__revision__ = "$Rev: 3076 $"
__date__ = "$Date: 2008-09-11 16:43:57 -0300 (qui, 11 set 2008) $"
__author__ = "$Author: johann $"

import re
import os
import httplib
import urllib
import tempfile
from xmlrpclib import Fault
from django.conf import settings
from shotserver04.nonces import crypto

ORIGINAL_SIZE = 'original'
HEADER_MATCH = re.compile(r'(\S\S)\s+(\d+)\s+(\d+)\s+').match
BUFFER_SIZE = 4096
DEBUG_HEADERS = False


def png_path(hashkey, size=ORIGINAL_SIZE):
    """Get the full filesystem path for a PNG directory."""
    return os.path.join(settings.PNG_ROOT, str(size), hashkey[:2])


def png_filename(hashkey, size=ORIGINAL_SIZE):
    """Get the full filesystem path for a PNG file."""
    return os.path.join(png_path(hashkey, size), hashkey + '.png')


def png_filesize(hashkey, size=ORIGINAL_SIZE):
    """Get file size of the PNG file in bytes."""
    return os.path.getsize(png_filename(hashkey, size))


def makedirs(path):
    """
    Make directory (and parents) if necessary.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def save_upload(screenshot):
    """
    Save uploaded screenshot file and return hashkey.
    """
    hashkey = crypto.random_md5()
    makedirs(png_path(hashkey))
    outfile = file(png_filename(hashkey), 'wb')
    outfile.write(screenshot.data)
    outfile.close()
    return hashkey


def pngtoppm(hashkey):
    """
    Decode PNG file and return temporary PPM filename.
    """
    pngname = png_filename(hashkey)
    ppmhandle, ppmname = tempfile.mkstemp()
    os.close(ppmhandle)
    error = os.system('pngtopnm "%s" > "%s"' % (pngname, ppmname))
    if error:
        makedirs(png_path(hashkey, 'error'))
        errorname = png_filename(hashkey, 'error')
        os.system('mv "%s" "%s"' % (pngname, errorname))
        raise Fault(415,
            "Could not decode uploaded PNG file (hashkey %s)." % hashkey)
    if not os.path.exists(ppmname):
        raise Fault(500, "Decoded screenshot file not found.")
    if os.path.getsize(ppmname) == 0:
        raise Fault(500, "Decoded screenshot file is empty.")
    return ppmname


def read_pnm_header(ppmname):
    """
    Try to read PNM header from decoded screenshot.
    """
    header = file(ppmname, 'rb').read(1024)
    match = HEADER_MATCH(header)
    if match is None:
        raise Fault(500,
            "Could not read PNM header after decoding uploaded PNG file.")
    return (
        match.group(1),
        int(match.group(2)),
        int(match.group(3)),
        )


def scale(ppmname, width, hashkey):
    """
    Make small preview image from uploaded screenshot.
    """
    makedirs(png_path(hashkey, size=width))
    pngname = png_filename(hashkey, size=width)
    error = os.system('pnmscale -width=%d "%s" | pnmtopng > %s' %
                      (width, ppmname, pngname))
    if error:
        raise Fault(500,
            "Could not create scaled preview image.")


def s3_upload(hashkey, size=ORIGINAL_SIZE):
    """
    Upload a screenshot PNG file to Amazon S3.

    This uses httplib directly and transfers the file in small chunks,
    so we don't have to load the whole PNG file into RAM.
    """

    from shotserver04.screenshots import s3
    aws = s3.AWSAuthConnection(
        settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
        is_secure=False)
    s3_bucket = settings.S3_BUCKETS[str(size)]
    s3_key = hashkey + '.png'
    server = s3.DEFAULT_HOST
    method = 'PUT'
    path = '/%s/%s' % (s3_bucket, urllib.quote_plus(s3_key))

    filename = png_filename(hashkey, size)
    f = file(filename, 'rb')
    f.seek(0, 2) # os.SEEK_END for Python < 2.5
    bytes_total = f.tell()
    f.seek(0, 0) # os.SEEK_SET for Python < 2.5

    headers = {
        'User-Agent': 'shotserver/0.4',
        'Host': server,
        'x-amz-acl': 'public-read',
        'Content-Type': 'image/png',
        'Content-Length': str(bytes_total),
        }
    query_args = {}
    aws._add_aws_auth_header(headers, method, s3_bucket, s3_key, query_args)

    host = '%s:%d' % (server, 80)
    conn = httplib.HTTPConnection(host)
    conn.putrequest(method, path)
    for header_key, header_value in headers.iteritems():
        conn.putheader(header_key, header_value)
    conn.endheaders()

    bytes_sent = 0
    while True:
        bytes = f.read(BUFFER_SIZE)
        if not bytes:
            break
        conn.send(bytes)
        bytes_sent += len(bytes)
        # print 'sent', bytes_sent, 'of', bytes_total, 'bytes',
        # print '(%.1f%%)' % (100.0 * bytes_sent / bytes_total)
    assert bytes_sent == bytes_total
    f.close()

    response = conn.getresponse()
    if response.status != 200:
        raise Fault(response.status, response.read())
    # print 'http://%s/%s' % (s3_bucket, s3_key)

    # Write response from S3 to tempfile for debugging
    if DEBUG_HEADERS and str(size) == '160':
        tempfile = file('/tmp/%s.txt' % hashkey, 'w')
        tempfile.write('==== Request headers ====\n')
        tempfile.write('%s %s HTTP/1.1\n' % (method, path))
        for header, value in headers.iteritems():
            tempfile.write('%s: %s\n' % (header, value))
        tempfile.write('\n')
        tempfile.write('==== Response headers ====\n')
        tempfile.write('HTTP/1.1 %s %s\n' % (response.status, response.reason))
        for header, value in response.getheaders():
            tempfile.write('%s: %s\n' % (header, value))
        tempfile.write('\n')
        tempfile.write(response.read())
        # tempfile.write(response.msg)
        tempfile.close()

    conn.close()
