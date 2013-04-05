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
Admin for screenshots app.
"""

__revision__ = "$Rev: 2957 $"
__date__ = "$Date: 2008-08-13 19:09:45 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.contrib import admin
from shotserver04.screenshots.models import Screenshot, ProblemReport


class ScreenshotAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
                    'hashkey',
                    ('website', 'factory', 'browser'),
                    ('width', 'height'),
                    # 'uploaded',
                    )}),
        )
    raw_id_fields = ('user', 'website', 'factory', 'browser')
    list_display = ('hashkey', 'factory', 'browser',
                    'width', 'height', 'uploaded')


class ProblemReportAdmin(admin.ModelAdmin):
    raw_id_fields = ('screenshot', )
    list_display = ('message', 'code', 'reported', 'ip')
    list_filter = ('code', 'ip')
    date_hierarchy = 'reported'


admin.site.register(Screenshot, ScreenshotAdmin)
admin.site.register(ProblemReport, ProblemReportAdmin)
