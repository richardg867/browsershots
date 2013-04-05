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
Self-documenting XML-RPC interface.
"""

__revision__ = "$Rev: 2913 $"
__date__ = "$Date: 2008-06-30 17:34:05 -0300 (seg, 30 jun 2008) $"
__author__ = "$Author: johann $"

import re
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.conf import settings
from shotserver04.xmlrpc.dispatcher import Dispatcher

RST_SETTINGS = {
    'initial_header_level': 2,
    'doctitle_xform': False,
    'docinfo_xform': False,
    }


def xmlrpc(http_request):
    """
    XML-RPC interface (for POST requests) and automatic human-readable
    HTML documentation (for GET requests).
    """
    try:
        is_post_request = len(http_request.POST)
    except (IOError, SystemError), error:
        return HttpResponse(content=str(error), status=500)
    if is_post_request:
        response = HttpResponse()
        response.write(dispatcher.dispatch_request(http_request))
        response['Content-length'] = str(len(response.content))
        return response
    else:
        method_list = dispatcher.list_methods(http_request)
        return render_to_response('xmlrpc/method_list.html', locals(),
            context_instance=RequestContext(http_request))


def method_help(http_request, method_name):
    """
    Display automatic help about an XML-RPC method.
    """
    if len(http_request.POST):
        raise Http404 # Don't POST here, only GET documentation
    if method_name not in dispatcher.list_methods(http_request):
        raise Http404 # Method not found
    signatures = dispatcher.method_signature(http_request, method_name)
    signature_lines = []
    for signature in signatures:
        result = signature[0]
        params = signature[1:]
        signature_lines.append('%s(%s) => %s' % (
            method_name, ', '.join(params), result))
    docstring = dispatcher.method_help(http_request, method_name)
    try:
        from docutils import core
        parts = core.publish_parts(
            source=docstring, writer_name='html',
            settings_overrides=RST_SETTINGS)
        docstring = parts['html_body']
    except ImportError:
        docstring = u'<pre>\n%s\n</pre>\n' % docstring
    for method in dispatcher.funcs:
        docstring = re.sub(r'(%s)(\W)' % re.escape(method),
            r'<a href="../\1/">\1</a>\2', docstring)
    docstring = mark_safe(docstring)
    return render_to_response('xmlrpc/method_help.html', locals(),
        context_instance=RequestContext(http_request))


dispatcher = Dispatcher()
for app in settings.INSTALLED_APPS:
    try:
        module = __import__(app + '.xmlrpc', globals(), locals(), ['xmlrpc'])
    except ImportError, error:
        if 'no module named xmlrpc' in str(error).lower():
            continue
        raise
    for name, item in module.__dict__.items():
        if hasattr(item, '_signature'):
            function_name = '%s.%s' % (app.split('.')[-1], name)
            dispatcher.register_function(item, function_name)
