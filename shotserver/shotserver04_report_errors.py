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
Report errors from Apache log files.
"""

__revision__ = "$Rev: 2229 $"
__date__ = "$Date: 2007-10-23 06:19:42 -0300 (ter, 23 out 2007) $"
__author__ = "$Author: johann $"

import sys
import re
import socket

PREFIX = sys.argv[-1].startswith('http') and sys.argv[-1].rstrip('/') or ''
NUMERIC = '-n' in sys.argv # No DNS queries if called with -n argument.
MAX_EXAMPLES = 5 # Can be overriden with the max_examples parameter.
ORPHANS = 3 # Show more examples if only few are left.

# Regular expression for combined log format.
log_match = re.compile(r"""
(?P<ip>\d+\.\d+\.\d+\.\d+)\s
(\S+)\s
(\S+)\s
\[
(?P<day>\d+)/(?P<month>\w+)/(?P<year>\d+):
(?P<hour>\d+):(?P<min>\d+):(?P<sec>\d+)\s
(?P<timezone>[+-]\d+)
\]\s
"(?P<method>\w+)\s(?P<path>.+?)\s(?P<protocol>\S+)"\s
(?P<status>\d+)\s
(?P<size>\S+)\s
"(?P<referer>.+?)"\s
"(?P<useragent>.+?)"\s
""", re.VERBOSE).match


def plural(noun):
    """
    Pluralize an english noun.
    """
    if noun.endswith('s'):
        return noun + 'es' # statuses
    else:
        return  noun + 's'


def categorize(matches, key, preposition='from',
               max_examples=MAX_EXAMPLES, prefix=None,
               display_key=None):
    """
    Show the most common values for a selected key.
    """
    if display_key is None:
        display_key = key
    categories = {}
    for match in matches:
        value = match.group(key)
        categories[value] = categories.get(value, 0) + 1
    counts = [(count, category) for category, count in categories.iteritems()]
    counts.sort()
    counts.reverse()
    if key != 'path' and len(counts) > 1:
        print '-' * 40
    stop = min(len(counts), max_examples)
    if stop + ORPHANS >= len(counts):
        stop = len(counts)
    for index in range(stop):
        count, category = counts[index]
        if key == 'path' and prefix:
            category = PREFIX + category
        elif key == 'ip' and not NUMERIC:
            category += ' (%s)' % socket.getfqdn(category)
        if count == len(matches):
            count = 'all'
            if key == 'path' and category.count('/') == 1:
                break
        print count, preposition,
        if display_key:
            print display_key,
        print category
    if stop < len(counts):
        rest = sum([count[0] for count in counts[stop:]])
        print rest, preposition, len(counts) - stop, 'other', plural(key)


def error_details(matches):
    """
    Show details about this group of errors.
    """
    categorize(matches, 'path', preposition='for',
               max_examples=10, prefix=PREFIX, display_key='')
    categorize(matches, 'status', preposition='with')
    categorize(matches, 'method', preposition='with')
    categorize(matches, 'ip', display_key='')
    categorize(matches, 'referer')
    categorize(matches, 'useragent')


def get_first_part(path):
    """
    Get the part before the first / or ? or #.
    """
    result = path.lstrip('/')
    for separator in '/?#':
        result = result.split(separator)[0]
    return result


# Collect all errors by first part of URL path.
errors = {}
for line in sys.stdin:
    match = log_match(line)
    if match is None:
        continue # Access log line could not be parsed.
    if match.group('status')[0] in '123':
        continue # Status codes 100, 200, 300 aren't error messages.
    firstpart = get_first_part(match.group('path'))
    if firstpart not in errors:
        errors[firstpart] = []
    errors[firstpart].append(match)

# Count errors and sort by number of occurrences
counts = []
for firstpart in errors:
    counts.append((len(errors[firstpart]), firstpart))
counts.sort()
counts.reverse()

# Print errors, most common first, with supporting info
for count, firstpart in counts:
    print '=' * 60
    print count, 'errors for /%s' % firstpart
    print '=' * 60
    error_details(errors[firstpart])
    print
