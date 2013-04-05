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
Admin for the requests app.
"""

__revision__ = "$Rev: 2957 $"
__date__ = "$Date: 2008-08-13 19:09:45 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.contrib import admin
from shotserver04.requests.models import RequestGroup, Request


class RequestGroupAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
                    'website',
                    ('width', 'bits_per_pixel'),
                    ('javascript', 'java', 'flash'),
                    'user', 'expire',
                    )}),
        )
    raw_id_fields = ('website', )
    search_fields = ('website__url', )
    list_display = ('__unicode__', 'width',
                    'javascript', 'java', 'flash',
                    'user', 'ip')
    date_hierarchy = 'submitted'


class RequestAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
                    'request_group',
                    'platform',
                    ('browser_group', 'major', 'minor'),
                    'priority',
                    )}),
        )
    raw_id_fields = ('request_group', 'browser', 'screenshot')
    list_display = ('browser_group', 'major', 'minor',
                    'platform', 'priority')
    list_filter = ('browser_group', 'platform')


admin.site.register(RequestGroup, RequestGroupAdmin)
admin.site.register(Request, RequestAdmin)
