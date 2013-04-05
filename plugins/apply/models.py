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
Apply models.
"""

__revision__ = "$Rev: 2295 $"
__date__ = "$Date: 2007-11-16 16:29:27 -0300 (sex, 16 nov 2007) $"
__author__ = "$Author: johann $"

from django.db import models
from django.contrib.auth.models import User

PHOTO_UPLOAD_PATH = '/var/www/v04.browsershots.org/static/applicants'


class Applicant(models.Model):
    user = models.ForeignKey(User, editable=False)

    degree = models.CharField(max_length=100, blank=True)
    current_job = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)

    cambridge = models.CharField(max_length=100, blank=True,
        help_text="Are you willing to move to Cambridge, MA" +
                  " for the summer of 2008?")
    bay_area = models.CharField(max_length=100, blank=True,
        help_text="Are you willing to move to Mountain View, CA" +
                  " for the beginning of 2009?")

    age = models.IntegerField(blank=True, null=True)
    languages = models.CharField(max_length=100, blank=True)
    family = models.CharField(max_length=100, blank=True,
        help_text="Do you have a husband/wife and/or kids?")

    editor = models.CharField(max_length=100, blank=True,
        help_text="Which is your favorite text editor?")
    python = models.CharField(max_length=200, blank=True,
        help_text="Please tell me about your Python experience.")
    django = models.CharField(max_length=200, blank=True)
    sql = models.CharField(max_length=200, blank=True)
    javascript = models.CharField(max_length=200, blank=True)
    web_design = models.CharField(max_length=200, blank=True)
    unix = models.CharField(max_length=200, blank=True)
    networking = models.CharField(max_length=200, blank=True)
    open_source = models.CharField(max_length=200, blank=True,
        help_text="Have you contributed to any open-source projects?")
    music = models.CharField(max_length=200, blank=True,
        help_text="Do you play a musical instrument?" +
                  " Who's your favorite band/artist?")
    urls = models.TextField(max_length=2000, blank=True,
        help_text="Please list URLs for any or all of the" +
        " above questions, one per line.")

    photo = models.ImageField(blank=True, null=True,
                              width_field=True, height_field=True,
                              upload_to=PHOTO_UPLOAD_PATH)
