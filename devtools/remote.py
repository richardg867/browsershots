#!/usr/bin/env python

"""
Test remote control for shotserver04.
Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
Free software, licensed under the terms of the GNU GPL.
"""

__revision__ = "$Rev: 2804 $"
__date__ = "$Date: 2008-05-07 21:26:26 -0700 (Wed, 07 May 2008) $"
__author__ = "$Author: johann $"

import sys
import os
import xmlrpclib
import time
from md5 import md5
from sha import sha

DEFAULT_SERVER_URL = 'api.browsershots.org/xmlrpc/'
DEFAULT_PASSWORD_FILE = '.passwd'


def encrypt_password(challenge, password):
    if challenge['algorithm'] == 'md5':
        inner = md5(challenge['salt'] + password).hexdigest()
    elif challenge['algorithm'] == 'sha1':
        inner = sha(challenge['salt'] + password).hexdigest()
    else:
        raise NotImplementedError(
            "Password encryption algorithm '%s' not implemented." %
            challenge['algorithm'])
    return md5(inner + challenge['nonce']).hexdigest()


def list_active_browsers(server, options):
    for browser in server.browsers.active():
        print browser


def submit_screenshot_requests(server, options, browsers):
    challenge = server.nonces.challengeUser(options.username)
    encrypted = encrypt_password(challenge, options.password)
    # print challenge, encrypted
    print server.requests.submit(options.username, encrypted,
                                 options.submit, browsers)


def get_request_status(server, options):
    for browser in server.requests.status(options.status):
        print browser


def _main():
    from optparse import OptionParser
    revision = __revision__.strip('$').replace('Rev: ', 'r')
    parser = OptionParser(version='%prog ' + revision)
    parser.add_option('--active', action='store_true',
                      help="list active browsers")
    parser.add_option('--submit', metavar='<url>', type='string',
                      help="submit screenshot requests")
    parser.add_option('--status', metavar='<id>', type='int',
                      help="show progress of request group")
    parser.add_option('--server', metavar='<url>', default=DEFAULT_SERVER_URL,
                      help="server url (default: %s)" % DEFAULT_SERVER_URL)
    parser.add_option('--username', metavar='<name>',
                      help="your user account on shotserver")
    parser.add_option('--password', metavar='<text>',
                      help="supply password on command line (insecure)")
    parser.add_option('--passfile', metavar='<path>',
                      help="plaintext password file (default: %s)" %
                      DEFAULT_PASSWORD_FILE)
    (options, args) = parser.parse_args()

    if not options.server.startswith('http://'):
        options.server = 'http://' + options.server

    if options.submit and options.username is None:
        print 'Username: ',
        options.username = sys.stdin.readline()

    if options.passfile and options.password:
        parser.error("can't use both --password and --passfile")
    if (options.passfile is None and options.password is None
        and os.path.exists(DEFAULT_PASSWORD_FILE)):
        options.passfile = DEFAULT_PASSWORD_FILE
    if options.passfile:
        if platform.system() not in 'Microsoft Windows':
            if os.stat(options.passfile).st_mode & stat.S_IROTH:
                parser.error("your password file is world-readable")
        options.password = file(options.passfile).readline().strip()
    if options.submit and options.password is None:
        from getpass import getpass
        options.password = getpass('Password: ')

    if not (options.active or options.submit or options.status):
        parser.error("Please select a function on the command line.")

    server = xmlrpclib.Server(options.server)
    if options.active:
        list_active_browsers(server, options)
    if options.submit:
        if not args:
            parser.error("Please select browsers on the command line.")
        submit_screenshot_requests(server, options, args)
    if options.status:
        get_request_status(server, options)


if __name__ == '__main__':
    _main()
