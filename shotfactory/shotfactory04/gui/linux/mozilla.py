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

__revision__ = "$Rev: 2560 $"
__date__ = "$Date: 2008-01-16 11:58:43 -0300 (qua, 16 jan 2008) $"
__author__ = "$Author: hawk $"


import os
from shotfactory04.gui import linux as base


class Gui(base.Gui):
    """
    Special functions for Mozilla.
    """

    def reset_browser(self):
        """
        Delete crash dialog and browser cache.
        """
        home = os.environ['HOME']
        for profile_name in ('default', 'mozilla*'):
            self.delete_if_exists(os.path.join(
                home, '.mozilla', profile_name, '*', 'Cache'))
            self.delete_if_exists(os.path.join(
                home, '.mozilla', profile_name, '*', 'history.dat'))
            self.delete_if_exists(os.path.join(
                home, '.mozilla', profile_name, '*', 'cookies.txt'))
