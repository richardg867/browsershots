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
XML-RPC interface.
"""

__revision__ = "$Rev: 2688 $"
__date__ = "$Date: 2008-02-10 18:57:23 -0300 (dom, 10 fev 2008) $"
__author__ = "$Author: johann $"

import xmlrpclib
from datetime import datetime
from shotserver04.common import get_or_fault


def signature(*types):
    """
    Add a signature to a function or method.
    """

    def wrapper(func):
        """Save the signature."""
        func._signature = types
        return func

    return wrapper


def factory_xmlrpc(func):
    """
    Convenience wrapper for screenshot factory XML-RPC methods.
    Functions in app.xmlrpc modules that have a signature will be
    auto-registered for the XML-RPC interface.
    """

    def wrapper(http_request, factory_name, *args, **kwargs):
        """
        Get factory by name and log errors in the database.
        """
        from shotserver04.factories.models import Factory
        # Shortcut for nested calls, e.g. nonces.verify
        if isinstance(factory_name, Factory):
            factory = factory_name
            return func(http_request, factory, *args, **kwargs)
        # Get factory by name and run wrapped function
        factory = get_or_fault(Factory, name=factory_name)
        try:
            return func(http_request, factory, *args, **kwargs)
        except xmlrpclib.Fault, fault:
            fault_class = fault.faultCode / 100
            if fault_class not in (2, 5): # Success or server error
                from shotserver04.messages.models import FactoryError
                # Save error message in the database
                FactoryError.objects.create(factory=factory,
                    code=fault.faultCode, message=fault.faultString,
                    request=getattr(fault, 'request', None),
                    hashkey=getattr(fault, 'hashkey', None))
                browser = getattr(fault, 'browser', None)
                if browser is not None:
                    browser.update_fields(last_error=datetime.now())
            raise

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    if hasattr(func, '_signature'):
        wrapper._signature = func._signature
    return wrapper
