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
Email screenshot problem reports to factory administrators.

It's a good idea to run this daily, e.g. by adding a symlink to this
file in /etc/cron.daily.
"""

__revision__ = "$Rev: 2716 $"
__date__ = "$Date: 2008-02-24 09:51:27 -0300 (dom, 24 fev 2008) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from shotserver04.factories.models import Factory, ScreenSize, ColorDepth
from shotserver04.browsers.models import Browser
from shotserver04.screenshots.models import Screenshot, ProblemReport
from shotserver04.common.templatetags import human
import sys

DEBUG = '--debug' in sys.argv
FACTORIES = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

DAYS = 1
PREFIX = 'http://' + Site.objects.all()[0].domain
MAX_EXAMPLES = 5
MAX_ORPHANS = 2


def all_reports(problems):
    for problem in problems:
        yield ''
        yield u'%s (Code %d)' % (problem.get_message(), problem.code)
        yield PREFIX + problem.screenshot.get_absolute_url()


def example_urls(problems):
    urls = set([problem.screenshot.get_absolute_url() for problem in problems])
    yield ''
    yield u'%s (Code %d)' % (problems[0].get_message(), problems[0].code)
    orphans = len(problems) - MAX_EXAMPLES
    if orphans > MAX_ORPHANS:
        orphans = 0
    for problem in problems[:MAX_EXAMPLES + orphans]:
        yield PREFIX + problem.screenshot.get_absolute_url()
    if len(problems) > MAX_EXAMPLES + orphans:
        yield "... (%d more)" % (len(problems) - MAX_EXAMPLES - orphans)


if FACTORIES:
    factories = Factory.objects.filter(name__in=FACTORIES)
else:
    factories = Factory.objects.all()
for factory in factories:
    problems = ProblemReport.objects.filter(
        screenshot__factory=factory,
        reported__gte=datetime.now() - timedelta(days=DAYS))
    if not len(problems):
        continue
    codes = {}
    for problem in problems:
        if not problem.code in codes:
            codes[problem.code] = []
        codes[problem.code].append(problem)
    body = [
        u"Hi %s," % factory.admin.first_name, '',
        u"This is an automated user feedback report from Browsershots 0.4.",
        ]
    if DAYS > 1:
        interval = '%d days' % DAYS
    else:
        interval = '%d hours' % (DAYS * 24)
    if len(problems) == 1:
        body.append(u"In the last %s, there was one %s for" % (
            interval, ProblemReport._meta.verbose_name))
    else:
        body.append(u"In the last %s, there were %d %s for" % (
            interval, len(problems), ProblemReport._meta.verbose_name_plural))
    body.append(PREFIX + factory.get_absolute_url())
    keys = codes.keys()
    keys.sort()
    for code in keys:
        if code == 999:
            body.extend(all_reports(codes[code]))
        else:
            body.extend(example_urls(codes[code]))
    body.extend(['', "Thanks for your time,", "Browsershots"])

    subject = "[browsershots] %d problem reports for %s" % (
        len(problems), factory.name)
    body = '\n'.join(body)
    from_email = u'"%s" <%s>' % settings.ADMINS[0]
    recipient_list=[u'"%s %s" <%s>' % (
        factory.admin.first_name, factory.admin.last_name,
        factory.admin.email)]
    if DEBUG:
        print '=' * len(subject)
        print 'From:', from_email.encode('utf-8')
        print 'To:', u', '.join(recipient_list).encode('utf-8')
        print subject
        print '=' * len(subject)
        print body
    else:
        EmailMessage(subject, body, from_email, recipient_list,
                     bcc=[from_email]).send()
