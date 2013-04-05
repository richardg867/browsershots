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
Start page models.
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.db import models


class NewsItem(models.Model):
    """
    RSS news entry for caching in the database.
    """
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    pubdate = models.DateTimeField()

    class Meta:
        ordering = ('-pubdate', 'url')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        """Get absolute URL."""
        return self.url
