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
Platform models.
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Platform(models.Model):
    """
    Screenshot factory platforms like Linux / Windows / Mac.
    """
    name = models.CharField(
        _('name'), max_length=30,
        help_text="e.g. Linux / Windows / Mac")
    position = models.IntegerField(
        _('position'), blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('platform')
        verbose_name_plural = _('platforms')
        ordering = ('position', 'name')


class OperatingSystem(models.Model):
    """
    Screenshot factory operating systems.
    """
    platform = models.ForeignKey(Platform,
        verbose_name=_('platform'))
    name = models.CharField(
        _('name'), max_length=30)
    version = models.CharField(
        _('version'), max_length=30, blank=True)
    codename = models.CharField(
        _('codename'), max_length=30, blank=True)
    maker = models.CharField(
        _('maker'), max_length=30, blank=True)

    class Meta:
        verbose_name = _('operating system')
        verbose_name_plural = _('operating systems')
        ordering = ('name', 'version')

    def __unicode__(self, show_codename=True):
        if self.codename and show_codename:
            return u'%s %s (%s)' % (self.name, self.version, self.codename)
        else:
            return u'%s %s' % (self.name, self.version)
