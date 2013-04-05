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
Load SQL for database tables.
"""

__revision__ = "$Rev: 2959 $"
__date__ = "$Date: 2008-08-14 05:05:48 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import os
import sys
import commands

PSQL = '/usr/bin/psql'

TABLES = """
auth user
django session site
revenue userdonation userpayment userrevenue
start newsitem
sponsors sponsor
factories factory screensize colordepth screenshotcount
browsers browser
invoices billingaddress
paypal paypallog
websites domain website
priority domainpriority
priority userpriority
screenshots screenshot problemreport
requests requestgroup request
messages factoryerror
""".splitlines()


for line in TABLES:
    models = line.split()
    if not models:
        continue
    app = models.pop(0)
    for model in models:
        table = '%s_%s' % (app, model)
        filename = table + '.modified.sql'
        if not os.path.exists(filename):
            filename = table + '.sql'
        command = PSQL + ' shotserver04'
        command += ' < ' + filename
        print command
        status, output = commands.getstatusoutput(command)
        for out in output.splitlines():
            if ' | ' in out or '-+-' in out:
                continue
            if out.strip() in ('(1 row)', 'DELETE 1'):
                continue
            print output
            sys.exit(1)
        if status:
            print 'error code', status
            sys.exit(status)
