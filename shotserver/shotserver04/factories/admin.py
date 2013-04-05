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
Admin for factories app.
"""

__revision__ = "$Rev: 2969 $"
__date__ = "$Date: 2008-08-14 07:51:19 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django.contrib import admin
from shotserver04.factories.models import Factory, ScreenshotCount
from shotserver04.factories.models import ScreenSize, ColorDepth


class ScreenSizeInline(admin.TabularInline):
    model = ScreenSize
    extra = 1


class ColorDepthInline(admin.TabularInline):
    model = ColorDepth
    extra = 1


class FactoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'admin', 'sponsor')}),
        ('Platform', {'fields': ('hardware', 'operating_system')}),
        )
    search_fields = ('name', 'admin__username',
                     'admin__first_name', 'admin__last_name')
    list_display = ('name', 'operating_system',
                    'created', 'last_poll', 'admin')
    list_filter = ('operating_system', )
    date_hierarchy = 'created'
    inlines = (ScreenSizeInline, ColorDepthInline)


class ScreenSizeAdmin(admin.ModelAdmin):
    list_display = ('width', 'height', 'factory')
    list_filter = ('factory', )


class ColorDepthAdmin(admin.ModelAdmin):
    list_display = ('bits_per_pixel', 'factory')
    list_filter = ('factory', )


class ScreenshotCountAdmin(admin.ModelAdmin):
    list_display = ('factory', 'date', 'screenshots')
    raw_id_fields = ('factory', )


admin.site.register(Factory, FactoryAdmin)
admin.site.register(ScreenSize, ScreenSizeAdmin)
admin.site.register(ColorDepth, ColorDepthAdmin)
admin.site.register(ScreenshotCount, ScreenshotCountAdmin)
