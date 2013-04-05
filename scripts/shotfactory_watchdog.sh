#!/bin/sh
# Restart screenshot factories when they die, or after reboot.
#
# Add me to /etc/crontab like this (make sure I'm on the PATH):
# * *   * * *   shotfactory1   shotfactory_watchdog.sh -d :1 -l 1
# * *   * * *   shotfactory2   shotfactory_watchdog.sh -d :2 -l 2
# * *   * * *   shotfactory3   shotfactory_watchdog.sh -d :3 -l 3
#
# All parameters will be passed to the shotfactory.py script.
USER=`whoami`

# Check if screen is already running.
ps -u $USER | grep screen > /dev/null && exit 0

# Send email to administrator, including previous output.
echo shotfactory_watchdog.sh:
echo Restarting shotfactory for $USER.
echo
echo Previous output in screenlog.0:
echo ...
tail -n30 /home/$USER/checkout/shotfactory/screenlog.0

# VNC server requires $USER environment variable.
export USER

# Change directory.
cd /home/$USER/checkout/shotfactory

# Start screen (detached, with logging).
# Set the display (-d) and load limit (-l) to the factory index.
screen -d -m -L python shotfactory.py "$@"
