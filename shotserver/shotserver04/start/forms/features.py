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
Input form with select fields for Javascript, Java, Flash.
"""

__revision__ = "$Rev: 2971 $"
__date__ = "$Date: 2008-08-14 08:21:38 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django import forms
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from shotserver04.features.models import Javascript, Java, Flash


def get_active(model, browsers):
    """
    Get choices for a feature from the database.
    """
    yield ('dontcare', capfirst(_("don't care")))
    available = set()
    attr = model._meta.module_name + '_id'
    for browser in browsers:
        feature_id = getattr(browser, attr)
        if feature_id:
            available.add(feature_id)
    if 1 in available:
        yield ('disabled', capfirst(_("disabled")))
        available.discard(1) # 1 means disabled
    if available:
        yield ('enabled', capfirst(_("enabled")))
        available.discard(2) # 2 means enabled
    for version in model.objects.filter(id__in=available):
        yield (version.version, version.version)


def feature_or_none(model, value):
    """
    Find feature instance by post value.
    """
    if value == 'dontcare':
        return None
    return model.objects.get(version=value)


class FeaturesForm(forms.Form):
    """
    Request features input form.
    """
    javascript = forms.ChoiceField(
        label=_("Javascript"), initial='dontcare')
    java = forms.ChoiceField(
        label=_("Java"), initial='dontcare')
    flash = forms.ChoiceField(
        label=_("Flash"), initial='dontcare')

    def load_choices(self, browsers):
        """
        Load available choices from the database.
        """
        self['javascript'].field.choices = get_active(Javascript, browsers)
        self['java'].field.choices = get_active(Java, browsers)
        self['flash'].field.choices = get_active(Flash, browsers)

    def clean_javascript(self):
        """Load matching Javascript version from database."""
        return feature_or_none(Javascript, self.cleaned_data['javascript'])

    def clean_java(self):
        """Load matching Java version from database."""
        return feature_or_none(Java, self.cleaned_data['java'])

    def clean_flash(self):
        """Load matching Flash version from database."""
        return feature_or_none(Flash, self.cleaned_data['flash'])
