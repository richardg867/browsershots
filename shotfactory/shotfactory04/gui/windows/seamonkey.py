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
GUI-specific interface functions for SeaMonkey on Microsoft Windows.
"""

__revision__ = "$Rev: 3048 $"
__date__ = "$Date: 2008-09-02 18:58:56 -0300 (ter, 02 set 2008) $"
__author__ = "$Author: johann $"

import os
import time
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory04.gui import windows


class Gui(windows.Gui):
    """
    Special functions for SeaMonkey on Windows.
    """

    def reset_browser(self):
        """
        Delete previous session and browser cache.
        """
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0)
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Profiles', '*', 'Cache'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'SeaMonkey', 'Profiles', '*', 'Cache'))
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Profiles', 'default', '*', 'history.dat'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Profiles', 'default', '*', 'cookies.txt'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'SeaMonkey', 'Profiles', '*', 'history.dat'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'SeaMonkey', 'Profiles', '*', 'cookies.txt'))

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        command = config['command'] or r'c:\progra~1\mozilla.org\seamon~1\seamonkey.exe'
        print 'running', command
        try:
            import subprocess
        except ImportError:
            os.spawnl(os.P_DETACH, command, os.path.basename(command), url)
        else:
            subprocess.Popen([command, url])
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait)

    def find_scrollable(self):
        """Find scrollable window."""
        seamonkey = self.find_window_by_title_suffix(' SeaMonkey')
        return self.get_child_window(seamonkey)


# Test scrolling from command line
if __name__ == '__main__':
    config = {
        'width': 1024,
        'bpp': 24,
        }

    class Options:
        verbose = 3

    gui = Gui(config, Options())
    gui.down()
    time.sleep(1)
    gui.scroll_bottom()
