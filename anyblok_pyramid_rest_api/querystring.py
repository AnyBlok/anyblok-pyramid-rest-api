# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

from .validator import (
    FILTER_OPERATORS, ORDER_BY_OPERATORS, deserialize_querystring
)


class QueryString:

    def __init__(self, request, Model):
        self.request = request
        self.Model = Model
        if request.params:
            parsed_params = deserialize_querystring(request.params)
            self.filter_by = parsed_params.get('filter_by', [])
            self.order_by = parsed_params.get('order_by', [])
            self.limit = parsed_params.get('limit')
            if self.limit and isinstance(self.limit, str):
                self.limit = int(self.limit)

            self.offset = parsed_params.get('offset')
            if self.offset and isinstance(self.offset, str):
                self.offset = int(self.offset)

    def update_sqlalchemy_query(self, query):
        query = self.from_filter_by(query)
        query = self.from_order_by(query)
        query = self.from_limit(query)
        query = self.from_offset(query)
        return query

    def from_filter_by(self, query):
        for item in self.filter_by:
            op = item.get('op')
            key = item.get('key')
            value = item.get('value')
            # Is operator valid?
            if op not in FILTER_OPERATORS:
                self.request.errors.add(
                    'querystring',
                    '400 Bad Request', 'Filter %r does not exist.' % op)
                self.request.errors.status = 400
            elif not key:
                self.request.errors.add(
                    'querystring',
                    '400 Bad Request',
                    "No key filled" % key)
                self.request.errors.status = 400
            else:
                res = self.get_model_and_key_from_relationship(
                    query, self.Model, key.split('.'))
                if isinstance(res, tuple):
                    _query, _model, _key = res
                    query = self.update_filter(_query, _model, _key, op, value)
                else:
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request',
                        "Filter %r: %s" % (key, res))
                    self.request.errors.status = 400

        return query

    def from_order_by(self, query):
        for item in self.order_by:
            op = item.get('op')
            key = item.get('key')
            # Is operator valid?
            if op not in ORDER_BY_OPERATORS:
                self.request.errors.add(
                    'querystring', '400 Bad Request',
                    "ORDER_by operator '%s' does not exist." % op)
                self.request.errors.status = 400
            # Column exists?
            elif not key:
                self.request.errors.add(
                    'querystring',
                    '400 Bad Request',
                    "No key ordered" % key)
                self.request.errors.status = 400
            else:
                res = self.get_model_and_key_from_relationship(
                    query, self.Model, key.split('.'))
                if isinstance(res, tuple):
                    _query, _model, _key = res
                    query = _query.order_by(
                        getattr(getattr(_model, _key), op)())
                else:
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request',
                        "Order %r: %s" % (key, res))
                    self.request.errors.status = 400

        return query

    def from_limit(self, query):
        if self.limit:
            query = query.limit(self.limit)

        return query

    def from_offset(self, query):
        if self.offset:
            query = query.offset(self.offset)

        return query

    def update_filter(self, query, model, key, op, value):
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

        self.request.errors.add('querystring', '400 Bad Request', error)
        self.request.errors.status = 400

    def get_remote_model_for(self, Model, fieldname):
        registry = Model.registry
        Field = registry.System.Field
        query = Field.query()
        models = [Model.__registry_name__]
        for base in Model.__anyblok_bases__:
            models.append(base.__registry_name__)

        query = query.filter(Field.model.in_(models))
        query = query.filter(Field.name == fieldname)
        field = query.first()
        if field and field.remote_model:
            return registry.get(field.remote_model)

        return None

    def get_model_and_key_from_relationship(self, query, model, keys):
        key = keys[0]
        if key not in model.fields_description():
            return '%r does not exist in model %s.' % (key, model)

        if len(keys) == 1:
            return (query, model, keys[0])
        else:
            print('plop')
            field = getattr(model, key)
            print(model, key, field)
            new_model = self.get_remote_model_for(model, key)
            if new_model is None:
                return '%r in model %s is not a relationship.' % (key, model)

            query = query.join(field)
            return self.get_model_and_key_from_relationship(
                query, new_model, keys[1:])
