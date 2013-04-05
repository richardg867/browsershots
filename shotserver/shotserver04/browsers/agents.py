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
Extract browser information from the User-Agent header.
"""

__revision__ = "$Rev: 3045 $"
__date__ = "$Date: 2008-09-02 18:07:43 -0300 (ter, 02 set 2008) $"
__author__ = "$Author: johann $"

import os
import re


def get_engines():
    """
    Get all rendering engines from the database.

    Some engines are always returned last, because there are browsers
    that include those names in their User-Agent string, in addition
    to their real engine name.
    """
    from shotserver04.browsers.models import Engine
    khtml = gecko = msie = None
    engines = list(Engine.objects.all())
    engines.sort(key=lambda e: -len(e.name)) # Longer names first.
    for engine in engines:
        if engine.name == 'Gecko':
            gecko = engine
        elif engine.name == 'KHTML':
            khtml = engine
        elif engine.name == 'MSIE':
            msie = engine
        else:
            yield engine
    if msie:
        yield msie
    if khtml:
        yield khtml
    if gecko:
        yield gecko


def get_browser_groups():
    """
    Get all browser groups from the database.

    Some browsers are always returned last, because other browsers
    include those names in their User-Agent string.
    """
    from shotserver04.browsers.models import BrowserGroup
    firefox = mozilla = msie = None
    browser_groups = list(BrowserGroup.objects.all())
    browser_groups.sort(key=lambda b: -len(b.name)) # Longer names first.
    for browser_group in browser_groups:
        if browser_group.name == 'Firefox':
            firefox = browser_group
        elif browser_group.name == 'Mozilla':
            mozilla = browser_group
        elif browser_group.name == 'MSIE':
            msie = browser_group
        else:
            yield browser_group
    if msie:
        yield msie
    if firefox:
        yield firefox
    if mozilla:
        yield mozilla


def extract_version(user_agent, name):
    """
    Extract version string that comes after the name.

    >>> extract_version('Mozilla/5.0', 'Mozilla')
    '5.0'
    >>> extract_version('Mozilla/5.0 (rv:1.7.8)', 'Mozilla')
    '1.7.8'
    >>> extract_version('Mozilla/5.0 Gecko/20061201 Firefox/2.0.0.4', 'Gecko')
    '20061201'
    >>> extract_version('Safari/417.8', 'Safari')
    '2.0.3'
    >>> extract_version('Version/3.0.2 Safari/522.13.1', 'Safari')
    '3.0.2'
    >>> extract_version('MSIE 6.0', 'MSIE')
    '6.0'
    """
    if name == 'Safari' and 'Version' in user_agent:
        name = 'Version'
    if name == 'Mozilla' and 'rv:' in user_agent:
        name = 'rv'
    index = user_agent.lower().index(name.lower())
    index += len(name)
    if user_agent[index] not in '/ :':
        return ''
    index += 1
    start = index
    while index < len(user_agent) and user_agent[index] in '.0123456789':
        index += 1
    version = user_agent[start:index]
    if name == 'Safari':
        return safari_version(version)
    return version


def extract_major(version, name=None):
    """
    Extract major version number from version string.

    >>> extract_major('2.0.0.4')
    2
    >>> extract_major('2')
    2
    """
    if version.count('.'):
        return int(version.split('.')[0])
    elif version.isdigit():
        return int(version)


def extract_minor(version, name=None):
    """
    Extract minor version number from version string.

    >>> extract_minor('2.18')
    18
    >>> extract_minor('2.0.0.4')
    0
    >>> extract_minor('4.01', 'MSIE')
    0
    >>> extract_minor('9.21', 'Opera')
    21
    """
    if version.count('.'):
        minor = version.split('.')[1]
        if minor and name == 'MSIE':
            minor = minor[0]
        return int(minor)


uamatrix_findall = re.compile(r"""
<update.*?
<os_ver>10.*?
<safari_ver>(.+?)</safari_ver>.*?
<safari_bld>(.+?)</safari_bld>.*?
</update>
""", re.VERBOSE | re.DOTALL).findall


def safari_version(build):
    """
    Convert Safari build number to version number.

    >>> safari_version('419.3')
    '2.0.4'
    """
    module_dir = os.path.dirname(__file__)
    uamatrix_filename = os.path.join(module_dir, 'uamatrix.xml')
    uamatrix = open(uamatrix_filename).read()
    for matrix_version, matrix_build in uamatrix_findall(uamatrix):
        if matrix_build == build:
            return matrix_version
    return build


if __name__ == '__main__':
    import doctest
    doctest.testmod()
