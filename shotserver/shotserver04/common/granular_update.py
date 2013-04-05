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
Update only selected fields of a model.

The problem with model.save() is that it also overwrites all other
fields with possibly stale data.
"""

__revision__ = "$Rev: 2954 $"
__date__ = "$Date: 2008-08-13 19:02:20 -0300 (qua, 13 ago 2008) $"
__author__ = "$Author: johann $"

from django.db import connection, models, transaction


def update_fields(self, **kwargs):
    """
    Update selected model fields in the database, but leave the other
    fields alone. Use this rather than model.save() for performance
    and data consistency.

    You can use this as a function or add it as a method to your models:
    import granular_update
    class Example(models.Model):
        name = models.CharField(max_length=20)
        number = models.IntegerField()
        update_fields = granular_update.update_fields
    """
    sql = ['UPDATE', connection.ops.quote_name(self._meta.db_table), 'SET']
    values = []
    for field_name in kwargs:
        setattr(self, field_name, kwargs[field_name])
        field = self._meta.get_field(field_name)
        value = kwargs[field_name]
        if isinstance(value, models.Model):
            value = value.id
        else:
            value = field.get_db_prep_save(value)
        sql.extend((connection.ops.quote_name(field.column), '=', '%s', ','))
        values.append(value)
    sql.pop(-1) # Remove the last comma
    sql.extend(['WHERE', 'id', '=', '%s'])
    values.append(self.id)
    sql = ' '.join(sql)
    connection.cursor().execute(sql, values)
    transaction.commit_unless_managed()


update_fields.alters_data = True
