# -*- coding: utf-8 -*-
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
Priority views.
"""

__revision__ = "$Rev: 3173 $"
__date__ = "$Date: 2008-10-17 02:06:31 -0300 (sex, 17 out 2008) $"
__author__ = "$Author: johann $"

import os
from decimal import Decimal, getcontext
import reportlab.pdfgen.canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter, A4
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django import forms
from shotserver04.common import error_page
from shotserver04.common.templatetags.human import human_date
from shotserver04.common.templatetags.countries import country_name
from shotserver04.priority.models import UserPriority
from shotserver04.invoices.models import BillingAddress
from shotserver04.paypal.models import PayPalLog


LEFT_COLUMN = 4*cm
MIDDLE_COLUMN = 6*cm
RIGHT_COLUMN = 13*cm
TABLE_TOP = 14*cm


def get_address(user, priorities=None):
    found = user.billingaddress_set.all()
    if found:
        return found[0].address.splitlines()
    lines = []
    business = None
    country = None
    if priorities:
        priority = priorities[0]
        country = priority.country
        logs = PayPalLog.objects.filter(txn_id=priority.txn_id).order_by('-id')
        if logs:
            log = logs[0]
            business = log.payer_business_name
    if business:
        lines.append(business)
    lines.append("%s %s" % (user.first_name.title(), user.last_name.title()))
    if country == 'DE':
        lines.append('Deutschland')
    elif country:
        lines.append(country_name(country))
    return lines


@login_required
def overview(http_request):
    priorities_list = UserPriority.objects.filter(
	user=http_request.user).order_by('-activated')
    address = get_address(http_request.user, priorities_list)
    return render_to_response('invoices/overview.html', locals(),
        context_instance=RequestContext(http_request))


@login_required
def details(http_request, id):
    id = int(id)
    priority = get_object_or_404(UserPriority, id=id)
    if http_request.user != priority.user:
        return error_page(http_request, _("Access Denied"),
            _("This invoice is for a different user."))
    return render_to_response('invoices/details.html', locals(),
        context_instance=RequestContext(http_request))


class AddressForm(forms.ModelForm):

    class Meta:
        model = BillingAddress
        exclude = ('user', )

    def clean_address(self):
        lines = list(self.cleaned_data['address'].splitlines())
        for index, line in enumerate(lines):
            if len(line) > 40:
                raise forms.ValidationError(
                    "Line %d is too long (%d characters)." %
                    (index + 1, len(line)))
        for index in range(len(lines) - 1, -1, -1):
            if lines[index].strip() == '':
                lines.pop(index)
        if len(lines) > 10:
            raise forms.ValidationError(
                "The billing address has too many lines.")
        return '\n'.join(lines)


@login_required
def address(http_request):
    priorities_list = UserPriority.objects.filter(
	user=http_request.user).order_by('-activated')
    address = get_address(http_request.user, priorities_list)
    form = AddressForm(http_request.POST or None,
                       initial={'address': u'\n'.join(address)})
    if http_request.method == 'POST' and form.is_valid():
        addresses = http_request.user.billingaddress_set.all()
        if addresses:
            address = addresses[0]
            address.update_fields(address=form.cleaned_data['address'])
        else:
            address = BillingAddress(
                user=http_request.user,
                address=form.cleaned_data['address'])
            address.save()
        return HttpResponseRedirect('/invoices/')
    form_title = _("billing address")
    form_submit = _("save")
    return render_to_response('form.html', locals(),
        context_instance=RequestContext(http_request))


def drawStrings(canvas, x, y, *lines):
    step = 0.5*cm
    for line in lines:
        if isinstance(line, int):
            if line < 0:
                canvas.setFont('Helvetica-Bold', abs(line))
            else:
                canvas.setFont('Helvetica', abs(line))
            step = abs(line) / 24.0 * cm
            continue
        canvas.drawString(x, y, line)
        y -= step


def pdf_draw_header(canvas, country):
    dir = os.path.dirname(__file__)
    logo = os.path.join(dir, 'logo.jpg')
    canvas.drawInlineImage(logo, RIGHT_COLUMN, 23.7*cm,
                           width=1*cm, height=1*cm)
    canvas.setFont('Helvetica', 16)
    canvas.drawString(RIGHT_COLUMN + 1.2*cm, 24*cm, u"Browsershots")

    drawStrings(canvas, RIGHT_COLUMN, 23*cm, 12,
                u"Johann C. Rocholl",
                u"Pütnitzer Str. 12",
                u"18311 Ribnitz-Damgarten")
    if country == 'DE':
        canvas.drawString(RIGHT_COLUMN, 21.5*cm, u"Deutschland")
    else:
        canvas.drawString(RIGHT_COLUMN, 21.5*cm, u"Germany")
    canvas.drawString(RIGHT_COLUMN, 20.5*cm, "johann@browsershots.org")


def pdf_draw_footer(canvas, country):
    width = canvas._pagesize[0]
    canvas.line(LEFT_COLUMN, 3.5*cm, width - LEFT_COLUMN, 3.5*cm)
    if country == 'DE':
        drawStrings(canvas, LEFT_COLUMN, 3*cm, 8,
                    u"Inhaber: Johann C. Rocholl",
                    u"PayPal: payment@browsershots.org")
        drawStrings(canvas, RIGHT_COLUMN, 3*cm, 8,
                    u"Konto: 3415213",
                    u"BLZ: 38070724")
    else:
        drawStrings(canvas, LEFT_COLUMN, 3*cm, 8,
                    u"Sole proprietor: Johann C. Rocholl",
                    u"PayPal: payment@browsershots.org")
        drawStrings(canvas, RIGHT_COLUMN, 3*cm, 8,
                    u"IBAN: DE63380707240341521300",
                    u"BIC / SWIFT: DEUTDEDBXXX")


@login_required
def pdf(http_request, id):
    id = int(id)
    priority = get_object_or_404(UserPriority, id=id)
    if (http_request.user != priority.user
        and not http_request.user.is_superuser):
        return error_page(http_request, _("Access Denied"),
            _("This invoice is for a different user."))
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%d.pdf' % id

    country = None
    if priority.country:
        country = priority.country.upper()
        assert len(country) == 2

    if country == 'US':
        pagesize = letter
    else:
        pagesize = A4

    if country == 'DE':
        payment = Decimal('%.2f' % (float(priority.payment) / 1.19))
        tax = Decimal('%.2f' % (float(priority.payment) - float(payment)))
        subject = u"Rechnung Nummer %d" % priority.id
        date = u"Datum: %s" % human_date(priority.activated)
        amounts = [-12, u"Menge", '', 12, u"1", '', '', u"19%", '', '']
        prices = [
            -12, u"Preis", '', 12,
            u"%s %.2f" % (priority.currency, payment), '', '',
            u"%s %.2f" % (priority.currency, tax), '',
            u"%s %.2f" % (priority.currency, priority.payment)]
        descriptions = [
            -12, u"Beschreibung", '', 12,
            u"Priority processing für %s" % priority.user.username,
            u"von %s bis %s" % (human_date(priority.activated),
                                human_date(priority.expire)), '',
            u"Mehrwertsteuer", '', u"Rechnungsbetrag (Brutto)"]
        amounts.extend(['', '',
            u"Vielen Dank für Ihren Auftrag.", '',
            u"Mit freundlichen Grüßen,",
            u"Johann C. Rocholl"])
    else:
        subject = u"Invoice Number %d" % id
        date = u"Date: %s" % human_date(priority.activated)
        amounts = [-12, u"Qty", '', 12, u"1", '']
        prices = [
            -12, u"Price", '', 12,
            u"%s %.2f" % (priority.currency, priority.payment)]
        descriptions = [
            -12, u"Description", '', 12,
            u"Priority processing for %s" % priority.user.username,
            u"from %s to %s" % (human_date(priority.activated),
                                human_date(priority.expire))]
        amounts.extend(['', '',
u"For customers outside Germany, this invoice does not include",
u"sales tax, value added tax (VAT) or goods and services tax (GST).",
u"You may have to pay use tax or reverse charge VAT, according",
u"to the tax laws in your country or state.",
'',
u"Thank you for your business.",
'',
u"Kind regards,",
u"Johann C. Rocholl"])

    canvas = reportlab.pdfgen.canvas.Canvas(response, pagesize=pagesize)
    width, height = pagesize
    pdf_draw_header(canvas, country)
    # canvas.drawString(LEFT_COLUMN, 25*cm, u"Customer:")
    address = get_address(priority.user, [priority])
    drawStrings(canvas, LEFT_COLUMN, 23*cm, *address)
    drawStrings(canvas, LEFT_COLUMN, 17.5*cm, -12, subject)
    drawStrings(canvas, LEFT_COLUMN, 17*cm, 12, date)
    drawStrings(canvas, LEFT_COLUMN, TABLE_TOP, *amounts)
    drawStrings(canvas, MIDDLE_COLUMN, TABLE_TOP, *descriptions)
    drawStrings(canvas, RIGHT_COLUMN, TABLE_TOP, *prices)
    pdf_draw_footer(canvas, country)
    canvas.showPage()
    canvas.save()
    return response
