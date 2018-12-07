#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck BRET <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_marshmallow import SchemaWrapper
from cornice.resource import view as cornice_view
from pyramid.security import Deny, Allow, Everyone, ALL_PERMISSIONS
from pyramid.httpexceptions import HTTPUnauthorized, HTTPNotFound
from anyblok_pyramid_rest_api.querystring import QueryString
from types import MethodType
from .validator import (collection_get_validator, collection_post_validator,
                        get_validator, delete_validator, put_validator,
                        patch_validator)
from marshmallow import ValidationError
from contextlib import contextmanager
from logging import getLogger

logger = getLogger(__name__)


@contextmanager
def saved_errors_in_request(request):
    try:
        yield
    except Exception as e:
        request.anyblok.registry.rollback()
        logger.exception(e)
        request.errors.add(
            'body', '500 Internal Server Error', str(e))
        request.errors.status = 500


def get_path(request):
    """Ensure we get a valid path
    """
    if 'path' in request.validated.keys():
        return request.validated.get('path')
    else:
        return request.matchdict


def update_from_query_string(request, Model, query, adapter):
    headers = request.response.headers
    if request.params:
        # TODO: Implement schema validation to use request.validated
        querystring = QueryString(request, Model, adapter=adapter)
        total_query = querystring.from_filter_by(query)
        total_query = querystring.from_tags(total_query)
        query = querystring.from_order_by(total_query)
        query = querystring.from_limit(query)
        query = querystring.from_offset(query)
        # TODO: Advanced pagination with Link Header
        # Link: '<https://api.github.com/user/repos?page=3&per_page=100>;
        # rel="next",
        # <https://api.github.com/user/repos?page=50&per_page=100>;
        # rel="last"'
        headers['X-Count-Records'] = str(query.count())
        headers['X-Total-Records'] = str(total_query.count())
        # TODO: Etag / timestamp / 304 if no changes
        # TODO: Cache headers
        return query
    else:
        # no querystring, returns all records (maybe we will want to apply
        # some default filters values
        headers['X-Count-Records'] = str(query.count())
        headers['X-Total-Records'] = str(query.count())
        return query


def post_item(request, Model):
    if request.errors:
        return

    if isinstance(Model, str):
        Model = request.anyblok.registry.get(Model)

    try:
        return Model.insert(**request.validated['body'])
    except Exception as e:
        request.anyblok.registry.rollback()
        request.errors.add('body', '500 Internal Server Error', str(e))
        request.errors.status = 500


def get_items(request, Model, Adapter=None):
    if request.errors:
        return

    if isinstance(Model, str):
        Model = request.anyblok.registry.get(Model)

    query = Model.query()
    query = update_from_query_string(request, Model, query, Adapter)
    if not query.count():
        return

    return query.all()


def get_item(request, Model):
    if request.errors:
        return

    if isinstance(Model, str):
        Model = request.anyblok.registry.get(Model)

    path = get_path(request)
    model_pks = Model.get_primary_keys()
    pks = {x: path[x] for x in model_pks}
    item = Model.from_primary_keys(**pks)
    if item:
        return item
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (
                Model.__registry_name__, path))
        request.errors.status = 404


def put_item(request, Model):
    """
    """
    if request.errors:
        return

    if isinstance(Model, str):
        Model = request.anyblok.registry.get(Model)

    item = get_item(request, Model)
    if item:
        body = request.validated.get('body', request.validated)
        with saved_errors_in_request(request):
            item.update(**body)

        return item


patch_item = put_item


def delete_item(request, Model):
    """
    """
    if request.errors:
        return

    if isinstance(Model, str):
        Model = request.anyblok.registry.get(Model)

    item = get_item(request, Model)
    if item:
        with saved_errors_in_request(request):
            item.delete()


