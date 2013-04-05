# -*- coding: utf-8 -*-
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
Django configuration for the ShotServer.
"""

__revision__ = "$Rev: 3077 $"
__date__ = "$Date: 2008-09-11 17:40:36 -0300 (qui, 11 set 2008) $"
__author__ = "$Author: johann $"

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Sender address for automated messages from Django.
DEFAULT_FROM_EMAIL = 'noreply@example.com'

# Send error 500 messages to these email addresses,
# but only if DEBUG is False.
ADMINS = (
    ('Your Name', 'you@example.com'),
    ('Other Name', 'other@example.com'),
)

DATABASE_ENGINE = 'postgresql' # 'postgresql', 'mysql', 'sqlite3', 'ado_mssql'.
DATABASE_NAME = 'shotserver04' # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost.
DATABASE_PORT = ''             # Set to empty string for default.

CACHE_BACKEND = 'locmem:///'
# CACHE_BACKEND = "memcached://127.0.0.1:11211/"
# CACHE_BACKEND = 'file:///var/cache/shotserver04'

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Don't append slash to URLs because of
# http://browsershots.org/http://www.example.com/no-slash
APPEND_SLASH = False

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    #('ar', u'العربية'),
    #('bg', u'Български'),
    ('cs', u'Česky'),
    ('da', u'Dansk'),
    ('de', u'Deutsch'),
    #('et', u'Eesti'),
    ('en-gb', u'English (UK)'),
    ('en', u'English (US)'),
    ('el', u'ελληνικά'),
    ('es', u'Español'),
    #('eu', u'Euskara'),
    ('fr', u'Français'),
    ('it', u'Italiano'),
    #('ja', u'日本語'),
    ('ko', u'한국어'),
    #('lt', u'Lietuviškai'),
    #('hu', u'Magyar'),
    ('nb', u'Norsk (Bokmål)'),
    ('nl', u'Nederlands'),
    ('fa', u'فارسی'),
    ('pl', u'Polski'),
    ('pt', u'Português'),
    ('pt-br', u'Português (Brasil)'),
    ('ro', u'Română'),
    ('ru', u'Русский'),
    #('fi', u'Suomi'),
    ('sv', u'Svenska'),
    #('tr', u'Türkçe'),
    #('zh-tw', u'中文'),
    )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

PNG_ROOT = '/var/www/v04.browsershots.org/png/'
PNG_URL = 'http://127.0.0.1:8000/png/'
API_URL = 'http://127.0.0.1:8000/'
ZIP_URL = 'http://127.0.0.1:8000/'

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    #'django.core.context_processors.request',
    'shotserver04.common.context_processors.http_request',
    )

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Deny requests unless Content-type header starts with one of these.
SUPPORTED_CONTENT_TYPES = """
text/
application/xml
application/xhtml+xml
application/rss+xml
application/rdf+xml
application/atom+xml
""".lower().strip().splitlines()

# Profanity filter.
PROFANITIES_LIST = """
asshole cunt fuck shit porn p0rn pr0n boys girls chicks babe cock
bukkake sex xxx nude nudist naked bitcafe stile omglol bitch adult
pussy boob handsfree disturb
""".lower().split()

# Tolerate a small number of profane words.
PROFANITIES_ALLOWED = 1

# Ignore requests for shock sites.
SHOCKSITE_KEYWORDS_LIST = """
gnaa measure omglol gook nigger niger nigga offensive penisbird
rolloffle rucas tubgirl lemonparty goatse dikky timecop faggots
lolichan trogg rlogin: telnet: callto: ed2k: altf4key ctrlkey
delkey movew0w
""".lower().split()

# Tolerate a small number of shocksite keywords.
SHOCKSITE_KEYWORDS_ALLOWED = 3

# Block requests for screenshots of special IP addresses.
DISALLOWED_SERVER_IP_LIST = """
0.0.0.0/8
10.0.0.0/8
14.0.0.0/8
127.0.0.0/8
128.0.0.0/16
169.254.0.0/16
172.16.0.0/12
191.255.0.0/16
192.0.0.0/24
192.0.2.0/24
192.88.99.0/24
192.168.0.0/16
198.18.0.0/15
223.255.255.0/24
224.0.0.0/4
240.0.0.0/4
255.255.255.255
""".splitlines()

# Block requests for screenshots of certain domain names.
DISALLOWED_DOMAIN_LIST = """
myminicity.com
myminicity.fr
myminicity.es
miniville.fr
ville-virtuelle.com
ucash.in
to-6.net
meine-nackte-ex.net
meine-nackte-ex.cc.gd
ex.cc.gd
sexy-lena.com
my-fucking-ex.org
""".splitlines()

# If you set this to False, only registered users can submit requests.
ALLOW_ANONYMOUS_REQUESTS = True

# Usage limits for (anonymous, registered, priority) users.
MAX_WEBSITE_REQUESTS_PER_DAY = (50, 100, 1000)
MAX_DOMAIN_REQUESTS_PER_DAY = (100, 200, 2000)
MAX_USER_REQUESTS_PER_DAY = (200, 300, 5000)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'y7v!*06i+q2e!4zqwr_wnc=#lnm*ew&!1o_z-cki^^*4*ww=16'

# Account number for Google Analytics, e.g. UA-123456-7.
GOOGLE_ANALYTICS_ACCOUNT = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    # 'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'shotserver04.common.middleware.RedirectMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    # 'django.middleware.http.SetRemoteAddrFromForwardedFor',
)

ROOT_URLCONF = 'shotserver04.urls'

# Dynamic path trickery.
import os
SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))

# Find templates in the same folder as settings.py.
TEMPLATE_DIRS = (
    os.path.join(SETTINGS_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'shotserver04.start',
    'shotserver04.accounts',
    'shotserver04.common',
    'shotserver04.platforms',
    'shotserver04.sponsors',
    'shotserver04.factories',
    'shotserver04.features',
    'shotserver04.browsers',
    'shotserver04.websites',
    'shotserver04.requests',
    'shotserver04.screenshots',
    'shotserver04.nonces',
    'shotserver04.xmlrpc',
    'shotserver04.redirect',
    'shotserver04.messages',
)

# Override secret settings from secrets.py,
# if that file exists in the same folder as settings.py.
try:
    from secrets import *
except ImportError:
    pass
if 'EXTRA_APPS' in locals():
    INSTALLED_APPS += EXTRA_APPS
if 'DESEB' in locals() and DESEB:
    import deseb
