#!/usr/bin/env python
# memory_hog.py - Simple test script for kill_memory_hogs.py
# Copyright (C) 2007 Johann C. Rocholl <johann@rocholl.net>
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

"""
Allocate 400 MiB of RAM and go to sleep:
# memory_hog.py 400

Then you can use the following to kill it:
# kill_memory_hogs.py 400
"""

__revision__ = "$Rev: 1464 $"
__date__ = "$Date: 2007-06-08 22:12:43 +0200 (Fri, 08 Jun 2007) $"
__author__ = "$Author: johann $"

import sys
import time
from array import array

MEGS = int(sys.argv[1])
KILOBYTE = array('B', [0] * 1024)

a = array('B')
for meg in range(MEGS):
    for i in range(1024):
        a.extend(KILOBYTE)
    sys.stdout.write(str(meg + 1) + chr(13))
    sys.stdout.flush()

while True:
    time.sleep(1)
