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
XML-RPC interface for screenshots app.
"""

__revision__ = "$Rev: 2849 $"
__date__ = "$Date: 2008-05-15 02:04:35 -0300 (qui, 15 mai 2008) $"
__author__ = "$Author: johann $"

import os
import commands
from xmlrpclib import Fault, Binary
from datetime import datetime
from django.utils.text import capfirst
from django.conf import settings
from shotserver04.common import serializable, get_or_fault
from shotserver04.xmlrpc import signature, factory_xmlrpc
from shotserver04.nonces import xmlrpc as nonces
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser
from shotserver04.requests.models import Request
from shotserver04.screenshots.models import Screenshot
from shotserver04.screenshots import storage

PREVIEW_SIZES = [512, 160]
# PREVIEW_SIZES = [512, 240, 160, 116, 92, 77, 57, 44, 32]
# PREVIEW_SIZES = [640, 316, 208, 154, 100, 64, 46]


class ExtraFault(Fault):
    def __init__(self, code, message, **extra):
        Fault.__init__(self, code, message, **extra)
        for key in extra:
            setattr(self, key, extra[key])


@serializable
def close_request(request_id, factory, screenshot):
    """
    Close a screenshot request after it has been completed.
    """
    # Check again that no other factory has locked the request
    request = get_or_fault(Request, pk=request_id)
    try:
        request.check_factory_lock(factory)
    except Fault:
        screenshot.delete()
        raise
    # Close the request
    request.update_fields(screenshot=screenshot)


@factory_xmlrpc
@signature(str, str, str, int, Binary)
def upload(http_request, factory, encrypted_password, request, screenshot):
    """
    Submit a multi-page screenshot as a lossless PNG file.

    Arguments
    ~~~~~~~~~
    * factory_name string (lowercase, normally from hostname)
    * encrypted_password string (lowercase hexadecimal, length 32)
    * request int (from requests.poll)
    * screenshot binary (BASE64-encoded PNG file)

    See nonces.verify for how to encrypt your password.

    Return value
    ~~~~~~~~~~~~
    * hashkey string (lowercase hexadecimal, length 32)

    Users can see the resulting uploaded screenshot at
    http://browsershots.org/screenshots/hashkey/
    """
    # Verify authentication
    nonces.verify(http_request, factory, encrypted_password)
    request_id = request
    request = get_or_fault(Request, pk=request_id)
    request_group = request.request_group
    # Make sure the request was locked by this factory
    request.check_factory_lock(factory)
    # Store and check screenshot file
    hashkey = storage.save_upload(screenshot)
    bytes = storage.png_filesize(hashkey)
    # Make sure the request was redirected by the browser
    browser = request.browser
    if browser is None or browser.factory_id != factory.id:
        guessed = factory.browser_set.filter(active=True,
            browser_group=request.browser_group,
            major=request.major, minor=request.minor)[:1]
        if not len(guessed):
            guessed = [None]
        raise ExtraFault(406,
            u"The browser has not visited the requested website.",
            request=request, hashkey=hashkey, browser=guessed[0])
    # Unpack PNG file and run more checks
    ppmname = storage.pngtoppm(hashkey)
    try:
        magic, width, height = storage.read_pnm_header(ppmname)
        if request_group.width and request_group.width != width:
            raise ExtraFault(412,
                u"The screenshot is %d pixels wide, not %d as requested." %
                (width, request_group.width),
                request=request, hashkey=hashkey, browser=browser)
        if height > width * 4:
            raise ExtraFault(413,
                u"The screenshot is too tall (more than 4 times the width).",
                request=request, hashkey=hashkey, browser=browser)
        if height < width / 2:
            raise ExtraFault(414,
                u"The screenshot is too short (less than half the width).",
                request=request, hashkey=hashkey, browser=browser)
        if os.path.exists('/usr/local/etc/pbmgrep'):
            check_ppm_problems(ppmname, request, hashkey, browser)
        # Make smaller preview images
        for size in PREVIEW_SIZES:
            storage.scale(ppmname, size, hashkey)
    finally:
        # Delete temporary PPM file
        os.unlink(ppmname)
    # Upload screenshots to Amazon S3 (but not for anonymous users)
    if hasattr(settings, 'S3_BUCKETS') and request_group.user_id is not None:
        storage.s3_upload(hashkey) # size='original'
        for size in PREVIEW_SIZES:
            storage.s3_upload(hashkey, size)
    # Save screenshot in database
    screenshot = Screenshot(hashkey=hashkey,
        user=request_group.user, website=request_group.website,
        factory=factory, browser=browser,
        width=width, height=height, bytes=bytes)
    screenshot.save()
    # Close the request
    close_request(request_id, factory, screenshot)
    # Update timestamps and estimates
    now = datetime.now()
    if request.priority == 0:
        factory.update_fields(last_upload=now,
            queue_estimate=(now - request_group.submitted).seconds)
    else:
        factory.update_fields(last_upload=now)
    browser.update_fields(last_upload=now)
    return hashkey


def check_ppm_problems(ppmname, request, hashkey, browser):
    """
    Check for known problems with pbmgrep.
    """
    command = ' '.join(('ppmfg', '<', ppmname, '|', 'pbmgrep',
                        '/usr/local/etc/pbmgrep/6??_*.pbm'))
    # print command
    status, output = commands.getstatusoutput(command)
    # print status, output
    if status == 0:
        return
    lines = output.splitlines()
    parts = lines[0].split('\t')
    if len(parts) == 5:
        filename = os.path.basename(parts[4]).split('.')[0]
        filename_parts = filename.split('_')
        code = int(filename_parts[0])
        message = capfirst(' '.join(filename_parts[1:]) + '.')
    else:
        code = status
        message = ' '.join(lines)
    raise ExtraFault(code, message,
                     request=request, hashkey=hashkey, browser=browser)
