#!/usr/bin/env python
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
Filter lines starting at a specified date, useful for SQL dumps.
"""

__revision__ = "$Rev: 2959 $"
__date__ = "$Date: 2008-08-14 05:05:48 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import sys
import re

min_date = sys.argv[-1]
date_search = re.compile(r'(20\d\d-\d\d-\d\d)').search
assert date_search(min_date) is not None

for line in sys.stdin:
    line = line.rstrip()
    match = date_search(line)
    if match is not None:
        date = match.group(1)
        if date < min_date:
            continue
    print line
