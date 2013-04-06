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
GUI-specific interface functions for Microsoft Windows.
"""

__revision__ = "$Rev: 3047 $"
__date__ = "$Date: 2008-09-02 18:41:17 -0300 (ter, 02 set 2008) $"
__author__ = "$Author: johann $"

import os
import time
import sys
import win32api
import win32gui
import win32con
import pywintypes
import getpass
from shotfactory04 import gui as base
from shotfactory04.utils import remove_version_number, short_filename


class Gui(base.Gui):
    """
    Special functions for Windows.
    """

    def shell(self, command):
        """Run a shell command."""
        return os.system(command)

    def prepare_screen(self):
        """
        Set screen resolution with Stefan Tucker's Resolution Changer
        Freeware, available from http://www.12noon.com/reschange.htm
        """
        self.shell('reschangecon.exe -width=%u -height=%u -depth=%u > NUL'
                   % (self.width, self.height, self.bpp))
        # Move the mouse cursor out of the way
        win32api.SetCursorPos((0, 0))

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        import ImageGrab
        import PpmImagePlugin
        im = ImageGrab.grab()
        outfile = open(filename, 'wb')
        im.save(outfile, 'PPM')
        outfile.close()

    def start_browser(self, config, url, options):
        """Start browser and load website."""
        command = config['command']
        print 'running', command
        os.spawnl(os.P_DETACH, command, os.path.basename(command), url)
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait)

    def close(self):
        """Close the browser."""
        # win32gui.PostMessage(self.msie_window, win32con.WM_CLOSE, 0, 0)
        username = getpass.getuser()
        process_names = (
            'iexplore.exe',
            'chrome.exe',
            'firefox.exe',
            'safari.exe',
            'opera.exe',
            'dwwin.exe',
            'dw15.exe',
            'iedw.exe',
            'telnet.exe',
            'msimn.exe',
            'seamonkey.exe',
            'k-meleon.exe',
            'flock.exe',
            'navigator.exe',
            'maxthon.exe',
            'avant.exe',
            'dillo.exe',
            'luna.exe',
            )
        for name in process_names:
            # Kill all processes matching name, using
            # pv.exe from teamcti.com (freeware):
            # http://www.teamcti.com/pview/prcview.htm
            os.system('pv.exe -kf -y%s %s "2>nul" > nul' % (username, name))
            short = short_filename(name)
            if short != name:
                os.system('pv.exe -kf -y%s %s "2>nul" > nul' % (username, short))


    def find_window_by_title_suffix(self, suffix):
        """Find a window on the desktop where the title ends as specified."""
        try:
            desktop = win32gui.GetDesktopWindow()
            if self.verbose >= 3:
                print "GetDesktopWindow() => %d" % desktop
            window = win32gui.GetWindow(desktop, win32con.GW_CHILD)
            if self.verbose >= 3:
                print "GetWindow(%d, GW_CHILD) => %d" % (desktop, window)
            while True:
                title = win32gui.GetWindowText(window)
                if self.verbose >= 3:
                    print "GetWindowText(%d) => '%s'" % (window, title)
                if remove_version_number(title).endswith(suffix):
                    break
                previous = window
                window = win32gui.GetWindow(previous, win32con.GW_HWNDNEXT)
                if self.verbose >= 3:
                    print "GetWindow(%d, GW_HWNDNEXT) => %d" % (
                        previous, window)
        except pywintypes.error:
            window = 0
        return window

    def get_child_window(self, parent):
        """Wrapper for GetWindow(parent, GW_CHILD)."""
        try:
            window = win32gui.GetWindow(parent, win32con.GW_CHILD)
        except pywintypes.error:
            window = 0
        if self.verbose >= 3:
            print "GetWindow(%d, GW_CHILD) => %d" % (parent, window)
        return window

    def find_window_by_classname(self, classname):
        """Wrapper for win32gui.FindWindow(classname, None)."""
        try:
            window = win32gui.FindWindow(classname, None)
        except pywintypes.error:
            window = 0
        if self.verbose >= 3:
            print "FindWindow('%s', None) => %d" % (classname, window)
        return window

    def find_child_window_by_classname(self, parent, classname):
        """Wrapper for win32gui.FindWindowEx(parent, 0, classname, None)."""
        try:
            window = win32gui.FindWindowEx(parent, 0, classname, None)
        except pywintypes.error:
            window = 0
        if self.verbose >= 3:
            print "FindWindowEx(%d, 0, '%s', None) => %d" % (
                parent, classname, window)
        return window

    def send_keypress(self, window, key):
        """
        Post key down and up events to the specified window.
        """
        if not window:
            return
        win32gui.PostMessage(window, win32con.WM_KEYDOWN, key)
        win32gui.PostMessage(window, win32con.WM_KEYUP, key)
        time.sleep(0.1)

    def find_scrollable(self):
        """Subclasses must override this method."""
        raise NotImplementedError(
            '%s.find_scrollable() is not implemented' % self.__class__)

    def down(self):
        """Scroll down one line."""
        self.send_keypress(self.find_scrollable(), win32con.VK_DOWN)

    def scroll_bottom(self):
        """Scroll down to the bottom of the page."""
        self.send_keypress(self.find_scrollable(), win32con.VK_END)
