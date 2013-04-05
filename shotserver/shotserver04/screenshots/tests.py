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
Test suite for screenshots app.
"""

__revision__ = "$Rev: 3052 $"
__date__ = "$Date: 2008-09-03 04:11:13 -0300 (qua, 03 set 2008) $"
__author__ = "$Author: johann $"

from datetime import datetime
from psycopg import IntegrityError
from unittest import TestCase
from django.db import transaction
from django.contrib.auth.models import User
from shotserver04.platforms.models import Platform, OperatingSystem
from shotserver04.factories.models import Factory
from shotserver04.screenshots.models import Screenshot
from shotserver04.browsers.models import Engine, BrowserGroup, Browser
from shotserver04.requests.models import RequestGroup, Request
from shotserver04.websites.models import Domain, Website

VALID_SIZES = [
    (640, 480),
    (800, 600),
    (1024, 768),
    (1280, 1024),
    (1600, 1200),
    (640, 320),
    (800, 400),
    (1024, 512),
    (1280, 640),
    (1600, 800),
    (640, 2560),
    (800, 3200),
    (1024, 4096),
    (1280, 5120),
    (1600, 6400),
    ]

INVALID_SIZES = [
    (640, 319),
    (800, 399),
    (1024, 511),
    (1280, 639),
    (1600, 799),
    (640, 2561),
    (800, 3201),
    (1024, 4097),
    (1280, 5121),
    (1600, 6401),
    (0, 0),
    (639, 480),
    (1681, 1200),
    ]


class SizeTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.factory = Factory.objects.create(
            name='factory',
            admin=self.user,
            hardware='MacBook, Intel Core Duo, 2 GB RAM',
            operating_system=OperatingSystem.objects.get(pk=1))
        self.browser = Browser.objects.create(
            factory=self.factory,
            user_agent="Firefox/2.0.0.4 Gecko/20061201",
            browser_group=BrowserGroup.objects.get(pk=1),
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

    def tearDown(self):
        self.website.delete()
        self.domain.delete()
        self.browser.delete()
        self.factory.delete()
        self.user.delete()

    def assertSizeValid(self, width, height):
        try:
            screenshot = Screenshot.objects.create(
                hashkey='0123456789abcdef' * 2,
                website=self.website,
                factory=self.factory,
                browser=self.browser,
                width=width,
                height=height)
            screenshot.delete()
        except IntegrityError:
            transaction.rollback()
            raise

    def testValidSizes(self):
        for width, height in VALID_SIZES:
            self.assertSizeValid(width, height)

    def assertSizeInvalid(self, width, height):
        try:
            try:
                screenshot = Screenshot.objects.create(
                    hashkey='0123456789abcdef' * 2,
                    website=self.website,
                    factory=self.factory,
                    browser=self.browser,
                    width=width,
                    height=height)
                screenshot.delete()
                self.fail(u'created screenshot with invalid size %dx%d' %
                          (width, height))
            except IntegrityError:
                pass
        finally:
            transaction.rollback()

    def testInvalidSizes(self):
        for width, height in INVALID_SIZES:
            self.assertSizeInvalid(width, height)
