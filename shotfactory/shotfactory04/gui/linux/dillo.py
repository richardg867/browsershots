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

__revision__ = "$Rev: 2569 $"
__date__ = "$Date: 2008-01-17 13:50:01 -0300 (qui, 17 jan 2008) $"
__author__ = "$Author: hawk $"


from shotfactory04.gui import linux as base


class Gui(base.Gui):
    """
    Special functions for Dillo.
    """

    def reset_browser(self):
        """
        Reset crashed state and delete browser cache.
        """
        pass

    def maximize(self):
        """Maximize the active window."""
        self.focus_browser()
        self.shell('xte "keydown Alt_L"')
        self.shell('xte "key F10"')
        self.shell('xte "keyup Alt_L"')

    def focus_browser(self):
        """
        Focus on the browser window.
        """
        self.shell('xte "mousemove 200 4"')
        self.shell('xte "mouseclick 1"')
