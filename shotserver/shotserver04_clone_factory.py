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
Create a new screenshot factory as a copy of an existing factory.
"""

__revision__ = "$Rev: 2961 $"
__date__ = "$Date: 2008-08-14 05:24:45 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'

import sys
from shotserver04.factories.models import Factory

source = Factory.objects.get(name=sys.argv[1])
dest = Factory.objects.create(
    name=sys.argv[2],
    admin_id=source.admin_id,
    sponsor_id=source.sponsor_id,
    operating_system_id=source.operating_system_id,
    ip=source.ip,
    hardware=source.hardware,
    )
