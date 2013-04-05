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
Input form with special options.
"""

__revision__ = "$Rev: 2974 $"
__date__ = "$Date: 2008-08-14 12:26:19 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

from django import forms
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _


class SpecialForm(forms.Form):
    """
    Special options input form.
    """
    own_factories_only = forms.BooleanField(
        label=_("only my own factories"),
        help_text=_("Test your own screenshot factories with priority."),
        initial=False, required=False)
