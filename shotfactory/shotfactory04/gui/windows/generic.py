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
GUI-specific interface functions for a generic browser on Microsoft Windows.
"""

import os
import time
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory04.gui import windows
from shotfactory04.utils import short_filename

class Gui(windows.Gui):
    """
    Special functions for a generic browser on Windows.
    """

    def reset_browser(self):
        """
        Delete all files from the browser cache.
        """
        # Nothing

    def find_scrollable(self):
        """
        Find the scrollable window.
        """
        # Nothing, assume the window is focused
    
    def close(self):
        """
        Close the browser.
        """
        try:
            if "command" in self.__dict__:
                name = os.path.basename(self.command.split(" ")[0])
                os.system('pv.exe -kf %s "2>nul" > nul' % name)
                short = short_filename(name)
                if short != name:
                    os.system('pv.exe -kf %s "2>nul" > nul' % short)
        except:
            doNothing = ""


# Test scrolling from command line
if __name__ == '__main__':
    config = {
        'width': 1024,
        'height': 768,
        'bpp': 24,
        'request': 123,
        }

    class Options:
        verbose = 3
        max_pages = 7

    gui = Gui(config, Options())
    gui.down()
    time.sleep(1)
    gui.scroll_bottom()
