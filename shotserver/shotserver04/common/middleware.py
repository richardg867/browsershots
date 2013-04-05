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
Custom URL rewriting, more granular than Django's APPEND_SLASH.
"""

__revision__ = "$Rev: 2323 $"
__date__ = "$Date: 2007-11-21 08:49:41 -0300 (qua, 21 nov 2007) $"
__author__ = "$Author: johann $"

from django.conf import settings
from django import http


class RedirectMiddleware(object):
    """
    Append missing slashes, but only if path starts with the name of
    an installed app. Special URLs like this will be left untouched::

      http://browsershots.org/http://www.example.com/no-slash

    Also redirect to XML-RPC documentation if subdomain is 'api' or
    'xmlrpc' and path is '/'.
    """

    def process_request(self, request):
        """
        Process an incoming HTTP GET or HEAD request.
        """
        # Don't rewrite POST requests
        if not request.method in ('GET', 'HEAD'):
            return
        parts = request.path.strip('/').split('/')
        first_part = parts[0]
        last_part = parts[-1]
        # Redirect to XML-RPC documentation
        host = http.get_host(request)
        subdomain = host.lower().split('.')[0]
        if subdomain in ('api', 'xmlrpc') and first_part == '':
            return http.HttpResponsePermanentRedirect('/xmlrpc/')
        # Fix double slash after http: or https:
        if first_part in ('http:', 'https:') and len(parts) >= 2 and parts[1]:
            new_path = request.get_full_path().replace(':/', '://', 1)
            return http.HttpResponsePermanentRedirect(new_path)
        # Add trailing slash if path starts with an installed app name
        if request.path.endswith('/') or not self.installed_app(first_part):
            return
        # Don't add trailing slash after filenames
        if '.' in last_part and first_part != 'xmlrpc':
            return
        new_path = request.path + '/'
        if request.GET:
            new_path += '?' + request.GET.urlencode()
        return http.HttpResponsePermanentRedirect(new_path)

    def installed_app(self, name):
        """
        Check if this is the name of an installed app.
        """
        name = '.' + name
        for app in settings.INSTALLED_APPS:
            if app.endswith(name):
                return True
