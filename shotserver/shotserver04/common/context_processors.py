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
Custom context processors.
"""

__revision__ = "$Rev: 2227 $"
__date__ = "$Date: 2007-10-23 06:11:47 -0300 (ter, 23 out 2007) $"
__author__ = "$Author: johann $"


def http_request(request):
    """
    Add the HTTP request to the request context, but as
    'http_request' rather than 'request' to avoid name clash.
    """
    return {'http_request': request}
