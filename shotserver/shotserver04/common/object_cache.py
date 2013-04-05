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
Simple object-level caching for Django.
Primary keys must be integers, and must be called 'id'.
"""

__revision__ = "$Rev: 2809 $"
__date__ = "$Date: 2008-05-10 03:15:14 -0300 (sáb, 10 mai 2008) $"
__author__ = "$Author: johann $"

from django.core.cache import cache

KEY_FORMAT = '%s:%s=%s' # e.g. pizza_pizza:id=1 or pizza_pizza:name=Hawaii
DEBUG = False


def get_object_by_id(model, id):
    """
    Get object by primary key, using the cache.
    """
    cache_key = KEY_FORMAT % (model._meta.db_table, 'id', id)
    object = cache.get(cache_key)
    if object is None:
        if DEBUG: print 'missed', cache_key
        object = model.objects.get(id=id)
        cache.set(cache_key, object)
    else:
        if DEBUG: print 'hit', cache_key
    return object


def is_cached(model, **kwargs):
    """
    Test if an object or index is already cached.
    """
    assert len(kwargs) == 1
    column = kwargs.keys()[0]
    value = kwargs[column]
    cache_key = KEY_FORMAT % (model._meta.db_table, column, value)
    return cache.get(cache_key) is not None


def get(model, **kwargs):
    """
    Get an object by any unique column, using the cache.
    """
    assert len(kwargs) == 1
    column = kwargs.keys()[0]
    value = kwargs[column]
    if column == 'id':
        return get_object_by_id(model, value)
    # Get primary key from cache.
    cache_key = KEY_FORMAT % (model._meta.db_table, column, value)
    id = cache.get(cache_key)
    if id is not None:
        if DEBUG: print 'hit', cache_key
        return get_object_by_id(model, id)
    # Get object by other column and store primary key.
    if DEBUG: print 'missed', cache_key
    object = model.objects.get(**kwargs)
    cache.set(cache_key, object.id)
    # Cache object by id.
    cache_key = KEY_FORMAT % (model._meta.db_table, 'id', object.id)
    cache.set(cache_key, object)
    return object


def get_many(model, id_list):
    """
    Efficiently get many objects from the cache.
    """
    format = KEY_FORMAT % (model._meta.db_table, 'id', '%d')
    result = {}
    misses = []
    # Get objects from cache.
    hits = cache.get_many(
        [KEY_FORMAT % (model._meta.db_table, 'id', id) for id in id_list])
    # Translate cache keys back to ids.
    for id in id_list:
        cache_key = format % id
        if cache_key in hits:
            if DEBUG: print 'many hit', cache_key
            result[id] = hits[cache_key]
        else:
            if DEBUG: print 'many missed', cache_key
            misses.append(id)
    bulk = model.objects.in_bulk(misses)
    for id, object in bulk.iteritems():
        cache_key = format % id
        cache.set(cache_key, object)
    result.update(bulk)
    return result


def update(object):
    """
    Update an object in the cache.
    """
    cache_key = KEY_FORMAT % (object._meta.db_table, 'id', object.id)
    cache.set(cache_key, object)


def preload_foreign_keys(instances, **kwargs):
    """
    Preload the object cache for some foreign key fields.

    Use this if you have a set of books and you want to avoid a new
    database query for each author when you display them.
    >>> preload_foreign_keys(books, author=True)

    You can preload more than one field, and nested foreign keys:
    >>> preload_foreign_keys(books, author=True, publisher=True)
    >>> preload_foreign_keys(books, publisher__city=True)

    The following examples are equivalent. Use the second form if you
    already have the list of authors:
    >>> preload_foreign_keys(books, author=True)
    >>> preload_foreign_keys(books, author=Author.objects.filter(
            id__in=set([book.author_id for book in books])))
    """
    if not len(instances):
        return # Nothing to do.
    fieldnames = kwargs.keys()
    fieldnames.sort() # Process short names before nested names.
    for fieldname in fieldnames:
        if '__' in fieldname:
            firstpart, rest = fieldname.split('__', 1)
            field = instances[0]._meta.get_field(firstpart)
            field_cache = field.get_cache_name()
            # Get values of foreign keys from the cache.
            values = []
            for instance in instances:
                if not hasattr(instance, field_cache):
                    # Preload cache if necessary.
                    preload_foreign_keys(instances, **{firstpart: True})
                value = getattr(instance, field_cache)
                if value not in values:
                    values.append(value)
            # Recursive call to preload nested foreign keys.
            preload_foreign_keys(values, **{rest: kwargs[fieldname]})
        else:
            field = instances[0]._meta.get_field(fieldname)
            field_id = fieldname + '_id'
            field_cache = field.get_cache_name()
            values = kwargs[fieldname]
            if values is True:
                # Load needed values from database with just one SQL query.
                # value_dict = field.rel.to.in_bulk(set(
                value_dict = get_many(field.rel.to, set(
                    [getattr(instance, field_id) for instance in instances]))
            else:
                value_dict = dict([(value.id, value) for value in values])
            # Fill the foreign key cache.
            for instance in instances:
                value_id = getattr(instance, field_id)
                if value_id in value_dict:
                    setattr(instance, field_cache, value_dict[value_id])
