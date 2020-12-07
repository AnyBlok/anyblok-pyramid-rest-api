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
from sqlalchemy import or_, and_
from logging import getLogger
logger = getLogger(__name__)


class QueryString:
    """Parse the validated querystring from the request to generate a
    SQLAlchemy query

    :param request: validated request from pyramid
    :param Model: AnyBlok Model, use to create the query
    :param adapter: Adapter to help to generate query on some filter of tags
    """
    def __init__(self, request, Model, adapter=None):
        self.request = request
        self.adapter = adapter
        self.Model = Model
        if request.params is not None:
            parsed_params = deserialize_querystring(request.params)
            self.filter_by = parsed_params.get('filter_by', [])
            self.filter_by_primary_keys = parsed_params.get(
                'filter_by_primary_keys', {})
            self.composite_filter_by = parsed_params.get(
                'composite_filter_by', [])
            self.tags = parsed_params.get('tags')
            self.order_by = parsed_params.get('order_by', [])
            self.context = parsed_params.get('context', {})
            self.limit = parsed_params.get('limit')
            if self.limit and isinstance(self.limit, str):
                self.limit = int(self.limit)

            self.offset = parsed_params.get('offset')
            if self.offset and isinstance(self.offset, str):
                self.offset = int(self.offset)

    def update_sqlalchemy_query(self, query, only_filter=False):
        query = self.from_filter_by(query)
        query = self.from_filter_by_primary_keys(query)
        query = self.from_composite_filter_by(query)
        query = self.from_tags(query)
        if not only_filter:
            query = self.from_order_by(query)
            query = self.from_limit(query)
            query = self.from_offset(query)

        return query

    def from_filter_by(self, query):
        for item in self.filter_by:
            op = item.get('op')
            key = item.get('key')
            value = item.get('value')
            mode = item.get('mode', 'include')
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
                    "No key filled %r" % item)
                self.request.errors.status = 400
            elif self.has_specific_filter(key, op):
                query = self.specific_filter(query, key, op, value, mode)
            else:
                res = self.get_model_and_key_from_relationship(
                    query, self.Model, key.split('.'))
                if isinstance(res, tuple):
                    _query, _model, _key = res
                    condition = self.update_filter(_model, _key, op, value)
                    if condition is not None:
                        if mode == 'include':
                            query = _query.filter(condition)
                        elif mode == 'exclude':
                            query = _query.filter(~condition)

                    if '.' in key:
                        query = query.reset_joinpoint()
                else:
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request',
                        "Filter %r: %s" % (key, res))
                    self.request.errors.status = 400

        return query

    def from_filter_by_primary_keys(self, query):
        composite_filters = []
        mode = self.filter_by_primary_keys.get('mode', 'include')
        has_error = False
        for primary_keys in self.filter_by_primary_keys.get('filters', []):
            for entry in primary_keys:
                key = entry['key']
                if '.' in key:
                    has_error = True
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request',
                        f"'{key.split('.')[0]}' is a relationship, "
                        "you should use 'composite-filter' instead of "
                        "'primary-keys'"
                    )
                elif key not in self.Model.get_primary_keys():
                    has_error = True
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request',
                        f"'{key.split('.')[0]}' is not a primary key column, "
                        "you should use 'composite-filter' instead of "
                        "'primary-keys'"
                    )

                entry['op'] = 'eq'

            composite_filters.append(primary_keys)

        if has_error:
            self.request.errors.status = 400
            return True

        return self.compute_composite_filters(query, composite_filters, mode)

    def from_composite_filter_by(self, query):
        has_error = False
        for composite_filters in self.composite_filter_by:
            filters = composite_filters.get('filters', [])
            for entry in filters:
                if len(entry) == 1:
                    has_error = True
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request',
                        "A composite filter must have more than 1 key, "
                        "You should use filter")

            mode = composite_filters.get('mode', 'include')
            query = self.compute_composite_filters(query, filters, mode)

        if has_error:
            self.request.errors.status = 400
            return True

        return query

    def compute_composite_filters_where_clause(self, where_clauses, mode):
        if len(where_clauses) == 1:
            return where_clauses[0]
        elif mode == 'include':
            return or_(*where_clauses)
        else:
            return and_(*where_clauses)

    def compute_composite_filters(self, query, composite_filters, mode):
        reset_joinpoint = False
        where_clauses = []
        for composite_filter in composite_filters:
            filters = []
            for entry in composite_filter:
                key = entry['key']
                op = entry['op']
                value = entry['value']
                if op not in FILTER_OPERATORS:
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request', 'Filter %r does not exist.' % op)
                    self.request.errors.status = 400
                    return

                res = self.get_model_and_key_from_relationship(
                    query, self.Model, key.split('.'))
                if isinstance(res, tuple):
                    query, _model, _key = res
                    filters.append(self.update_filter(_model, _key, op, value))
                    if '.' in key:
                        reset_joinpoint = True

                else:
                    self.request.errors.add(
                        'querystring',
                        '400 Bad Request',
                        "Filter %r: %s" % (key, res))
                    self.request.errors.status = 400

            if not filters:
                continue

            if len(filters) == 1:
                where_clauses.append(
                    filters[0] if mode == 'include' else ~filters[0])
            else:
                where_clauses.append(
                    and_(*filters) if mode == 'include' else ~and_(*filters))

        if not where_clauses:
            pass
        else:
            query = query.filter(self.compute_composite_filters_where_clause(
                where_clauses, mode))

        if reset_joinpoint:
            query = query.reset_joinpoint()

        return query

    def has_specific_filter(self, key, op):
        if self.adapter is None:
            return False

        return self.adapter.has_filter_for(key, op)

    def specific_filter(self, query, key, op, value, mode):
        try:
            return self.adapter.get_filter_for(key, op)(
                self, query, op, value, mode)
        except Exception as e:
            self.request.errors.add(
                'querystring',
                "Filter %s %s %r" % (key, op, value),
                str(e)
            )
            self.request.errors.status = 400
            logger.exception(str(e))

        return query

    def has_specific_order_by(self, key):
        if self.adapter is None:
            return False

        return self.adapter.has_order_by_for(key)

    def specific_order_by(self, query, key, op):
        try:
            return self.adapter.get_order_by_for(key)(self, query, op)
        except Exception as e:
            self.request.errors.add(
                'querystring',
                "Order by %s %s" % (key, op),
                str(e)
            )
            self.request.errors.status = 400
            logger.exception(str(e))

        return query

    def from_tags(self, query):
        grouped_tags = {}
        for tag in self.tags:
            if self.has_tag(tag):
                try:
                    query = self.from_tag(query, tag)
                except Exception as e:
                    self.request.errors.add(
                        'querystring',
                        "Tag %r" % tag,
                        str(e)
                    )
                    self.request.errors.status = 400
                    logger.exception(str(e))
            elif self.has_grouped_tag(tag):
                grouped_tag = self.get_grouped_tag_for(tag)
                if grouped_tag not in grouped_tags:
                    grouped_tags[grouped_tag] = []

                grouped_tags[grouped_tag].append(tag)
            else:
                self.request.errors.add(
                    'querystring',
                    "Tag %r" % tag,
                    "Unexisting tag"
                )
                self.request.errors.status = 400

        for grouped_tag in grouped_tags:
            try:
                query = self.from_grouped_tags(
                    query, grouped_tag, grouped_tags[grouped_tag])
            except Exception as e:
                self.request.errors.add(
                    'querystring',
                    "Tag %r" % tag,
                    str(e)
                )
                self.request.errors.status = 400
                logger.exception(str(e))

        return query

    def has_tag(self, tag):
        if self.adapter is None:
            return False

        return self.adapter.has_tag_for(tag)

    def has_grouped_tag(self, tag):
        if self.adapter is None:
            return False

        return self.adapter.has_grouped_tag_for(tag)

    def get_grouped_tag_for(self, tag):
        return self.adapter.grouped_tags[tag]

    def from_tag(self, query, tag):
        return self.adapter.get_tag_for(tag)(self, query)

    def from_grouped_tags(self, query, group, tags):
        return self.adapter.get_grouped_tag_for(group)(self, query, tags)

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
                    "No key ordered %r" % item)
                self.request.errors.status = 400
            elif self.has_specific_order_by(key):
                query = self.specific_order_by(query, key, op)
            else:
                res = self.get_model_and_key_from_relationship(
                    query, self.Model, key.split('.'))
                if isinstance(res, tuple):
                    _query, _model, _key = res
                    query = _query.order_by(
                        getattr(getattr(_model, _key), op)())

                    if '.' in key:
                        query = query.reset_joinpoint()
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

    def update_or_filter(self, model, key, op, value):
        if not value:
            self.request.errors.add(
                'querystring', '400 Bad Request',
                'not splitting entries for %r: %r' % (key, value)
            )
            self.request.errors.status = 400
            return
        return or_(*[
            self.update_filter(model, key, op, v.strip())
            for v in value.split(',')
        ])

    def update_filter(self, model, key, op, value):
        if op == "eq":
            return getattr(model, key) == value
        elif op in ("like", "ilike"):
            return getattr(getattr(model, key), op)("%" + value + "%")
        elif op == "lt":
            return getattr(model, key) < value
        elif op == "lte":
            return getattr(model, key) <= value
        elif op == "gt":
            return getattr(model, key) > value
        elif op == "gte":
            return getattr(model, key) >= value
        elif op == "in":
            # ensure we have a comma separated value string...
            if value:
                values = value.split(',')
                return getattr(model, key).in_(values)
            error = 'Filter %r except a comma separated string value' % op
        elif op.startswith("or-"):
            return self.update_or_filter(model, key, op.split('-')[1], value)

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

    def get_model_and_key_from_relationship(self, query, model, keys,
                                            already_join=False):
        key = keys[0]
        if not hasattr(model, 'fields_description'):
            return '%r is not an SQL Model you should use Adapter' % model
        if key not in model.fields_description():
            return '%r does not exist in model %s.' % (key, model)

        if len(keys) == 1:
            return (query, model, keys[0])
        else:
            field = getattr(model, key)
            new_model = self.get_remote_model_for(model, key)
            if new_model is None:
                return '%r in model %s is not a relationship.' % (key, model)

            query = query.join(field, aliased=True, from_joinpoint=already_join)
            return self.get_model_and_key_from_relationship(
                query, new_model, keys[1:], already_join=already_join)
