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
GUI-specific interface functions for Mozilla Firefox on Microsoft Windows.
"""

__revision__ = "$Rev: 2919 $"
__date__ = "$Date: 2008-07-03 10:02:57 -0300 (qui, 03 jul 2008) $"
__author__ = "$Author: hawk $"

import os
import time
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory04.gui import windows


class Gui(windows.Gui):
    """
    Special functions for Firefox on Windows.
    """

    def reset_browser(self):
        """
        Delete previous session and browser cache.
        """
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0)
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Firefox', 'Profiles', '*', 'Cache'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Firefox', 'Profiles', '*', 'urlclassifier3.sqlite'))
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Firefox', 'Profiles', '*', 'sessionstore.js'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Firefox', 'Profiles', '*', 'history.dat'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Firefox', 'Profiles', '*', 'cookies.txt'))
        self.delete_if_exists(os.path.join(
            appdata, 'Mozilla', 'Firefox', 'Profiles', '*', 'urlclassifier*.sqlite'))

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        command = config['command'] or r'c:\progra~1\mozill~1\firefox.exe'
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
        firefox = self.find_window_by_title_suffix(' Firefox')
        return self.get_child_window(firefox)


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