# HOOK
# * deactivate some access
#   - has_collection_get: bool default True
#   - has_collection_post: bool default True
#   - has_get: bool default True
#   - has_delete: bool default True
#   - has_patch: bool default True
#   - has_put: bool default True
# * get schema
#   - default_schema: classmethod of AnyBlokMarshmallow schema, by default use
#     model to defined it
# * get serialize schema
#   - default_serialize_schema: method of AnyBlokMarshmallow schema, by
#     default use default_schema
#   - serialize_collection_get: method of AnyBlokMarshmallow schema,
#                               by default use default_serialize_schema
#   - serialize_collection_post: method of AnyBlokMarshmallow schem
#                                by default use default_serialize_schema
#   - serialize_get: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
#   - serialize_delete: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
#   - serialize_patch: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
#   - serialize_put: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
# * get serialize opts
#   - get_serialize_opts: method return dict of option to use
# * get deserialize schema
#   - default_deserialize_schema: method of AnyBlokMarshmallow schema, by
#     default use default_schema
#   - deserialize_collection_post: method of AnyBlokMarshmallow schema,
#                                  by default use default_deserialize_schema
#   - deserialize_patch: method of AnyBlokMarshmallow schema,
#                        by default use default_deserialize_schema
#   - deserialize_put: method of AnyBlokMarshmallow schema,
#                      by default use default_deserialize_schema
# * get deserialize opts
#   - get_deserialize_opts: method return dict of option to use
# * get path schema
#   - default_path_schema: method of AnyBlokMarshmallow schema, by default use
#     default_schema
#   - path_get: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
#   - path_delete: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
#   - path_patch: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
#   - path_put: method of AnyBlokMarshmallow schema, by default use
#     default_serialize_schema
# * get path opts
#   - get_path_opts: method return dict of option to use
# * update_collection_get_filter: method to improve query to filter
# * create
# * update
# * delete_entry
# * get_model_name:


