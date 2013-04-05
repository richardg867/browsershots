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
Include Javascript for Google Analytics.
"""

__revision__ = "$Rev: 2229 $"
__date__ = "$Date: 2007-10-23 06:19:42 -0300 (ter, 23 out 2007) $"
__author__ = "$Author: johann $"

from django import template
from django.conf import settings

register = template.Library()

JAVASCRIPT = u"""
<script src="%s" type="text/javascript">
</script>
<script type="text/javascript">
_uacct = "%s";
urchinTracker();
</script>
""".strip()


@register.simple_tag
def google_analytics(secure=False):
    """
    Include Javascript for Google Analytics, if account is configured.
    """
    if not hasattr(settings, 'GOOGLE_ANALYTICS_ACCOUNT'):
        return ''
    if not settings.GOOGLE_ANALYTICS_ACCOUNT:
        return ''
    if secure:
        url = 'https://ssl.google-analytics.com/urchin.js'
    else:
        url = 'http://www.google-analytics.com/urchin.js'
    return JAVASCRIPT % (url, settings.GOOGLE_ANALYTICS_ACCOUNT)
