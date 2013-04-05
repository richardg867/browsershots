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
Simple queue on local filesystem (or NFS).
"""

__revision__ = "$Rev: 2453 $"
__date__ = "$Date: 2007-12-09 13:13:51 -0300 (dom, 09 dez 2007) $"
__author__ = "$Author: johann $"

import os
import re
import time
from xmlrpclib import Fault
from shotfactory04.servers import Server

EXPIRE_SECONDS = 300 # request lock expiration timeout
LOCKTIME_FORMAT = '%y%m%d-%H%M%S'
INTEGER_KEYS = 'width height bpp major minor'.split()

config_line_match = re.compile(r'(\w+)\s*(.*)').match


class FileSystemServer(Server):
    """
    Simple queue on local filesystem (or NFS).
    """

    def __init__(self, options):
        Server.__init__(self, options)
        self.factory = options.factory
        self.queue = options.queue
        self.output = options.output
        self.resize = options.resize_output

    def parse_locktime(self, filename):
        """
        Parse the lock timestamp from the filename.
        """
        parts = filename.split('-')
        timestamp = '-'.join(parts[-2:])
        try:
            return time.mktime(time.strptime(timestamp, LOCKTIME_FORMAT))
        except ValueError:
            return time.time()

    def get_oldest_filename(self):
        """
        Find the oldest file in the queue (by mtime) that isn't locked yet.
        """
        mtimes = []
        expire = time.time() - EXPIRE_SECONDS
        for filename in os.listdir(self.queue):
            fullpath = os.path.join(self.queue, filename)
            if not os.path.isfile(fullpath):
                continue
            if 'locked' in filename:
                locktime = self.parse_locktime(filename)
                if locktime > expire:
                    continue
            try:
                mtime = os.stat(fullpath).st_mtime
            except OSError:
                continue
            mtimes.append((mtime, filename))
        if not len(mtimes):
            return None
        mtimes.sort()
        return mtimes[0][1]

    def poll(self):
        """
        Get the next screenshot request from the queue.
        """
        while True:
            oldest = self.get_oldest_filename()
            if oldest is None:
                raise Fault(204, 'No matching request.')
            filename = oldest
            pos = filename.find('-locked-')
            if pos > -1:
                filename = filename[:pos]
            self.request_filename = '-'.join((
                filename, 'locked', self.factory,
                time.strftime(LOCKTIME_FORMAT)))
            fullpath = os.path.join(self.queue, self.request_filename)
            try:
                os.rename(os.path.join(self.queue, oldest), fullpath)
            except OSError:
                continue # Somebody else locked this request already.
            config = {
                'filename': filename,
                'browser': 'Firefox',
                'width': 1024,
                'bpp': 24,
                'command': '',
                }
            for line in open(fullpath).readlines():
                line = line.strip()
                if not len(line):
                    continue
                match = config_line_match(line)
                if match is None:
                    raise Fault(500, 'Bad request line "%s" in %s.' %
                                (line, self.request_filename))
                key, value = match.groups()
                if key in INTEGER_KEYS:
                    value = int(value)
                config[key] = value
            if 'request' not in config:
                config['request'] = config['filename']
            return config

    def get_request_url(self, config):
        """
        Get the URL for the screenshot request.
        """
        return config['url']

    def upload_png(self, config, pngfilename):
        """
        Store PNG file in the output folder(s), possibly resizing it.
        """
        filename = config['request'] + '.png'
        for width, folder in self.resize:
            os.system('pngtopnm "%s" | pnmscale -width %d | pnmtopng > "%s"' %
                      (pngfilename, width, os.path.join(folder, filename)))
        bytes = os.path.getsize(pngfilename)
        if self.output:
            os.rename(pngfilename, os.path.join(self.output, filename))
        os.unlink(os.path.join(self.queue, self.request_filename))
        return bytes
