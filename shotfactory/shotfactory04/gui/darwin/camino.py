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
GUI-specific functions for Camino on Mac OS X.
You need to set "browser.sessionstore.resume_from_crash" to "false" in about:config
"""

__revision__ = "$Rev: 3048 $"
__date__ = "$Date: 2008-09-02 18:58:56 -0300 (ter, 02 set 2008) $"
__author__ = "$Author: johann $"

import os
import time
import appscript
import MacOS
from shotfactory04.gui import darwin as base


class Gui(base.Gui):
    """
    Special functions for Camino on Mac OS X.
    """

    def reset_browser(self):
        """
        Delete browser cache.
        """
        home = os.environ['HOME']
        self.delete_if_exists(os.path.join(
            home, 'Library', 'Caches', 'Camino', 'Cache'))
        self.delete_if_exists(os.path.join(
            home, 'Library', 'Application Support', 'Camino',
            'WindowState.plist'))

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        try:
            self.sysevents = appscript.app('System Events')
        except MacOS.Error, error:
            code, message = error
            raise RuntimeError(message)
        if not self.sysevents.UI_elements_enabled():
            print "Please enable access for assistive devices"
            print "in System Preferences -> Universal Access"
            print "http://www.apple.com/applescript/uiscripting/01.html"
            raise RuntimeError("AppleScript for UI elements not enabled")
        binary = '/Applications/Camino.app/Contents/MacOS/Camino'
        self.shell('%s -url "%s" &' % (binary, url))
        time.sleep(5)
        self.camino_bin = self.sysevents.processes['Camino']
        print "maximizing window"
        retry = 3
        while True:
            try:
                self.camino_bin.frontmost.set(True)
                self.window = self.camino_bin.windows[1]
                self.window.position.set((0, 22))
                self.window.size.set((self.width, self.height - 26))
                break
            except (appscript.CommandError, AttributeError):
                print "Camino not ready, retrying in 10 seconds..."
                time.sleep(10)
                retry -= 1
            if not retry:
                raise RuntimeError("AppleScript for Camino failed")
        time.sleep(options.wait)
        return True

    def down(self):
        """Scroll down one line."""
        self.sysevents.key_code(125)
        time.sleep(0.1)

    def scroll_bottom(self):
        """Scroll down to the bottom of the page."""
        self.sysevents.key_code(119)
        time.sleep(0.2)

    def close(self):
        """Close browser and helper programs."""
        base.Gui.close(self)
        self.shell('killall Camino > /dev/null 2>&1')
