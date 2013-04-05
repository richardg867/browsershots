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

__revision__ = "$Rev: 2966 $"
__date__ = "$Date: 2008-08-14 06:44:49 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import sys
import os
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
from datetime import datetime, timedelta
from decimal import Decimal
from shotserver04.revenue import month_priorities
from shotserver04.revenue.models import UserPayment

year = int(sys.argv[1])
month = int(sys.argv[2])

priorities = month_priorities(year, month)
print 'total:', sum([priority.euros for priority in priorities])

german = priorities.filter(country='DE')
brutto = sum([priority.euros for priority in german])
netto = Decimal('%.2f' % (float(brutto) / 1.19))
mwst = brutto - netto
print 'german:', brutto, 'brutto,', netto, 'netto,', mwst, 'MwSt'

untaxed = priorities.exclude(country='DE')
print 'untaxed:', sum([priority.euros for priority in untaxed])

payments = UserPayment.objects.filter(date__year=year, date__month=month)
print 'payments:', sum([payment.euros for payment in payments])
