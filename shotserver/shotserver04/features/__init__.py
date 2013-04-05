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
Configure available Javascript, Java, Flash versions.
"""

__revision__ = "$Rev: 2306 $"
__date__ = "$Date: 2007-11-18 13:27:31 -0300 (dom, 18 nov 2007) $"
__author__ = "$Author: johann $"


def satisfies(candidate_id, requested_id):
    """
    Check if the candidate version satisfies the requested version.
    """
    if requested_id is None:
        return True
    if requested_id == 2 and candidate_id >= 2:
        return True
    return candidate_id == requested_id
