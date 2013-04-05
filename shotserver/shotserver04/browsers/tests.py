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
Test suite for browsers app.
"""

__revision__ = "$Rev: 2956 $"
__date__ = "$Date: 2008-08-13 19:04:39 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from psycopg import IntegrityError, ProgrammingError
from unittest import TestCase
from django.db import transaction
from django.contrib.auth.models import User
from shotserver04.platforms.models import Platform, OperatingSystem
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Engine, BrowserGroup, Browser


class SizeTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.operatingsystem = OperatingSystem.objects.get(pk=1)
        self.factory = Factory.objects.create(
            name='factory',
            admin=self.user,
            hardware='MacBook, Intel Core Duo, 2 GB RAM',
            operating_system=self.operatingsystem)
        self.engine = Engine.objects.get(pk=1)
        self.browser_group = BrowserGroup.objects.get(pk=1)

    def tearDown(self):
        self.factory.delete()
        self.user.delete()

    def createBrowser(self, user_agent, **kwargs):
        return Browser.objects.create(
            factory=self.factory,
            user_agent=user_agent,
            browser_group=self.browser_group,
            version=kwargs.get('version', ''),
            major=kwargs.get('major', 0),
            minor=kwargs.get('minor', 0),
            engine=self.engine,
            engine_version=kwargs.get('engine_version', ''),
            javascript_id=kwargs.get('javascript', 1),
            java_id=kwargs.get('java', 1),
            flash_id=kwargs.get('flash', 1),
            command=kwargs.get('command', ''),
            active=kwargs.get('active', True),
            )

    def assertBrowserValid(self, user_agent, **kwargs):
        try:
            self.createBrowser(user_agent, **kwargs).delete()
        except (IntegrityError, ProgrammingError):
            transaction.rollback()
            self.fail('\n'.join((
                u"could not create browser with valid settings:",
                u'"%s"' % user_agent, repr(kwargs))))

    def assertBrowserInvalid(self, user_agent, **kwargs):
        try:
            try:
                self.createBrowser(user_agent, **kwargs).delete()
                self.fail('\n'.join((
                    u"created browser with invalid settings:",
                    u'"%s"' % user_agent, repr(kwargs))))
            except IntegrityError:
                pass
        finally:
            transaction.rollback()

    def testFirefox15(self):
        self.assertBrowserValid('Firefox/1.5.0.8',
                                version='1.5.0.8', major=1, minor=5)

    def testFirefox20(self):
        self.assertBrowserValid('Firefox/2.0.0.1',
                                version='2.0.0.1', major=2, minor=0)

    def testGecko(self):
        self.assertBrowserValid('Gecko/20061226 Firefox/2.0.0.1',
                                version='2.0.0.1', major=2, minor=0,
                                engine_version='20061226')
