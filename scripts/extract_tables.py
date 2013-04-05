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
Extract SQL data from stdin and write each table to an SQL file.
"""

__revision__ = "$Rev: 2859 $"
__date__ = "$Date: 2008-05-21 22:26:31 -0300 (qua, 21 mai 2008) $"
__author__ = "$Author: johann $"

import sys


def copy_table(line, table, tables):
    if len(tables) == 1:
        outfile = sys.stdout
    else:
        outfile = open(table + '.sql', 'w')
    header = line
    outfile.write(line)
    while line.strip() != r'\.':
        line = sys.stdin.readline()
        outfile.write(line)
    if ' (id,' in header:
        outfile.write("""
SELECT '%s' AS table_name,
setval('%s_id_seq', (
    SELECT max(id) FROM %s
)) as pkey_max;
""" % (table, table, table))
    if outfile is not sys.stdout:
        outfile.close()

if __name__ == '__main__':
    tables = sys.argv[1:]
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        if line.startswith('COPY '):
            table = line.split()[1]
            if len(tables) == 0 or table in tables:
                copy_table(line, table, tables)
