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
Apply views.
"""

__revision__ = "$Rev: 2295 $"
__date__ = "$Date: 2007-11-16 16:29:27 -0300 (sex, 16 nov 2007) $"
__author__ = "$Author: johann $"

from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from shotserver04.apply.models import Applicant

ApplicantForm = forms.form_for_model(Applicant)


@login_required
def apply(http_request):
    """
    Partner application form.
    """
    form_title = "Want to join Browsershots?"
    form_action = '/apply/'
    form = ApplicantForm(http_request.POST or None)
    form_submit = "submit"
    form_extra_before = '<p class="admonition warning">%s<p>' % ' '.join((
            "This page is only a mock-up.",
            "Your info will not be saved.",
            "Please try again later.",
            ))
    form_extra = '<ul>\n%s\n</ul>' % '\n'.join(
        map(lambda text: '<li>%s</li>' % text, (
"All fields are optional.",
"To edit your information later, simply come back to this page.",
'<a href="http://trac.browsershots.org/wiki/BlogStartupFoundersWanted">' +
    "More information is available in the wiki." +
'</a>',
'<a href="http://trac.browsershots.org/browser/trunk/plugins/apply">' +
    "This application form is an open-source Django app." +
'</a>',
)))
    return render_to_response('form.html', locals(),
        context_instance=RequestContext(http_request))
