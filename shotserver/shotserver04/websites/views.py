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
Website views.
"""

__revision__ = "$Rev: 2970 $"
__date__ = "$Date: 2008-08-14 08:20:26 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.http import Http404
from django.core.paginator import Paginator
from shotserver04.websites.models import Website, Domain
from shotserver04.browsers.models import Browser, BrowserGroup
from shotserver04.requests.models import RequestGroup
from shotserver04.factories.models import Factory
from shotserver04.common.object_cache import preload_foreign_keys
from shotserver04.websites import normalize_url, extract_domain


def overview(http_request):
    """
    List recently requested websites, with keyword search filter.
    """
    request_group_list = RequestGroup.objects
    search_query = http_request.GET.get('q', '')
    for search in search_query.split():
        if search.islower(): # Case insensitive search
            request_group_list = request_group_list.filter(
                website__url__icontains=search)
        else: # Case sensitive search if mixed case in query
            request_group_list = request_group_list.filter(
                website__url__contains=search)
    if http_request.user.is_anonymous():
        request_group_list = request_group_list.filter(user__isnull=True)
    else:
        request_group_list = request_group_list.filter(user=http_request.user)
    request_group_list = request_group_list.order_by('-submitted')[:60]
    preload_foreign_keys(request_group_list, website=True)
    return render_to_response('websites/overview.html', locals(),
        context_instance=RequestContext(http_request))


def unknown_url(http_request, url):
    """
    Error page for unknown URL.
    """
    domains = Domain.objects.filter(name=extract_domain(url, remove_www=True))
    if len(domains):
        domain_website_list = domains[0].website_set.all()
    return render_to_response('websites/unknown.html', locals(),
        context_instance=RequestContext(http_request))


def details(http_request, url):
    """
    Show details for a selected website.
    """
    page = 1
    if url.isdigit():
        website = get_object_or_404(Website, id=int(url))
        if 'page' in http_request.GET:
            page = int(http_request.GET['page'])
    else:
        if http_request.META['QUERY_STRING']:
            url += '?' + http_request.META['QUERY_STRING']
        url = normalize_url(url) # Replace ' ' with '%20' etc.
        try:
            website = Website.objects.get(url=url)
        except Website.DoesNotExist:
            return unknown_url(http_request, url)
    # Use caching to reduce number of SQL queries
    domain = website.domain
    browsers = Browser.objects.all()
    preload_foreign_keys(browsers, browser_group=True)
    factories = Factory.objects.all()
    preload_foreign_keys(factories, operating_system=True)
    request_groups = list(website.requestgroup_set.all())
    paginator = Paginator(request_groups, 5, orphans=2)
    if page < 1 or page > paginator.num_pages:
        raise Http404('Requested page out of range.')
    request_group_list = paginator.page(page).object_list
    pages_list = []
    if paginator.num_pages > 1:
        for number in range(1, paginator.num_pages + 1):
            extra_classes = ''
            if page == number:
                extra_classes = ' current'
            pages_list.append(
                u'<a class="page%s" href="%s?page=%d">%d</a>' % (
                extra_classes, website.get_numeric_url(), number, number))
    user_has_priority = False
    if 'shotserver04.priority' in settings.INSTALLED_APPS:
        if not http_request.user.is_anonymous():
            user_has_priority = http_request.user.userpriority_set.filter(
                expire__gte=datetime.now()).count()
        if not user_has_priority:
            website_details_head_extra = """
<p class="admonition new">
<a href="/priority/">Support the Browsershots project!<br />
Get a month of priority processing for 10 Euros or 15 Dollars.</a>
</p>
""".strip()
    for index, request_group in enumerate(request_groups):
        request_group._http_request = http_request
        request_group._index = len(request_groups) - index
        request_group._browsers_cache = browsers
        request_group._factories_cache = factories
        request_group._website_cache = website
        request_group._website_cache._domain_cache = domain
    # Get other websites on the same domain
    domain_website_list = domain.website_set.exclude(id=website.id)
    return render_to_response('websites/details.html', locals(),
        context_instance=RequestContext(http_request))
