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
Global URL configuration.

This dispatches to the configuration for each installed app according
to the first part of the request URL.

URLs of the form http://browsershots.org/http://www.example.com/
will be handled by the websites app.

If settings.DEBUG is enabled (typically when the development server is
running), URLs starting with /static/ or /png/ will be handled by
Django, otherwise you should include them in the Apache configuration.
"""

__revision__ = "$Rev: 2967 $"
__date__ = "$Date: 2008-08-14 07:33:44 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


def load_app_patterns(prefix, ignore=()):
    """
    Include URL configuration for installed apps.
    """
    pairs = []
    for app in settings.INSTALLED_APPS:
        if app.startswith(prefix):
            segment = app.split('.')[-1]
            if segment not in ignore:
                pairs.append((r'^%s/' % segment, include(app + '.urls')))
    return pairs


admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'shotserver04.start.views.start'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^(?P<url>https?://.+)$', 'shotserver04.websites.views.details'),
    *load_app_patterns('shotserver04.', ignore=[
        'common', 'start', 'messages', 'nonces', 'features', 'platforms']))


def get_static_path():
    """Get path to static CSS, Javascript, image files."""
    import os
    return os.path.join(os.path.normpath(os.path.dirname(__file__)), 'static')


if settings.DEBUG:
    # Serve CSS and image files from shotserver04/static/
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': get_static_path()}),
        (r'^png/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.PNG_ROOT}),
        )
