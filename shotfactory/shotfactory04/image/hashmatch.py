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
Efficient overlap matching for tall screenshots.
"""

__revision__ = "$Rev: 2010 $"
__date__ = "$Date: 2007-08-19 22:55:43 -0300 (dom, 19 ago 2007) $"
__author__ = "$Author: johann $"

import re

STEP = 3*64
header_match = re.compile(r'(P\d) (\d+) (\d+) (\d+)').match


def read_ppm_header(infile):
    """
    Read a PPM file header and return magic, width, height, maxval.
    """
    header = []
    while True:
        line = infile.readline()
        sharp = line.find('#')
        if sharp > -1:
            line = line[:sharp]
        line = line.strip()
        if not line:
            continue
        header.append(line)
        match = header_match(' '.join(header))
        if match:
            magic = match.group(1)
            width = int(match.group(2))
            height = int(match.group(3))
            maxval = int(match.group(4))
            return magic, width, height, maxval
        elif len(header) >= 4:
            raise SyntaxError("could not parse PPM header")


def debug_values(hashtable, minimum = 1):
    """
    Print a hash table sorted by value.
    >>> debug_values({'a': 1, 'b': 3, 'c': 2}, 2)
    2 c
    3 b
    """
    keys = hashtable.keys()
    values = hashtable.values()
    pairs = zip(values, keys)
    pairs.sort()
    for value, key in pairs:
        if value >= minimum:
            print value, key


def build_hash(pixels, start, height, row_skip):
    """
    Build a dict from a vertical column of detail markers.
    Non-unique markers will be removed.
    """
    positions = {}
    frequencies = {}
    frequencies_get = frequencies.get
    previous = pixels[start:start+STEP]
    for y in range(1, height):
        start += row_skip
        this = pixels[start:start+STEP]
        marker = previous + this
        previous = this
        frequencies[marker] = frequencies_get(marker, 0) + 1
        positions[marker] = y
    positions_pop = positions.pop
    for marker, counter in frequencies.iteritems():
        if counter > 1:
            positions_pop(marker)
    return positions


def match_markers(pixels, start, height, row_skip, positions, votes):
    """
    Match markers and collect votes for different offset positions.
    """
    positions_get = positions.get
    votes_get = votes.get
    previous = pixels[start:start+STEP]
    for y in range(1, height):
        start += row_skip
        this = pixels[start:start+STEP]
        marker = previous + this
        previous = this
        position = positions_get(marker, -1)
        if position > -1:
            offset = position - y
            votes[offset] = votes_get(offset, 0) + 1


def winner(votes, minimum):
    """
    Get the offset with the most votes, but 0 only if no other option exists.
    All entries with less than minimum votes will be ignored.
    >>> winner({0:0, 1:1, 2:2, 3:3}, 1)
    3
    >>> winner({0:100, 1:1, 2:2, 3:3}, 1)
    3
    >>> winner({0:100, 1:1, 2:2, 3:3}, 0)
    3
    >>> winner({0:100, 1:1, 2:2, 3:3}, 4)
    0
    >>> winner({}, 1)
    0
    """
    maximum = minimum - 1
    result = 0
    for offset, count in votes.items():
        if count > maximum and offset > 0:
            maximum = count
            result = offset
    return result


def find_offset(filename1, filename2):
    """
    Find the best vertical match between two PPM files.
    Return the offset in pixels.
    """
    infile1 = open(filename1, 'rb')
    infile2 = open(filename2, 'rb')
    header1 = read_ppm_header(infile1)
    header2 = read_ppm_header(infile2)
    assert header1[0] == header2[0] == 'P6'
    assert header1[3] == header2[3] == 255
    assert header1[1] == header2[1]
    width = header1[1]
    height1 = header1[2]
    height2 = header2[2]

    pixels1 = infile1.read()
    pixels2 = infile2.read()
    # print width*height1*3, len(pixels1), width*height2*3, len(pixels2)

    row_skip = 3*width
    votes = {}
    for start in range(0, row_skip, STEP):
        positions = build_hash(pixels1, start, height1, row_skip)
        match_markers(pixels2, start, height2, row_skip, positions, votes)
    # debug_values(votes, minimum = 1)
    return winner(votes, 3*width/STEP)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
