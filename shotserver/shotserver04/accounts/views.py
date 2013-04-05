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
Account views.
"""

__revision__ = "$Rev: 2971 $"
__date__ = "$Date: 2008-08-14 08:21:38 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import time
from datetime import datetime, timedelta
from psycopg import IntegrityError
import smtplib
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django import forms
from django.forms.util import ErrorList
from django.db import transaction, connection
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.conf import settings
from shotserver04.factories.models import Factory
from shotserver04.messages.models import FactoryError
from shotserver04.common.object_cache import preload_foreign_keys
from shotserver04.common import error_page, success_page
from shotserver04.nonces import crypto
from shotserver04.nonces.models import Nonce


USERNAME_CHAR_FIRST = 'abcdefghijklmnopqrstuvwxyz'
USERNAME_CHAR = USERNAME_CHAR_FIRST + '0123456789_-'
PASSWORD_MIN_LENGTH = 6


def logout_required(func):
    """
    The opposite of the login_required decorator.
    """

    def wrapper(http_request, *args, **kwargs):
        """
        Display an error page if the user is already signed in.
        """
        if http_request.user.is_authenticated():
            return error_page(http_request, _("You're already signed in"),
                _("Please log out and then try again."))
        return func(http_request, *args, **kwargs)
    return wrapper


class LoginForm(forms.Form):
    """
    Simple login form.
    """
    username = forms.CharField(max_length=30, label=_("Username"))
    password = forms.CharField(max_length=40, label=_("Password"),
        widget=forms.PasswordInput(render_value=False))


@logout_required
def login(http_request):
    """
    Show login form and then log in, if correct password was submitted.
    """
    next = http_request.REQUEST.get('next', '')
    if not next or '//' in next or ' ' in next:
        next = settings.LOGIN_REDIRECT_URL
    form = LoginForm(http_request.POST or None)
    form_errors = []
    user = None
    if form.is_valid():
        if not http_request.session.test_cookie_worked():
            form_errors.append(_("Please enable cookies in your browser."))
        else:
            user = auth.authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            if user is None:
                form_errors.append(_("Incorrect username or password."))
            elif not user.is_active:
                form_errors.append(_("This account is inactive."))
    if form_errors or not user:
        form_title = _("Welcome to Browsershots!")
        form_submit = _("let me in")
        form_hidden = '<input type="hidden" name="next" value="%s" />' % next
        form_extra = u"""
<ul>
<li><a href="../email/">%s</a></li>
<li><a href="../email/">%s</a></li>
</ul>
""".strip() % (_("Forgot your password?"),
               _("Create a new account?"))
        form_javascript = "document.getElementById('id_username').focus()"
        http_request.session.set_test_cookie()
        return render_to_response('form.html', locals(),
            context_instance=RequestContext(http_request))
    auth.login(http_request, user)
    http_request.session.delete_test_cookie()
    return HttpResponseRedirect(next)


def logout(http_request):
    """
    De-authenticate the current user.
    """
    auth.logout(http_request)
    result_title = _("logged out")
    result_class = 'success'
    result_message = _("You have successfully logged out.")
    return render_to_response('result.html', locals(),
        context_instance=RequestContext(http_request))


def totals(where=None):
    """
    Count monthly screenshots.
    """
    sql = [
        "SELECT",
        "date_part('year', date) AS year,",
        "date_part('month', date) AS month,",
        "sum(screenshots)",
        "FROM factories_screenshotcount",
        ]
    if where:
        sql.append(where)
    sql.append("GROUP BY year, month")
    cursor = connection.cursor()
    cursor.execute('\n'.join(sql))
    result = {}
    for year, month, screenshots in cursor.fetchall():
        result[(int(year), int(month))] = screenshots
    return result


def user_month_totals(user):
    """
    Get monthly statistics about uploaded screenshots and revenue.
    """
    factories = user.factory_set.all()
    if not factories.count():
        return
    all_factories = totals()
    my_factories = totals("WHERE factory_id IN (%s)" % ','.join(
        [str(factory.id) for factory in factories]))
    keys = all_factories.keys()
    keys.sort()
    for year, month in keys:
        all = all_factories.get((year, month), 0)
        my = my_factories.get((year, month), 0)
        revenue = 0
        if 'shotserver04.revenue' in settings.INSTALLED_APPS:
            from shotserver04.revenue import month_revenue
            revenue = month_revenue(year, month)
        yield ('%04d-%02d' % (year, month), all, my,
               '%.3f%%' % (100.0 * my / all),
               '%.2f' % (revenue * my / all))


@login_required
def profile(http_request):
    """
    Show a user's private profile page.
    """
    month_totals = list(user_month_totals(http_request.user))
    factory_table_header = Factory.table_header()
    factory_list = Factory.objects.select_related().filter(
        admin=http_request.user)
    if 'shotserver04.priority' in settings.INSTALLED_APPS:
        priorities = http_request.user.userpriority_set.order_by('-expire')
        if len(priorities):
            user_has_priority_until = priorities[0].expire
            if user_has_priority_until < datetime.now():
                user_has_priority_until = False
    return render_to_response('accounts/profile.html', locals(),
        context_instance=RequestContext(http_request))


class EmailForm(forms.Form):
    """
    Email input for address verification.
    """
    email = forms.EmailField()


def email_message(domain, hashkey, user):
    """
    Email template for verification message.
    """
    if user:
        salutation = unicode(_("Hi %(first_name)s!"))
        salutation %= {'first_name': capfirst(user.first_name)}
        what = "set a new password"
    else:
        salutation = unicode(_("Welcome to Browsershots!"))
        what = "finish the registration process"
    parts = [
salutation,
"""If you have not requested this verification email, you may ignore it.""",
"""Click the following link (or copy it into your browser's address bar)
to verify your email address and %s:""" % what,
"""http://%(domain)s/accounts/verify/%(hashkey)s/""" % locals(),
    ]
    if user:
        parts.append("Your username is %s." % user.username)
    parts.append("Cheers,\nBrowsershots\n")
    return u'\n\n'.join(parts)


