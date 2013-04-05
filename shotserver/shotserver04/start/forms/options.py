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
Input form with select fields for screen size and color depth.
"""

__revision__ = "$Rev: 2971 $"
__date__ = "$Date: 2008-08-14 08:21:38 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django import forms
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from shotserver04.factories.models import ScreenSize, ColorDepth
from shotserver04.common import int_or_none


def screen_size_choices(active_factories):
    """
    Get screen sizes that are supported by active factories.
    """
    yield ('dontcare', capfirst(_("don't care")))
    previous = None
    for size in ScreenSize.objects.filter(factory__in=active_factories):
        if size.width != previous:
            yield (size.width, capfirst(
                   _("%(width)d pixels wide") % {'width': size.width}))
            previous = size.width


def color_depth_choices(active_factories):
    """
    Get color depths that are supported by active factories.
    """
    yield ('dontcare', capfirst(_("don't care")))
    previous = None
    for depth in ColorDepth.objects.filter(factory__in=active_factories):
        if depth.bits_per_pixel != previous:
            yield (depth.bits_per_pixel, capfirst(
                   _("%(color_depth)d bits per pixel") %
                   {'color_depth': depth.bits_per_pixel}))
            previous = depth.bits_per_pixel


class OptionsForm(forms.Form):
    """
    Request options input form.
    """
    width = forms.ChoiceField(
        label=_("screen size"), initial='dontcare')
    bits_per_pixel = forms.ChoiceField(
        label=_("color depth"), initial='dontcare')

    def load_choices(self, factories):
        """
        Load available choices from the database.
        """
        self['width'].field.choices = screen_size_choices(factories)
        self['bits_per_pixel'].field.choices = color_depth_choices(factories)

    def clean_width(self):
        """Convert screen size to integer."""
        return int_or_none(self.cleaned_data['width'])

    def clean_bits_per_pixel(self):
        """Convert color depth to integer."""
        return int_or_none(self.cleaned_data['bits_per_pixel'])
