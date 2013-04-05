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
Redirect the browser to the requested URL for each screenshot.
"""

__revision__ = "$Rev: 2482 $"
__date__ = "$Date: 2007-12-12 21:07:51 -0300 (qua, 12 dez 2007) $"
__author__ = "$Author: johann $"

from xmlrpclib import Fault
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from shotserver04.common import error_page, result_page
from shotserver04.nonces import xmlrpc as nonces
from shotserver04.factories.models import Factory
from shotserver04.requests.models import Request
from shotserver04.browsers.models import Browser
from shotserver04.messages.models import FactoryError
from datetime import datetime


def redirect(http_request, factory_name, encrypted_password, request_id):
    """
    Redirect the browser to the requested URL for the screenshot, and
    save the browser in the database.
    """
    try:
        factory = get_object_or_404(Factory, name=factory_name)
        nonces.verify(http_request, factory, encrypted_password)
        request = get_object_or_404(Request, id=request_id)
        request.check_factory_lock(factory)
        user_agent = http_request.META['HTTP_USER_AGENT']
        try:
            browser = Browser.objects.get(
                factory=factory,
                user_agent=user_agent,
                active=True)
        except Browser.DoesNotExist:
            raise Fault(404, u"Unknown user agent: %s." % user_agent)
        # Check that the browser matches the request
        if (request.browser_group_id is not None and
            request.browser_group_id != browser.browser_group_id):
            raise Fault(409, u"Requested browser %s but got %s." %
                        (request.browser_group.name,
                         browser.browser_group.name))
        if ((request.major is not None and request.major != browser.major) or
            (request.minor is not None and request.minor != browser.minor)):
            raise Fault(409,
                u"Requested browser version %s.%s but got %s.%s." %
                (request.major, request.minor,
                 browser.major, browser.minor))
        # Update request with browser and redirect timestamp
        request.update_fields(browser=browser,
                              redirected=datetime.now())
        return HttpResponseRedirect(request.request_group.website.url)
    except Fault, fault:
        FactoryError.objects.create(factory=factory,
            code=fault.faultCode, message=fault.faultString)
        return error_page(http_request, "redirect error", fault.faultString)


def redirect_help(http_request):
    """
    Help message.
    """
    return result_page(http_request, 'hint', "Redirect",
        "This page is used to redirect the browser for screenshots.",
        "It must be loaded with appropriate parameters.")
