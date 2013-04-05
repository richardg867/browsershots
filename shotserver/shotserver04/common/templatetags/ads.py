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
Display ads on the site, if configured in settings.py.
"""

__revision__ = "$Rev: 2900 $"
__date__ = "$Date: 2008-06-16 05:19:06 -0300 (seg, 16 jun 2008) $"
__author__ = "$Author: johann $"

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def ads_leaderboard():
    """
    Display a leaderboard ad, if configured in settings.py.
    """
    if not hasattr(settings, 'ADS_LEADERBOARD'):
        return ''
    return settings.ADS_LEADERBOARD.strip()


class AdNode(template.Node):

    def __init__(self, name):
        self.name = name

    def render(self, context):
        http_request = template.resolve_variable('http_request', context)
        if http_request.is_secure() or http_request.user.is_authenticated():
            return ''
        variable = 'ADS_' + self.name.upper()
        if not hasattr(settings, variable):
            return ''
        content = getattr(settings, variable).strip()
        return '<div id="%s">\n%s\n</div>' % (self.name, content)


@register.tag
def show_ad(parser, token):
    """
    Display an ad block, if configured in settings.py.
    The name of the variable in settings.py must be given as parameter,
    e.g. {% show_ad skyscraper %} will use settings.ADS_SKYSCRAPER.
    """
    try:
        tag_name, name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0])
    return AdNode(name)
