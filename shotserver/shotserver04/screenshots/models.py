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
Screenshot models.
"""

__revision__ = "$Rev: 2949 $"
__date__ = "$Date: 2008-08-13 18:34:02 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

import os
import cgi
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from shotserver04.websites.models import Website
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import Browser
from shotserver04.screenshots import storage

PROBLEM_CHOICES = {
    811: _("This is not the requested browser."),
    812: _("This is not the requested operating system."),

    821: _("This is not the requested Javascript version."),
    822: _("This is not the requested Java version."),
    823: _("This is not the requested Flash version."),
    824: _("A language pack needs to be installed."),

    861: _("There is a dialog box in front of the browser window."),
    862: _("The browser window is not maximized."),
    863: _("The page is not finished loading."),
    }

PROBLEM_CHOICES_EXPLICIT = {
    811: _("This is not %(browser)s."),
    812: _("This is not %(operating_system)s."),

    821: _("Javascript is not %(javascript)s."),
    822: _("Java is not %(java)s."),
    823: _("Flash is not %(flash)s."),
    }

S3_DEPLOYMENT_DATE = datetime(2008, 2, 22, 13, 0)


class ScreenshotManager(models.Manager):
    """
    Extended database manager for Screenshot model.
    """

    def _quote(self, name):
        """Quote column name, with table name."""
        from django.db import connection
        qn = connection.ops.quote_name
        return '%s.%s' % (
            qn(self.model._meta.db_table),
            qn(name))

    def recent(self, user=None):
        """
        Get recent screenshots, but only one per website.
        """
        from django.db import connection
        qn = connection.ops.quote_name
        cursor = connection.cursor()
        fields = ','.join(
            [self._quote(field.column) for field in self.model._meta.fields])
        if user is None or user.is_anonymous():
            user_filter = qn('user_id') + ' IS NULL'
        else:
            user_filter = qn('user_id') + ' = ' + str(user.id)
        cursor.execute("""
            SELECT """ + fields + """
            FROM """ + qn(self.model._meta.db_table) + """
            WHERE """ + self._quote('id') + """ IN (
                SELECT MAX(""" + self._quote('id') + """)
                AS """ + qn('maximum') + """
                FROM  """ + qn(self.model._meta.db_table) + """
                WHERE """ + user_filter + """
                GROUP BY """ + self._quote('website_id') + """
                ORDER BY """ + qn('maximum') + """ DESC
                LIMIT 60)
            ORDER BY """ + self._quote('id') + """ DESC
            """)
        for row in cursor.fetchall():
            yield self.model(*row)


class Screenshot(models.Model):
    """
    Uploaded screenshot files.
    """
    hashkey = models.SlugField(
        _('hashkey'), max_length=32, unique=True)
    user = models.ForeignKey(User, blank=True, null=True,
        verbose_name=_('user'))
    website = models.ForeignKey(Website,
        verbose_name=_('website'))
    factory = models.ForeignKey(Factory,
        verbose_name=_('factory'))
    browser = models.ForeignKey(Browser,
        verbose_name=_('browser'))
    width = models.IntegerField(
        _('width'))
    height = models.IntegerField(
        _('height'))
    bytes = models.IntegerField(
        _('bytes'), null=True)
    uploaded = models.DateTimeField(
        _('uploaded'), auto_now_add=True)

    objects = ScreenshotManager()

    class Meta:
        verbose_name = _('screenshot')
        verbose_name_plural = _('screenshots')
        ordering = ('uploaded', )

    def __unicode__(self):
        return self.hashkey

    def get_absolute_url(self):
        """URL for screenshot detail page."""
        return '/screenshots/%s/' % self.hashkey

    def get_png_url(self, size='original'):
        """URL for screenshot images of different sizes."""
        if (self.user_id is not None and
            self.uploaded > S3_DEPLOYMENT_DATE and
            hasattr(settings, 'S3_BUCKETS') and
            str(size) in settings.S3_BUCKETS):
            return 'http://%s/%s.png' % (
                settings.S3_BUCKETS[str(size)], self.hashkey)
        return '/'.join((settings.PNG_URL.rstrip('/'),
            str(size), self.hashkey[:2], self.hashkey + '.png'))

    def get_large_url(self):
        """URL for large preview image."""
        return self.get_png_url(size=512)

    def get_preview_height(self, width=160):
        """Calculate zoomed height."""
        return (self.height * width + self.width / 2) / self.width

    def get_large_height(self):
        """Calculate zoomed height for large preview."""
        return self.get_preview_height(width=512)

    def preview_img(self, width=160, title=None):
        """
        HTML img with screenshot preview.
        """
        height = self.get_preview_height(width)
        style = 'width:%spx;height:%spx;z-index:0' % (width / 2, height / 2)
        if title is None:
            title = unicode(self.browser)
        title = cgi.escape(title, quote=True)
        return mark_safe(' '.join((
            u'<img class="preview" style="%s"' % style,
            u'src="%s"' % self.get_png_url(width),
            u'alt="%s" title="%s"' % (title, title),
            u'onmouseover="larger(this,%s,%s)"' % (width, height),
            u'onmouseout="smaller(this,%s,%s)" />' % (width, height),
            )))

    def preview_div(self, width=80, height=None, style="float:left",
                    title=None, caption=None, href=None):
        """
        HTML div with screenshot preview image and link.
        """
        auto_height = self.get_preview_height(width)
        if height is None:
            height = auto_height
        if caption:
            height += 20
        style = 'width:%dpx;height:%dpx;%s' % (width, height, style)
        href = href or self.get_absolute_url()
        if title is None:
            title = unicode(self.browser)
        lines = ['<div class="preview" style="%s">' % style]
        lines.append(u'<a href="%s">%s</a>' %
            (cgi.escape(href, quote=True),
             self.preview_img(width=2*width, title=title)))
        if caption is True:
            caption = '<br />'.join((
                unicode(self.browser),
                self.factory.operating_system.
                    __unicode__(show_codename=False)))
        if caption:
            lines.append(
                u'<div class="caption" style="padding-top:%dpx">%s</div>' %
                (auto_height, caption))
        lines.append('</div>')
        return mark_safe('\n'.join(lines))

    def preview_div_with_browser(self):
        """Shortcut for templates."""
        return self.preview_div(caption=unicode(self.browser))

    def arrow(self, screenshot, img, alt):
        """
        HTML link to next or previous screenshot in a group.
        """
        if not screenshot:
            return mark_safe(
                u'<img src="/static/css/%s-gray.png" alt="%s" />' %
                (img, alt))
        return mark_safe(''.join((
            u'<a href="%s">' % screenshot.get_absolute_url(),
            u'<img src="/static/css/%s.png" alt="%s" />' % (img, alt),
            u'</a>',
            )))

    def get_first(self, **kwargs):
        """Get the first screenshot in a group."""
        return Screenshot.objects.filter(**kwargs).order_by('id')[:1]

    def get_last(self, **kwargs):
        """Get the last screenshot in a group."""
        return Screenshot.objects.filter(**kwargs).order_by('-id')[:1]

    def get_previous(self, **kwargs):
        """Get the previous screenshot in a group."""
        return Screenshot.objects.filter(
            id__lt=self.id, **kwargs).order_by('-id')[:1]

    def get_next(self, **kwargs):
        """Get the next screenshot in a group."""
        return Screenshot.objects.filter(
            id__gt=self.id, **kwargs).order_by('id')[:1]

    def not_me(self, screenshots):
        """
        Try to get the first screenshot from a (possibly empty) list,
        but only if it's different from self.
        """
        if screenshots and screenshots[0] != self:
            return screenshots[0]

    def arrows(self, **kwargs):
        """
        Show links for related screenshots.
        """
        first = self.not_me(self.get_first(**kwargs))
        previous = self.not_me(self.get_previous(**kwargs))
        next = self.not_me(self.get_next(**kwargs))
        last = self.not_me(self.get_last(**kwargs))
        return mark_safe('\n'.join((
            self.arrow(first, 'first', capfirst(_("first"))),
            self.arrow(previous, 'previous', capfirst(_("previous"))),
            self.arrow(next, 'next', capfirst(_("next"))),
            self.arrow(last, 'last', capfirst(_("last"))),
            )))

    def navigation(self, title, min_count=2, already=0, **kwargs):
        """
        Show arrows to go to first/previous/next/last screenshot.
        """
        total = Screenshot.objects.filter(**kwargs).count()
        if total < min_count or total == already:
            return ''
        index = Screenshot.objects.filter(id__lt=self.id, **kwargs).count() + 1
        index = _(u"%(index)d out of %(total)d") % locals()
        arrows = self.arrows(**kwargs)
        return mark_safe('\n'.join((
            u'<tr>',
            u'<th>%s</th>' % arrows,
            u'<td>%s %s</td>' % (index, title),
            u'</tr>',
            )))

    def website_navigation(self):
        """
        Navigation links to other screenshots of the same website.
        """
        return self.navigation(
            _("screenshots"),
            min_count=1,
            website=self.website)

    def browser_navigation(self):
        """
        Navigation links for screenshots of the same browser.
        """
        browser_group = self.browser.browser_group
        return self.navigation(
            unicode(_("with %(browser)s")) % {'browser': browser_group.name},
            already=self.website.screenshot_set.count(),
            website=self.website,
            browser__browser_group=browser_group)

    def platform_navigation(self):
        """
        Navigation links for screenshots of the same platform.
        """
        platform = self.factory.operating_system.platform
        return self.navigation(
            unicode(_("on %(platform)s")) % {'platform': platform.name},
            already=self.website.screenshot_set.count(),
            website=self.website,
            factory__operating_system__platform=platform)

    def png_filename(self):
        """
        Get user-friendly screenshot filename for use within ZIP files.
        """
        return u' '.join((
            self.uploaded.strftime('%y%m%d-%H%M%S'),
            self.browser.__unicode__(),
            self.factory.operating_system.__unicode__(show_codename=False),
            self.hashkey,
            )).lower().replace(' ', '-') + '.png'


class ProblemReport(models.Model):
    """
    User feedback about problems with a screenshot, e.g.
    This is not the requested browser version.
    """
    screenshot = models.ForeignKey(Screenshot,
        verbose_name=_("screenshot"))
    code = models.IntegerField(
        _("error code"))
    message = models.CharField(
        _("error message"), max_length=200)
    reported = models.DateTimeField(
        _("reported"), auto_now_add=True)
    ip = models.IPAddressField(
        _("IP address"))

    class Meta:
        verbose_name = _("problem report")
        verbose_name_plural = _("problem reports")
        ordering = ('-reported', )

    def __unicode__(self):
        return unicode(self.get_message_explicit())

    def get_absolute_url(self):
        """Get URL for problem screenshot."""
        return self.screenshot.get_absolute_url()

    def get_message(self):
        """
        Get generic problem message, e.g.
        "This is not the requested browser."
        """
        if self.code in PROBLEM_CHOICES:
            return PROBLEM_CHOICES[self.code]
        else:
            return self.message

    def get_message_explicit(self):
        """
        Get explicit problem message, e.g.
        "This is not Firefox 2.0."
        """
        if self.code in PROBLEM_CHOICES_EXPLICIT:
            message = unicode(PROBLEM_CHOICES_EXPLICIT[self.code])
            if '%(browser)s' in message:
                browser = unicode(self.screenshot.browser)
            if '%(operating_system)s' in message:
                operating_system = unicode(
                    self.screenshot.factory.operating_system)
            if '%(java)s' in message:
                java = unicode(self.screenshot.browser.java)
            if '%(javascript)s' in message:
                javascript = unicode(self.screenshot.browser.javascript)
            if '%(flash)s' in message:
                flash = unicode(self.screenshot.browser.flash)
            return message % locals()
        else:
            return self.get_message()
