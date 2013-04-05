#!/usr/bin/env python
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
Test the @serializable decorator by overloading the server with
factory poll requests.
"""

__revision__ = "$Rev: 2005 $"
__date__ = "$Date: 2007-08-19 21:22:02 -0300 (dom, 19 ago 2007) $"
__author__ = "$Author: johann $"

import thread
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
from django.db import transaction
from xmlrpclib import Fault
from shotserver04.factories.models import Factory
from shotserver04.websites.models import Website
from shotserver04.browsers.models import BrowserGroup
from shotserver04.requests.models import RequestGroup, Request
from shotserver04.requests import xmlrpc as requests
from datetime import datetime, timedelta
import time


def generator():
    factory = Factory.objects.get(pk=1)
    browser_group = BrowserGroup.objects.get(pk=1)
    website = Website.objects.all()[0]
    request_group = RequestGroup.objects.create(
        website=website,
        expire=datetime.now() + timedelta(1, 0, 0))
    while True:
        request = Request.objects.create(
            request_group=request_group,
            browser_group=browser_group,
            major=2, minor=0,
            )
        sys.stdout.write('+')
        sys.stdout.flush()
        time.sleep(1)


def overload(thread_id):
    try:
        transaction.enter_transaction_management()
        transaction.managed()
        factory = Factory.objects.get(pk=1)
        features = factory.features_q()
        transaction.rollback()
        while True:
            try:
                request = requests.find_and_lock_request(factory, features)
            except Fault, error:
                if error.faultString != "No matching request.":
                    print
                    print message
            sys.stdout.write(str(thread_id))
            sys.stdout.flush()
    finally:
        transaction.leave_transaction_management()


if __name__ == '__main__':
    thread.start_new_thread(generator, ())
    thread.start_new_thread(overload, (1, ))
    thread.start_new_thread(overload, (2, ))
    thread.start_new_thread(overload, (3, ))
    thread.start_new_thread(overload, (4, ))
    thread.start_new_thread(overload, (5, ))
    thread.start_new_thread(overload, (6, ))
    thread.start_new_thread(overload, (7, ))
    sys.stdin.readline()
