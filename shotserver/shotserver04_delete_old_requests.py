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
Delete old PNG files.
"""

__revision__ = "$Rev: 2960 $"
__date__ = "$Date: 2008-08-14 05:07:00 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
import sys
import time
from shotserver04.requests.models import RequestGroup
from datetime import datetime, timedelta


if __name__ == '__main__':
    groups = RequestGroup.objects.filter(
        user__isnull=True).order_by('submitted')[:1000]
    print groups.query.as_sql()
    for index, group in enumerate(groups):
        if datetime.now() - group.submitted < timedelta(hours=48):
            break
        print chr(13), index, group.id, group.submitted, '    ',
        group.delete()
    print
