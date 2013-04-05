#!/bin/sh
# flight_recorder.sh - Dump table of processes in /var/log/flight
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
#
# This script will dump the output of top(1) to files named like this:
# /var/log/flight/top-HHMM.log (HHMM is the current time)
#
# It is useful to diagnose crashes, performance issues and intrusions.
# To enable this script, add the following line to /etc/crontab:
# * *     * * *   root    flight_recorder.sh
#
# Make sure that line comes after the following in /etc/crontab, and
# that this script (or a symlink to it) is in one of these folders:
# PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

DATE=`date +%H%M`
LOGDIR=/var/log/flight
mkdir -p $LOGDIR
COLUMNS=160 top -cbn1 > $LOGDIR/top-$DATE.log
