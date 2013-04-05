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
Paypal views.
"""

__revision__ = "$Rev: 3173 $"
__date__ = "$Date: 2008-10-17 02:06:31 -0300 (sex, 17 out 2008) $"
__author__ = "$Author: johann $"

import urllib2
from datetime import datetime
from django.http import HttpResponse
from django.db import transaction
from django import forms
from django.shortcuts import render_to_response
from django.core.mail import mail_admins, EmailMessage
from django.contrib.auth.models import User
from django.utils.text import capfirst
from django.conf import settings
from shotserver04.paypal.models import PayPalLog
from shotserver04.priority.models import UserPriority
from shotserver04.priority.utils import expiration_date


def guess(**kwargs):
    """
    Try to guess the user account for a PayPal transaction.
    """
    users = User.objects.filter(**kwargs)
    if len(users) == 1:
        return users[0]
    iexact = {}
    for key in kwargs:
        iexact[key + '__iexact'] = kwargs[key]
    users = User.objects.filter(**iexact)
    if len(users) == 1:
        return users[0]


def ipn(http_request):
    """
    Process IPN (instant payment notification) from PayPal.
    """
    if not http_request.POST:
        if settings.DEBUG:
            form_title = "PayPal IPN test form"
            form_action = '/paypal/ipn/'
            form = PayPalForm()
            form_submit = 'Submit'
            return render_to_response('form.html', locals())
        else:
            error_title = "Invalid request"
            error_message = "You must send a POST request to this page."
            return render_to_response('error.html', locals())
    # Log post request in the database
    attributes = {
        'raw_post_data': http_request.raw_post_data,
        'payer_business_name': '',
        }
    for field in PayPalLog._meta.fields:
        if field.name in http_request.POST:
            attributes[field.name] = http_request.POST[field.name]
    paypallog = PayPalLog.objects.create(**attributes)
    # Post data back to PayPal
    if int(http_request.POST.get('test_ipn', '0')):
        paypal_url = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
    else:
        paypal_url = 'https://www.paypal.com/cgi-bin/webscr'
    data = http_request.raw_post_data + '&cmd=_notify-validate'
    req = urllib2.Request(paypal_url, data=data)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    response = urllib2.urlopen(req).read()
    paypallog.response = response
    paypallog.save()
    transaction.commit()
    # Check the response
    if response == 'VERIFIED':
        payment_status = http_request.POST['payment_status']
        if payment_status in ('Completed', 'Pending'):
            priority = create_user_priority(paypallog)
            if isinstance(priority, UserPriority):
                send_priority_email(paypallog, priority)
        else:
            mail_admins("Payment not completed",
                        u"%s: %s" % (payment_status , paypallog))
    else:
        mail_admins("Invalid PayPal IPN",
                    u"%s: %s" % (response, paypallog))
    return HttpResponse(response, mimetype="text/plain")


def create_user_priority(log):
    if UserPriority.objects.filter(txn_id=log.txn_id).count():
        mail_admins("Already processed txn %s" % log.txn_id, log)
        return
    if not log.receiver_email.endswith('@browsershots.org'):
        mail_admins("Wrong receiver %s" % log.receiver_email, log)
        return
    activated = datetime.now()
    if ((log.mc_currency == 'EUR' and log.mc_gross == '10.00') or
        (log.mc_currency == 'USD' and log.mc_gross == '15.00')):
        expire = expiration_date(activated, 1)
    elif ((log.mc_currency == 'EUR' and log.mc_gross == '100.00') or
          (log.mc_currency == 'USD' and log.mc_gross == '150.00')):
        expire = expiration_date(activated, 12)
    else:
        mail_admins("Wrong payment", log)
        return
    user = None
    if (log.item_name and
        log.item_name.lower().startswith('priority processing for ')):
        user = guess(username=log.item_name.split()[-1])
    if user is None and log.memo:
        # Try to guess user from comment field.
        user = (
            guess(username=log.memo) or
            guess(username=log.memo.split()[-1]) or
            guess(username=log.memo.split(':')[-1].strip()))
    if user is None and log.payer_email:
        # Try to guess user from email address.
        user = (
            guess(email=log.payer_email) or
            guess(username=log.payer_email.split('@')[0]))
    if user is None and log.last_name:
        # Try to guess user from first and last name.
        user = (
            guess(first_name=log.first_name, last_name=log.last_name) or
            guess(last_name=log.last_name))
    if user is None:
        mail_admins("Could not guess user for payment", log)
        return
    payment = float(log.mc_gross)
    if log.mc_currency == 'EUR':
        euros = payment
    elif log.mc_currency == 'USD':
        euros = payment / 1.5
    else:
        mail_admins("Wrong currency", log)
        return
    payment = '%.2f' % payment
    euros = '%.2f' % euros
    priority = UserPriority(user=user, priority=1,
                            activated=activated, expire=expire,
                            txn_id=log.txn_id, currency=log.mc_currency,
                            payment=payment, euros=euros,
                            country=log.residence_country)
    priority.save()
    transaction.commit()
    mail_admins(unicode(priority), log)
    return priority


def send_priority_email(log, priority):
    user = priority.user
    first_name = capfirst(user.first_name)
    username = user.username
    expire = priority.expire.strftime('%Y-%m-%d')
    admin_name, admin_email = settings.ADMINS[0]
    mail = EmailMessage()
    mail.subject = "Browsershots priority processing activated"
    mail.body = """
Hi %(first_name)s,

Thank you for supporting the Browsershots project.

Priority processing has been activated for %(username)s
until %(expire)s. Please let me know how it works for you,
and if you have ideas for improvement.

Cheers,
%(admin_name)s
%(admin_email)s
""".strip() % locals()
    mail.to = ['"%s %s" <%s>' % (user.first_name, user.last_name, user.email)]
    mail.bcc = [admin_email]
    mail.from_email = '"%s" <%s>' % (admin_name, admin_email)
    # mail.headers = {'Reply-To': admin_email}
    mail.send()


class PayPalForm(forms.Form):
    """
    Simple form to generate POST requests for testing PayPal IPN.
    """
    txn_id = forms.CharField(initial='3Y366594SP996132H')
    item_name = forms.CharField(initial='Priority processing for tester')
    payment_date = forms.CharField(initial='22:20:41 Jul 23, 2007 PDT')
    payer_id = forms.CharField(initial='UXJ9E3MSX72E4')
    payer_email = forms.EmailField(initial='payer@example.com')
    receiver_id = forms.CharField(initial='U24R4KFWJQF5J')
    receiver_email = forms.EmailField(initial='receiver@example.com')
    mc_currency = forms.CharField(initial='EUR')
    mc_gross = forms.CharField(initial='10.00')
    mc_fee = forms.CharField(initial='0.70')
    payment_status = forms.CharField(initial='Completed')
    test_ipn = forms.IntegerField(initial=1)
