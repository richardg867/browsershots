#!/bin/sh
# clone_user.sh - Copy home directory and clean it up
# Copyright (C) 2007 Johann C. Rocholl <johann@rocholl.net>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

if [ -z "$1" ]; then echo usage: clone_user.sh user1 user2; exit 1; fi
if [ -z "$2" ]; then echo usage: clone_user.sh user1 user2; exit 1; fi
if [ ! -d "/home/$1" ]; then echo /home/$1 does not exist; exit 1; fi
if [ -d "/home/$2" ]; then echo /home/$2 already exists; exit 1; fi
echo copying home directory from $1 to $2
cp -a /home/$1 /home/$2
find /home/$2 -name "*.pyc" | xargs -r rm
find /home/$2 -name "screenlog.*" | xargs -r rm
find /home/$2 -name "pg????.ppm" | xargs -r rm
rm -f /home/$2/.mozilla/firefox/*/history.dat
rm -f /home/$2/.mozilla/firefox/*/secmod.db
rm -f /home/$2/.mozilla/firefox/*/lock
rm -rf /home/$2/.opera/images
rm -rf /home/$2/.kde/socket-*
rm -f /home/$2/.kde/cache-*
rm -f /home/$2/.kde/tmp-*
rm -f /home/$2/.DCOPserver*
rm -f /home/$2/.vnc/*.log
rm -f /home/$2/.vnc/*.pid
sed -i s/$1/$2/g /home/$2/.opera/opera6.ini
sed -i s/$1/$2/g /home/$2/.opera/mail/*.ini
sed -i s/$1/$2/g /home/$2/.emacs-places
chown -R $2:$2 /home/$2
