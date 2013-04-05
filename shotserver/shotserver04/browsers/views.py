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
Browser views.
"""

__revision__ = "$Rev: 2971 $"
__date__ = "$Date: 2008-08-14 08:21:38 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import re
from django import forms
from django.forms.util import ErrorList
from django.db import connection
from django.http import HttpResponseRedirect
from django.contrib.auth.models import check_password
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy, ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings
from shotserver04.common import error_page, results
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser
from shotserver04.browsers import agents

# Security: allow only alphanumeric browser commands
# Optionally within a subfolder, relative to working directory
safe_command = re.compile(r'^([\w_\-]+[\\/])*[\w_\-\.]+$').match


class PasswordForm(forms.Form):
    """
    Simple password input form.
    """
    factory_name = forms.CharField(
        label=ugettext_lazy("factory"))
    password = forms.CharField(
        label=ugettext_lazy("password"),
        widget=forms.PasswordInput)

    def clean_factory_name(self):
        name = self.cleaned_data['factory_name']
        try:
            self.cleaned_data['factory'] = Factory.objects.get(name=name)
        except Factory.DoesNotExist, error:
            raise forms.ValidationError(_("Unknown factory name."))
        return name

    def clean(self):
        if ('factory' not in self.cleaned_data or
            'password' not in self.cleaned_data):
            return # ValidationError was already raised above.
        factory = self.cleaned_data['factory']
        password = self.cleaned_data['password']
        if not check_password(password, factory.admin.password):
            self.errors['password'] = ErrorList([_("Password mismatch.")])
        return self.cleaned_data


class BrowserForm(forms.ModelForm):
    class Meta:
        model = Browser
        exclude = ('factory', )

    def clean_command(self):
        command = self.cleaned_data['command']
        if not command:
            return command
        if ' ' in command:
            raise forms.ValidationError(u' '.join((
                _("Unsafe command."),
                _("Whitespace is not permitted."))))
        if (command.startswith('/') or command.startswith('\\') or
            command[1:].startswith(':')):
            raise forms.ValidationError(u' '.join((
                _("Unsafe command."),
                _("Absolute path is not permitted."))))
        if not safe_command(command):
            raise forms.ValidationError(u' '.join((
                _("Unsafe command."),
                _("Simple filename required."))))
        return command


def guess_factory_name(ip, user_agent):
    """
    Guess factory name from IP address and User-Agent.
    """
    # Try to find a factory with matching IP address
    factories = Factory.objects.select_related().filter(
        ip=ip, last_poll__isnull=False).order_by('-last_poll')
    if not factories:
        factories = Factory.objects.select_related().filter(
            ip=ip).order_by('-last_poll')
    if not factories:
        factories = Factory.objects.select_related().order_by('-last_poll')
    # Try to match Ubuntu or Mac OS X
    for factory in factories:
        if factory.operating_system.name in user_agent:
            return factory.name
    # Try to match Linux or Windows
    for factory in factories:
        if factory.operating_system.platform.name in user_agent:
            return factory.name
    # Return first candidate (latest poll)
    if factories:
        return factories[0].name


def add(http_request):
    """
    Add a browser that is installed on a screenshot factory.
    """
    # Check that User-Agent header was transmitted.
    if 'HTTP_USER_AGENT' not in http_request.META:
        return error_page(http_request, "Missing User-Agent header",
"Your browser cannot be detected because it didn't send a User-Agent header.",
"Or maybe you have a firewall that removed this header from the HTTP request.")
    if not http_request.META['HTTP_USER_AGENT'].strip():
        return error_page(http_request, "Empty User-Agent header",
"Your browser cannot be detected because it sent an empty User-Agent header.",
"Or maybe you have a firewall that removed this header from the HTTP request.")
    # Update translation for field labels
    for key in BrowserForm.base_fields:
        BrowserForm.base_fields[key].label = _(
            Browser._meta.get_field(key).verbose_name)
    # Prefill form fields with user agent from HTTP request
    ip = http_request.META['REMOTE_ADDR']
    user_agent = http_request.META['HTTP_USER_AGENT']
    initial = {
        'user_agent': user_agent,
        'javascript': 1, # disabled
        'java': 1, # disabled
        'flash': 1, # disbled
        }
    # Extract engine and engine version from user agent string
    user_agent_lower = user_agent.lower()
    for engine in agents.get_engines():
        if engine.name.lower() in user_agent_lower:
            initial['engine'] = engine.id
            initial['engine_version'] = agents.extract_version(
                user_agent, engine.name)
            break
    # Extract browser group and version from user agent string
    for browser_group in agents.get_browser_groups():
        if browser_group.name.lower() in user_agent_lower:
            initial['browser_group'] = browser_group.id
            version = agents.extract_version(
                user_agent, browser_group.name)
            initial['version'] = version
            initial['major'] = agents.extract_major(
                version, browser_group.name)
            initial['minor'] = agents.extract_minor(
                version, browser_group.name)
            break
    form = BrowserForm(http_request.POST or initial)
    password_form = PasswordForm(http_request.POST or None)
    password_form['password'].field.widget.render_value = False
    if not http_request.POST:
        password_form['factory_name'].field.initial = (
            http_request.GET.get('factory', None) or
            guess_factory_name(ip, user_agent))
    field_groups = [[
        [form['user_agent']],
        [form['command']],
        ], [
        [form['browser_group'], form['version'], form['major'], form['minor']],
        [form['engine'], form['engine_version']],
        ], [
        [form['javascript'], form['java'], form['flash']],
        ], [
        [password_form['factory_name']],
        [password_form['password']],
        ]]
    admin_email = mark_safe(u'<a href="mailto:%s">%s</a>' % (
        settings.ADMINS[0][1], settings.ADMINS[0][0]))
    if form.is_valid() and password_form.is_valid():
        form.cleaned_data['factory'] = password_form.cleaned_data['factory']
    else:
        return render_to_response('browsers/add.html', locals(),
            context_instance=RequestContext(http_request))
    # Activate or add browser in the database
    activate_or_add_browser(form.cleaned_data)
    # Save IP address, to guess the factory when adding the next browser
    form.cleaned_data['factory'].update_fields(ip=ip)
    # Redirect to factory detail page
    return results.redirect(form.cleaned_data['factory'],
                            form.cleaned_data['action'],
                            form.cleaned_data['browser'],
                            'browsers')


def activate_or_add_browser(data):
    """
    Add or activate browser in the database.
    """
    activated = activate_browser(data)
    if activated:
        delete_or_deactivate_similar_browsers(data, exclude=activated)
        return
    else:
        delete_or_deactivate_similar_browsers(data)
    # Create new browser with submitted data
    data['active'] = True
    data['browser'] = Browser.objects.create(**data)
    data['action'] = 'added_browser'


def activate_browser(data):
    """
    Try to activate existing browser, and update settings.
    """
    existing_browsers = Browser.objects.filter(
        factory=data['factory'],
        user_agent=data['user_agent'],
        browser_group=data['browser_group'],
        version=data['version'],
        javascript=data['javascript'],
        java=data['java'],
        flash=data['flash'],
        )
    if len(existing_browsers) == 0:
        return False
    browser = existing_browsers[0]
    data['browser'] = browser
    for candidate in existing_browsers:
        if candidate.active:
            browser = candidate
            break
    modified = False
    data['active'] = True
    data['action'] = 'activated_browser'
    for field in 'active command major minor engine engine_version'.split():
        if getattr(browser, field) != data[field]:
            setattr(browser, field, data[field])
            modified = True
    if modified:
        data['action'] = 'updated_browser'
        browser.save()
    return browser


def delete_or_deactivate_similar_browsers(data, exclude=None):
    """
    Delete or deactivate similar browsers in the database.
    """
    where = u"""(
(factory_id = %s AND user_agent = %s) OR
(factory_id = %s AND browser_group_id = %s AND major = %s AND minor = %s)
)"""
    params = [
        data['factory'].id,
        data['user_agent'],
        data['factory'].id,
        data['browser_group'].id,
        data['major'],
        data['minor'],
        ]
    if exclude:
        where += "AND id != %s"
        params += [exclude.id]
    # Delete old unused versions of the same browsers
    cursor = connection.cursor()
    cursor.execute("""
DELETE FROM browsers_browser
WHERE """ + where + """
AND NOT EXISTS(SELECT 1 FROM screenshots_screenshot
               WHERE browser_id = browsers_browser.id LIMIT 1)
AND NOT EXISTS(SELECT 1 FROM requests_request
               WHERE browser_id = browsers_browser.id LIMIT 1)
""", params)
    # Deactivate old versions of the same browser
    cursor.execute("""
UPDATE browsers_browser SET active = FALSE
WHERE """ + where, params)
