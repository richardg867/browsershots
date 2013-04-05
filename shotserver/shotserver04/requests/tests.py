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
Test suite for requests app.
"""

__revision__ = "$Rev: 2956 $"
__date__ = "$Date: 2008-08-13 19:04:39 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

import os
from md5 import md5
from datetime import datetime, timedelta
from psycopg import IntegrityError
from xmlrpclib import Fault
from unittest import TestCase
from django.db import transaction, connection
from django.contrib.auth.models import User
from shotserver04.platforms.models import Platform, OperatingSystem
from shotserver04.factories.models import Factory, ScreenSize, ColorDepth
from shotserver04.screenshots.models import Screenshot
from shotserver04.browsers.models import Engine, BrowserGroup, Browser
from shotserver04.websites.models import Domain, Website
from shotserver04.requests.models import RequestGroup, Request
from shotserver04.requests import xmlrpc as requests
from shotserver04.nonces import xmlrpc as nonces
from shotserver04.factories import xmlrpc as factories

SHA1_PASSWORD = 'edefaf28ff4645d1dfd075c18b8ac36a5fe691f9'


class FakeHttpRequest:

    def __init__(self):
        self.META = {'REMOTE_ADDR': '127.0.0.1'}


class PollTestCase(TestCase):

    def setUp(self):
        self.http_request = FakeHttpRequest()
        self.user = User.objects.create(
            password='sha1$a5481$' + SHA1_PASSWORD)
        self.factory = Factory.objects.create(
            name='factory',
            admin=self.user,
            hardware='MacBook, Intel Core Duo, 2 GB RAM',
            operating_system=OperatingSystem.objects.get(pk=1))
        self.screen_size = ScreenSize.objects.create(
            factory=self.factory,
            width=1024,
            height=768)
        self.color_depth = ColorDepth.objects.create(
            factory=self.factory,
            bits_per_pixel=24)
        self.browser = Browser.objects.create(
            factory=self.factory,
            user_agent="Firefox/2.0.0.4 Gecko/20061201",
            browser_group_id=1,
            version='2.0.0.4', major=2, minor=0,
            command='firefox',
            engine=Engine.objects.get(pk=1),
            engine_version='20061201',
            javascript_id=1,
            java_id=1,
            flash_id=1,
            active=True)
        self.domain = Domain.objects.create(
            name='browsershots.org')
        self.website = Website.objects.create(
            url='http://browsershots.org/',
            domain=self.domain)
        self.request_group = RequestGroup.objects.create(
            website=self.website,
            expire=datetime.now() + timedelta(0, 300, 0),
            ip='127.0.0.1')
        self.request = Request.objects.create(
            request_group=self.request_group,
            platform_id=1,
            browser_group_id=1,
            priority=1)

    def tearDown(self):
        self.request.delete()
        self.request_group.delete()
        self.website.delete()
        self.domain.delete()
        self.browser.delete()
        self.color_depth.delete()
        self.screen_size.delete()
        self.factory.delete()
        self.user.delete()

    def testFeatures(self):
        features = factories.features(self.http_request, 'factory')

    def encrypted_password(self):
        challenge = nonces.challenge(
            self.http_request, 'factory')
        if challenge['algorithm'] == 'sha1':
            return md5(SHA1_PASSWORD + challenge['nonce']).hexdigest()
        elif challenge['algorithm'] == 'md5':
            return md5(MD5_PASSWORD + challenge['nonce']).hexdigest()
        else:
            self.fail(u"Unsupported algorithm: %s." % challenge['algorithm'])

    def testPoll(self):
        # Poll for matching request.
        try:
            result = requests.poll(self.http_request, self.factory,
                                   self.encrypted_password())
        except Fault, fault:
            transaction.rollback()
            raise
        # Now expect no match because the previous request was locked.
        try:
            result = requests.poll(self.http_request, self.factory,
                                   self.encrypted_password())
            self.fail("Unexpected matching request.")
        except Fault, fault:
            transaction.rollback()
            if fault.faultString != 'No matching request.':
                raise
