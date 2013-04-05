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
Screenshot views.
"""

__revision__ = "$Rev: 2971 $"
__date__ = "$Date: 2008-08-14 08:21:38 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import os
import cgi
import zipfile
import tempfile
from datetime import timedelta
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from shotserver04.common import results
from shotserver04.common.object_cache import preload_foreign_keys
from shotserver04.screenshots.models import Screenshot, ProblemReport
from shotserver04.screenshots.models import PROBLEM_CHOICES
from shotserver04.screenshots.models import PROBLEM_CHOICES_EXPLICIT
from shotserver04.screenshots import storage
from shotserver04.requests.models import Request, RequestGroup

COLUMNS = 10
WIDTH = 80 # pixels
MARGIN = 12 # pixels


def recent_screenshots(user=None):
    """
    Iterator for the most recent screenshots, one per website.
    """
    screenshots = list(Screenshot.objects.recent(user))
    preload_foreign_keys(screenshots, website=True)
    preload_foreign_keys(screenshots, browser__browser_group=True)
    for screenshot in screenshots:
        if (hasattr(settings, 'PROFANITIES_ALLOWED') and
            screenshot.website.profanities > settings.PROFANITIES_ALLOWED):
            # Hide screenshots that are not safe for work
            continue
        if (screenshot.browser.browser_group.unusual or
            screenshot.browser.browser_group.terminal):
            # Find a better representative for this website
            better = Screenshot.objects.filter(
                website=screenshot.website_id,
                browser__browser_group__unusual=False,
                browser__browser_group__terminal=False,
                uploaded__gte=screenshot.uploaded - timedelta(minutes=30))
            better = better.order_by('-uploaded')[:1]
            if len(better):
                website = screenshot._website_cache
                screenshot = better[0]
                screenshot._website_cache = website
        yield screenshot


def overview(http_request):
    """
    Full-screen display of recent screenshots (one per website).
    """
    columns = [[0, index * (WIDTH + MARGIN)] for index in range(COLUMNS)]
    previews = []
    for screenshot in recent_screenshots(http_request.user):
        width = WIDTH
        height = screenshot.height * width / screenshot.width
        columns.sort()
        top, left = columns[0]
        previews.append(screenshot.preview_div(
            style=u"left:%dpx;top:%dpx;position:absolute" % (left, top),
            title=screenshot.website.url,
            href=screenshot.website.get_absolute_url()))
        columns[0][0] += height + MARGIN
    columns.sort()
    previews.insert(0,
        u'<div class="previews" style="height:%dpx">' % columns[-1][0])
    previews.append('</div>')
    previews = mark_safe('\n'.join(previews))
    return render_to_response('screenshots/overview.html', locals(),
        context_instance=RequestContext(http_request))


class ProblemForm(forms.Form):
    """
    Simple form for user feedback about screenshot problems.
    """
    code = forms.ChoiceField(widget=forms.RadioSelect)
    message = forms.CharField(max_length=200, required=False,
        help_text="Please write in English if possible.")

    def clean_message(self):
        """
        Disallow HTML and URL spam in user-supplied problem messages.
        """
        message = self.cleaned_data['message'].lower()
        if '<' in message and '>' in message:
            raise forms.ValidationError(
                unicode(_("HTML is not allowed here.")))
        for word in 'http:// https:// www. .com .net .org'.split():
            if word in message:
                raise forms.ValidationError(
                    unicode(_("URLs are not allowed here.")))
        return cgi.escape(self.cleaned_data['message'])

    def clean_code(self):
        return int(self.cleaned_data['code'])


def details(http_request, hashkey):
    """
    Show large preview and detailed information about a screenshot.
    """
    screenshot = get_object_or_404(Screenshot, hashkey=hashkey)
    request = get_object_or_404(Request, screenshot=screenshot)
    problem_form = ProblemForm(http_request.POST)
    requested = {
        'browser': unicode(screenshot.browser),
        'operating_system': unicode(screenshot.factory.operating_system),
        'java': unicode(screenshot.browser.java),
        'javascript': unicode(screenshot.browser.javascript),
        'flash': unicode(screenshot.browser.flash),
        }
    choices = []
    codes = PROBLEM_CHOICES.keys()
    codes.sort()
    for code in codes:
        if code in PROBLEM_CHOICES_EXPLICIT:
            choices.append((code, PROBLEM_CHOICES_EXPLICIT[code] % requested))
        else:
            choices.append((code, PROBLEM_CHOICES[code]))
    choices.append((999, ''))
    problem_form.fields['code'].choices = choices
    if problem_form.is_valid():
        code = int(problem_form.cleaned_data['code'])
        if code in PROBLEM_CHOICES_EXPLICIT:
            problem_form.cleaned_data['message'] = (
                PROBLEM_CHOICES_EXPLICIT[code] % requested)
        elif code in PROBLEM_CHOICES:
            problem_form.cleaned_data['message'] = PROBLEM_CHOICES[code]
        if problem_form.cleaned_data['message']:
            problem_report = ProblemReport.objects.create(
                screenshot=screenshot,
                ip=http_request.META['REMOTE_ADDR'],
                **problem_form.cleaned_data)
            return results.redirect(
                screenshot.factory, 'added_problem_report',
                problem_report, 'problems')
    length = len(PROBLEM_CHOICES)
    select = "document.forms['problem_form'].code[%d].checked=true" % length
    message_field = problem_form['message'].as_text(
        {'onclick': select, 'onchange': 'if (this.value) ' + select})
    return render_to_response('screenshots/details.html', locals(),
        context_instance=RequestContext(http_request))


def download_zip(http_request, request_group_id):
    """
    Output a ZIP file containing all screenshots in a request group.
    """
    request_group = get_object_or_404(RequestGroup, id=request_group_id)
    requests = request_group.request_set.filter(screenshot__isnull=False)
    preload_foreign_keys(requests, screenshot=True)
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_STORED)
    for request in requests:
        filename = storage.png_filename(request.screenshot.hashkey)
        if not os.path.exists(filename):
            continue
        archive.write(filename, str(request.screenshot.png_filename()))
    archive.close()
    # Send result to browser
    response = HttpResponse(FileWrapper(temp), content_type='application/zip')
    response['Content-Disposition'] = 'attachment' # ; filename=screenshots.zip
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
