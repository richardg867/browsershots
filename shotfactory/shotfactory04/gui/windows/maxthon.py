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
GUI-specific interface functions for Maxthon on Microsoft Windows.
"""

__revision__ = "$Rev: 3053 $"
__date__ = "$Date: 2008-09-03 04:32:38 -0300 (qua, 03 set 2008) $"
__author__ = "$Author: johann $"

import os
import time
import win32gui
import win32con
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory04.gui import windows


class Gui(windows.Gui):
    """
    Special functions for Maxthon on Windows.
    """

    def reset_browser(self):
        """
        Delete previous session and browser cache.
        """
        # TODO: Maxthon dislikes having its user folder deleted

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        self.major = config['major']
        command = config['command'] or r'c:\progra~1\maxthon\bin\maxthon.exe'
        print 'running', command
        try:
            import subprocess
        except ImportError:
            os.spawnl(os.P_DETACH, command, os.path.basename(command), url)
        else:
            subprocess.Popen([command, url])
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait)

    def find_maximizable(self):
        """Find window to maximize."""
        return self.find_window_by_classname('Maxthon3Cls_MainFrm')

    def find_scrollable(self):
        """Find scrollable window."""
        hwnd = win32gui.WindowFromPoint((self.width/2, self.height/2))
        for dummy in range(20):
            if not hwnd:
                return None
            if self.verbose >= 3:
                print 'handle', hwnd
                print 'classname', win32gui.GetClassName(hwnd)
                print 'text', win32gui.GetWindowText(hwnd)
                print
            if win32gui.GetClassName(hwnd) == 'Maxthon3Cls_WebViewHost':
                return hwnd
            hwnd = win32gui.GetParent(hwnd)


# Test browser interface from command line                                              
if __name__ == '__main__':
    config = {
        'width': 1024,
        'height': 768,
        'bpp': 24,
        'request': 123,
        }

    class Options:
        verbose = 3
        max_pages = 7

    gui = Gui(config, Options())
    gui.maximize()
