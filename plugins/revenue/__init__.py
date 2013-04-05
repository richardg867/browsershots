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
Utility functions for revenue sharing.
"""

__revision__ = "$Rev: 2935 $"
__date__ = "$Date: 2008-07-21 17:25:28 -0300 (seg, 21 jul 2008) $"
__author__ = "$Author: johann $"

from datetime import datetime
from shotserver04.priority.models import UserPriority


def month_priorities(year, month):
    return UserPriority.objects.filter(
        activated__year=year,
        activated__month=month)


def month_revenue(year, month):
    """
    Get the total monthly shared revenue, in Euros.
    """
    return float(sum([p.euros for p in month_priorities(year, month)])) / 2
