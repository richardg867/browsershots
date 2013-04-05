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
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from decimal import Decimal
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from shotserver04.factories.models import Factory
from shotserver04.common import granular_update


class UserRevenue(models.Model):
    user = models.ForeignKey(User)
    year = models.IntegerField()
    month = models.IntegerField()
    screenshots = models.IntegerField()
    percent = models.FloatField()
    euros = models.DecimalField(max_digits=7, decimal_places=2)
    balance = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'year', 'month')
        ordering = ('-date', )

    def __unicode__(self):
        return u'revenue share for %d screenshots (%.3f%%) in %04d-%02d' % (
            self.screenshots, self.percent, self.year, self.month)

    update_fields = granular_update.update_fields


class UserPayment(models.Model):
    user = models.ForeignKey(User)
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    euros = models.DecimalField(max_digits=7, decimal_places=2)
    balance = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateTimeField()
    paypal_email = models.EmailField(blank=True, default='')

    class Meta:
        ordering = ('-date', )

    def __unicode__(self):
        if self.paypal_email:
            return u'payment of %s %s to %s' % (
                self.currency, abs(self.amount), self.paypal_email)
        else:
            return u'payment of %s %s' % (self.currency, abs(self.amount))

    update_fields = granular_update.update_fields


class NonProfit(models.Model):
    name = models.CharField(max_length=40)
    url = models.URLField()

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.url

    update_fields = granular_update.update_fields


class UserDonation(models.Model):
    user = models.ForeignKey(User)
    non_profit = models.ForeignKey(NonProfit)
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    euros = models.DecimalField(max_digits=7, decimal_places=2)
    balance = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateTimeField()

    class Meta:
        ordering = ('-date', )

    def __unicode__(self):
        return u'donation of %s %.2f to %s' % (
            self.currency, abs(self.amount), self.non_profit)


    update_fields = granular_update.update_fields


def latest_balance(user, before=None):
    """
    Get the latest balance for a user, before a given date (default now).
    """
    if before is None:
        before = datetime.now()
    candidates = []
    revenues = UserRevenue.objects.filter(
        user=user, date__lt=before).order_by('-date')[:1]
    payments = UserPayment.objects.filter(
        user=user, date__lt=before).order_by('-date')[:1]
    donations = UserDonation.objects.filter(
        user=user, date__lt=before).order_by('-date')[:1]
    if len(revenues):
        candidates.append((revenues[0].date, revenues[0].balance))
    if len(payments):
        candidates.append((payments[0].date, payments[0].balance))
    if len(donations):
        candidates.append((donations[0].date, donations[0].balance))
    if len(candidates):
        candidates.sort()
        return candidates[-1][1]
    return Decimal('0.00')
