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
Make screenshots and combine them into one tall image.
"""

__revision__ = "$Rev: 2006 $"
__date__ = "$Date: 2007-08-19 21:32:52 -0300 (dom, 19 ago 2007) $"
__author__ = "$Author: johann $"

import platform
import optparse
import time


def _main():
    from optparse import OptionParser
    version = '%prog ' + __revision__.strip('$').replace('Rev: ', 'r')
    parser = OptionParser(version=version)
    parser.add_option("-d", dest="display", action="store", type="string",
                      metavar="<name>", default=":0",
                      help="run on a different display (default :0)")
    parser.add_option("-w", dest="wait", action="store", type="int",
                      metavar="<seconds>", default=5,
                      help="wait before taking screenshots (default 5)")
    (options, args) = parser.parse_args()
    config = {'width': 1024, 'bpp': 32}

    system = platform.system()
    if system == 'Linux':
        from shotfactory04.gui import linux
        gui = linux.Gui(config, options)
    else:
        raise NotImplemented(system)

    print "Waiting %d seconds, please activate your browser window..." \
          % options.wait
    time.sleep(options.wait)
    gui.browsershot()

if __name__ == '__main__':
    _main()
