#!/usr/bin/env python
# header.py - Copy header comments between Python source files
# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
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
Adjust comment header in a batch of source files.
"""

__revision__ = '$Rev: 1464 $'
__date__ = '$Date: 2007-06-08 17:12:43 -0300 (sex, 08 jun 2007) $'
__author__ = '$Author: johann $'

CRLF = """
"""

import sys
import os


def remove_shebang(lines):
    """Remove shebang and coding from lines and return removed lines."""
    result = []
    if lines and lines[0].startswith('#!'):
        result.append(lines.pop(0))
    if lines and lines[0].count(' coding: '):
        result.append(lines.pop(0))
    return result


def remove_comment(lines):
    """Remove block comment from lines and return removed lines."""
    result = []
    while lines and lines[0].startswith('#'):
        result.append(lines.pop(0))
    return result


def remove_docstring(lines):
    """Remove docstring from lines and return removed lines."""
    if not lines or not lines[0].startswith('"""'):
        return ['"""' + CRLF, '"""' + CRLF]
    first_line = lines.pop(0)
    result = [first_line]
    if first_line.count('"') < 6:
        while lines and lines[0].strip() != '"""':
            result.append(lines.pop(0))
        result.append(lines.pop(0))
    return result


def extract_value(line):
    """Extract string from subversion keyword line."""
    for char in ('"', "'"):
        if line.count(char):
            return char.join(line.split(char)[1:-1])


def remove_keywords(lines):
    """Remove subversion keywords and return old values or defaults."""
    result = [None] * 3
    while lines:
        line = lines[0].strip()
        if line.startswith('__revision__'):
            result[0] = extract_value(lines.pop(0))
        elif line.startswith('__date__'):
            result[1] = extract_value(lines.pop(0))
        elif line.startswith('__author__'):
            result[2] = extract_value(lines.pop(0))
        else:
            break
    if result[0] is None:
        result[0] = '$Rev: 1464 $'
    if result[1] is None:
        result[1] = '$Date: 2007-06-08 17:12:43 -0300 (sex, 08 jun 2007) $'
    if result[2] is None:
        result[2] = '$Author: johann $'
    return result


def remove_blank_lines(lines):
    """Remove blank lines from the beginning."""
    while lines and lines[0].strip() == '':
        lines.pop(0)


def adjust_lines(lines, header):
    """Replace the header comment and add subversion keywords."""
    old_lines = lines[:]
    shebang = remove_shebang(lines)
    remove_comment(lines)
    remove_blank_lines(lines)
    old_docstring = remove_docstring(lines)
    remove_blank_lines(lines)
    old_revision, old_date, old_author = remove_keywords(lines)
    if lines and (lines[0].startswith('def ') or
                  lines[0].startswith('class ') or
                  lines[0].startswith('@')):
        lines[0:0] = [CRLF, CRLF]
    elif lines and lines[0].strip():
        lines[0:0] = [CRLF]
    lines[0:0] = shebang + header + [CRLF] + old_docstring + [
        CRLF,
        '__revision__ = "%s"%s' % (old_revision, CRLF),
        '__date__ = "%s"%s' % (old_date, CRLF),
        '__author__ = "%s"%s' % (old_author, CRLF),
        ]
    return lines != old_lines


def adjust_file(filename, header):
    """Adjust header comment in file and print filename if changed."""
    lines = file(filename).readlines()
    if adjust_lines(lines, header):
        print filename
        file(filename, 'w').write(''.join(lines))


def adjust_files(filenames, header):
    """Adjust header comment in many files."""
    filenames.sort()
    for filename in filenames:
        adjust_file(filename, header)


def _main():
    """Main function."""
    reference = file(sys.argv[1]).readlines()
    remove_shebang(reference)
    header = remove_comment(reference)
    adjust_files(sys.argv[2:], header)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Copy header comment from one file to many others."
        print "usage: %s <from-file> <to-file-1> <to-file-2> ..." % (
            os.path.basename(sys.argv[0]))
    else:
        _main()
