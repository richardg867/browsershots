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
Convert times to a short human-readable format.
"""

__revision__ = "$Rev: 2736 $"
__date__ = "$Date: 2008-03-05 14:40:02 -0300 (qua, 05 mar 2008) $"
__author__ = "$Author: johann $"

import cgi
from datetime import datetime
from django import template
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def human_seconds(seconds):
    """
    >>> human_seconds(0)
    '0 s'
    >>> human_seconds(1)
    '1 s'
    >>> human_seconds(5*60)
    '5 min'
    >>> human_seconds(5*3600)
    '5 h'
    >>> human_seconds(5*24*3600)
    '5 d'
    """
    if seconds is None:
        return ''
    if seconds < 180:
        return _("%(seconds)d s") % locals()
    minutes = seconds / 60
    if minutes < 180:
        return _("%(minutes)d min") % locals()
    hours = minutes / 60
    if hours < 72:
        return _("%(hours)d h") % locals()
    days = hours / 24
    return _("%(days)d d") % locals()


@register.filter
def human_timesince(then):
    """
    Short human-readable formatting of interval since given datetime.
    """
    if then is None:
        return ''
    delta = datetime.now() - then
    return human_seconds(delta.days * 24 * 3600 + delta.seconds)


@register.filter
def human_timeuntil(then):
    """
    Short human-readable formatting of interval until given datetime.
    """
    if then is None:
        return ''
    delta = then - datetime.now()
    return human_seconds(delta.days * 24 * 3600 + delta.seconds)


@register.filter
def human_bytes(bytes):
    """
    >>> human_bytes(0)
    '0 bytes'
    >>> human_bytes(100)
    '100 bytes'
    >>> human_bytes(9999)
    '9999 bytes'
    >>> human_bytes(10000)
    '10 000 bytes'
    >>> human_bytes(10000000)
    '10 000 000 bytes'
    >>> human_bytes(123456789)
    '123 456 789 bytes'
    """
    bytes = str(bytes)
    if len(bytes) > 4:
        for index in range(len(bytes) - 3, 0, -3):
            bytes = bytes[:index] + ' ' + bytes[index:]
    return _("%(bytes)s bytes") % locals()


@register.filter
def human_link(instance, max_length=None):
    """
    HTML link to the detail page.
    """
    text = unicode(instance)
    if max_length and len(text) > max_length:
        text = text[:max_length-1] + '...'
    return mark_safe(u'<a href="%s">%s</a>' % (
        cgi.escape(instance.get_absolute_url(), quote=True), text))


@register.filter
def human_br(text):
    """
    Add <br /> tags for narrow table headers.

    >>> human_br('test')
    'test'
    >>> human_br('last upload')
    'last<br />upload'
    >>> human_br('browser-group')
    'browser-<br />group'
    >>> human_br('a b c d')
    'a b<br />c d'
    """
    if not isinstance(text, basestring):
        text = unicode(text)
    middle = len(text) / 2
    candidates = []
    for index, char in enumerate(text):
        if char in ' -':
            candidates.append((abs(middle - index), index, char))
    candidates.sort()
    if not candidates:
        return mark_safe(text)
    middle, index, char = candidates[0]
    if char == '-':
        return mark_safe(text[:index+1] + '<br />' + text[index+1:])
    else:
        return mark_safe(text[:index] + '<br />' + text[index+1:])


@register.filter
def human_datetime(timestamp):
    """
    Short human-readable formatting of timestamp.
    """
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


@register.filter
def human_date(timestamp):
    """
    Short human-readable formatting of date.
    """
    return timestamp.strftime('%Y-%m-%d')


if __name__ == '__main__':
    import doctest
    _ = lambda x: x
    doctest.testmod()
