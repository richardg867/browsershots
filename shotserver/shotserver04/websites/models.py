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
Website models.
"""

__revision__ = "$Rev: 3088 $"
__date__ = "$Date: 2008-09-13 13:18:16 -0300 (sáb, 13 set 2008) $"
__author__ = "$Author: johann $"

import cgi
from django.db import models
from django.utils.translation import ugettext_lazy as _
from shotserver04.common import granular_update


class Domain(models.Model):
    """
    Normalized domain names.
    """

    name = models.CharField(
        _('name'), max_length=200, unique=True)
    submitted = models.DateTimeField(
        _('submitted'), auto_now_add=True)

    class Meta:
        verbose_name = _('domain')
        verbose_name_plural = _('domains')

    update_fields = granular_update.update_fields

    def __unicode__(self):
        if len(self.name) > 60:
            return self.name[:56] + '...'
        else:
            return self.name


class Website(models.Model):
    """
    URLs of requested web pages, and some background info.
    """

    url = models.URLField(
        _('URL'), max_length=400, unique=True)
    domain = models.ForeignKey(Domain,
        verbose_name=_('domain'))
    profanities = models.IntegerField(
        _('profanities'), blank=True, null=True)
    fetched = models.DateTimeField(
        _('fetched'), auto_now_add=True)
    submitted = models.DateTimeField(
        _('submitted'), auto_now_add=True)

    class Meta:
        verbose_name = _('website')
        verbose_name_plural = _('websites')

    update_fields = granular_update.update_fields

    def __unicode__(self):
        if len(self.url) >= 80:
            return cgi.escape(self.url[:76] + '...')
        else:
            return cgi.escape(self.url)

    def get_absolute_url(self):
        """Get absolute URL."""
        if self.url.count('#'):
            return '/websites/%d/' % self.id
        else:
            return '/' + self.url

    def get_numeric_url(self):
        """Get absolute URL, in numeric format."""
        return '/websites/%d/' % self.id
