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
Collect statistics for ShotServer 0.4.

You should run this every few minutes, e.g. by adding the following
line in /etc/crontab (replace www-data with the database owner):

*/5 *   * * *   www-data   shotserver04_statistics.py
"""

__revision__ = "$Rev: 2620 $"
__date__ = "$Date: 2008-02-02 16:57:55 -0300 (sab, 02 fev 2008) $"
__author__ = "$Author: johann $"

import sys
import os
import fcntl

# Allow a single instance of this script only
LOCKFILENAME = os.path.join('/var/lock',
    os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.pid')
LOCKFILE = open(LOCKFILENAME, 'w')
try:
    fcntl.flock(LOCKFILE.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
except IOError, e:
    if e.errno == 11:
        sys.exit(1)
LOCKFILE.write(str(os.getpid()) + '\n')
LOCKFILE.truncate()

os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
from datetime import datetime, timedelta
from shotserver04.sponsors.models import Sponsor
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser
from shotserver04.screenshots.models import Screenshot, ProblemReport
from shotserver04.websites.models import Website
from shotserver04.websites.utils import count_profanities, http_get, HTTPError

ONE_HOUR_AGO = datetime.now() - timedelta(0, 3600, 0)
ONE_DAY_AGO = datetime.now() - timedelta(1, 0, 0)
PREMIUM_UPLOADS_PER_DAY = 4800

# Count uploads per day and hour for factories, browsers, sponsors
sponsor_per_day = {}
factories = Factory.objects.all()
for factory in factories:
    factory_per_hour = 0
    factory_per_day = 0
    browsers = Browser.objects.filter(factory=factory)
    for browser in browsers:
        browser_per_hour = Screenshot.objects.filter(
            browser=browser, uploaded__gte=ONE_HOUR_AGO).count()
        browser_per_day = Screenshot.objects.filter(
            browser=browser, uploaded__gte=ONE_DAY_AGO).count()
        if (browser_per_hour != browser.uploads_per_hour or
            browser_per_day != browser.uploads_per_day):
            browser.update_fields(
                uploads_per_hour=browser_per_hour,
                uploads_per_day=browser_per_day)
        factory_per_hour += browser_per_hour
        factory_per_day += browser_per_day
    errors_per_hour = factory.factoryerror_set.filter(
        occurred__gte=ONE_HOUR_AGO).count()
    errors_per_day = factory.factoryerror_set.filter(
        occurred__gte=ONE_DAY_AGO).count()
    problems_per_day = ProblemReport.objects.filter(
        screenshot__factory=factory,
        reported__gte=ONE_DAY_AGO).count()
    if (factory_per_hour != factory.uploads_per_hour or
        factory_per_day != factory.uploads_per_day or
        errors_per_hour != factory.errors_per_hour or
        errors_per_day != factory.errors_per_day or
        problems_per_day != factory.problems_per_day):
        factory.update_fields(
            uploads_per_hour=factory_per_hour,
            uploads_per_day=factory_per_day,
            errors_per_hour=errors_per_hour,
            errors_per_day=errors_per_day,
            problems_per_day=problems_per_day)
    if factory.sponsor_id is not None:
        sponsor_per_day[factory.sponsor_id] = (
            sponsor_per_day.get(factory.sponsor_id, 0) +
            factory_per_day)

# Show premium sponsors and very active factories on the front page
sponsors = Sponsor.objects.all()
for sponsor in sponsors:
    front_page = sponsor.premium or (
        sponsor.id in sponsor_per_day and
        sponsor_per_day[sponsor.id] >= PREMIUM_UPLOADS_PER_DAY)
    if sponsor.front_page != front_page:
        sponsor.update_fields(front_page=front_page)
