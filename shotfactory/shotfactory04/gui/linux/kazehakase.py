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

__revision__ = "$Rev: 2568 $"
__date__ = "$Date: 2008-01-17 13:32:32 -0300 (qui, 17 jan 2008) $"
__author__ = "$Author: hawk $"


import os
from shotfactory04.gui import linux as base


class Gui(base.Gui):
    """
    Special functions for Kazehakase.
    """

    def reset_browser(self):
        """
        Delete browser cache.
        """
        home = os.environ['HOME']
        self.delete_if_exists(os.path.join(
            home, '.kazehakase', 'mozilla', '*', 'Cache'))
        self.delete_if_exists(os.path.join(
            home, '.kazehakase', 'mozilla', '*', 'history.dat'))
        self.delete_if_exists(os.path.join(
            home, '.kazehakase', 'mozilla', '*', 'cookies.txt'))
        self.delete_if_exists(os.path.join(
            home, '.kazehakase', 'favicon'))

    def focus_browser(self):
        """
        Focus on the browser window.
        """
        self.shell('xte "mousemove 200 4"')
        self.shell('xte "mouseclick 1"')
        self.shell('xte "key Tab"')
        self.shell('xte "key Tab"')
