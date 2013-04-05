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
Sponsors for screenshot factories.
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from shotserver04.common import granular_update


class Sponsor(models.Model):
    """
    Show sponsor links near screenshots from sponsored factories.
    """

    name = models.CharField(
        _('name'), max_length=50)
    slug = models.SlugField(
        _('slug'), max_length=50,
        help_text=_("This is used to generate the link to the logo image."))
    url = models.URLField(
        _('URL'), max_length=400, unique=True, verify_exists=False)
    alt = models.CharField(max_length=100)
    width = models.IntegerField(_('width'))
    height = models.IntegerField(_('height'))
    premium = models.BooleanField(
        _('premium'),
        help_text=_("Premium sponsors are always shown on the front page."))
    front_page = models.BooleanField(
        _('front page'), editable=False, default=False)

    class Meta:
        verbose_name = _('sponsor')
        verbose_name_plural = _('sponsors')
        ordering = ('-premium', 'id', )

    update_fields = granular_update.update_fields

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Get sponsor URL."""
        return self.url

    def get_redirect_url(self):
        """Get redirect URL for counting clicks on sponsor links."""
        return '/sponsors/%s/' % self.slug

    def get_logo_url(self):
        """Get absolute URL of logo image."""
        return '/static/logos/%dx%d/%s.png' % (
            self.width, self.height, self.slug)

    def logo(self):
        """Get HTML image with link to sponsor website."""
        img = '<img width="%d" height="%d" src="%s" alt="%s" title="%s" />' % (
            self.width, self.height, self.get_logo_url(),
            self.alt or self.name, self.alt or self.name)
        return mark_safe(
            '<a href="%s">%s</a>' % (self.get_absolute_url(), img))
