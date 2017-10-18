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


def get_remote_model_for(Model, fieldname):
    registry = Model.registry
    Field = registry.System.Field
    query = Field.query()
    models = [Model.__registry_name__]
    for base in Model.__anyblok_bases__:
        models.append(base.__registry_name__)

    query = query.filter(Field.model.in_(models))
    query = query.filter(Field.name == fieldname)
    field = query.first()
    if field.remote_model:
        return registry.get(field.remote_model)

    return None


def rec_filter(query, model, keys):
    key = keys[0]
    if key not in model.fields_description():
        return '%r not exist in model %s.' % (key, model)

    if len(keys) == 1:
        return (query, model, keys[0])
    else:
        field = getattr(model, keys[0])
        query = query.join(field)
        model = get_remote_model_for(model, keys[0])
        if model is None:
            return '%r in model %s is not a relationship.' % (key, model)

        return rec_filter(query, model, keys[1:])


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
        elif not key:
            request.errors.add(
                'querystring',
                '400 Bad Request',
                "No key filled" % key)
            request.errors.status = 400
        else:
            res = rec_filter(query, model, key.split('.'))
            if isinstance(res, tuple):
                _query, _model, _key = res
                print(res)
                query = update_query_filter_by_add_filter(
                    request, _query, _model, _key, op, value)
            else:
                request.errors.add(
                    'querystring',
                    '400 Bad Request',
                    "Filter %r: %s" % (key, res))
                request.errors.status = 400

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
