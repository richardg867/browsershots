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
Automatic form with active browsers for each platform.
"""

__revision__ = "$Rev: 2971 $"
__date__ = "$Date: 2008-08-14 08:21:38 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django import forms
from django.utils.safestring import mark_safe


def is_latest_minor_version(browser, platform, active_browsers):
    """
    Check if this browser has the newest minor version among all of
    the same browsers with the same major version number on the same
    platform. Used for default browser selection on start page.
    """
    for other in active_browsers:
        if (other.browser_group != browser.browser_group or
            other.major != browser.major or
            other.factory.operating_system.platform_id != platform.id):
            continue
        if other.minor > browser.minor:
            return False
    return True


class BrowsersForm(forms.BaseForm):
    """
    Browser chooser form for one platform.
    """

    errors = {}
    base_fields = forms.forms.SortedDict()

    def __init__(self, active_browsers, platform,
                 data=None, selected_browsers=None):
        forms.BaseForm.__init__(self, data)
        self.platform = platform
        self.columns = 1
        field_dict = {}
        for browser in active_browsers:
            if browser.factory.operating_system.platform_id != platform.id:
                continue
            label = browser.browser_group.name
            if browser.major is not None:
                label += ' ' + str(browser.major)
                if browser.minor is not None:
                    label += '.' + str(browser.minor)
            platform_name = platform.name.lower().replace(' ', '-')
            browser_name = browser.browser_group.name.lower()
            name = '_'.join((
                platform_name,
                browser_name,
                str(browser.major),
                str(browser.minor),
                ))
            if name in field_dict:
                continue
            if data is not None:
                initial = name in data and 'on' in data[name]
            elif selected_browsers is not None:
                initial = False
                for sel in selected_browsers:
                    if sel in name:
                        initial = True
            else:
                initial = is_latest_minor_version(
                    browser, platform, active_browsers)
            field = forms.BooleanField(
                label=label, initial=initial, required=False)
            field.platform_name = platform_name
            field.browser_name = browser_name
            field.browser = browser
            field_dict[name] = field
        field_names = field_dict.keys()
        field_names.sort()
        for name in field_names:
            self.fields[name] = field_dict[name]

    def __unicode__(self):
        fields = list(self.fields)
        output = []
        for column in range(self.columns):
            output.append('<div class="browsers_column">')
            for index in range(self.column_length()):
                if not fields:
                    break
                field = fields.pop(0)
                #img = u'<img src="/static/icons/browser/%s.png" alt="" />' % (
                #    self.fields[field].browser_name)
                label = u' <label for="id_%s">%s</label><br />' % (
                    field, self[field].label)
                output.append(unicode(self[field]) + label)
            output.append('</div>')
        return mark_safe(u'\n'.join(output))

    def column_length(self):
        """Get the length of the longest column after wrapping."""
        return (len(self.fields) + self.columns - 1) / self.columns
