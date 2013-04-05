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
Share last month's revenue from priority processing.
"""

__revision__ = "$Rev: 2962 $"
__date__ = "$Date: 2008-08-14 06:41:44 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import sys
import os
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from shotserver04.factories.models import Factory, ScreenshotCount
from shotserver04.revenue import month_revenue
from shotserver04.revenue.models import UserRevenue, latest_balance

year = int(sys.argv[1])
month = int(sys.argv[2])

next_year = year
next_month = month + 1
if next_month == 13:
    next_month = 1
    next_year += 1

date = datetime(next_year, next_month, 1, 0, 0, 0)
counts = ScreenshotCount.objects.filter(
    date__gte='%04d-%02d-01' % (year, month),
    date__lt='%04d-%02d-01' % (next_year, next_month),
    )
total_screenshots = sum([c.screenshots for c in counts])
total_revenue = month_revenue(year, month)

for user in User.objects.all():
    screenshots = sum([c.screenshots
                       for c in counts.filter(factory__admin=user)])
    percent = 100.0 * screenshots / total_screenshots
    revenue = total_revenue * screenshots / total_screenshots
    euros = Decimal('%.2f' % revenue)
    if euros < Decimal('0.01'):
        euros = Decimal('0.01')
    balance = latest_balance(user, before=date) + euros
    existing = UserRevenue.objects.filter(
        user=user,
        year=year,
        month=month)
    if not screenshots:
        existing.delete()
        continue
    print screenshots, '%.3f%%' % percent, '%.2f' % euros, user,
    if len(existing) == 1:
        existing[0].update_fields(
            screenshots=screenshots, percent=percent,
            euros=euros, balance=balance, date=date)
        print 'updated'
    else:
        UserRevenue.objects.create(
            user=user, year=year, month=month,
            screenshots=screenshots, percent=percent,
            euros=euros, balance=balance, date=date)
        print 'created'
