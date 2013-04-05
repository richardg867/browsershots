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

__revision__ = "$Rev: 2369 $"
__date__ = "$Date: 2007-11-26 08:02:10 -0300 (seg, 26 nov 2007) $"
__author__ = "$Author: johann $"

from django.conf.urls.defaults import patterns

urlpatterns = patterns('shotserver04.browsers.views',
    (r'^add/$', 'add'),
)
