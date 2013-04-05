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
Priority models.
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.db import models
from django.contrib.auth.models import User
from shotserver04.websites.models import Domain


class UserPriority(models.Model):
    user = models.ForeignKey(User)
    priority = models.IntegerField()
    activated = models.DateTimeField()
    expire = models.DateTimeField()
    txn_id = models.CharField(max_length=40)
    currency = models.CharField(max_length=3)
    payment = models.DecimalField(max_digits=7, decimal_places=2)
    euros = models.DecimalField(max_digits=7, decimal_places=2)
    country = models.CharField(max_length=2, null=True)

    class Meta:
        verbose_name_plural = "user priority"
        verbose_name_plural = "user priorities"

    def __unicode__(self):
        return u"Priority %d for %s until %s" % (
            self.priority, self.user, self.expire.strftime('%Y-%m-%d'))


class DomainPriority(models.Model):
    domain = models.ForeignKey(Domain)
    priority = models.IntegerField()
    expire = models.DateTimeField()

    class Meta:
        verbose_name_plural = "domain priority"
        verbose_name_plural = "domain priorities"

    def __unicode__(self):
        return u"Priority %d for %s until %s" % (
            self.priority, self.domain, self.expire.strftime('%Y-%m-%d'))
