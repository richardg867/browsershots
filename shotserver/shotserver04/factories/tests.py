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
Test suite for factories app.
"""

__revision__ = "$Rev: 2894 $"
__date__ = "$Date: 2008-06-14 18:27:37 -0300 (sab, 14 jun 2008) $"
__author__ = "$Author: johann $"

from psycopg import IntegrityError, DatabaseError
from unittest import TestCase
from django.db import transaction
from django.contrib.auth.models import User
from shotserver04.platforms.models import Platform, OperatingSystem
from shotserver04.factories.models import Factory, ScreenSize, ColorDepth


class FactoriesTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create()
        self.operating_system = OperatingSystem.objects.get(pk=1)
        self.factory = Factory.objects.create(
            name='factory',
            admin=self.user,
            hardware='MacBook, Intel Core Duo, 2 GB RAM',
            operating_system=self.operating_system)
        self.size_640 = ScreenSize.objects.create(
            factory=self.factory, width=640, height=480)
        self.size_800 = ScreenSize.objects.create(
            factory=self.factory, width=800, height=600)
        self.size_1024 = ScreenSize.objects.create(
            factory=self.factory, width=1024, height=768)
        self.depth_16 = ColorDepth.objects.create(
            factory=self.factory, bits_per_pixel=16)
        self.depth_24 = ColorDepth.objects.create(
            factory=self.factory, bits_per_pixel=24)

    def tearDown(self):
        self.depth_16.delete()
        self.depth_24.delete()
        self.size_640.delete()
        self.size_800.delete()
        self.size_1024.delete()
        self.factory.delete()
        self.user.delete()

    def testFactoryName(self):
        self.factory.name = 'factory'
        self.factory.save()
        self.assertEqual(len(Factory.objects.filter(name='factory')), 1)

    def testFactoryNameEmpty(self):
        try:
            self.factory.name = ''
            self.assertRaises(IntegrityError, self.factory.save)
        finally:
            transaction.rollback()

    def testFactoryNameInvalid(self):
        try:
            self.factory.name = '-'
            self.assertRaises(IntegrityError, self.factory.save)
        finally:
            transaction.rollback()

    def testFactoryCreateDuplicate(self):
        try:
            self.assertRaises(IntegrityError, Factory.objects.create,
                              name='factory', admin=self.user,
                              operating_system=self.operating_system)
        finally:
            transaction.rollback()

    def testFactoryCreateEmpty(self):
        try:
            self.assertRaises(IntegrityError, Factory.objects.create,
                              admin=self.user,
                              operating_system=self.operating_system)
        finally:
            transaction.rollback()

    def testFactoryCreateInvalid(self):
        try:
            self.assertRaises(IntegrityError, Factory.objects.create,
                              name='-', admin=self.user,
                              operating_system=self.operating_system)
        finally:
            transaction.rollback()

    def testScreenSize(self):
        queryset = self.factory.screensize_set
        self.assertEqual(len(queryset.all()), 3)
        self.assertEqual(len(queryset.filter(width=800)), 1)
        self.assertEqual(len(queryset.filter(width__exact=800)), 1)
        self.assertEqual(len(queryset.filter(width__gte=800)), 2)
        self.assertEqual(len(queryset.filter(width__lte=800)), 2)
        self.assertEqual(len(queryset.filter(width__gt=800)), 1)
        self.assertEqual(len(queryset.filter(width__lt=800)), 1)

    def testScreenSizeDuplicate(self):
        try:
            self.assertRaises(IntegrityError, ScreenSize.objects.create,
                              factory=self.factory, width=800, height=600)
        finally:
            transaction.rollback()

    def testColorDepth(self):
        queryset = self.factory.colordepth_set
        self.assertEqual(len(queryset.all()), 2)

    def testColorDepthDuplicate(self):
        try:
            self.assertRaises(IntegrityError, ColorDepth.objects.create,
                              factory=self.factory, bits_per_pixel=24)
        finally:
            transaction.rollback()


class ForeignKeyTestCase(TestCase):

    def testInvalidOperatingSystem(self):
        try:
            self.assertRaises(DatabaseError, Factory.objects.create,
                              operating_system_id=-1)
        finally:
            transaction.rollback()

    def testInvalidAdmin(self):
        try:
            self.assertRaises(DatabaseError, Factory.objects.create,
                              admin_id=-1)
        finally:
            transaction.rollback()

    def testInvalidFactoryForScreenSize(self):
        try:
            self.assertRaises(DatabaseError, ScreenSize.objects.create,
                              factory_id=-1, width=800, height=600)
        finally:
            transaction.rollback()

    def testInvalidFactoryForColorDepth(self):
        try:
            self.assertRaises(DatabaseError, ColorDepth.objects.create,
                              factory_id=-1, bits_per_pixel=24)
        finally:
            transaction.rollback()