@logout_required
def email(http_request):
    """
    Ask user for email address, then send verification message.
    """
    ip = http_request.META['REMOTE_ADDR']
    nonces_per_day = Nonce.objects.filter(ip=ip, email__isnull=False,
       created__gt=datetime.now() - timedelta(hours=24)).count()
    if nonces_per_day >= 3:
        return error_page(http_request, _("too many verification emails"),
_("There were too many email requests from your IP in the last 24 hours."),
_("Please try again later."))
    form = EmailForm(http_request.POST or None)
    if not form.is_valid():
        form_title = _("email verification")
        form_action = '/accounts/email/'
        form_submit = _("send email")
        form_javascript = "document.getElementById('id_email').focus()"
        return render_to_response('form.html', locals(),
            context_instance=RequestContext(http_request))
    address = form.cleaned_data['email']
    user = None
    users = User.objects.filter(email=address)
    if len(users):
        user = users[0]
    hashkey = crypto.random_md5()
    Nonce.objects.create(email=address, hashkey=hashkey, ip=ip)
    domain = Site.objects.get_current().domain
    message = email_message(domain, hashkey, user)
    try:
        send_mail("Browsershots email verification", message,
                  settings.DEFAULT_FROM_EMAIL, [address],
                  fail_silently=False)
    except smtplib.SMTPException, e:
        return error_page(http_request, _("email error"),
            _("Could not send email."), str(e))
    hide_hashkey(hashkey)
    return success_page(http_request, _("email sent"),
_("A verification email was sent to %(address)s.") % locals(),
_("Check your email inbox and follow the instructions in the message."),
_("If your email provider uses graylisting, it may take a few minutes."))


def hide_hashkey(hashkey):
    """
    Remove hashkey from debug output.
    """
    from django.db import connection
    for index, query in enumerate(connection.queries):
        if hashkey in query['sql']:
            query['sql'] = query['sql'].replace(hashkey, '[hidden]')


class UserForm(forms.Form):
    """
    Username and realname.
    """
    username = forms.CharField(
        max_length=User._meta.get_field('username').max_length,
        label=capfirst(_("username")))
    first_name = forms.CharField(
        max_length=User._meta.get_field('first_name').max_length,
        label=capfirst(_("first name")))
    last_name = forms.CharField(
        max_length=User._meta.get_field('last_name').max_length,
        label=capfirst(_("last name")))

    def clean_username(self):
        """
        Check that the username is sensible.
        """
        username = self.cleaned_data['username']
        if username[0] not in USERNAME_CHAR_FIRST:
            raise forms.ValidationError(unicode(
                _("Username must start with a lowercase letter.")))
        for index in range(len(username)):
            if username[index] not in USERNAME_CHAR:
                raise forms.ValidationError(unicode(
_("Username may contain only lowercase letters, digits, underscore, hyphen.")))
        if username in 'admin administrator root webmaster'.split():
            raise forms.ValidationError(unicode(
                _("This username is reserved.")))
        return username


