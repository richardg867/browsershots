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
GUI-specific interface functions for Internet Explorer on Microsoft Windows.
"""

__revision__ = "$Rev: 2754 $"
__date__ = "$Date: 2008-04-11 22:06:52 -0300 (sex, 11 abr 2008) $"
__author__ = "$Author: johann $"

import os
import time
import _winreg
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory04.gui import windows


class Gui(windows.Gui):
    """
    Special functions for MSIE on Windows.
    """

    def reset_browser(self):
        """
        Delete all files from the browser cache.
        """
        cache = shell.SHGetFolderPath(0, shellcon.CSIDL_INTERNET_CACHE, 0, 0)
        cache = os.path.join(cache, 'Content.IE5')
        if not os.path.exists(cache):
            return
        if self.verbose:
            print 'deleting cache', cache
        for filename in os.listdir(cache):
            if filename.lower() != 'index.dat':
                self.delete_if_exists(os.path.join(cache, filename))

    def check_version_override(self, major, minor):
        """
        Raise RuntimeError if conditional comments will be broken.
        """
        root_key = _winreg.HKEY_LOCAL_MACHINE
        key_name = r'Software\Microsoft\Internet Explorer\Version Vector'
        try:
            key = _winreg.OpenKey(root_key, key_name)
            registered = _winreg.QueryValueEx(key, 'IE')[0]
            key.Close()
        except EnvironmentError:
            return
        expected_minor = '%d' % minor
        registered_minor = registered.split('.')[1]
        while len(expected_minor) < len(registered_minor):
            requested_minor += '0'
        requested = '%d.%d' % (major, requested_minor)
        if registered != requested:
            print "This registry key overrides the browser version:"
            print r"HKEY_LOCAL_MACHINE\%s\IE" % key_name
            print "Requested version: %s, Registry override: %s" % (
                requested, registered)
            print "Please rename or delete the key 'IE' with regedit."
            raise RuntimeError("browser version override in the registry")

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        self.major = config['major']
        self.check_version_override(config['major'], config['minor'])
        command = config['command'] or r'c:\progra~1\intern~1\iexplore.exe'
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
        """
        Find the scrollable window.
        """
        if self.major < 5:
            ieframe = self.find_window_by_classname('CabinetWClass')
        else:
            ieframe = self.find_window_by_classname('IEFrame')
        frametab = self.find_child_window_by_classname(
            ieframe, "Frame Tab")
        if frametab:
            ieframe = frametab
        tabs = self.find_child_window_by_classname(
            ieframe, "TabWindowClass")
        if tabs:
            ieframe = tabs
        return self.find_child_window_by_classname(
            ieframe, "Shell DocObject View")


# Test scrolling from command line
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
    gui.down()
    time.sleep(1)
    gui.scroll_bottom()
