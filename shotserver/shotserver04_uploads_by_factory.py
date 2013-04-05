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
Count screenshots per factory per day.
"""

__revision__ = "$Rev: 2516 $"
__date__ = "$Date: 2008-01-03 09:43:52 -0300 (qui, 03 jan 2008) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'

import sys
import time
from django.contrib.auth.models import User
from shotserver04.factories.models import Factory, ScreenshotCount
from shotserver04.screenshots.models import Screenshot


def save_factory(factory, date, screenshots):
    if screenshots:
        count, created = ScreenshotCount.objects.get_or_create(
            factory=factory, date=date, defaults={'screenshots': screenshots})
        if not created and count.screenshots != screenshots:
            count.update_fields(screenshots=screenshots)
    else:
        ScreenshotCount.objects.filter(factory=factory, date=date).delete()


def save(date, factory_uploads):
    for factory in Factory.objects.all():
        save_factory(factory, date, factory_uploads.get(factory.id, 0))


if '--stdin' not in sys.argv:
    now = time.time()
    yesterday = '%04d-%02d-%02d' % time.localtime(now - 24 * 3600)[:3]
    today = '%04d-%02d-%02d' % time.localtime(now)[:3]
    for factory in Factory.objects.all():
        screenshots = Screenshot.objects.filter(factory=factory,
            uploaded__gte=yesterday, uploaded__lt=today).count()
        save_factory(factory, yesterday, screenshots)
    sys.exit(0)

previous_date = None
factory_uploads = {}
for line in sys.stdin:
    parts = line.split('\t')
    if not parts or not parts[0].isdigit():
        continue
    factory_id = int(parts[3])
    date, time = parts[7].split()
    if previous_date and date != previous_date:
        save(previous_date, factory_uploads)
        factory_uploads = {}
    previous_date = date
    factory_uploads[factory_id] = factory_uploads.get(factory_id, 0) + 1
save(previous_date, factory_uploads)
