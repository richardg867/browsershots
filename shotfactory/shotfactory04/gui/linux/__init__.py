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
GUI-specific interface functions for X11.
"""

__revision__ = "$Rev: 2690 $"
__date__ = "$Date: 2008-02-13 17:16:36 -0300 (qua, 13 fev 2008) $"
__author__ = "$Author: johann $"


import os
import time
from shotfactory04 import gui as base


class Gui(base.Gui):
    """
    Special functions for the X11 screen.
    """

    def prepare_screen(self):
        """
        Start a VNC server with requested resolution.
        """
        command = ('vncserver %s -geometry %dx%d -depth %d -dpi %d'
                   % (self.display, self.width, self.height,
                      self.bpp, self.dpi))
        if self.rfbport is not None:
            command = '%s -rfbport %d' % (command, self.rfbport)
        attempts = 3
        for attempt in range(attempts):
            error = self.shell(command)
            if not error:
                break
            print "vncserver error (attempt %d out of %d)" % (
                attempt + 1, attempts)
            if attempt + 1 < attempts:
                time.sleep(5)
        if error:
            self.force_quit_vnc_server()
            raise RuntimeError("could not start vncserver")
        # Move the mouse cursor out of the way
        self.shell('xte "mousemove 400 0"')

    def force_quit_vnc_server(self):
        """
        Try to kill old VNC server on my display.
        """
        print "Trying to kill old VNC server"
        self.shell('vncserver -kill %s' % self.display)
        time.sleep(3)
        self.shell('killall -q -9 vncserver')
        host, numeric = self.display.rsplit(':', 1)
        numeric = int(numeric)
        self.delete_if_exists('/tmp/.X%d-lock' % numeric)
        self.delete_if_exists('/tmp/.X11-unix/X%d' % numeric)

    def shell(self, command):
        """Run a shell command on my display."""
        command = 'DISPLAY=%s %s' % (self.display, command)
        if self.verbose < 3:
            if command.endswith('&'):
                command = command[:-1].rstrip() + ' >/dev/null 2>/dev/null &'
            else:
                command += ' >/dev/null 2>/dev/null'
        else:
            print command
        return os.system(command)

    def scroll_top(self):
        """Scroll to the top."""
        self.shell('xte "key Home"')

    def scroll_bottom(self):
        """Scroll to the bottom."""
        self.shell('xte "key End"')

    def pageup(self):
        """Scroll up by one screen page."""
        self.shell('xte "key Page_Up"')

    def pagedown(self):
        """Scroll down by one screen page."""
        self.shell('xte "key Page_Down"')

    def up(self):
        """Scroll up by one line."""
        self.shell('xte "key Up"')

    def down(self):
        """Scroll down by one line."""
        self.shell('xte "key Down"')

    def close_window(self):
        """Close the active window."""
        self.shell('xte "keydown Alt_L"')
        self.shell('xte "key F4"')
        self.shell('xte "keyup Alt_L"')

    def maximize(self):
        """Maximize the active window."""
        self.shell('xte "keydown Alt_L"')
        self.shell('xte "key F10"')
        self.shell('xte "keyup Alt_L"')

    def screenshot(self, filename):
        """
        Save the full screen to a PPM file.
        """
        error = self.shell('scrot "%s"' % filename)
        if error:
            raise RuntimeError("screenshot failed")

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        command = config['command'] or config['browser'].lower()
        command = '%s "%s" &' % (command, url)
        print "Running", command
        error = self.shell(command)
        if error:
            raise RuntimeError("could not start the browser")
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait - 10)
        self.maximize()
        time.sleep(10)

    def close(self):
        """
        Shut down the VNC server.
        """
        self.shell('vncserver -kill %s' % self.display)
        time.sleep(1)
        self.shell('killall -q -9 nspluginviewer')
        self.shell('killall -q -9 klauncher')
        self.shell('killall -q -9 dcopserver')
        self.shell('killall -q -9 kio_http')
        self.shell('killall -q -9 artsd')
