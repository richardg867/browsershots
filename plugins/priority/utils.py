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
Helper functions for priority app.
"""

__revision__ = "$Rev: 2963 $"
__date__ = "$Date: 2008-08-14 06:43:06 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from datetime import datetime


def expiration_date(activated, months):
    """
    >>> expiration_date(datetime(2008, 1, 1), 1)
    datetime.datetime(2008, 2, 1, 0, 0)
    >>> expiration_date(datetime(2008, 1, 2), 1)
    datetime.datetime(2008, 2, 2, 0, 0)
    >>> expiration_date(datetime(2008, 1, 29), 1)
    datetime.datetime(2008, 2, 29, 0, 0)
    >>> expiration_date(datetime(2008, 1, 30), 1)
    datetime.datetime(2008, 2, 29, 0, 0)
    >>> expiration_date(datetime(2008, 1, 31), 1)
    datetime.datetime(2008, 2, 29, 0, 0)
    >>> expiration_date(datetime(2008, 12, 31), 1)
    datetime.datetime(2009, 1, 31, 0, 0)
    >>> expiration_date(datetime(2008, 1, 1), 12)
    datetime.datetime(2009, 1, 1, 0, 0)
    >>> expiration_date(datetime(2008, 12, 31), 12)
    datetime.datetime(2009, 12, 31, 0, 0)
    >>> expiration_date(datetime(2008, 2, 29), 12)
    datetime.datetime(2009, 2, 28, 0, 0)
    """
    year, month, day, hour, minute, sec = activated.timetuple()[:6]
    month += months
    if month > 12:
        year += 1
        month -= 12
    while True:
        try:
            return datetime(year, month, day, hour, minute, sec)
        except ValueError:
            if day <= 28:
                raise
            day -= 1 # February 31st doesn't exist, reduce and try again.


if __name__ == '__main__':
    import doctest
    doctest.testmod()
