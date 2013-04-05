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
PayPal models.
"""

__revision__ = "$Rev: 3089 $"
__date__ = "$Date: 2008-09-13 15:50:23 -0300 (sab, 13 set 2008) $"
__author__ = "$Author: johann $"

from django.db import models
from django.contrib.auth.models import User
from shotserver04.common import granular_update


class PayPalEmail(models.Model):
    """
    Store the preferred PayPal email address for each user.
    """
    user = models.ForeignKey(User, unique=True)
    email = models.EmailField()

    class Meta:
        verbose_name = 'PayPal email'
        verbose_name_plural = 'PayPal emails'

    update_fields = granular_update.update_fields

    def __unicode__(self):
        return self.email

    def user_email(self):
        return self.user.email


class PayPalLog(models.Model):
    """
    Database log for PayPal IPN (instant payment notification).
    """
    raw_post_data = models.CharField(max_length=2000)
    response = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    residence_country = models.CharField(max_length=200, blank=True)
    charset = models.CharField(max_length=200, blank=True)

    test_ipn = models.CharField(max_length=200, blank=True)
    txn_id = models.CharField(max_length=200, blank=True)
    txn_type = models.CharField(max_length=200, blank=True)
    item_name = models.CharField(max_length=200, blank=True)
    item_number = models.CharField(max_length=200, blank=True)
    memo = models.CharField(max_length=200, blank=True)

    mc_currency = models.CharField(max_length=200, blank=True)
    mc_gross = models.CharField(max_length=200, blank=True)
    mc_fee = models.CharField(max_length=200, blank=True)

    payment_date = models.CharField(max_length=200, blank=True)
    payment_type = models.CharField(max_length=200, blank=True)
    payment_fee = models.CharField(max_length=200, blank=True)
    payment_gross = models.CharField(max_length=200, blank=True)
    payment_status = models.CharField(max_length=200, blank=True)
    pending_reason = models.CharField(max_length=200, blank=True)

    payer_id = models.CharField(max_length=200, blank=True)
    payer_email = models.CharField(max_length=200, blank=True)
    payer_business_name = models.CharField(max_length=200, blank=True)
    payer_status = models.CharField(max_length=200, blank=True)

    receiver_id = models.CharField(max_length=200, blank=True)
    receiver_email = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'PayPal log'
        verbose_name_plural = 'PayPal logs'

    update_fields = granular_update.update_fields

    def __unicode__(self):
        return ' '.join((self.mc_currency, self.mc_gross, 'from',
                         self.payer_email, self.first_name, self.last_name,
                         self.memo.replace('\n', ' ')))
