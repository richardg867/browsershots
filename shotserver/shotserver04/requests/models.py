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
Request models.
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from datetime import datetime, timedelta
import os
from xmlrpclib import Fault
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timesince import timesince, timeuntil
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.template.defaultfilters import filesizeformat
from shotserver04.websites.models import Website
from shotserver04.platforms.models import Platform
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import BrowserGroup, Browser
from shotserver04.features.models import Javascript, Java, Flash
from shotserver04.screenshots.models import Screenshot
from shotserver04.screenshots import storage
from shotserver04.common import lock_timeout, last_poll_timeout
from shotserver04.common.object_cache import preload_foreign_keys
from shotserver04.common import granular_update
from shotserver04.features import satisfies


class RequestGroup(models.Model):
    """
    Common options for a group of screenshot requests.
    """
    website = models.ForeignKey(Website,
        verbose_name=_("website"))
    width = models.IntegerField(
        _("screen width"), null=True, blank=True)
    height = models.IntegerField(
        _("screen height"), null=True, blank=True)
    bits_per_pixel = models.IntegerField(
        _("bits per pixel"), null=True, blank=True)
    javascript = models.ForeignKey(Javascript,
        verbose_name=_("Javascript"), blank=True, null=True)
    java = models.ForeignKey(Java,
        verbose_name=_("Java"), blank=True, null=True)
    flash = models.ForeignKey(Flash,
        verbose_name=_("Flash"), blank=True, null=True)
    own_factories_only = models.BooleanField(
        _("only my own factories"), default=False)
    user = models.ForeignKey(User,
        verbose_name=_("submitter"), blank=True, null=True)
    priority = models.IntegerField(
        _("priority"), default=0)
    ip = models.IPAddressField(
        _("IP"))
    submitted = models.DateTimeField(
        _("submitted"), auto_now_add=True)
    expire = models.DateTimeField(
        _("expire"))

    class Meta:
        verbose_name = _("request group")
        verbose_name_plural = _("request groups")
        ordering = ('-submitted', )

    update_fields = granular_update.update_fields

    def __unicode__(self):
        """
        Get string representation.
        """
        return u'%s %d' % (capfirst(_("screenshot request group")),
                           self.index())

    def get_absolute_url(self):
        """
        Get absolute URL.
        """
        return '/requests/%d/' % self.id

    def is_pending(self):
        """True if there are pending screenshot requests in this group."""
        if not hasattr(self, '_pending'):
            self._pending = self.expire > datetime.now() and \
                self.request_set.filter(screenshot__isnull=True).count()
        return self._pending

    def time_since_submitted(self):
        """
        Human-readable formatting of interval since submitted.
        """
        return mark_safe('<li>%s</li>' % (
            capfirst(_("submitted %(interval)s ago")) %
            {'interval': timesince(self.submitted)}))

    def time_until_expire(self):
        """
        Human-readable formatting of interval before expiration.
        """
        now = datetime.now()
        remaining = self.expire - now
        disabled = ''
        if remaining >= timedelta(minutes=29, seconds=50):
            remaining = timedelta(minutes=30)
            disabled = ' disabled="disabled"'
        interval = timeuntil(now + remaining, now)
        expire = capfirst(_("expires in %(interval)s")) % \
            {'interval': interval}
        if self.same_user():
            expire += '\n'.join(('',
'<input type="hidden" name="request_group_id" value="%d" />' % self.id,
'<input type="submit" name="extend" value="%s"%s />' % (
    unicode(capfirst(_("extend"))), disabled),
'<input type="submit" name="cancel" value="%s" />' % (
    unicode(capfirst(_("cancel"))))))
        return mark_safe('<li>%s</li>' % (expire))

    def options(self):
        """
        Human-readable output of requested options.
        """
        lines = []
        if self.own_factories_only:
            lines.append('<li>%s</li>' % unicode(
                _("Only for screenshot factories run by %(admin)s") %
                {'admin': self.user.username}))
        result = []
        for attr in ('javascript', 'java', 'flash',
                     'width', 'bits_per_pixel'):
            option = getattr(self, attr)
            if option is None:
                continue
            name = self._meta.get_field(attr).verbose_name
            if attr == 'width':
                result.append(_("%(width)d pixels wide") %
                              {'width': option})
            elif attr == 'bits_per_pixel':
                result.append(_("%(color_depth)d bits per pixel") %
                              {'color_depth': option})
            else:
                result.append(u'%s %s' % (name, option))
        if result:
            lines.append('<li>%s</li>' % ', '.join(result))
        return mark_safe('\n'.join(lines))

    def preload_cache(self):
        """
        Load database objects to save many SQL queries later.
        """
        if not hasattr(self, '_browsers_cache'):
            self._browsers_cache = Browser.objects.all()
            preload_foreign_keys(self._browsers_cache, browser_group=True)
        if not hasattr(self, '_factories_cache'):
            self._factories_cache = Factory.objects.all()
            preload_foreign_keys(self._factories_cache,
                operating_system=True)

    def previews(self):
        """
        Thumbnails of screenshots for this request group.
        """
        screenshots = []
        requests = self.request_set.filter(screenshot__isnull=False)
        # Preload browsers and factories from cache.
        self.preload_cache()
        preload_foreign_keys(requests,
            screenshot__browser=self._browsers_cache)
        preload_foreign_keys(requests,
            screenshot__factory=self._factories_cache)
        # Get screenshots and sort by id.
        screenshots = [(request.screenshot_id, request.screenshot)
                       for request in requests]
        if screenshots:
            total_bytes = sum([screenshot.bytes or 0
                               for index, screenshot in screenshots])
            screenshots.sort()
            max_height = max([screenshot.height * 80 / screenshot.width
                              for index, screenshot in screenshots])
            result = [screenshot.preview_div(height=max_height, caption=True)
                      for index, screenshot in screenshots]
            if len(screenshots) > 1:
                result.append(self.zip_link(len(screenshots), total_bytes))
            return mark_safe('\n'.join(result))
        elif self.is_pending():
            return mark_safe(
u'<p class="admonition hint">%s<br />\n%s</p>' % (
_("Your screenshots will appear here when they are uploaded."),
bracket_link(self.website.get_absolute_url(),
_("[Reload this page] or bookmark it and come back later."))))
        else:
            hint = _(u"Your screenshot requests have expired.")
            return mark_safe(u'<p class="admonition warning">%s</p>' % hint)

    def queue_overview(self):
        """
        Quick overview of queuing screenshots requests.
        """
        parts = []
        requests = self.request_set.all()
        total = requests.count()
        parts.append(_("%(count)d browsers selected") % {'count': total})
        uploaded = requests.filter(screenshot__isnull=False).count()
        queuing = requests.filter(screenshot__isnull=True)
        starting = queuing.filter(factory__isnull=False,
                                  browser__isnull=True).count()
        loading = queuing.filter(browser__isnull=False).count()
        if datetime.now() < self.expire:
            if starting:
                parts.append(_("%(count)d starting") % {'count': starting})
            if loading:
                parts.append(_("%(count)d loading") % {'count': loading})
            if uploaded:
                parts.append(_("%(count)d uploaded") % {'count': uploaded})
        else:
            if uploaded:
                parts.append(_("%(count)d uploaded") % {'count': uploaded})
            failed = starting + loading
            if failed:
                parts.append(_("%(count)d failed") % {'count': failed})
            expired = total - uploaded - failed
            if expired:
                parts.append(_("%(count)d expired") % {'count': expired})
        return mark_safe(u'<li>%s</li>' % ', '.join(parts))

    def matching_factories(self):
        """
        Get active factories that are compatible with this request group.
        """
        factories = Factory.objects.filter(
            last_poll__gte=last_poll_timeout())
        result = []
        for factory in factories:
            if self.width and self.height:
                if not factory.supports_screen_size(self.width, self.height):
                    continue
            elif self.width:
                if not factory.supports_screen_width(self.width):
                    continue
            elif self.height:
                if not factory.supports_screen_height(self.height):
                    continue
            if self.bits_per_pixel:
                if not factory.supports_color_depth(self.bits_per_pixel):
                    continue
            result.append(factory)
        preload_foreign_keys(result, operating_system=True)
        return result

    def matching_browsers(self):
        """
        Get active browsers that are compatible with this request group.
        """
        factories = self.matching_factories()
        browsers = Browser.objects.filter(
            factory__in=factories,
            active=True)
        result = []
        for browser in browsers:
            if not satisfies(browser.java_id, self.java_id):
                continue
            if not satisfies(browser.javascript_id, self.javascript_id):
                continue
            if not satisfies(browser.flash_id, self.flash_id):
                continue
            result.append(browser)
        preload_foreign_keys(result, factory=factories)
        return result

    def queue_estimate(self):
        """
        One-line info for estimated remaining queue wait.
        """
        now = datetime.now()
        if self.priority > 0:
            min_seconds = 60
            max_seconds = 180
            link = u'<a href="/priority/">%s</a>' % capfirst(_("priority"))
        else:
            self.preload_cache()
            browsers = self.matching_browsers()
            preload_foreign_keys(browsers, browser_group=True)
            requests = self.request_set.filter(screenshot__isnull=True)
            preload_foreign_keys(requests, browser_group=True)
            elapsed = now - self.submitted
            elapsed = elapsed.seconds + elapsed.days * 24 * 3600
            estimates = []
            for request in requests:
                estimate = request.queue_estimate(browsers)
                if estimate:
                    estimates.append(estimate - elapsed)
            if not estimates:
                return ''
            min_seconds = max(180, min(estimates) + 30)
            max_seconds = max(180, max(estimates) + 30)
            link = u'<a href="%s">%s</a>' % (
                self.get_absolute_url(), capfirst(_("details")))
        if min_seconds == max_seconds:
            estimate = timeuntil(now + timedelta(seconds=min_seconds))
        else:
            min_interval = timeuntil(now + timedelta(seconds=min_seconds))
            max_interval = timeuntil(now + timedelta(seconds=max_seconds))
            estimate = _("%(min_interval)s to %(max_interval)s") % locals()
        return mark_safe(u'<li>%s: %s (%s)</li>' % (
            capfirst(_("queue estimate")), estimate, link))

    def same_user(self):
        """
        Check if the current user submitted this request group.
        """
        if self.user_id:
            return self.user_id == self._http_request.user.id
        else:
            return self.ip == self._http_request.META['REMOTE_ADDR']

    def index(self):
        """
        Get the number among all request groups for the same website.
        """
        if not hasattr(self, '_index'):
            self._index = RequestGroup.objects.filter(
                id__lte=self.id, website=self.website).count()
        return self._index

    def zip_filename(self):
        """Filename for ZIP file with screenshots."""
        return '-'.join((
            self.submitted.strftime('%y%m%d-%H%M%S'),
            self.website.domain.name,
            '%d.zip' % self.id,
            ))

    def zip_link(self, count=None, bytes=None):
        """
        Link to ZIP file with screenshots.
        """
        if count is None:
            text = unicode(capfirst(_("download all screenshots")))
        else:
            text = unicode(capfirst(
                _("download %(count)d screenshots") % locals()))
        if bytes:
            text += ' (%s)' % filesizeformat(bytes).replace(' ', '&nbsp;')
        link = u'<a href="%s/screenshots/%s">%s</a>' % (
            settings.ZIP_URL.rstrip('/'), self.zip_filename(), text)
        return mark_safe(u'<div class="floatleft">%s</div>' % link)



