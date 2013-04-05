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
Factory models.
"""

__revision__ = "$Rev: 3044 $"
__date__ = "$Date: 2008-09-02 17:40:40 -0300 (ter, 02 set 2008) $"
__author__ = "$Author: johann $"

from xmlrpclib import Fault
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from shotserver04.platforms.models import OperatingSystem
from shotserver04.sponsors.models import Sponsor
from shotserver04.common.templatetags import human
from shotserver04.common import granular_update, last_error_timeout

FACTORY_FIELDS = (
    'name', 'operating_system', 'last_poll', 'last_upload',
    'uploads_per_hour', 'uploads_per_day', 'queue_estimate')
FACTORY_FIELDS_SECONDS = ('queue_estimate')
FACTORY_FIELDS_TIMESINCE = ('last_poll', 'last_upload', 'created')


class Factory(models.Model):
    """
    Screenshot factory configuration.
    """
    name = models.SlugField(
        _('name'), unique=True,
        help_text=_('Hostname (lowercase)'))
    admin = models.ForeignKey(User,
        verbose_name=_('administrator'))
    sponsor = models.ForeignKey(Sponsor,
        verbose_name=_('sponsor'), blank=True, null=True)
    hardware = models.CharField(
        _('hardware'), max_length=100, blank=True,
        help_text=_("e.g. ThinkPad R32, P4 1.8 GHz, 768 MB"))
    operating_system = models.ForeignKey(OperatingSystem,
        verbose_name=_('operating system'))
    ip = models.IPAddressField(
        _('IP'), blank=True, null=True, editable=False,
        help_text=_("The last poll came from this IP address."))
    last_poll = models.DateTimeField(
        _('last poll'), blank=True, null=True, editable=False)
    last_upload = models.DateTimeField(
        _('last upload'), blank=True, null=True, editable=False)
    uploads_per_hour = models.IntegerField(
        _('uploads per hour'), blank=True, null=True, editable=False)
    uploads_per_day = models.IntegerField(
        _('uploads per day'), blank=True, null=True, editable=False)
    errors_per_hour = models.IntegerField(
        _('errors per hour'), blank=True, null=True, editable=False)
    errors_per_day = models.IntegerField(
        _('errors per day'), blank=True, null=True, editable=False)
    problems_per_day = models.IntegerField(
        _('problems per day'), blank=True, null=True, editable=False)
    queue_estimate = models.IntegerField(
        _('queue estimate'), blank=True, null=True, editable=False,
        help_text=_("Seconds between screenshot request and upload."))
    created = models.DateTimeField(
        _('created'), auto_now_add=True)

    class Meta:
        verbose_name = _('factory')
        verbose_name_plural = _('factories')
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        """Get absolute URL."""
        return '/factories/%s/' % urlquote(self.name)

    def features_q(self):
        """Get SQL query to match screenshot requests."""
        return (self.platform_q() &
                self.screensizes_q() &
                self.colordepths_q() &
                self.browsers_q())

    def platform_q(self):
        """Get SQL query to match requested platforms."""
        return (models.Q(platform__isnull=True) |
                models.Q(platform__id=self.operating_system.platform.id))

    def browsers_q(self):
        """Get SQL query to match requested browsers."""
        q = models.Q()
        browsers = self.browser_set.filter(active=True)
        if not browsers.count():
            raise Fault(404,
                u"No active browsers registered for factory %s." % self.name)
        browsers = browsers.filter(
            models.Q(last_error__isnull=True) |
            models.Q(last_error__lt=last_error_timeout()))
        if not len(browsers):
            raise Fault(204,
u"All active browsers on %s are temporarily blocked because of errors." %
self.name)
        for browser in browsers:
            q |= browser.features_q()
        return q

    def screensizes_q(self):
        """Get SQL query to match requested screen sizes."""
        q = models.Q(request_group__width__isnull=True)
        for screensize in self.screensize_set.all():
            q |= models.Q(request_group__width=screensize.width)
        return q

    def colordepths_q(self):
        """Get SQL query to match requested color depths."""
        q = models.Q(request_group__bits_per_pixel__isnull=True)
        for colordepth in self.colordepth_set.all():
            q |= models.Q(request_group__bits_per_pixel=
                          colordepth.bits_per_pixel)
        return q

    @classmethod
    def table_header(cls):
        """
        HTML table header cells for factory list.
        """
        fields = []
        for field in FACTORY_FIELDS:
            try:
                name = cls._meta.get_field(field).verbose_name
            except models.FieldDoesNotExist:
                name = _(field.replace('_', ' '))
            fields.append(u'<th>%s</th>' % human.human_br(capfirst(name)))
        return mark_safe(''.join(fields))

    def table_row(self):
        """
        HTML table row cells for this factory.
        """
        fields = []
        for field in FACTORY_FIELDS:
            extra = []
            if field == 'uploads_per_day':
                if self.errors_per_day:
                    extra.append('<a href="%s#errors">%s</a>' % (
                            self.get_absolute_url(),
                            _("%d errors") % self.errors_per_day))
                if self.problems_per_day:
                    extra.append('<a href="%s#problems">%s</a>' % (
                            self.get_absolute_url(),
                            _("%d problems") % self.problems_per_day))
            if field == 'uploads_per_hour':
                if self.errors_per_hour:
                    extra.append('<a href="%s#errors">%s</a>' % (
                            self.get_absolute_url(),
                            _("%d errors") % self.errors_per_hour))
            value = getattr(self, field)
            if callable(value):
                value = value()
            if field == 'name':
                value = human.human_link(self, 16)
            if field in FACTORY_FIELDS_TIMESINCE:
                value = human.human_timesince(value)
            if field in FACTORY_FIELDS_SECONDS:
                value = human.human_seconds(value)
            if value is None or value == 0:
                value = ''
            if extra:
                value = '%s (%s)' % (value, ', '.join(extra))
            fields.append(u'<td>%s</td>' % value)
        return mark_safe(''.join(fields))

    def supports_screen_size(self, width, height):
        """Return true if the requested screen size is supported."""
        return self.screensize_set.filter(
                width=width, height=height).count() >= 1

    def supports_screen_width(self, width):
        """Return true if the requested screen width is supported."""
        return self.screensize_set.filter(width=width).count() >= 1

    def supports_screen_height(self, height):
        """Return true if the requested screen height is supported."""
        return self.screensize_set.filter(height=height).count() >= 1

    def supports_color_depth(self, bits_per_pixel):
        """Return true if the requested screen height is supported."""
        return self.colordepth_set.filter(
            bits_per_pixel=bits_per_pixel).count() >= 1

    update_fields = granular_update.update_fields

class ScreenSize(models.Model):
    """
    Supported screen resolutions for screenshot factories.
    """
    factory = models.ForeignKey(Factory,
        verbose_name=_('factory'))
    width = models.IntegerField(
        _('width'))
    height = models.IntegerField(
        _('height'))

    class Meta:
        verbose_name = _('screen size')
        verbose_name_plural = _('screen sizes')
        ordering = ('width', )
        unique_together = (('factory', 'width', 'height'), )

    def __unicode__(self):
        return u'%dx%d' % (self.width, self.height)


class ColorDepth(models.Model):
    """
    Supported color depths (bits per pixel) for screenshot factories.
    """
    factory = models.ForeignKey(Factory,
        verbose_name=_('factory'))
    bits_per_pixel = models.IntegerField(
        _('bits per pixel'))

    class Meta:
        verbose_name = _('color depth')
        verbose_name_plural = _('color depths')
        ordering = ('bits_per_pixel', )
        unique_together = (('factory', 'bits_per_pixel'), )

    def __unicode__(self):
        return unicode(self.bits_per_pixel)


class ScreenshotCount(models.Model):
    factory = models.ForeignKey(Factory,
        verbose_name=_('factory'))
    date = models.DateField(_('date'))
    screenshots = models.IntegerField(_('screenshots'))

    class Meta:
        unique_together = ('factory', 'date')

    def __unicode__(self):
        if self.factory is None:
            return u'%d screenshots total on %s' % (
                self.screenshots, self.date.strftime('%Y-%m-%d'))
        else:
            return u'%d screenshots from %s on %s' % (
                self.screenshots, self.factory, self.date.strftime('%Y-%m-%d'))

    update_fields = granular_update.update_fields
