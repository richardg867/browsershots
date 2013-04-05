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
Show account balances and transactions.
"""

__revision__ = "$Rev: 2965 $"
__date__ = "$Date: 2008-08-14 06:44:17 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import sys
import os
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils.text import capfirst
from django.contrib.auth.models import User
from shotserver04.revenue.models import UserRevenue

# year = int(sys.argv[1])
# month = int(sys.argv[2])
selected_users = sys.argv[1:]
errors = 0
for user in User.objects.all():
    if '--all' not in selected_users and user.username not in selected_users:
        continue
    transactions = (
        list(user.userrevenue_set.all()) +
        list(user.userpayment_set.all()) +
        list(user.userdonation_set.all()))
    if not transactions:
        continue
    transactions.sort(key=lambda t: t.date)
    if '--latest' in sys.argv[1:]:
        print transactions[-1].balance, user.username,
        print user.first_name.encode('utf-8'), user.last_name.encode('utf-8'),
        print user.email
        continue
    balance = Decimal('0.00')
    for transaction in transactions:
        print str(user.id).ljust(6),
        print user.username.ljust(16),
        print str(transaction.date).ljust(20),
        print str(transaction.euros).rjust(8),
        print str(transaction.balance).rjust(8),
        print '  ', capfirst(unicode(transaction))
        balance += transaction.euros
        if balance != transaction.balance:
            print '### balance should be', balance
            errors += 1
    print
print errors, 'errors'
