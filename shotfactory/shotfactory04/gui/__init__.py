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
Base class for GUI-specific wrappers.
"""

__revision__ = "$Rev: 2499 $"
__date__ = "$Date: 2007-12-29 13:51:29 -0300 (sáb, 29 dez 2007) $"
__author__ = "$Author: hawk $"

import time
import os
import shutil
from array import array
from glob import glob
from shotfactory04.image import hashmatch, png


class Gui:
    """
    Base class for all GUI wrappers.
    """

    def __init__(self, config, options):
        """
        Save settings for internal use later.
        """
        self.request = config['request']
        self.width = config['width']
        if not self.width:
            self.width = 1024
        self.height = config['height']
        if not self.height:
            if self.width == 1280:
                self.height = 1024
            else:
                self.height = self.width / 4 * 3
        self.bpp = config['bpp']
        if not self.bpp:
            self.bpp = 24
        self.dpi = 90
        if hasattr(options, 'display'):
            self.display = options.display
        if hasattr(options, 'rfbport'):
            self.rfbport = options.rfbport
        if hasattr(options, 'verbose'):
            self.verbose = options.verbose
        self.max_pages = options.max_pages
        self.top_skip = 0
        self.bottom_skip = 0

    def delete_if_exists(self, pattern):
        """
        Print a message and delete files and folders matching pattern,
        e.g. /home/shotfactory1/.mozilla/firefox/*/sessionstore.js to
        delete Firefox sessions for all profiles.
        """
        for filename in glob(pattern):
            filename = os.path.realpath(filename)
            if not os.path.exists(filename):
                continue
            if self.verbose:
                print "Deleting", filename
            if os.path.isdir(filename):
                delete = shutil.rmtree
            else:
                delete = os.unlink
            try:
                delete(filename)
            except OSError, error:
                print error

    def page_filename(self, page_number, direction='dn'):
        """Create a PPM filename."""
        return '%s-pg%s%02d.ppm' % (self.request, direction, page_number)

    def check_screenshot(self, filename):
        """
        Check if the screenshot file looks ok.
        """
        if not os.path.exists(filename):
            raise RuntimeError("screenshot file %s not found" % filename)
        if not os.path.getsize(filename):
            raise RuntimeError("screenshot file %s is empty" % filename)
        magic, width, height, maxval = hashmatch.read_ppm_header(
            open(filename, 'rb'))
        if magic != 'P6':
            raise RuntimeError("%s isn't a PPM file with 24 bpp" % filename)
        if width != self.width or height != self.height:
            raise RuntimeError(
                "%s has %dx%d pixels, not the requested size %dx%d" %
                (filename, width, height, self.width, self.height))
        if maxval != 255:
            raise RuntimeError(
                "%s has maxval %d, but only maxval 255 is supported" %
                (maxval, filename))

    def reset_browser(self):
        """Delete cache, history, cookies, previous sessions..."""
        raise NotImplementedError(
            "%s.reset_browser() is not implemented" % self.__class__)

    def down(self):
        """Scroll down one line."""
        raise NotImplementedError(
            "%s.down() is not implemented" % self.__class__)

    def scroll_bottom(self):
        """Scroll down to the bottom of the page."""
        raise NotImplementedError(
            "%s.scroll_bottom() is not implemented" % self.__class__)

    def screenshot(self, filename):
        """Take a screenshot and save it to a PPM file."""
        raise NotImplementedError(
            "%s.screenshot(filename) is not implemented" % self.__class__)

    def scroll_pages(self, height):
        """
        Take screenshots and scroll down between them.
        """
        good_offset = height / 2 - 40 # Constant browser chrome
        filename = self.page_filename(1)
        pixels_per_line = 100
        scroll_lines = max(1, good_offset / pixels_per_line)
        offsets = []
        top_pages = self.max_pages
        if top_pages > 2:
            top_pages -= 1 # enable jump to last page
        for page in range(2, top_pages + 1):
            previous = filename
            filename = self.page_filename(page)
            attempts = 1
            if hasattr(self, 'scroll_attempts'):
                attempts = self.scroll_attempts
            for attempt in range(attempts):
                if hasattr(self, 'scroll_down'):
                    self.scroll_down(good_offset)
                else:
                    for dummy in range(scroll_lines):
                        self.down()
                time.sleep(0.5)
                self.screenshot(filename)
                self.check_screenshot(filename)
                offset = hashmatch.find_offset(previous, filename)
                if offset:
                    break
                if attempt + 1 < attempts:
                    os.rename(filename, previous)
            if not offset:
                break
            offsets.append(offset)

            apparently = offset / scroll_lines
            if apparently == 0:
                if self.verbose:
                    print "Apparently no offset per keypress: %d/%d=%d" % (
                        offset, scroll_lines, apparently)
            elif apparently != pixels_per_line:
                pixels_per_line = apparently
                scroll_lines = max(1, min(good_offset / pixels_per_line, 40))
                if self.verbose:
                    print "%d pixels/keypress, %d keypresses/scroll" % (
                        pixels_per_line, scroll_lines)
        else:
            if top_pages == self.max_pages:
                return offsets
            self.scroll_bottom()
            time.sleep(0.5)
            previous2 = previous
            previous = filename
            filename = self.page_filename(self.max_pages)
            self.screenshot(filename)
            self.check_screenshot(filename)
            offset = hashmatch.find_offset(previous, filename)
            if offset:
                # Need enough overlap to avoid browser chrome between pages.
                offset = min(offset, height - 200)
                # Just another page.
                offsets.append(offset)
            else:
                # Check that it's not the same bottom page as before.
                if not hashmatch.find_offset(previous2, filename):
                    # Bottom page, just tack it on.
                    offsets.append(height - 200)
        return offsets

    def scanlines(self, offsets):
        """
        Merge multi-page screenshots and yield scanlines.
        """
        overlaps = [self.height - offset for offset in offsets]
        # print "offsets: ", offsets
        # print "overlaps:", overlaps
        total = 0
        row_bytes = 3 * self.width
        for index in range(0, len(overlaps) + 1):
            top = 0
            bottom = 0
            if index == 0:
                top = self.top_skip
            else:
                top = overlap_top(overlaps[index-1])
            if index == len(offsets):
                bottom = self.bottom_skip
            else:
                bottom = overlap_bottom(overlaps[index])
            bottom = self.height - bottom
            segment = bottom - top
            total += segment
            filename = self.page_filename(index+1)
            print filename, top, bottom, segment, total
            infile = open(filename, 'rb')
            hashmatch.read_ppm_header(infile)
            infile.seek(top*row_bytes, 1)
            for dummy in range(top, bottom):
                scanline = array('B')
                scanline.fromfile(infile, row_bytes)
                yield scanline
            infile.close()

    def browsershot(self, pngfilename = 'browsershot.png'):
        """
        Take a number of screenshots and merge them into one tall image.
        """
        if hasattr(self, 'focus_browser'):
            self.focus_browser()
        # Screenshot of the first page.
        filename = self.page_filename(1)
        self.screenshot(filename)
        self.check_screenshot(filename)
        # Scroll down and take more screenshots.
        offsets = self.scroll_pages(self.height)
        total = self.height + sum(offsets) - self.top_skip - self.bottom_skip
        # Create PNG file.
        outfile = file(pngfilename, 'wb')
        writer = png.Writer(self.width, total)
        writer.write(outfile, self.scanlines(offsets))
        outfile.close()
        # Delete all page screenshots.
        for page in range(1, len(offsets) + 3):
            filename = self.page_filename(page)
            if os.path.exists(filename):
                os.unlink(filename)


def overlap_top(overlap):
    """
    >>> overlap_top(0) >= 0 and overlap_top(1) >= 0
    True
    """
    return overlap - overlap / 4


def overlap_bottom(overlap):
    """
    >>> overlap_bottom(0) >= 0 and overlap_bottom(1) >= 0
    True
    """
    return overlap / 4


def overlap_test(max_overlap=1000):
    """
    >>> overlap_test()
    """
    for overlap in range(max_overlap):
        assert overlap == overlap_top(overlap) + overlap_bottom(overlap)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
