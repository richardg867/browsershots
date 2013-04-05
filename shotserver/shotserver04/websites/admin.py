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
Admin for website app.
"""

__revision__ = "$Rev: 2957 $"
__date__ = "$Date: 2008-08-13 19:09:45 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.contrib import admin
from shotserver04.websites.models import Domain, Website


class DomainAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'submitted')
    search_fields = ('name', )
    date_hierarchy = 'submitted'


class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'submitted')
    raw_id_fields = ('domain', )
    search_fields = ('url', )
    date_hierarchy = 'submitted'


admin.site.register(Domain, DomainAdmin)
admin.site.register(Website, WebsiteAdmin)
