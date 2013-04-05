#!/usr/bin/env python
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
Kill crashed Apache processes. Useful as an hourly cronjob.
"""

__revision__ = "$Rev: 2961 $"
__date__ = "$Date: 2008-08-14 05:24:45 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import sys
import os
from glob import glob
import urllib
import re

SERVER_STATUS_URL = 'http://api.browsershots.org/server-status'
process_match = re.compile(r'<tr><td><b>\d+-\d+</b></td><td>(\d+)</td>').match
seconds_match = re.compile(r'</td><td>[\d\.]+</td><td>(\d+)</td>').match

# Get active processes
active = set()
status = urllib.urlopen(SERVER_STATUS_URL)
pid = None
seconds = {}
for line in status:
    previous_pid = pid
    pid = None
    if previous_pid:
        match = seconds_match(line)
        if match:
            seconds[previous_pid] = (
                seconds.get(previous_pid, 0) + int(match.group(1)))
    else:
        match = process_match(line)
        if match:
            pid = int(match.group(1))
            active.add(pid)

# Get all processes and parents
parents = set()
processes = []
for filename in glob('/proc/*/stat'):
    if not os.path.isfile(filename):
        continue
    parts = file(filename).read().split()
    pid, comm, state, ppid = parts[:4]
    if comm != '(apache2)':
        continue
    parents.add(int(ppid))
    utime, stime, cutime, cstime = parts[13:17]
    starttime, vsize, rss = parts[21:24]
    processes.append((starttime, int(pid), comm, state, ppid, utime, stime))
processes.sort()

for starttime, pid, comm, state, ppid, utime, stime in processes:
    print pid, comm, state, ppid, utime, stime, starttime,
    if pid in parents:
        print 'parent'
    elif pid in active and seconds[pid] > 20000:
        os.system('kill -9 %d' % pid)
        print 'KILLED', seconds[pid]
    elif pid in active:
        print 'active', seconds[pid]
    elif utime == stime == '0':
        print 'idle'
    else:
        os.system('kill -9 %d' % pid)
        print 'KILLED'
