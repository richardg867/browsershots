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
Check data integrity for ShotServer 0.4.

This script looks for missing configuration details in the database.
It's a good idea to run this daily and email the results, e.g. by
adding a symlink to this file in /etc/cron.daily.
"""

__revision__ = "$Rev: 2005 $"
__date__ = "$Date: 2007-08-19 21:22:02 -0300 (dom, 19 ago 2007) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from shotserver04.factories.models import Factory, ScreenSize, ColorDepth
from shotserver04.browsers.models import Browser
from shotserver04.screenshots.models import Screenshot


sites = Site.objects.all()
if not len(sites):
    print "No sites found."
for site in sites:
    if site.domain == 'example.com':
        print "Site %s needs to be adjusted." % site


users = User.objects.all()
if not len(sites):
    print "No users found."
for user in users:
    if not user.first_name or not user.last_name:
        print "User %s doesn't have a first and last name." % user


factories = Factory.objects.all()
if not len(sites):
    print "No factories found."
for factory in factories:
    if not ScreenSize.objects.filter(factory=factory).count():
        print "Factory %s doesn't have any screen sizes." % factory
    if not ColorDepth.objects.filter(factory=factory).count():
        print "Factory %s doesn't have any color depths." % factory
    browsers = Browser.objects.filter(factory=factory)
    if not len(browsers):
        print "Factory %s doesn't have any browsers." % factory
