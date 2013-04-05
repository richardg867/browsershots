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
Admin for the browsers app.
"""

__revision__ = "$Rev: 2957 $"
__date__ = "$Date: 2008-08-13 19:09:45 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.contrib import admin
from shotserver04.browsers.models import Engine, BrowserGroup, Browser


class EngineAdmin(admin.ModelAdmin):
    list_display = ('name', 'maker')
    search_fields = ('name', 'maker')


class BrowserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'maker', 'terminal', 'unusual')
    search_fields = ('name', 'maker')


class BrowserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
                    'factory',
                    'user_agent',
                    'command',
                    'browser_group',
                    ('version', 'major', 'minor'),
                    ('engine', 'engine_version'),
                    ('javascript', 'java', 'flash'),
                    'active',
                    )}),
        )
    list_display = ('browser_group', 'version', 'command',
                    'uploads_per_day', 'factory', 'active')
    list_filter = ('factory', 'browser_group')
    search_fields = ('user_agent', 'command',
                     'javascript', 'java', 'flash')


admin.site.register(Engine, EngineAdmin)
admin.site.register(BrowserGroup, BrowserGroupAdmin)
admin.site.register(Browser, BrowserAdmin)
