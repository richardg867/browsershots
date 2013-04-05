#! /usr/bin/python
# release.py - Make ZIP files for software releases
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Make ZIP files for software releases.
"""

__revision__ = "$Rev: 1328 $"
__date__ = "$Date: 2007-05-28 13:44:25 -0300 (seg, 28 mai 2007) $"
__author__ = "$Author: johann $"

import sys
import os


def error(message, code = 1):
    """Print error message and exit."""
    print message.strip()
    sys.exit(code)


def shell(command):
    """Run a shell command and exit on error."""
    print command
    code = os.system(command)
    if code:
        error('failed with exit code %d' % code, code / 256)


def pack(package, package_version):
    """Copy and cleanup."""
    shell('rm -rf %s' % package_version)
    shell('cp -r %s %s' % (package, package_version))
    shell('find %s -name .svn | xargs rm -rf' % package_version)
    shell('find %s -name "*.rej" | xargs rm -f' % package_version)
    shell('find %s -name "shotfactory.log" | xargs rm -f' % package_version)
    shell('find %s -name "screenlog.0" | xargs rm -f' % package_version)
    shell('find %s -name "\#*\#" | xargs rm -f' % package_version)


def _main():
    """Get command line arguments and make ZIP files."""
    version = sys.argv[1]
    for package in sys.argv[2:]:
        package = package.strip('/')
        if package.count('/'):
            error('package "%s" contains a slash' % package)
        package_version = package + '-' + version
        pack(package, package_version)
        zip_filename = package_version + '.zip'
        shell('rm -f %s' % zip_filename)
        shell('zip -qr %s %s' % (zip_filename, package_version))

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        _main()
    else:
        error("""\
usage: release.py <version> <packages>
example: release.py 0.3-alpha1 shotserver shotfactory
""")
