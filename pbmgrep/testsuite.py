#!/usr/bin/env python
import os
import commands

for png in os.listdir('testsuite'):
    pipe = [
        'pngtopnm testsuite/%s' % png,
        './ppmfg',
        './pbmgrep 6??_*.pbm',
        ]
    status, output = commands.getstatusoutput(' | '.join(pipe))
    if png.split('.')[0] not in output:
        print png
        print 'status', status
        print output
