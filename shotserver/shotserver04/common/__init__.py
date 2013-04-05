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
Common utilities.
"""

__revision__ = "$Rev: 2685 $"
__date__ = "$Date: 2008-02-10 00:41:27 -0300 (dom, 10 fev 2008) $"
__author__ = "$Author: johann $"

import sys
import xmlrpclib
import psycopg
from django.db import connection, transaction
from django.template import RequestContext
from django.shortcuts import render_to_response
from datetime import datetime, timedelta

LOCK_TIMEOUT = 5 # minutes before request lock expires
POLL_TIMEOUT = 10 # minutes since last poll for active factory
ERROR_TIMEOUT = 10 # minutes blocked after browser error

MAX_ATTEMPTS = 10 # for @serializable


def lock_timeout():
    """Request lock is expired if it was created before this datetime."""
    return datetime.now() - timedelta(minutes=LOCK_TIMEOUT)


def last_poll_timeout():
    """Factory is inactive if last poll was before this datetime."""
    return datetime.now() - timedelta(minutes=POLL_TIMEOUT)


def last_error_timeout():
    """Browser is blocked if last error is more recent than this."""
    return datetime.now() - timedelta(minutes=ERROR_TIMEOUT)


def int_or_none(value):
    """Convert string to int, if possible."""
    if value.isdigit():
        return int(value)


def get_or_fault(model, *args, **kwargs):
    """
    Get the specified object, or raise xmlrpclib.Fault with a detailed
    error message. Similar to django.shortcuts.get_object_or_404.
    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        filters = u' and '.join(
            [u'%s=%s' % (key, kwargs[key]) for key in kwargs])
        raise xmlrpclib.Fault(404, u'%s not found with %s.' % (
            model.__name__, filters))


def serializable(func):
    """
    Decorator that changes the PostgreSQL transaction isolation level
    to serializable. Use this for minimal functions that need to be
    isolated from concurrent access. The operation will be attempted
    again if a serialization error occurs (up to MAX_ATTEMPTS times).
    """

    @transaction.commit_manually
    def wrapper(*args, **kwargs):
        """
        Set the transaction isolation level to serializable, then run
        the wrapped function. Automatically retry on serialize error.
        """
        if transaction.is_dirty():
            transaction.commit()
        else:
            transaction.rollback()
        cursor = connection.cursor()
        for attempt in range(1, MAX_ATTEMPTS + 1):
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            try:
                result = func(*args, **kwargs)
                transaction.commit()
                return result
            except psycopg.DatabaseError, error:
                transaction.rollback()
                serialize_error = "serialize access" in str(error).lower()
                if attempt == MAX_ATTEMPTS or not serialize_error:
                    raise
                # sys.stdout.write('!') # For test_overload.py
            except:
                transaction.rollback()
                raise

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def result_page(http_request, result_class, result_title, result_message,
                *extra_messages):
    """Render result page with title and message."""
    return render_to_response('result.html', locals(),
        context_instance=RequestContext(http_request))


def error_page(http_request, result_title, result_message, *extra_messages):
    """Render error page with title and message."""
    return result_page(http_request, 'error',
                       result_title, result_message,
                       *extra_messages)


def success_page(http_request, result_title, result_message, *extra_messages):
    """Render success page with title and message."""
    return result_page(http_request, 'success',
                       result_title, result_message,
                       *extra_messages)
