# Copyright (c) 2008 Johann C. Rocholl <johann@browsershots.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import os
from s3tools import S3

AWS_ACCESS_KEY_ID = file(
    os.path.join(os.environ['HOME'], '.s3', 'access_key_id')
    ).readline().strip()
AWS_SECRET_ACCESS_KEY = file(
    os.path.join(os.environ['HOME'], '.s3', 'secret_access_key')
    ).readline().strip()

conn = S3.AWSAuthConnection(
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
generator = S3.QueryStringAuthGenerator(
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)


def url(bucket, key=''):
    return 's3://%s/%s' % (bucket, key)


def usage(expected=None, message=None):
    if expected is None:
        print "usage:", os.path.basename(sys.argv[0])
    else:
        print "usage:", os.path.basename(sys.argv[0]), expected
    if message:
        print "error:", message
    sys.exit(1)


def parse_url(expected, url):
    parts = url.split('/', 3)
    if len(parts) < 3 or parts[0] != 's3:' or parts[1] or not parts[2]:
        usage(expected, "Not a valid S3 URL: '%s'." % url)
    return parts[2:]


def parse_bucket(expected, url):
    parts = parse_url(expected, url)
    if len(parts) > 1 and parts[1]:
        usage(expected, "Unexpected object key: '%s'." % parts[1])
    return parts[0]


def parse_bucket_key(expected, url):
    parts = parse_url(expected, url)
    if len(parts) < 2:
        usage(expected, "Missing object key: '%s'." % url)
    return parts


def argv_empty():
    if len(sys.argv) > 1:
        usage(None, "Unexpected arguments.")


def argv_buckets():
    expected = 's3://<bucket>/ [...]'
    if len(sys.argv) < 2:
        usage(expected, "Missing argument.")
    result = []
    for argument in sys.argv[1:]:
        result.append(parse_bucket(expected, argument))
    return result


def argv_bucket_keys():
    expected = 's3://<bucket>/<key> [...]'
    if len(sys.argv) < 2:
        usage(expected, "Missing argument.")
    result = []
    for argument in sys.argv[1:]:
        result.append(parse_bucket_key(expected, argument))
    return result


def argv_filenames_bucket():
    expected = '<filename> [...] s3://<bucket>/'
    if len(sys.argv) < 3:
        usage(expected, "Missing argument.")
    bucket = parse_bucket(expected, sys.argv[-1])
    result = []
    for filename in sys.argv[1:-1]:
        if not os.path.exists(filename):
            usage(expected, "File not found: '%s'." % filename)
        result.append(filename)
    return result, bucket
