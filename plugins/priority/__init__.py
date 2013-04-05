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
Priority processing for selected users or domains.
"""

__revision__ = "$Rev: 2376 $"
__date__ = "$Date: 2007-11-28 06:33:44 -0300 (qua, 28 nov 2007) $"
__author__ = "$Author: johann $"

from datetime import datetime
from shotserver04.factories.models import Factory
from shotserver04.priority.models import UserPriority, DomainPriority


def user_uploads_per_day(user):
    """
    Get the total number of screenshot uploads in the last 24 hours
    for this screenshot factory admin.
    """
    if user.is_anonymous():
        return 0
    return sum([f.uploads_per_day
                for f in Factory.objects.filter(admin=user)
                if f.uploads_per_day])


def user_priority(user):
    """
    Get the best active priority for this user.
    """
    if user.is_anonymous():
        return 0
    priorities = [p.priority for p in UserPriority.objects.filter(
        user=user, expire__gte=datetime.now())]
    priorities.append(user_uploads_per_day(user) / 1000)
    return max(priorities)


def domain_priority(domain):
    """
    Get the best active priority for this domain name.
    """
    priorities = [p.priority for p in DomainPriority.objects.filter(
        domain=domain, expire__gte=datetime.now())]
    priorities.append(0) # In case it's empty
    return max(priorities)
