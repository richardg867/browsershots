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
Update news items from RSS feed.

You can run this manually or with a cronjob, e.g. by adding the following
line in /etc/crontab (replace www-data with the database owner):

23 *   * * *   www-data   shotserver04_update_news.py
"""

__revision__ = "$Rev: 2380 $"
__date__ = "$Date: 2007-11-28 06:45:57 -0300 (qua, 28 nov 2007) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
import sys
import re
import time
from datetime import datetime
import urllib2
from shotserver04.start.models import NewsItem

find_items = re.compile(
    r'<item>\s*' +
    r'<title>(.+?)</title>\s*' +
    r'<pubDate>(.+?)</pubDate>\s*' +
    r'<link>(http.+?)</link>',
    re.IGNORECASE).findall

updated = []
rss = urllib2.urlopen('http://trac.browsershots.org/blog?format=rss').read()
for title, date_string, url in find_items(rss):
    date_tuple = time.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    pubdate = datetime(*date_tuple[:6])
    print date_string
    print pubdate
    print title
    print url
    print
    item, created = NewsItem.objects.get_or_create(
        url=url, defaults={'pubdate': pubdate, 'title': title})
    if item.pubdate != pubdate or item.title != title:
        item.pubdate = pubdate
        item.title = title
        item.save()
    updated.append(item.id)
NewsItem.objects.exclude(id__in=updated).delete()
