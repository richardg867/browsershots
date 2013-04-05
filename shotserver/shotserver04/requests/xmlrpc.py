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
XML-RPC interface for requests app.
"""

__revision__ = "$Rev: 3051 $"
__date__ = "$Date: 2008-09-03 04:10:24 -0300 (qua, 03 set 2008) $"
__author__ = "$Author: johann $"

import os
import random
from xmlrpclib import Fault
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from shotserver04.common import serializable, int_or_none, lock_timeout
from shotserver04.common.object_cache import preload_foreign_keys
from shotserver04.xmlrpc import signature, factory_xmlrpc
from shotserver04.nonces import xmlrpc as nonces
from shotserver04.websites import normalize_url, extract_domain
from shotserver04.websites.models import Domain, Website
from shotserver04.factories.models import Factory, ScreenSize, ColorDepth
from shotserver04.platforms.models import Platform
from shotserver04.browsers.models import BrowserGroup, Browser
from shotserver04.requests.models import RequestGroup, Request
from datetime import datetime, timedelta
# import time # For test_overload.py

# Priority for e.g. Mac OS X because there are few factories.
PRIORITY_PLATFORMS = []
ACCEPTABLE_SERVER_LOAD = 8.0


@serializable
def find_and_lock_request(factory, features):
    """
    Find a matching screenshot request and lock it.
    """
    # Find matching request
    now = datetime.now()
    five_minutes_ago = now - timedelta(0, 300)
    matches = Request.objects.all()
    matches = matches.filter(features)
    matches = matches.filter(screenshot__isnull=True)
    matches = matches.filter(request_group__expire__gt=now)
    matches = matches.filter(
        models.Q(locked__isnull=True) | models.Q(locked__lt=five_minutes_ago))
    matches = matches.filter(priority__gte=0) # Ignore shock sites
    matches = matches.order_by(
        '-priority', 'requests_requestgroup.submitted')
    own_matches = matches.filter(
        request_group__own_factories_only=True,
        request_group__user=factory.admin_id)
    own_matches = own_matches[:1]
    if len(own_matches):
        matches = own_matches
    else:
        matches = matches.filter(request_group__own_factories_only=False)
        matches = matches[:1]
    # time.sleep(0.1) # For test_overload.py
    if len(matches) == 0:
        raise Fault(204, 'No matching request.')
    request = matches[0]
    # Lock request
    request.update_fields(
        factory=factory,
        browser=None,
        locked=datetime.now())
    return request


def add_version(filters, value, name, exact=False):
    """
    Update filters to get the browser for a matching request.
    """
    if value is None:
        return
    if hasattr(value, 'id'):
        value = value.id
    if value == 2 and not exact: # request for 'enabled'
        filters[name + '__gte'] = 2 # match 'enabled' or version
    else:
        filters[name] = value # specific requested version


def version_or_empty(feature):
    """Return version field, or empty string if feature is None."""
    if feature is None:
        return ''
    else:
        return feature.version


@factory_xmlrpc
@signature(dict, str, str)
def poll(http_request, factory, encrypted_password):
    """
    Try to find a matching screenshot request for a given factory.

    Arguments
    ~~~~~~~~~
    * factory_name string (lowercase, normally from hostname)
    * encrypted_password string (lowercase hexadecimal, length 32)

    See nonces.verify for how to encrypt your password.

    Return value
    ~~~~~~~~~~~~
    * options dict (screenshot request configuration)

    If successful, the options dict will have the following keys:

    * request int (for redirect and screenshots.upload)
    * browser string (browser name)
    * version string (browser version)
    * major int (major browser version number)
    * minor int (minor browser version number)
    * command string (browser command to run, empty for default)
    * width int (screen width in pixels)
    * height int (screen height in pixels)
    * bpp int (color depth in bits per pixel)
    * javascript string (javascript version)
    * java string (java version)
    * flash string (flash version)

    Locking
    ~~~~~~~
    The matching screenshot request is locked for five minutes. This
    is to make sure that no requests are processed by two factories at
    the same time. If your factory takes longer to process a request,
    it is possible that somebody else will lock it. In this case, your
    upload will fail.
    """
    # Verify authentication
    nonces.verify(http_request, factory, encrypted_password)
    # Update last_poll timestamp
    factory.update_fields(last_poll=datetime.now(),
                          ip=http_request.META['REMOTE_ADDR'])
    if hasattr(settings, 'FACTORY_THROTTLE_INTERVAL'):
        if factory.name in settings.FACTORY_THROTTLE_INTERVAL:
            interval = settings.FACTORY_THROTTLE_INTERVAL[factory.name]
            if datetime.now() - factory.last_upload < interval:
                raise Fault(205, ' '.join((
"Sorry, your screenshot factory is blocked for a few minutes.",
"Please check your email for error messages from Browsershots.")))
    # Check server load
    randomized_load = max(os.getloadavg()) * random.random()
    if factory.operating_system.platform_id in PRIORITY_PLATFORMS:
        randomized_load /= 2
    if randomized_load > ACCEPTABLE_SERVER_LOAD:
        raise Fault(503,
"The server is currently overloaded. Please try again in a minute.")
    # Get matching request
    request = find_and_lock_request(factory, factory.features_q())
    # Get matching browser
    filters = {'factory': factory,
               'browser_group': request.browser_group,
               'active': True}
    add_version(filters, request.major, 'major', exact=True)
    add_version(filters, request.minor, 'minor', exact=True)
    add_version(filters, request.request_group.javascript, 'javascript__id')
    add_version(filters, request.request_group.java, 'java__id')
    add_version(filters, request.request_group.flash, 'flash__id')
    try:
        browser = Browser.objects.select_related().get(**filters)
    except Browser.DoesNotExist:
        raise Fault(404, "No matching browser for selected request.")
    # Build result dict
    screen_size = select_screen_size(factory, request)
    color_depth = select_color_depth(factory, request)
    return {
        'request': request.id,
        'browser': browser.browser_group.name,
        'version': browser.version,
        'major': browser.major,
        'minor': browser.minor,
        'command': browser.command,
        'width': screen_size.width,
        'height': screen_size.height,
        'bpp': color_depth.bits_per_pixel,
        'javascript': version_or_empty(request.request_group.javascript),
        'java': version_or_empty(request.request_group.java),
        'flash': version_or_empty(request.request_group.flash),
        }


def select_screen_size(factory, request):
    """
    Select a matching screen size for this screenshot request.
    """
    screen_sizes = ScreenSize.objects.filter(factory=factory)
    if request.request_group.width:
        screen_sizes = screen_sizes.filter(width=request.request_group.width)
    if request.request_group.height:
        screen_sizes = screen_sizes.filter(height=request.request_group.height)
    # Fallback to default size if factory configuration incomplete
    if not len(screen_sizes):
        return ScreenSize(factory=factory, width=1024, height=768)
    # Try most popular screen sizes first
    if len(screen_sizes) > 1:
        for popular in (1024, 800, 1152, 1280, 640):
            for screen_size in screen_sizes:
                if screen_size.width == popular:
                    return screen_size
    # Return the smallest matching screen size
    return screen_sizes[0]


def select_color_depth(factory, request):
    """
    Select a matching color depth for this screenshot request.
    """
    color_depths = ColorDepth.objects.filter(factory=factory)
    color_depths = color_depths.order_by('-bits_per_pixel')
    if request.request_group.bits_per_pixel:
        color_depths = color_depths.filter(
            bits_per_pixel=request.request_group.bits_per_pixel)
    # Fallback to default depth if factory configuration incomplete
    if not len(color_depths):
        return ColorDepth(factory=factory, bits_per_pixel=24)
    # Return greatest matching color depth
    return color_depths[0]


def find_by_name(candidates, name):
    name = name.lower()
    for candidate in candidates:
        if candidate.name.lower() == name:
            return candidate


@signature(int, str, str, str, list)
def submit(http_request, username, encrypted_password, url, browsers):
    """
    Submit a new group of screenshot requests.

    Arguments
    ~~~~~~~~~
    * username string (your user account on the server)
    * encrypted_password string (lowercase hexadecimal, length 32)
    * url string (request screenshots of this website)
    * browsers list (platform, name and version for each browser)

    Return value
    ~~~~~~~~~~~~
    * id int (request group id)

    You can use the returned request group id to check the progress of
    the screenshot requests with requests.status.
    """
    # Get user from database
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Fault(404, "User not found.")
    # Verify authentication
    nonces.verifyUser(http_request, user, encrypted_password)
    # Check priority
    priority = 0
    if 'shotserver04.priority' in settings.INSTALLED_APPS:
        from shotserver04.priority import user_priority
        priority = user_priority(user)
        if priority < 1:
            raise Fault(402, "Priority processing is required.")
    # Create domain and website if needed
    url = normalize_url(url)
    domain_name = extract_domain(url, remove_www=True)
    domain = Domain.objects.get_or_create(name=domain_name)[0]
    website = Website.objects.get_or_create(domain=domain, url=url)[0]
    # Create request group
    expire = datetime.now() + timedelta(minutes=30)
    ip = http_request.META['REMOTE_ADDR']
    request_group = RequestGroup.objects.create(
        website=website, user=user, ip=ip,
        expire=expire, priority=priority)
    # Create browser requests
    platforms = Platform.objects.all()
    browser_groups = BrowserGroup.objects.all()
    for name in browsers:
        parts = name.split('_')
        if len(parts) != 4:
            continue
        platform_name, browser_name, major, minor = parts
        platform_name = platform_name.replace('-', ' ')
        platform = find_by_name(platforms, platform_name)
        if platform is None:
            continue
        browser_group = find_by_name(browser_groups, browser_name)
        if browser_group is None:
            continue
        Request.objects.get_or_create(
            request_group=request_group,
            platform=platform,
            browser_group=browser_group,
            major=int_or_none(major),
            minor=int_or_none(minor),
            priority=priority,
            )
    return request_group.id


@signature(list, int)
def status(http_request, request_group_id):
    """
    List the status of all screenshot requests in a group.

    Arguments
    ~~~~~~~~~
    * id int (request group id from requests.submit)

    Return value
    ~~~~~~~~~~~~
    * status list (request status for each requested browser)

    The list will contain a dictionary for each browser, with the
    following entries:

    * browser string (browser name)
    * status string (pending / starting / loading / uploaded / failed)
    * seconds int (estimated or actual time between request and upload)
    * hashkey string (after the screenshot is uploaded)

    You can use the hashkey to generate the resulting PNG file URL,
    for example if the hashkey is beef1234:

    * http://api.browsershots.org/png/original/be/beef1234.png
    * http://api.browsershots.org/png/512/be/beef1234.png
    * http://api.browsershots.org/png/160/be/beef1234.png

    The /be/ part is the first two characters of the hashkey.
    Normally, the hashkey consists of 32 random lowercase hex
    characters.
    """
    try:
        request_group = RequestGroup.objects.get(id=request_group_id)
    except RequestGroup.DoesNotExist:
        raise Fault(404, "Request group not found.")
    results = []
    matching_browsers = request_group.matching_browsers()
    requests = request_group.request_set.all()
    preload_foreign_keys(requests, browser_group=True, platform=True)
    this_lock_timeout = lock_timeout()
    for request in requests:
        platform_name = request.platform.name.lower()
        browser_name = request.browser_group.name.lower()
        major = str(request.major)
        minor = str(request.minor)
        name = '_'.join((platform_name, browser_name, major, minor))
        name = name.replace(' ', '-')
        hashkey = ''
        if request.screenshot_id is not None:
            status = 'uploaded'
            seconds = (request.screenshot.uploaded -
                       request_group.submitted).seconds
            hashkey = request.screenshot.hashkey
        elif request.locked and request.locked < this_lock_timeout:
            status = 'failed'
            seconds = 0
        elif request.redirected:
            status = 'loading'
            seconds = (request.redirected -
                       request_group.submitted).seconds + 45
        elif request.locked:
            status = 'starting'
            seconds = (request.locked -
                       request_group.submitted).seconds + 60
        else:
            status = 'pending'
            seconds = request.queue_estimate(matching_browsers) or 0
        results.append({'browser': name,
                        'status': status,
                        'seconds': seconds,
                        'hashkey': hashkey,
                        })
    return results
