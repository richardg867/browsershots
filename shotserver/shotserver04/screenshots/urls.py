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
URL configuration for the screenshots app.
"""

__revision__ = "$Rev: 2005 $"
__date__ = "$Date: 2007-08-19 21:22:02 -0300 (dom, 19 ago 2007) $"
__author__ = "$Author: johann $"

from django.conf.urls.defaults import patterns

urlpatterns = patterns('shotserver04.screenshots.views',
    (r'^$', 'overview'),
    (r'^(?P<hashkey>[0-9a-f]{32})/$', 'details'),
    (r'.+-(?P<request_group_id>\d+).zip', 'download_zip'),
)
