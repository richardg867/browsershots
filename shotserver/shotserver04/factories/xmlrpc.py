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
XML-RPC interface for factories app.
"""

__revision__ = "$Rev: 2804 $"
__date__ = "$Date: 2008-05-08 01:26:26 -0300 (qui, 08 mai 2008) $"
__author__ = "$Author: johann $"

from shotserver04.xmlrpc import signature, factory_xmlrpc
from shotserver04.requests.models import Request


@factory_xmlrpc
@signature(str, str)
def features(http_request, factory):
    """
    Generate SQL WHERE clause to match requests for this factory.

    Arguments
    ~~~~~~~~~
    * factory_name string (lowercase, normally from hostname)

    Return value
    ~~~~~~~~~~~~
    * where string (SQL WHERE clause)
    """
    queryset = Request.objects.filter(factory.features_q())
    where, params = queryset.query.as_sql()
    return where % params
