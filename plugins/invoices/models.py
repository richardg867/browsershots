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
Invoices models.
"""

__revision__ = "$Rev: 2966 $"
__date__ = "$Date: 2008-08-14 06:44:49 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django.db import models
from django.contrib.auth.models import User
from shotserver04.common import granular_update


class BillingAddress(models.Model):
    user = models.ForeignKey(User, unique=True)
    address = models.TextField()

    class Meta:
        verbose_name_plural = "user billing address"
        verbose_name_plural = "user billing addresses"

    def __unicode__(self):
        return self.address.splitlines()[0].strip()

    update_fields = granular_update.update_fields
