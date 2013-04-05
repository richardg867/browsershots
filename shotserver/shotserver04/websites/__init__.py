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
Websites.
"""

__revision__ = "$Rev: 2723 $"
__date__ = "$Date: 2008-02-25 17:08:25 -0300 (seg, 25 fev 2008) $"
__author__ = "$Author: johann $"

import urllib


def normalize_url(url):
    """
    Normalize URL for storage in the database (and retrieval).

    >>> normalize_url('http://www.example.com/')
    u'http://www.example.com/'
    >>> normalize_url(u'http://www.example.com/\xfc')
    u'http://www.example.com/\\xfc'
    >>> normalize_url('http://www.example.com/%C3')
    u'http://www.example.com/\\xc3'
    >>> normalize_url('http://www.example.com/%C3%BC')
    u'http://www.example.com/\\xfc'
    >>> normalize_url('http://www.example.com/space here')
    u'http://www.example.com/space%20here'
    >>> normalize_url('http://www.example.com/%20')
    u'http://www.example.com/%20'
    >>> normalize_url('\t http://www.example.com/ ')
    u'http://www.example.com/'
    >>> normalize_url(r'\\\\server\\test\\index.htm')
    u'//server/test/index.htm'
    >>> normalize_url(r'//server/?q=\\backslash')
    u'//server/?q=\\\\backslash'
    """
    url = url.strip()
    if isinstance(url, unicode):
        url = url.encode('utf-8')
    result = urllib.unquote(url)
    result = result.replace(' ', '%20')
    if result.startswith('\\\\'):
        result = result.replace('\\', '/')
    try:
        return result.decode('utf-8')
    except UnicodeDecodeError:
        return result.decode('latin-1')


def extract_domain(url, remove_www=False):
    """
    Extract domain name from URL, without user, password, or port.

    >>> extract_domain('http://www.example.com')
    'www.example.com'
    >>> extract_domain('http://www.example.com/')
    'www.example.com'
    >>> extract_domain('http://www.example.com/index.html')
    'www.example.com'
    >>> extract_domain('http://www.example.com:8000')
    'www.example.com'
    >>> extract_domain('http://user:password@www.example.com:8000')
    'www.example.com'
    >>> extract_domain('http://www.example.com', remove_www=True)
    'example.com'
    >>> extract_domain('http://www.www.example.com', remove_www=True)
    'example.com'
    >>> extract_domain('www.example.com')
    'www.example.com'
    """
    # Remove http:// and /index.html
    if url.count('/') >= 2:
        domain = url.split('/')[2]
    else:
        domain = url.strip('/')
    # Remove user:password@
    if domain.count('@'):
        domain = domain.split('@')[1]
    # Remove port (e.g. :8000)
    if domain.count(':'):
        domain = domain.split(':')[0]
    # Remove www. if requested
    while domain.startswith('www.') and remove_www:
        domain = domain[4:]
    return domain


if __name__ == '__main__':
    import doctest
    doctest.testmod()
