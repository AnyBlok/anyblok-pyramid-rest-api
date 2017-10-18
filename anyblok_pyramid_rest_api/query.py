# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

from .validator import FILTER_OPERATORS, ORDER_BY_OPERATORS


def update_query_filter_by_add_filter(request, query, model, key, op, value):
    if op == "eq":
        return query.filter(getattr(model, key) == value)
    elif op == "like":
        return query.filter(getattr(model, key).like("%" + value + "%"))
    elif op == "ilike":
        return query.filter(getattr(model, key).ilike("%" + value + "%"))
    elif op == "lt":
        return query.filter(getattr(model, key) < value)
    elif op == "lte":
        return query.filter(getattr(model, key) <= value)
    elif op == "gt":
        return query.filter(getattr(model, key) > value)
    elif op == "gte":
        return query.filter(getattr(model, key) >= value)
    elif op == "in":
        # ensure we have a comma separated value string...
        if value:
            values = value.split(',')
            return query.filter(getattr(model, key).in_(values))
        error = 'Filter %r except a comma separated string value' % op
    # elif op == "not":
    #     error = "'%s' filter not implemented yet" % op

    request.errors.add('querystring', '400 Bad Request', error)
    request.errors.status = 400


def update_query_filter_by(request, query, model, filter_by):
    for item in filter_by:
        op = item.get('op')
        key = item.get('key')
        value = item.get('value')
        # Is operator valid?
        if op not in FILTER_OPERATORS:
            request.errors.add(
                'querystring',
                '400 Bad Request', 'Filter %r does not exist.' % op)
            request.errors.status = 400
        # Column exists?
        elif key not in model.fields_description().keys():
            request.errors.add(
                'querystring',
                '400 Bad Request',
                "Key '%s' does not exist in model" % key)
            request.errors.status = 400
            # set key to None to avoid making a query filter based
            # on it
        else:
            query = update_query_filter_by_add_filter(
                request, query, model, key, op, value)

    return query


def update_query_order_by(request, query, model, order_by):
    for item in order_by:
        op = item.get('op')
        key = item.get('key')
        # Is operator valid?
        if op not in ORDER_BY_OPERATORS:
            request.errors.add(
                'querystring', '400 Bad Request',
                "ORDER_by operator '%s' does not exist." % op)
            request.errors.status = 400
            op = None
        # Column exists?
        if key not in model.fields_description().keys():
            request.errors.add(
                'querystring', '400 Bad Request',
                "Key '%s' does not exist in model" % key)
            request.errors.status = 400
            key = None

        if key and op:
            if op == "asc":
                query = query.order_by(getattr(model, key).asc())
            if op == "desc":
                query = query.order_by(getattr(model, key).desc())

    return query
