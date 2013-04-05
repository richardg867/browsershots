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
XML-RPC interface for nonces app.
"""

__revision__ = "$Rev: 2914 $"
__date__ = "$Date: 2008-06-30 23:00:58 -0300 (seg, 30 jun 2008) $"
__author__ = "$Author: johann $"

from xmlrpclib import Fault
from django.contrib.auth.models import User
from shotserver04.xmlrpc import signature, factory_xmlrpc
from shotserver04.nonces import crypto
from shotserver04.nonces.models import Nonce
from datetime import datetime, timedelta


@factory_xmlrpc
@signature(dict, str)
def challenge(http_request, factory):
    """
    Generate a nonce for authentication.

    Arguments
    ~~~~~~~~~
    * factory_name string (lowercase, normally from hostname)

    Return value
    ~~~~~~~~~~~~
    * challenge dict

    The return value is a dict with the following keys:

    * algorithm string (sha1 or md5)
    * salt string (few random characters)
    * nonce string (random lowercase hexadecimal, length 32)

    See nonces.verify for how to encrypt your password with the nonce.
    """
    hashkey = crypto.random_md5()
    ip = http_request.META['REMOTE_ADDR']
    Nonce.objects.create(factory=factory, hashkey=hashkey, ip=ip)
    password = factory.admin.password
    if password.count('$'):
        algorithm, salt, hashed = password.split('$')
    else:
        algorithm, salt, hashed = 'md5', '', password
    return {
        'algorithm': algorithm,
        'salt': salt,
        'nonce': hashkey,
        }


@factory_xmlrpc
@signature(bool, str, str)
def verify(http_request, factory, encrypted_password):
    """
    Test authentication with an encrypted password.

    Arguments
    ~~~~~~~~~
    * factory_name string (lowercase, normally from hostname)
    * encrypted_password string (lowercase hexadecimal, length 32)

    Return value
    ~~~~~~~~~~~~
    * success boolean (or XML-RPC fault with error message)

    Password encryption
    ~~~~~~~~~~~~~~~~~~~
    To encrypt the password, you must first generate a nonce and get
    the encryption algorithm and salt (see nonces.challenge). Then you
    can compute the encrypted password like this::

        encrypted_password = md5(sha1(salt + password) + nonce)

    If requested by the challenge, you must use md5 rather than sha1
    for the inner hash. The result of each hash function call must be
    formatted as lowercase hexadecimal. The calls to nonces.challenge
    and nonces.verify must be made from the same IP address.
    """
    ip = http_request.META['REMOTE_ADDR']
    # Get password hash from database
    password = factory.admin.password
    if password.count('$'):
        algo, salt, hashed = password.split('$')
    else:
        algo, salt, hashed = 'md5', '', password
    # Get matching nonces
    nonces = Nonce.objects.filter(factory=factory).extra(
        where=["MD5(%s || hashkey) = %s"],
        params=[hashed, encrypted_password])
    if len(nonces) == 0:
        raise Fault(401, "Password mismatch.")
    if len(nonces) > 1:
        raise Fault(401, "Authentication failed (hash collision).")
    nonce = nonces[0]
    # Check IP address
    if nonce.ip != ip:
        raise Fault(401, "Authentication failed (different IP address).")
    # Check nonce freshness
    if datetime.now() - nonce.created > timedelta(minutes=10):
        nonce.delete()
        raise Fault(408, "Authentication failed (nonce expired).")
    # Success!
    nonce.delete()
    return True


@signature(dict, str)
def challengeUser(http_request, username):
    """
    Generate a nonce for authentication.

    Arguments
    ~~~~~~~~~
    * username string (your user account on the server)

    Return value
    ~~~~~~~~~~~~
    * challenge dict

    The return value is a dict with the following keys:

    * algorithm string (sha1 or md5)
    * salt string (few random characters)
    * nonce string (random lowercase hexadecimal, length 32)

    See nonces.verifyUser for how to encrypt your password with the
    nonce.
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Fault(404, "User not found.")
    hashkey = crypto.random_md5()
    ip = http_request.META['REMOTE_ADDR']
    Nonce.objects.create(email=username, hashkey=hashkey, ip=ip)
    password = user.password
    if password.count('$'):
        algorithm, salt, hashed = password.split('$')
    else:
        algorithm, salt, hashed = 'md5', '', password
    return {
        'algorithm': algorithm,
        'salt': salt,
        'nonce': hashkey,
        }


@signature(bool, str, str)
def verifyUser(http_request, username, encrypted_password):
    """
    Test authentication with an encrypted password.

    Arguments
    ~~~~~~~~~
    * username string (your user account on the server)
    * encrypted_password string (lowercase hexadecimal, length 32)

    Return value
    ~~~~~~~~~~~~
    * success boolean (or XML-RPC fault with error message)

    Password encryption
    ~~~~~~~~~~~~~~~~~~~
    To encrypt the password, you must first generate a nonce and get
    the encryption algorithm and salt (see nonces.challengeUser). Then
    you can compute the encrypted password like this::

        encrypted_password = md5(sha1(salt + password) + nonce)

    If requested by the challenge, you must use md5 rather than sha1
    for the inner hash. The result of each hash function call must be
    formatted as lowercase hexadecimal. The calls to
    nonces.challengeUser and nonces.verifyUser must be made from the
    same IP address.
    """
    if isinstance(username, User):
        user = username
        username = user.username
    else:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Fault(404, "User not found.")
    ip = http_request.META['REMOTE_ADDR']
    # Get password hash from database
    password = user.password
    if password.count('$'):
        algo, salt, hashed = password.split('$')
    else:
        algo, salt, hashed = 'md5', '', password
    # Get matching nonces
    nonces = Nonce.objects.filter(email=username).extra(
        where=["MD5(%s || hashkey) = %s"],
        params=[hashed, encrypted_password])
    if len(nonces) == 0:
        raise Fault(401, "Password mismatch.")
    if len(nonces) > 1:
        raise Fault(401, "Authentication failed (hash collision).")
    nonce = nonces[0]
    # Check IP address
    if nonce.ip != ip:
        raise Fault(401, "Authentication failed (different IP address).")
    # Check nonce freshness
    if datetime.now() - nonce.created > timedelta(minutes=10):
        nonce.delete()
        raise Fault(408, "Authentication failed (nonce expired).")
    # Success!
    nonce.delete()
    return True
