#!/usr/bin/env python
# django_dump.py - Dump table data from Django models
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

"""
Dump table data from Django models.
"""

__revision__ = "$Rev: 2236 $"
__date__ = "$Date: 2007-10-24 03:39:00 -0300 (qua, 24 out 2007) $"
__author__ = "$Author: johann $"

import os
import sys
from pprint import pprint


def sql(instance):
    from django.db import connection
    field_names = [connection.ops.quote_name(f.column)
                   for f in instance._meta.fields]
    db_values = []
    for f in instance._meta.fields:
        value = f.get_db_prep_save(f.pre_save(instance, True))
        if isinstance(value, basestring):
            value = "'%s'" % value.encode('utf-8').replace('\\', r'\\')
        elif value is None:
            value = 'NULL'
        else:
            value = str(value)
        db_values.append(value)
    return 'INSERT INTO %s (%s) VALUES (%s);' % (
        connection.ops.quote_name(instance._meta.db_table),
        ','.join(field_names),
        ','.join(db_values),
        )


def dump(options, model):
    from django.db import connection
    if options.install:
        module = sys.modules[model.__module__]
        dirname = os.path.dirname(os.path.normpath(module.__file__))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = os.path.join(dirname, 'sql',
                                model._meta.module_name + '.sql')
        outfile = open(filename, 'w')
    elif options.source:
        dirname = os.path.join(options.source, model._meta.app_label, 'sql')
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = os.path.join(dirname, model._meta.module_name + '.sql')
        outfile = open(filename, 'w')
    elif options.output:
        dirname = os.path.join(options.output, model._meta.app_label)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = os.path.join(dirname, model._meta.module_name + '.sql')
        outfile = open(filename, 'w')
    else:
        outfile = sys.stdout
    for instance in model.objects.all().order_by(model._meta.fields[0].column):
        outfile.write(sql(instance) + '\n')
    pk_sql = """SELECT setval('%s_id_seq', (SELECT max("id") FROM %s));""" % (
        model._meta.db_table, connection.ops.quote_name(model._meta.db_table))
    outfile.write(pk_sql + '\n')


def dump_by_name(options, model_name=None):
    from django.db import models
    for app in models.get_apps():
        for model in models.get_models(app):
            if options.all:
                dump(options, model)
            elif model_name in (model.__name__, model._meta.db_table):
                return dump(options, model)


def _main():
    from optparse import OptionParser
    version = '%prog ' + __revision__.strip('$').replace('Rev: ', 'r')
    usage = '%prog [options] <model> ...'
    parser = OptionParser(version=version, usage=usage,
                          description=__doc__.strip())
    parser.add_option('-p', '--project',
                      help="import models from PROJECT")
    parser.add_option('-o', '--output', type='string',
                      help="save SQL in this folder")
    parser.add_option('-s', '--source', type='string',
                      help="save custom SQL in project source")
    parser.add_option('-i', '--install', action='store_true',
                      help="save custom SQL in installed project")
    parser.add_option('-a', '--all', action='store_true',
                      help="dump all models")
    (options, args) = parser.parse_args()
    if options.project:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.project + '.settings'
    if options.all:
        if args:
            parser.error("no extra models allowed with --all")
        dump_by_name(options)
    else:
        if not args:
            parser.error("no models specified")
        for model_name in args:
            dump_by_name(options, model_name)


if __name__ == '__main__':
    _main()
