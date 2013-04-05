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
Show language selector.
"""

__revision__ = "$Rev: 2174 $"
__date__ = "$Date: 2007-10-04 18:42:25 -0300 (qui, 04 out 2007) $"
__author__ = "$Author: johann $"

from django import template
from django.conf import settings
from django.utils import translation

register = template.Library()

JAVASCRIPT = "this.form.submit()"

FORM_TEMPLATE = u"""
<form action="/i18n/setlang/" method="post">
<div id="setlang">
<select name="language" id="language" onchange="%s">
%s
</select>
</div>
</form>
""".strip()


@register.simple_tag
def select_lang():
    """
    Display an HTML form with language drop-down box.
    """
    options = []
    current = translation.get_language()
    for lang, name in settings.LANGUAGES:
        sel = ''
        if lang == current:
            sel = ' selected="selected"'
        options.append(u'<option value="%s"%s>%s</option>' %
                       (lang, sel, name))
    return FORM_TEMPLATE % (JAVASCRIPT, '\n'.join(options))
