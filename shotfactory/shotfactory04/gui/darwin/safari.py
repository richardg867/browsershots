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
GUI-specific functions for Safari on Mac OS X.
"""

__revision__ = "$Rev: 2470 $"
__date__ = "$Date: 2007-12-10 10:12:17 -0300 (seg, 10 dez 2007) $"
__author__ = "$Author: johann $"

import os
import time
import appscript
import MacOS
from shotfactory04.gui import darwin as base

MIN_WAIT = 10 # seconds
# Shotfactory will auto-detect when Safari is ready
# if it says it's finished loading for 10 seconds.


def retry(func, *args, **kwargs):
    retry = 5
    while retry > 0:
        try:
            return func(*args, **kwargs)
        except (appscript.CommandError, AttributeError), error:
            print error
        print "Safari not ready, retrying in 3 seconds..."
        time.sleep(3)
        retry -= 1
    raise RuntimeError("could not run appscript in Safari")


class Gui(base.Gui):
    """
    Special functions for Safari on Mac OS X.
    """

    def reset_browser(self):
        """
        Delete crash dialog and browser cache.
        """
        home = os.environ['HOME']
        self.delete_if_exists(os.path.join(
            home, 'Library', 'Caches', 'Safari'))
        self.delete_if_exists(os.path.join(
            home, 'Library', 'Safari', 'Icons'))
        self.delete_if_exists(os.path.join(
            home, 'Library', 'Safari', 'History.plist'))
        self.delete_if_exists(os.path.join(
            home, 'Library', 'Cookies', 'Cookies.plist'))

    def js(self, command):
        """Run JavaScript in Safari."""
	try:
            return retry(self.safari.do_JavaScript,
                         command, in_=self.safari.documents[0])
        except RuntimeError:
            self.close()
            raise

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        try:
            self.safari = appscript.app('Safari')
            retry(self.safari.activate)
        except MacOS.Error, error:
            code, message = error
            raise RuntimeError(message)
        except RuntimeError:
            self.close()
            raise
        time.sleep(0.1)
        self.js("window.moveTo(0,0)")
        time.sleep(0.1)
        self.js("window.resizeTo(screen.availWidth,screen.availHeight)")
        time.sleep(0.1)
        self.js("document.location='%s'" % url)
        ready_count = 0
        max_wait = time.time() + 60
        while time.time() < max_wait:
            time.sleep(1)
            if self.ready_state():
                ready_count += 1
                print ready_count,
                if ready_count >= MIN_WAIT:
                    break
            elif ready_count:
                print 'still loading'
                ready_count = 0
        if ready_count >= MIN_WAIT:
            print 'done'
        elif ready_count:
            print 'timeout'
        return True

    def ready_state(self):
        """Get progress indicator."""
        state = self.js("document.readyState")
        # print state
        return state == 'complete'

    def scroll_down(self, pixels):
        """Scroll down by specified number of pixels."""
        self.js('window.scrollBy(0,%d)' % pixels)

    def scroll_bottom(self):
        """Scroll to the bottom of the page."""
        self.js('window.scrollTo(0,99999)')

    def close(self):
        """Close Safari."""
        base.Gui.close(self)
        self.shell('killall Safari > /dev/null 2>&1')
