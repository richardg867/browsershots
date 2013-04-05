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
Test suite for websites app.
"""

__revision__ = "$Rev: 2005 $"
__date__ = "$Date: 2007-08-19 21:22:02 -0300 (dom, 19 ago 2007) $"
__author__ = "$Author: johann $"

from psycopg import IntegrityError, ProgrammingError
from unittest import TestCase
from django.db import transaction
from shotserver04.websites import extract_domain
from shotserver04.websites.models import Domain, Website

INVALID_URLS = [
    '',
    ' ',
    'h',
    'http',
    'http:',
    'http:/',
    'http://',
    'http:///',
    'http://browsershots/',
    'htp://browsershots.org/',
    'http//browsershots.org/',
    'http:/browsershots.org/',
    'http://browsershots.org:abc/',
    'http://browsershots.org',
    'http://browsershots..org/',
    'http://browsershots.org/ ',
    'http://.browsershots.org/',
    ' http://browsershots.org/',
    'http://1.2.3/',
    'http://1.2.3.4.5/',
    'http://1234.123.123.123/',
    'http://123.1234.123.123/',
    'http://123.123.1234.123/',
    'http://123.123.123.1234/',
    'http://123.123.123.123:abc/',
    'http://0x12.0x45.0x9a.0xfg/',
    'http://0x123.0x45.0x9a.0xef/',
    ]

VALID_URLS = [
    'http://browsershots.org/',
    'http://browsershots.org:80/',
    'https://browsershots.org/',
    'https://browsershots.org:443/',
    'http://www.browsershots.org/',
    'http://svn.browsershots.org/',
    'http://BrowserShots.org/',
    'http://WWW.BROWSERSHOTS.ORG/',
    'hTtP://WwW.BroWSersHotS.oRg/',
    'HTTP://BROWSERSHOTS.ORG/',
    'Https://browsershots.org/',
    'hTtps://browsershots.org/',
    'htTps://browsershots.org/',
    'httPs://browsershots.org/',
    'httpS://browsershots.org/',
    'http://1234567890:12345/',
    'http://1234567890:12345/123',
    'http://0x12.0x45.0x9a.0xef/',
    'http://0x12.0x45.0x9a.0xef:80/',
    'http://123.123.123.123/',
    'http://123.123.123.123/test/',
    'http://browsershots.org/index.html',
    'http://browsershots.org/robots.txt',
    'http://browsershots.org/http://example.com/',
    'http://browsershots.org/?url=http://example.com/',
    'https://trac.browsershots.org/blog?format=rss',
    ]


class WebsitesTestCase(TestCase):

    def setUp(self):
        self.domain, created = Domain.objects.get_or_create(
            name='browsershots.org')
        self.website = Website.objects.create(
            url='http://browsershots.org/',
            domain=self.domain)

    def tearDown(self):
        self.website.delete()
        self.domain.delete()

    def testChangeURL(self):
        self.website.url = 'https://browsershots.org/websites/'
        self.website.save()
        self.assertEqual(len(Website.objects.filter(
            url__contains='browsershots.org')), 1)

    def testCreateDuplicate(self):
        try:
            self.assertRaises(IntegrityError, Website.objects.create,
                              url='http://browsershots.org/')
        finally:
            transaction.rollback()

    def testMaxLength(self, length=400):
        try:
            website = Website.objects.create(url='http://browsershots.org/' +
                'x' * (length - len('http://browsershots.org/')),
                domain=self.domain)
            website.delete()
        except ProgrammingError:
            transaction.rollback()
            self.fail(u'could not create URL with %d characters' % length)

    def testTooLong(self, length=401):
        try:
            website = Website.objects.create(url='http://browsershots.org/' +
                'x' * (length - len('http://browsershots.org/')),
                domain=self.domain)
            website.delete()
            self.fail(u'created URL with %d characters' % length)
        except ProgrammingError:
            transaction.rollback()


class UrlTestCase(TestCase):

    def assertInvalid(self, url):
        try:
            domain = Domain.objects.create(name=extract_domain(url))
            website = Website.objects.create(url=url, domain=domain)
            website.delete()
            domain.delete()
            self.fail(u"invalid URL did not raise IntegrityError: '%s'" % url)
        except IntegrityError:
            transaction.rollback()

    def testInvalidUrls(self):
        for url in INVALID_URLS:
            self.assertInvalid(url)

    def assertValid(self, url):
        self.assertEqual(Website.objects.filter(url=url).count(), 0)
        domain, created = Domain.objects.get_or_create(
            name=extract_domain(url))
        try:
            website = Website.objects.create(url=url, domain=domain)
        except IntegrityError:
            transaction.rollback()
            self.fail(u"valid URL raised IntegrityError: '%s'" % url)
        self.assertEqual(Website.objects.filter(url=url).count(), 1)
        website.delete()
        self.assertEqual(Website.objects.filter(url=url).count(), 0)

    def testValidUrls(self):
        for url in VALID_URLS:
            self.assertValid(url)
