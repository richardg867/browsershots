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
Count screenshots per factory admin during the last month.
"""

__revision__ = "$Rev: 2510 $"
__date__ = "$Date: 2008-01-01 20:44:06 -0300 (ter, 01 jan 2008) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'

import sys
from django.contrib.auth.models import User
from shotserver04.factories.models import Factory

REVENUE = float(sys.argv[1])
TEMPLATE = u'%7d %7.4f%% %6.2f\u20ac %s'

total = 0
factory_uploads = {}
for line in sys.stdin:
    parts = line.split('\t')
    if not parts or not parts[0].isdigit():
        continue
    factory_id = int(parts[3])
    factory_uploads[factory_id] = factory_uploads.get(factory_id, 0) + 1
    total += 1

admin_uploads = {}
admin_output = {}
for user in User.objects.all():
    user_uploads = 0
    factory_lines = []
    for factory in Factory.objects.filter(admin=user):
        if factory.id in factory_uploads:
            uploads = factory_uploads[factory.id]
            user_uploads += uploads
            percent = 100.0 * uploads / total
            revenue = REVENUE * uploads / total
            factory_lines.append(TEMPLATE % (
                uploads, percent, revenue, factory.name))
    if user_uploads:
        admin_uploads[user.id] = user_uploads
        percent = 100.0 * user_uploads / total
        revenue = REVENUE * user_uploads / total
        admin_output[user.id] = [u'%s %s %s <%s>' % (
            user.username, user.first_name, user.last_name, user.email)]
        if len(factory_lines) > 1:
            admin_output[user.id].extend(factory_lines)
        admin_output[user.id].append(TEMPLATE % (
            user_uploads, percent, revenue, 'total'))

admin_ids = admin_uploads.keys()
admin_ids.sort(key=lambda id: admin_uploads[id])
for admin_id in admin_ids:
    for line in admin_output[admin_id]:
        print line.encode('utf-8')
    print
line = TEMPLATE % (total, 100, REVENUE, 'total')
print line.encode('utf-8')
