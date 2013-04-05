#!/usr/bin/env python
# kill_memory_hogs.py - Kill runaway processes
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
This is a useful workaround when some processes start to misbehave. It
checks the virtual memory size and kills processes that are over the
limit. The default limit is 400 MiB, but you can specify a different
size on the command line.

To check for processes over 300 MiB once every minute, add the
following line to your /etc/crontab:
* *     * * *   root    kill_memory_hogs.py 300

Make sure that line comes after the following in /etc/crontab, and
that this script (or a symlink to it) is in one of these folders:
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
"""

__revision__ = "$Rev: 1464 $"
__date__ = "$Date: 2007-06-08 22:12:43 +0200 (Fri, 08 Jun 2007) $"
__author__ = "$Author: johann $"

import sys
import commands

if len(sys.argv) == 2:
    MAXIMUM_VIRTUAL_SIZE = int(sys.argv[-1]) # mebibytes
else:
    MAXIMUM_VIRTUAL_SIZE = 400 # mebibytes

processes = commands.getoutput('ps -eo vsize=,pid=,args=')
for process in processes.splitlines():
    parts = process.split()
    if len(parts) < 3:
        print 'expected 3 or more words:', process
        continue
    if parts[0].isdigit():
        vsize = int(parts[0])
    else:
        print 'expected integer for first word:', process
        continue
    if parts[1].isdigit():
        pid = int(parts[1])
    else:
        print 'expected integer for second word:', process
        continue
    megs = vsize / 1024.0
    if megs <= MAXIMUM_VIRTUAL_SIZE:
        continue
    rest = ' '.join(parts[2:])
    text = '%s (%.1f MiB, pid %d)' % (rest, megs, pid)
    status, output = commands.getstatusoutput('kill -9 %d' % pid)
    if status:
        print 'could not kill', text
        print output
    else:
        print 'killed', text
