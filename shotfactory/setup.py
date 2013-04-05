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
Installation script for use with distutils.
"""

__revision__ = "$Rev: 3047 $"
__date__ = "$Date: 2008-09-02 18:41:17 -0300 (ter, 02 set 2008) $"
__author__ = "$Author: johann $"

from distutils.core import setup
import sys

kwargs = {
    'name': 'ShotFactory',
    'version': '0.4.0',
    'description': 'Screenshot factory for browsershots.org',
    'author': 'Johann C. Rocholl',
    'author_email': 'johann@browsershots.org',
    'url': 'http://v04.browsershots.org/',
    'packages': [
        'shotfactory04',
        'shotfactory04.gui',
        'shotfactory04.gui.darwin',
        'shotfactory04.gui.linux',
        'shotfactory04.gui.windows',
        'shotfactory04.image',
        'shotfactory04.servers',
        ],
    'scripts': [
        'shotfactory.py',
        'browsershot.py',
        'ppmoffset.py',
        ],
    }

if 'py2exe' in sys.argv:
    import py2exe
    # modulefinder can't handle runtime changes to __path__,
    # but win32com uses them
    import modulefinder
    import win32com
    for path in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", path)
    __import__("win32com.shell")
    m = sys.modules["win32com.shell"]
    for path in m.__path__[1:]:
        modulefinder.AddPackagePath("win32com.shell", path)
    # py2exe configuration
    kwargs['console'] = [{
        'script': 'shotfactory.py',
        'icon_resources': [(1, 'favicon.ico')],
        }]
    kwargs['options'] = {
        'py2exe': {
            'includes': ','.join([
                'shotfactory04.gui.windows.firefox',
                'shotfactory04.gui.windows.shiretoko',
                'shotfactory04.gui.windows.chrome',
                'shotfactory04.gui.windows.flock',
                'shotfactory04.gui.windows.k_meleon',
                'shotfactory04.gui.windows.msie',
                'shotfactory04.gui.windows.minefield',
                'shotfactory04.gui.windows.navigator',
                'shotfactory04.gui.windows.opera',
                'shotfactory04.gui.windows.safari',
                'shotfactory04.gui.windows.seamonkey',
                ]),
            'dist_dir': 'bin',
            }
        }

setup(**kwargs)
