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
Admin for paypal app.
"""

__revision__ = "$Rev: 3089 $"
__date__ = "$Date: 2008-09-13 15:50:23 -0300 (sab, 13 set 2008) $"
__author__ = "$Author: johann $"

from django.contrib import admin
from shotserver04.paypal.models import PayPalEmail,PayPalLog


class PayPalEmailAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'user_email')
    raw_id_fields = ('user', )


class PayPalLogAdmin(admin.ModelAdmin):
    list_display = ('txn_id', 'payment_date', 'payer_email',
                    'mc_currency', 'mc_gross', 'payment_status',
                    'response', 'posted')


admin.site.register(PayPalEmail, PayPalEmailAdmin)
admin.site.register(PayPalLog, PayPalLogAdmin)
