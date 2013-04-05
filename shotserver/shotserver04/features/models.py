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
Javascript, Java, Flash versions.
"""

__revision__ = "$Rev: 3172 $"
__date__ = "$Date: 2008-10-15 13:21:35 -0300 (qua, 15 out 2008) $"
__author__ = "$Author: johann $"

from django.db import models
from django.utils.translation import ugettext_lazy as _


def version_unicode(self):
    """
    Human-readable version output, with translation.
    """
    if self.version == 'enabled':
        return unicode(_("enabled"))
    elif self.version == 'disabled':
        return unicode(_("disabled"))
    else:
        return self.version


def version_q(self):
    """
    SQL query to match requests for a given factory.
    """
    field = 'request_group__' + self._meta.module_name
    result = models.Q(**{field + '__isnull': True})
    result |= models.Q(**{field: self.id})
    # Specific installed versions match requests for 'enabled' too.
    if self.version not in ('disabled', 'enabled'):
        result |= models.Q(**{field: 2}) # 2 means 'enabled'
    return result


class Javascript(models.Model):
    """
    Javascript versions.
    """

    version = models.CharField(
        _('version'), max_length=30, unique=True,
        help_text=_("e.g. 1.4 / 1.5 / 1.6"))

    class Meta:
        verbose_name = _('Javascript version')
        verbose_name_plural = _('Javascript versions')
        ordering = ('id', )

    __unicode__ = version_unicode
    features_q = version_q


class Java(models.Model):
    """
    Java versions.
    """

    version = models.CharField(
        _('version'), max_length=30, unique=True,
        help_text=_("e.g. 1.4 / 1.5 / 1.6"))

    class Meta:
        verbose_name = _('Java version')
        verbose_name_plural = _('Java versions')
        ordering = ('id', )

    __unicode__ = version_unicode
    features_q = version_q


class Flash(models.Model):
    """
    Flash plugin versions.
    """

    version = models.CharField(
        _('version'), max_length=30, unique=True,
        help_text=_("e.g. 5 / 6 / 7 / 8 / 9 / 10"))

    class Meta:
        verbose_name = _('Flash version')
        verbose_name_plural = _('Flash versions')
        ordering = ('id', )

    __unicode__ = version_unicode
    features_q = version_q