class PasswordForm(forms.Form):
    """
    Password and again.
    """
    password = forms.CharField(max_length=40,
        label=capfirst(_("password")),
        widget=forms.PasswordInput(render_value=False))
    again = forms.CharField(max_length=40,
        label=capfirst(_("again")),
        widget=forms.PasswordInput(render_value=False))

    def clean_password(self):
        """
        Check that the password is long enough and not too silly.
        """
        password = self.cleaned_data['password']
        if len(password) < PASSWORD_MIN_LENGTH:
            raise forms.ValidationError(unicode(
                _("The password must have %d or more characters.")) %
                PASSWORD_MIN_LENGTH)
        if password.isdigit():
            raise forms.ValidationError(unicode(
                _("The password must not be completely numeric.")))
        return password

    def clean_again(self):
        """
        Check that the password and again is the same.
        """
        if 'password' not in self.cleaned_data:
            return
        password = self.cleaned_data['password']
        again = self.cleaned_data['again']
        if again != password:
            raise forms.ValidationError(unicode(
                _("Repeat password is not the same.")))
        return again


class RegistrationForm(UserForm, PasswordForm):
    """
    User registration form, mixed from user and password form.
    """

    def create_user(self, address):
        """
        Try to create the user in the database.
        Return None if the username is already taken.
        """
        try:
            return User.objects.create_user(self.cleaned_data['username'],
                address, self.cleaned_data['password'])
        except IntegrityError, e:
            transaction.rollback()
            if 'duplicate' in str(e).lower():
                self.errors['username'] = ErrorList([
                    _("This username is already taken.")])
            else:
                self.errors[forms.NON_FIELD_ERRORS] = ErrorList([str(e)])


@logout_required
def verify(http_request, hashkey):
    """
    Register a new user or set a new password,
    after successful email verification.
    """
    nonce = get_object_or_404(Nonce, hashkey=hashkey)
    ip = http_request.META['REMOTE_ADDR']
    if nonce.ip != ip:
        return error_page(http_request, _("Wrong IP address"),
_("The verification email was requested from a different IP address."))
    if not nonce.email:
        return error_page(http_request, _("Bad verification code"),
_("The verification code has no email address."))
    if nonce.created < datetime.now() - timedelta(hours=24):
        return error_page(http_request, _("Verification code expired"),
_("The verification email was requested more than 24 hours ago."))
    users = User.objects.filter(email=nonce.email)
    if len(users):
        return change_password(http_request, nonce, users[0])
    else:
        return register(http_request, nonce)


def change_password(http_request, nonce, user):
    """
    Change password after email verification.
    """
    form = PasswordForm(http_request.POST or None)
    if not form.is_valid():
        form_title = _("choose a new password")
        form_action = '/accounts/verify/%s/' % nonce.hashkey
        form_submit = _("change password")
        form_javascript = "document.getElementById('id_password').focus()"
        return render_to_response('form.html', locals(),
            context_instance=RequestContext(http_request))
    user.set_password(form.cleaned_data['password'])
    user.save()
    nonce.delete()
    return success_page(http_request, _("Password changed"),
        _("Your new password has been saved."),
        _("Click the link in the top right corner to log in."))


def register(http_request, nonce):
    """
    Register a new user after email verification.
    """
    form = RegistrationForm(http_request.POST or None)
    user = None
    if form.is_valid():
        user = form.create_user(nonce.email)
    if user is None:
        form_title = _("create a new account")
        form_action = '/accounts/verify/%s/' % nonce.hashkey
        form_submit = _("create account")
        form_javascript = "document.getElementById('id_username').focus()"
        return render_to_response('form.html', locals(),
            context_instance=RequestContext(http_request))
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    user.save()
    nonce.delete()
    return success_page(http_request, _("Account created"),
        _("A new user account was created."),
        _("Click the link in the top right corner to log in."))