class Request(models.Model):
    """
    Request for a screenshot of a specified browser.
    Contains state during processing.
    """
    request_group = models.ForeignKey(RequestGroup,
        verbose_name=_("request group"))
    platform = models.ForeignKey(Platform,
        verbose_name=_("platform"))
    browser_group = models.ForeignKey(BrowserGroup,
        verbose_name=_("browser group"))
    major = models.IntegerField(
        _("major"), blank=True, null=True)
    minor = models.IntegerField(
        _("minor"), blank=True, null=True)
    priority = models.IntegerField(
        _("priority"))
    factory = models.ForeignKey(Factory,
        verbose_name=_("factory"), blank=True, null=True)
    locked = models.DateTimeField(
        _("locked"), blank=True, null=True)
    browser = models.ForeignKey(Browser,
        verbose_name=_("browser"), blank=True, null=True)
    redirected = models.DateTimeField(
        _("redirected"), blank=True, null=True)
    screenshot = models.ForeignKey(Screenshot,
        verbose_name=_("screenshot"), blank=True, null=True)

    class Meta:
        verbose_name = _("request")
        verbose_name_plural = _("requests")

    update_fields = granular_update.update_fields

    def __unicode__(self):
        return u"%s on %s" % (self.browser_string(), self.platform.name)

    def browser_string(self):
        """
        Human-readable formatting of requested browser.
        """
        result = [self.browser_group.name]
        if self.major is not None:
            result.append(u' ' + unicode(self.major))
            if self.minor is not None:
                result.append(u'.' + unicode(self.minor))
        return u''.join(result)

    def status(self):
        """
        Human-readable output of request status.
        """
        if self.screenshot_id is not None:
            return _("uploaded")
        if self.locked and self.locked < lock_timeout():
            return _("failed")
        if self.redirected:
            return _("loading")
        if self.locked:
            return _("starting")
        return ''

    def check_factory_lock(self, factory):
        """
        Check that the request is locked by this factory.
        """
        if self.factory is None:
            raise Fault(409,
                u"Request %d was not locked." % self.id)
        if factory != self.factory:
            raise Fault(423,
                u"Request %d was locked by factory %s." %
                (self.id, self.factory.name))

    def queue_estimate(self, matching_browsers):
        """
        Queue estimate for the fastest matching browser for this request.
        """
        result = None
        for browser in matching_browsers:
            operating_system = browser.factory.operating_system
            if (operating_system.platform_id == self.platform_id and
                browser.browser_group_id == self.browser_group_id and
                (browser.major == self.major or self.major is None) and
                (browser.minor == self.minor or self.minor is None)):
                estimate = browser.factory.queue_estimate
                if estimate and (result is None or estimate < result):
                    result = estimate
        return result


def bracket_link(href, text):
    """Replace square brackets with a HTML link."""
    return text.replace('[', u'<a href="%s">' % href).replace(']', '</a>')
