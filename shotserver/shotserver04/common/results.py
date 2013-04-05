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
Utilities for the results of HTTP POST requests.
"""

__revision__ = "$Rev: 2960 $"
__date__ = "$Date: 2008-08-14 05:07:00 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.utils.text import capfirst


def redirect(url, result=None, id=None, fragment=None):
    if hasattr(url, 'get_absolute_url'):
        url = url.get_absolute_url()
    if result is not None:
        url += '?result=' + result
        if hasattr(id, 'id'):
            url += '_%d' % id.id
        elif id is not None:
            url += '_' + unicode(id)
    if fragment is not None:
        url += '#' + fragment
    return HttpResponseRedirect(url)


def filter(items, func):
    if isinstance(func, int):
        id = func
        func = lambda item: item.id == id
    elif isinstance(func, basestring):
        text = func
        func = lambda item: unicode(item) == text
    for item in items:
        if func(item):
            return item


def message(result, id=None):
    parts = result.split('_')
    action = parts.pop(0)
    if id is None:
        id = parts.pop(-1)
    else:
        parts.pop(-1)
        id = unicode(id)
    item = _(' '.join(parts))
    if action == 'added':
        return _("Added %(item)s %(id)s.") % locals()
    elif action == 'removed':
        return _("Removed %(item)s %(id)s.") % locals()
    elif action == 'updated':
        return _("Updated %(item)s %(id)s.") % locals()
    return "%s %s %s." % (capfirst(action), item, id)
