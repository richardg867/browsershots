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
Copy active browsers from one factory to another.
"""

__revision__ = "$Rev: 2961 $"
__date__ = "$Date: 2008-08-14 05:24:45 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'

import sys
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser

source = Factory.objects.get(name=sys.argv[1])
dest, created = Factory.objects.get_or_create(
    name=sys.argv[2],
    defaults={
        'admin_id': source.admin_id,
        'sponsor_id': source.sponsor_id,
        'operating_system_id': source.operating_system_id,
        'ip': source.ip,
        'hardware': source.hardware,
        })

source_browsers = source.browser_set.filter(active=True)
active_dest_browser_ids = []
for source_browser in source_browsers:
    settings = {
        'browser_group_id': source_browser.browser_group_id,
        'version': source_browser.version,
        'major': source_browser.major,
        'minor': source_browser.minor,
        'engine_id': source_browser.engine_id,
        'engine_version': source_browser.engine_version,
        'javascript_id': source_browser.javascript_id,
        'java_id': source_browser.java_id,
        'flash_id': source_browser.flash_id,
        'command': source_browser.command,
        'active': True,
        }
    dest_browser, created = Browser.objects.get_or_create(
        factory=dest,
        user_agent=source_browser.user_agent,
        defaults=settings)
    if not created:
        for key in list(settings.keys()):
            if key.endswith('_id'):
                new_key = key[:-3]
                settings[new_key] = settings[key]
                del(settings[key])
        dest_browser.update_fields(**settings)
    active_dest_browser_ids.append(dest_browser.id)


# Deactivate all other browsers on destination
for browser in dest.browser_set.filter(active=True):
    if browser.id not in active_dest_browser_ids:
        browser.update_fields(active=False)