class CrudResource:
    model = None
    adapter_cls = None
    cache_default_schema = True  # TODO
    has_collection_get = True
    has_collection_post = True
    has_get = True
    has_delete = True
    has_patch = True
    has_put = True

    def __init__(self, request, **kwargs):
        self.request = request
        self.registry = self.request.anyblok.registry
        self.adapter = None
        if self.adapter_cls:
            self.adapter = self.adapter_cls(
                self.registry,
                Model=self.get_model('collection_get'))
            self.adapter.load_decorators()

    @classmethod
    def get_model_name(cls, request, rest_action=None, base=None):
        return cls.model

    def model_name(self, rest_action=None):
        return self.get_model_name(
            self.request,
            rest_action=rest_action,
            base=self.request.validated
        )

    def __acl__(self):
        if not hasattr(self, 'registry'):
            raise HTTPUnauthorized("ACL have not get AnyBlok registry")

        Blok = self.registry.System.Blok
        if not Blok.is_installed('auth'):
            return [(Allow, Everyone, ALL_PERMISSIONS)]

        userid = self.request.authenticated_userid
        if userid:
            return self.registry.User.get_acl(
                userid, self.model_name(), params=dict(self.request.matchdict)
            )

        return [(Deny, Everyone, ALL_PERMISSIONS)]

    @classmethod
    def apply_validator_schema(cls, request, part, Schema, opts, base):
        if 'context' not in opts:
            opts['context'] = {}

        opts['context']['registry'] = request.anyblok.registry
        try:
            logger.debug('Validate %r with schema %r and option %r',
                         base[part], Schema, opts)
            schema = Schema(**opts)
            result = schema.load(base[part])
            request.validated[part] = result
        except ValidationError as err:
            request.anyblok.registry.rollback()
            logger.exception(err)
            errors = err.messages
            for k, v in errors.items():
                request.errors.add(
                    part, 'Validation error for %s' % part,
                    {k: v})

    def get_model(self, rest_action):
        return self.registry.get(self.model_name(rest_action=rest_action))

    def update_collection_get_filter(self, query):
        return query

    @classmethod
    def get_value_or_call_method(cls, attribute, *args, **kwargs):
        value = None
        if hasattr(cls, attribute):
            value = getattr(cls, attribute)
            if isinstance(value, MethodType):
                value = value(*args, **kwargs)

        return value

    @classmethod
    def default_schema(cls, name, model_name):
        name = '%s.%s.%s' % (cls.__name__, name, model_name)
        return type(name, (SchemaWrapper,), {'model': model_name})

    @classmethod
    def default_serialize_schema(cls, model_name):
        return cls.get_value_or_call_method(
            'default_schema', 'Serialize', model_name)

    @classmethod
    def get_serialize_schema(cls, rest_action, model_name):
        Schema = cls.get_value_or_call_method(
            'serialize_' + rest_action, model_name)
        if Schema is None:
            Schema = cls.get_value_or_call_method(
                'default_serialize_schema', model_name)

        return Schema

    @classmethod
    def get_serialize_opts(cls, rest_action):
        opts = {}
        if rest_action == 'collection_get':
            opts['many'] = True

        return opts

    @classmethod
    def default_deserialize_schema(cls, model_name):
        return cls.get_value_or_call_method(
            'default_schema', 'Deserialize', model_name)

    @classmethod
    def get_deserialize_schema(cls, rest_action, model_name):
        Schema = cls.get_value_or_call_method(
            'deserialize_' + rest_action, model_name)
        if Schema is None:
            Schema = cls.get_value_or_call_method(
                'default_deserialize_schema', model_name)

        return Schema

    @classmethod
    def get_deserialize_opts(cls, rest_action):
        opts = {}
        if rest_action == 'patch':
            opts['partial'] = True

        return opts

    @classmethod
    def default_path_schema(cls):
        return cls.get_value_or_call_method('default_schema', 'Path', cls.model)

    @classmethod
    def get_path_schema(cls, rest_action):
        Schema = cls.get_value_or_call_method('path_' + rest_action)
        if Schema is None:
            Schema = cls.get_value_or_call_method('default_path_schema')

        return Schema

    @classmethod
    def get_path_opts(cls, rest_action):
        opts = {'context': {'only_primary_key': True}}
        return opts

    def serialize(self, rest_action, entry):
        Schema = self.get_serialize_schema(
            rest_action, self.model_name(rest_action))
        opts = self.get_serialize_opts(rest_action)
        opts['context'] = {'registry': self.registry}
        schema = Schema(**opts)
        return schema.dump(entry)

    @cornice_view(validators=(collection_get_validator,), permission="read")
    def collection_get(self):
        if not self.has_collection_get:
            raise HTTPNotFound()

        if self.request.errors:
            return

        Model = self.get_model('collection_get')
        query = self.update_collection_get_filter(Model.query())
        query = update_from_query_string(
            self.request, Model, query, self.adapter)
        if not query.count():
            return []

        return self.serialize('collection_get', query.all())

    def create(self, Model, params):
        return Model.insert(**params)

    @cornice_view(validators=(collection_post_validator,), permission="create")
    def collection_post(self):
        if not self.has_collection_post:
            raise HTTPNotFound()

        if self.request.errors:
            return

        body = self.request.validated.get('body', self.request.validated)
        item = None
        if body:
            Model = self.get_model('collection_post')
            with saved_errors_in_request(self.request):
                item = self.create(Model, params=body)
        else:
            self.request.errors.add(
                'body', '400 bad request',
                'You can not post an empty body')
            self.request.errors.status = 400

        if item:
            return self.serialize('collection_post', item)

    @cornice_view(validators=(get_validator,), permission="read")
    def get(self):
        if not self.has_get:
            raise HTTPNotFound()

        if self.request.errors:
            return

        Model = self.get_model('get')
        item = get_item(self.request, Model)
        if item:
            return self.serialize('get', item)

    def delete_entry(self, item):
        item.delete()

    @cornice_view(validators=(delete_validator,), permission="delete")
    def delete(self):
        """
        """
        if not self.has_delete:
            raise HTTPNotFound()

        if self.request.errors:
            return

        Model = self.get_model('delete')
        item = get_item(self.request, Model)
        if item:
            with saved_errors_in_request(self.request):
                self.delete_entry(item)

        return {}

    def update(self, item, params=None):
        if params is None:
            return item

        item.update(**params)

    @cornice_view(validators=(patch_validator,), permission="update")
    def patch(self):
        """
        """
        if not self.has_patch:
            raise HTTPNotFound()

        if self.request.errors:
            return

        Model = self.get_model('patch')
        item = get_item(self.request, Model)
        if item:
            body = self.request.validated.get('body', self.request.validated)
            with saved_errors_in_request(self.request):
                self.update(item, params=body)

            return self.serialize('patch', item)

    @cornice_view(validators=(put_validator,), permission="update")
    def put(self):
        """
        """
        if not self.has_put:
            raise HTTPNotFound()

        if self.request.errors:
            return

        Model = self.get_model('put')
        item = get_item(self.request, Model)
        if item:
            body = self.request.validated.get('body', self.request.validated)
            with saved_errors_in_request(self.request):
                self.update(item, params=body)

            return self.serialize('put', item)
