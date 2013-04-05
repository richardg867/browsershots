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
XML-RPC interface to the ShotServer.
"""

__revision__ = "$Rev: 2450 $"
__date__ = "$Date: 2007-12-09 10:12:11 -0300 (dom, 09 dez 2007) $"
__author__ = "$Author: johann $"

import xmlrpclib
import socket
import time
from md5 import md5
from sha import sha
from shotfactory04.servers import Server


class ProxyTransport(xmlrpclib.Transport):
    """
    Support for HTTP proxy.
    """

    def __init__(self, proxy):
        if hasattr(xmlrpclib.Transport, '__init__'):
            xmlrpclib.Transport.__init__(self)
        self.proxy = proxy

    def make_connection(self, host):
        """Make a connection through the proxy."""
        self.realhost = host
        import httplib
        return httplib.HTTP(self.proxy)

    def send_request(self, connection, handler, request_body):
        """Send a request through the proxy."""
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))

    def send_host(self, connection, host):
        """Send the stored real host as a HTTP header."""
        connection.putheader('Host', self.realhost)


class XMLRPCServer(Server):
    """
    XML-RPC interface to the ShotServer.
    """

    def __init__(self, options):
        Server.__init__(self, options)
        self.factory = options.factory
        self.server_url = options.server.rstrip('/')
        self.xmlrpc_url = self.server_url + '/xmlrpc/'
        self.password = options.password

        socket.setdefaulttimeout(180.0)
        if options.proxy:
            transport = ProxyTransport(options.proxy)
        else:
            transport = xmlrpclib.Transport()
        transport.user_agent = self.get_user_agent()
        self.server = xmlrpclib.Server(self.xmlrpc_url, transport)
        challenge = self.server.nonces.challenge(self.factory)
        encrypted = self.encrypt_password(challenge)
        self.server.nonces.verify(self.factory, encrypted)

    def encrypt_password(self, challenge):
        """
        Encrypt a password for transmission.
        """
        if challenge['algorithm'] == 'md5':
            inner = md5(challenge['salt'] + self.password).hexdigest()
        elif challenge['algorithm'] == 'sha1':
            inner = sha(challenge['salt'] + self.password).hexdigest()
        else:
            raise NotImplementedError(
                "Password encryption algorithm '%s' not implemented." %
                challenge['algorithm'])
        return md5(inner + challenge['nonce']).hexdigest()

    def get_request_url(self, config):
        """
        Get the URL for this screenshot request.
        """
        challenge = self.server.nonces.challenge(self.factory)
        encrypted = self.encrypt_password(challenge)
        return '/'.join((self.server_url, 'redirect',
            self.factory, encrypted, str(config['request']), ''))

    def upload_png(self, config, pngfilename):
        """
        Upload PNG file to server.
        """
        binary_file = file(pngfilename, 'rb')
        binary_data = binary_file.read()
        binary = xmlrpclib.Binary(binary_data)
        binary_file.close()

        challenge = self.server.nonces.challenge(self.factory)
        encrypted = self.encrypt_password(challenge)
        upload_started = time.time()
        self.server.screenshots.upload(
            self.factory, encrypted, int(config['request']), binary)
        seconds = time.time() - upload_started
        bytes = len(binary_data) * 8 / 6 # base64 encoding
        print "Uploaded %d bytes in %.2f seconds (%.2f kbps)." % (
            bytes, seconds, 8 * bytes / seconds / 1000.0)
        return bytes

    def debug_factory_features(self):
        """
        Print the SQL WHERE clause for a given factory, with linebreaks.
        """
        features = self.server.factories.features(self.factory)
        start = 0
        nested = 0
        for index in range(len(features)):
            if features[index] == '(':
                nested += 1
                if nested <= 4 and index > 0:
                    print features[start:index].strip()
                    start = index
            elif features[index] == ')':
                nested -= 1
                if nested == 0 and features[index - 1] == ')':
                    print features[start:index].strip()
                    start = index
        rest = features[start:].strip()
        if rest:
            print rest

    def poll(self):
        """
        Get the next screenshot request from the server.
        """
        challenge = self.server.nonces.challenge(self.factory)
        encrypted = self.encrypt_password(challenge)
        poll_start = time.time()
        try:
            config = self.server.requests.poll(self.factory, encrypted)
        finally:
            poll_latency = time.time() - poll_start
            print 'server poll latency: %.2f seconds' % poll_latency
        return config
