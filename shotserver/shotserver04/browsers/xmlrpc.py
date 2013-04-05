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
XML-RPC interface for browsers app.
"""

__revision__ = "$Rev: 2960 $"
__date__ = "$Date: 2008-08-14 05:07:00 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from shotserver04.common import last_poll_timeout, last_error_timeout
from shotserver04.common.object_cache import preload_foreign_keys
from shotserver04.xmlrpc import signature, factory_xmlrpc
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser


@signature(list)
def active(http_request):
    """
    Get a list of currently active browsers.

    Return value
    ~~~~~~~~~~~~
    * active list (browser version identifiers)

    Each identifier consists of 4 parts joined with underscores:

    * platform string (e.g. linux / windows / mac-os)
    * browser string (e.g. firefox / msie / opera / safari)
    * major int (major version, e.g. 1)
    * minor int (minor version, e.g. 5)
    """
    factories = Factory.objects.filter(last_poll__gte=last_poll_timeout())
    preload_foreign_keys(factories, operating_system__platform=True)
    browsers = Browser.objects.filter(factory__in=factories, active=True)
    preload_foreign_keys(browsers, factory=factories)
    results = set()
    for browser in browsers:
        platform_name = browser.factory.operating_system.platform.name
        browser_name = browser.browser_group.name
        major = str(browser.major)
        minor = str(browser.minor)
        name = '_'.join((platform_name, browser_name, major, minor))
        name = name.lower().replace(' ', '-')
        results.add(name)
    results = list(results)
    results.sort()
    return results
