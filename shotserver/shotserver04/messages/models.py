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
Error log models.
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.db import models
from django.utils.translation import ugettext_lazy as _
from shotserver04.factories.models import Factory
from shotserver04.requests.models import Request


class FactoryError(models.Model):
    """
    Database log for errors in the screenshot factory interface.
    """
    factory = models.ForeignKey(Factory,
        verbose_name=_("factory"))
    code = models.IntegerField(
        _("error code"))
    message = models.CharField(
        _("error message"), max_length=600)
    request = models.ForeignKey(Request,
         verbose_name=_("request"), blank=True, null=True)
    hashkey = models.CharField(
        _("hashkey"), max_length=32, blank=True, null=True)
    occurred = models.DateTimeField(
        _("occurred"), auto_now_add=True)

    class Meta:
        verbose_name = _("factory error message")
        verbose_name_plural = _("factory error messages")
        ordering = ('-occurred', )

    def __unicode__(self):
        return self.message
