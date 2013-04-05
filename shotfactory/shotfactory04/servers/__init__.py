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
Base class for server queue.
"""

__revision__ = "$Rev: 2261 $"
__date__ = "$Date: 2007-10-26 15:47:50 -0300 (sex, 26 out 2007) $"
__author__ = "$Author: johann $"

import platform


class Server:
    """
    Base class for server queue.
    """

    def __init__(self, options):
        self.revision = options.revision

    def get_user_agent(self):
        """
        Generate a user agent to send to the server.
        """
        return ' '.join((
            'ShotFactory/0.4', self.revision,
            'Python/%s' % (platform.python_version()),
            '%s/%s' % (platform.system(), platform.release()),
            platform.machine(),
            ))
