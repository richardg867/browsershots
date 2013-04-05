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
URL configuration for the accounts app.
"""

__revision__ = "$Rev: 2160 $"
__date__ = "$Date: 2007-09-18 20:12:50 -0300 (ter, 18 set 2007) $"
__author__ = "$Author: johann $"

from django.conf.urls.defaults import patterns

urlpatterns = patterns('shotserver04.accounts.views',
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^profile/$', 'profile'),
    (r'^email/$', 'email'),
    (r'^verify/(?P<hashkey>[0-9a-f]{32})/$', 'verify'),
)
