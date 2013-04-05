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
Server status views.
"""

__revision__ = "$Rev: 3105 $"
__date__ = "$Date: 2008-09-14 17:39:42 -0300 (dom, 14 set 2008) $"
__author__ = "$Author: johann $"

import os
import socket
from datetime import datetime, timedelta
from django.conf import settings
from django.db import connection
from django.utils.translation import ugettext as _
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from shotserver04.common import error_page
from shotserver04.common.object_cache import preload_foreign_keys
from shotserver04.websites.models import Website, Domain
from shotserver04.requests.models import RequestGroup


@login_required
def overview(http_request):
    """
    Server status overview.
    """
    # Local time and server uptime.
    local_time = datetime.now()
    if os.path.exists('/proc/uptime'):
        uptime = float(open('/proc/uptime').read().split()[0])
        started = local_time - timedelta(seconds=uptime)
    # Load averages.
    load_averages = '%.2f %.2f %.2f' % os.getloadavg()
    # Free disk space.
    stat = os.statvfs(settings.PNG_ROOT)
    total_disk_space = stat.f_blocks * stat.f_frsize
    free_disk_space = stat.f_bavail * stat.f_frsize
    free_disk_percent = 100 * stat.f_bavail / stat.f_blocks
    return render_to_response('status/overview.html', locals(),
        context_instance=RequestContext(http_request))


@login_required
def usage(http_request, usage_interval='7d'):
    """
    Show the heaviest users in the last 7 days (or other timeframe).
    """
    website_list = usage_list(Website, """\
SELECT website_id, COUNT(*) AS groups FROM requests_requestgroup
WHERE requests_requestgroup.submitted > NOW() - %s::interval
GROUP BY website_id""", usage_interval)
    domain_list = usage_list(Domain, """\
SELECT domain_id, COUNT(*) AS groups FROM requests_requestgroup
JOIN websites_website ON (websites_website.id = website_id)
WHERE requests_requestgroup.submitted > NOW() - %s::interval
GROUP BY domain_id""", usage_interval)
    user_list = usage_list(User, """\
SELECT user_id, COUNT(*) AS groups FROM requests_requestgroup
WHERE requests_requestgroup.submitted > NOW() - %s::interval
AND user_id IS NOT NULL
GROUP BY user_id""", usage_interval)
    ip_list = usage_list(None, """\
SELECT ip, COUNT(*) AS groups FROM requests_requestgroup
WHERE requests_requestgroup.submitted > NOW() - %s::interval
GROUP BY ip""", usage_interval)
    ip_list = [(row[0], socket.getfqdn(row[0]), row[1]) for row in ip_list]
    plaintext = usage_interval.replace('d', ' days').replace('h', ' hours')
    if plaintext == '1 hours':
        plaintext = 'hour'
    if plaintext == '7 days':
        plaintext = 'week'
    usage_intervals_list = '1h 4h 12h 24h 2d 4d 7d 14d 30d 120d 365d'.split()
    return render_to_response('status/usage.html', locals(),
        context_instance=RequestContext(http_request))


def usage_list(Model, sql, interval):
    cursor = connection.cursor()
    cursor.execute(sql + " ORDER BY groups DESC LIMIT 10", (interval, ))
    rows = cursor.fetchall()
    if Model is None:
        return rows
    result_dict = Model.objects.in_bulk([row[0] for row in rows])
    result_list = [result_dict[row[0]] for row in rows]
    for index in range(len(result_list)):
        result_list[index].request_groups_per_day = rows[index][1]
    return result_list


@login_required
def user_report(http_request, username):
    user = get_object_or_404(User, username=username)
    if user != http_request.user and not http_request.user.is_staff:
        return error_page(http_request, _("Access denied"),
                          _("Only staff members can see this page."))
    request_groups_list = user.requestgroup_set.order_by('-submitted')[:50]
    preload_foreign_keys(request_groups_list, website=True)
    return render_to_response('status/user_report.html', locals(),
        context_instance=RequestContext(http_request))
