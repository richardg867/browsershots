#!/usr/bin/env python
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

# Installation:
# ln -s shotserver04_munin.py /etc/munin/plugins/shotserver04_rates
# ln -s shotserver04_munin.py /etc/munin/plugins/shotserver04_counts


"""
Create graphs of object rates and counts with Munin.
"""

__revision__ = "$Rev: 2959 $"
__date__ = "$Date: 2008-08-14 05:05:48 -0300 (qui, 14 ago 2008) $"
__author__ = "$Author: johann $"

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'shotserver04.settings'
import sys
from django.db import models

DATASET_TYPES = {'rates': 'DERIVE', 'counts': 'GAUGE'}


def has_id(model):
    return model._meta.fields[0].name == 'id'


def config(dataset):
    print 'graph_title ShotServer -', dataset.title()
    print 'graph_args --base 1000'
    print 'graph_category shotserver'
    if dataset == 'rates':
        print 'graph_period minute'
        print 'graph_vlabel /${graph_period}'
    elif dataset == 'counts':
        print 'graph_vlabel Totals'
    order = [model._meta.db_table
             for model in models.get_models()
             if dataset != 'rates' or has_id(model)]
    order.sort()
    print 'graph_order', ' '.join(order)
    for model in models.get_models():
        if dataset == 'rates' and not has_id(model):
            continue
        key = model._meta.db_table
        print key + '.label', model._meta.db_table
        print key + '.type', DATASET_TYPES[dataset]
        print key + '.min 0'
        # print 'max 5000'
        print key + '.draw LINE2'
        print key + '.info',
        if dataset == 'rates':
            print u'New %s per ${graph_period}' % (
                model._meta.verbose_name_plural)
        elif dataset == 'counts':
            print u'Total %s' % model._meta.verbose_name_plural


def values(dataset):
    for model in models.get_models():
        if dataset == 'rates' and not has_id(model):
            continue
        print model._meta.db_table + '.value',
        if dataset == 'counts':
            print model.objects.count()
        elif dataset == 'rates':
            objects = model.objects.order_by('-id')[:1]
            if len(objects):
                print objects[0].id
            else:
                print 0


if __name__ == '__main__':
    dataset = sys.argv[0].split('_')[-1]
    assert dataset in DATASET_TYPES
    if len(sys.argv) == 2 and sys.argv[1] =='config':
        config(dataset)
    else:
        values(dataset)
