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
URL input form.
"""

__revision__ = "$Rev: 3077 $"
__date__ = "$Date: 2008-09-11 17:40:36 -0300 (qui, 11 set 2008) $"
__author__ = "$Author: johann $"

import re
import urlparse
import socket
from datetime import datetime
from psycopg import IntegrityError
from django import forms
from django.forms.util import ValidationError
from django.utils.text import capfirst
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf import settings
from shotserver04.websites.utils import \
     split_netloc, unsplit_netloc, http_get, count_profanities, \
     HTTP_TIMEOUT, HTTPError, ConnectError, RedirectError, RequestError, \
     dotted_ip, long_ip, bit_mask, slash_mask
from shotserver04.websites.models import Domain, Website
from shotserver04.websites import normalize_url
from shotserver04.start.forms import robotexclusionrulesparser

SUPPORTED_SCHEMES = ['http', 'https']

scheme_match = re.compile(r'[A-Za-z0-9\.+-]+:').match


class UrlForm(forms.Form):
    """
    URL input form.
    """
    url = forms.CharField(
        max_length=Website._meta.get_field('url').max_length,
        label=_("Enter your web address here:"))

    def clean_url(self):
        """
        Clean URL and attempt HTTP GET request.
        """
        self.cleaned_data['url'] = normalize_url(self.cleaned_data['url'])
        self.add_scheme()
        self.split_url()
        self.punycode_url()
        self.check_server_disallowed()
        self.add_slash()
        self.robots_txt()
        response = self.http_get()
        self.cleaned_data['headers'] = response[0]
        self.cleaned_data['content'] = response[1]
        self.check_content_type()
        self.check_content()
        self.cleaned_data['domain'] = self.get_or_create_domain()
        self.cleaned_data['website'] = self.get_or_create_website()
        return self.cleaned_data['url']

    def add_scheme(self):
        """
        Add http:// if it's missing.
        """
        url = self.cleaned_data['url']
        if not scheme_match(url):
            self.cleaned_data['url'] = 'http://' + url.lstrip('/')

    def split_url(self):
        """
        Parse URL into components.
        """
        url = self.cleaned_data['url']
        self.url_parts = list(urlparse.urlsplit(url, 'http'))
        # print self.url_parts
        if self.url_parts[0] not in SUPPORTED_SCHEMES:
            raise ValidationError(
                unicode(_("URL scheme %(scheme)s is not supported.") %
                        {'scheme': self.url_parts[0]}))
        self.netloc_parts = split_netloc(self.url_parts[1])
        if not self.url_parts[1] or not self.netloc_parts[2]:
            raise ValidationError(
                unicode(_("Malformed URL (server name not specified).")))
        if '%20' in self.netloc_parts[2]:
            raise ValidationError(
                unicode(_("Malformed URL (spaces in server name).")))
        # print self.netloc_parts

    def punycode_url(self):
        """
        Convert url to punycode if necessary.
        """
        hostname = original = self.netloc_parts[2]
        hostname = hostname.strip('.')
        while '..' in hostname:
            hostname = hostname.replace('..', '.')
        punycode = hostname.encode('idna').decode('ascii')
        if punycode == original:
            return
        self.netloc_parts[2] = punycode
        self.url_parts[1] = unsplit_netloc(self.netloc_parts)
        self.cleaned_data['url'] = urlparse.urlunsplit(self.url_parts)
        # print self.cleaned_data['url']

    def check_server_disallowed(self):
        """
        Check if server domain name or IP is disallowed in settings.py.
        """
        hostname = self.netloc_parts[2].lower()
        if (hasattr(settings, 'DISALLOWED_DOMAIN_LIST') and
            settings.DISALLOWED_DOMAIN_LIST):
            for domain in settings.DISALLOWED_DOMAIN_LIST:
                if hostname == domain or hostname.endswith('.' + domain):
                    raise ValidationError(unicode(
                        _("Domain name %(domain)s is disallowed.") % locals()))
        try:
            ip = socket.gethostbyname(hostname)
        except socket.error:
            raise ValidationError(unicode(
                _("Could not resolve IP address for %(hostname)s.") %
                locals()))
        if (not hasattr(settings, 'DISALLOWED_SERVER_IP_LIST') or
            not settings.DISALLOWED_SERVER_IP_LIST):
            return
        server = long_ip(ip)
        # print 'server', server, dotted_ip(server), ip
        for disallowed in settings.DISALLOWED_SERVER_IP_LIST:
            disallowed = disallowed.strip()
            if disallowed == '' or disallowed.startswith('#'):
                continue
            mask = bit_mask(32)
            if '/' in disallowed:
                disallowed, bits = disallowed.split('/', 1)
                mask = slash_mask(int(bits))
            identifier = long_ip(disallowed) & mask
            masked = server & mask
            if masked == identifier:
                raise ValidationError(unicode(
                    _("Server IP address %(ip)s is disallowed.") % locals()))

    def add_slash(self):
        """
        Add slash after hostname if it's missing.
        """
        if not self.url_parts[2]: # path
            self.url_parts[2] = '/'
            self.cleaned_data['url'] = urlparse.urlunsplit(self.url_parts)

    def robots_txt(self):
        """
        Check if automatic screenshots are allowed by robots.txt
        for the requested URL on the remote server.
        """
        robots_txt_url = ''.join((
                self.url_parts[0], '://', self.url_parts[1], '/robots.txt'))
        robots_txt_link = '<a href="%s">%s/robots.txt</a>' % (
            robots_txt_url, self.url_parts[1])
        # print robots_txt_url
        parser = robotexclusionrulesparser.RobotExclusionRulesParser()
        parser.user_agent = 'Browsershots'
        socket.setdefaulttimeout(HTTP_TIMEOUT)
        try:
            parser.fetch(robots_txt_url)
        except EOFError:
            return
        except (IOError, socket.error, UnicodeError), error:
            raise ValidationError(mark_safe(u' '.join((
                _("Could not read %(robots_txt_link)s.") % locals(),
                human_error(error)))))
        if not parser.is_allowed('Browsershots', self.cleaned_data['url']):
            faq = u'<a href="%s/%s">FAQ</a>' % (
                'http://trac.browsershots.org/wiki',
                'FrequentlyAskedQuestions#Blockedbyrobots.txt')
            raise ValidationError(mark_safe(u' '.join((
_("Browsershots was blocked by %(robots_txt_link)s.") % locals(),
_("Please read the %(faq)s.") % locals(),
))))

    def http_get(self):
        """
        Load headers and content from remote HTTP server.
        """
        try:
            return http_get(self.cleaned_data['url'])
        except HTTPError, error:
            if isinstance(error, ConnectError):
                text = _("Could not connect to %(hostname)s.")
            elif isinstance(error, RequestError):
                text = _("Could not send HTTP request to %(hostname)s.")
            elif isinstance(error, RedirectError):
                if not error.location:
                    text = u' '.join((
unicode(_("The server at %(hostname)s sent a HTTP redirect.")),
unicode(_("The response did not contain a Location header."))))
                else:
                    self.data._mutable = True
                    self.data['url'] = error.location
                    self.data._mutable = False
                    text = u' '.join((
unicode(_("The server at %(hostname)s sent a HTTP redirect.")),
unicode(_("Your web address has been updated.")),
unicode(_("Please try again."))))
            else:
                text = _("Could not get page content from %(hostname)s.")
            text %= {'hostname': error.hostname}
            error = human_error(error)
            raise ValidationError(' '.join((text, error)).strip())

    def check_content_type(self):
        """
        Check that the content type is supported.
        """
        headers = self.cleaned_data['headers']
        content_type = headers.get('content-type', '').strip()
        if not content_type:
            raise ValidationError(
unicode(_("The server did not send a content type header.")))
        self.cleaned_data['content-type'] = content_type
        for prefix in settings.SUPPORTED_CONTENT_TYPES:
            if content_type.lower().startswith(prefix):
                break
        else:
            raise ValidationError(' '.join((
unicode(_("Unsupported content type: %s.")) % content_type,
unicode(_("This service is for HTML or XHTML content.")))))

    def check_content(self):
        """
        Check URL and page content for profanities or shock sites.
        """
        url_content = ' '.join(
            (self.cleaned_data['url'], self.cleaned_data['content']))
        self.cleaned_data['profanities'] = \
            count_profanities(settings.PROFANITIES_LIST, url_content)
        self.cleaned_data['shocksite_keywords'] = \
            count_profanities(settings.SHOCKSITE_KEYWORDS_LIST, url_content)

    def get_or_create_domain(self):
        """
        Get or create domain entry in database.
        """
        domain_name = self.netloc_parts[2] # hostname
        if domain_name.startswith('www.'):
            domain_name = domain_name[4:]
        transaction.commit() # Because we may need to call rollback below.
        try:
            domain, created = Domain.objects.get_or_create(name=domain_name)
        except IntegrityError, error:
            if 'duplicate key' in str(error):
                transaction.rollback()
                domain = Domain.objects.get(name=domain_name)
            else:
                raise
        return domain

    def get_or_create_website(self):
        """
        Get or create website entry in database.
        """
        defaults = {}
        defaults['domain'] = self.cleaned_data['domain']
        # defaults['content'] = self.cleaned_data['content']
        defaults['profanities'] = self.cleaned_data['profanities']
        transaction.commit() # Because we may need to call rollback below.
        try:
            website, created = Website.objects.get_or_create(
                url=self.cleaned_data['url'], defaults=defaults)
        except IntegrityError, error:
            if 'duplicate key' in str(error):
                transaction.rollback()
                website = Website.objects.get(url=self.cleaned_data['url'])
                created = False
            elif 'websites_website_url_check' in str(error):
                transaction.rollback()
                raise ValidationError(
                    unicode(_("Malformed URL (database integrity error).")))
            else:
                raise
        # Update content cache
        if not created:
            website.update_fields(
                profanities=self.cleaned_data['profanities'],
                fetched=datetime.now())
        return website


def human_error(error):
    """
    Human-readable error formatting.
    """
    if hasattr(error, 'message') and error.message:
        error = error.message
    else:
        error = unicode(error)
    if not error:
        return ''
    if 'timed out' in error.lower():
        return (_("Server failed to respond within %d seconds.") %
                HTTP_TIMEOUT)
    return capfirst(error).rstrip('.') + '.'
