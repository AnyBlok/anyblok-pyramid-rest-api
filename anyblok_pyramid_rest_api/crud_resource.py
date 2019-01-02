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
from cornice.resource import view as cornice_view, add_resource, add_view
from cornice import Service
from pyramid.security import Deny, Allow, Everyone, ALL_PERMISSIONS
from pyramid.httpexceptions import HTTPUnauthorized, HTTPNotFound
from anyblok_pyramid_rest_api.querystring import QueryString
from types import MethodType
from .validator import (
    collection_get_validator, collection_post_validator, get_validator,
    delete_validator, put_validator, patch_validator, execute_validator,
    collection_execute_validator, collection_put_validator,
    collection_patch_validator, collection_delete_validator
)
from marshmallow import ValidationError
from contextlib import contextmanager
from logging import getLogger

logger = getLogger(__name__)


@contextmanager
def saved_errors_in_request(request):
    try:
        yield
    except Exception as e:
        logger.exception(e)
        request.errors.add(
            'body', '500 Internal Server Error', str(e))
        request.errors.status = 500
    finally:
        if request.errors:
            logger.debug('Request error found: rollback the registry')
            request.anyblok.registry.rollback()


def get_path(request):
    """Ensure we get a valid path
    """
    return request.validated.get('path', request.matchdict)


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
    if not request.errors:
        if isinstance(Model, str):
            Model = request.anyblok.registry.get(Model)

        with saved_errors_in_request(request):
            return Model.insert(**request.validated['body'])


def get_items(request, Model, Adapter=None):
    if not request.errors:
        if isinstance(Model, str):
            Model = request.anyblok.registry.get(Model)

        query = Model.query()
        query = update_from_query_string(request, Model, query, Adapter)
        if not query.count():
            return

        return query.all()


def get_item(request, Model):
    if not request.errors:
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
    if not request.errors:
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
    if not request.errors:
        if isinstance(Model, str):
            Model = request.anyblok.registry.get(Model)

        item = get_item(request, Model)
        if item:
            with saved_errors_in_request(request):
                item.delete()


def add_execute_on_crud_resource(cls, service_path=None, **kwargs):
    if service_path is None:
        service_path = '%(path)s/execute/%(name)s'

    services = {}
    for attr in dir(cls):
        method = getattr(cls, attr)
        service_kwargs = kwargs.copy()

        # auto-wire klass as its own view factory, unless one
        # is explicitly declared.
        if 'factory' not in kwargs:
            service_kwargs['factory'] = cls

        if getattr(method, 'is_a_crud_resource_execute_on_collection', None):
            service_name = 'collection_' + cls.__name__.lower() + '_execute_'
            service_name += method.crud_resource_execute_name
            service_kwargs['path'] = service_path % {
                'path': service_kwargs.pop('collection_path'),
                'name': method.crud_resource_execute_name,
            }
        elif getattr(method, 'is_a_crud_resource_execute', None):
            service_name = cls.__name__.lower() + '_execute_'
            service_name += method.crud_resource_execute_name
            del service_kwargs['collection_path']
            service_kwargs['path'] = service_path % {
                'path': service_kwargs['path'],
                'name': method.crud_resource_execute_name,
            }
        else:
            continue

        if method.crud_resource_execute_path:
            service_kwargs['path'] = method.crud_resource_execute_path

        service = services[service_name] = Service(
            name=service_name, depth=2, **service_kwargs)
        for view_args in method.__views__:
            verb = view_args.pop('verb', 'POST')
            service.add_view(verb, attr, klass=cls, **view_args)

    cls._services.update(services)
    return cls


def resource(depth=2, **kwargs):

    def wrapper(cls):
        service_path = kwargs.pop('service_path', None)
        klass = add_resource(cls, depth, **kwargs)
        klass = add_execute_on_crud_resource(
            klass, service_path=service_path, **kwargs)
        return klass

    return wrapper


class CrudResource:
    """Main class to define a RESTFUL API on an AnyBlok resource

    ::

        from anyblok_pyramid_rest_api.crud_resource import (
            CrudResource, resource)
        from anyblok_pyramid import current_blok

        @resource(
            collection_path='/myresourcepaths'
            path='/myresourcepath/{my model pk},
            installed_blok=current_blok()
        )
        class MyResource(CrudResource):
            model = 'MyModel'

    This action create view to acces on the AnyBlok Model (MyModel):

    * collection_get: validate the querystring, serialize the output
    * collection_post: deserialize the body input, serialize the output
    * collection_put: validate the querystring, serialize the output
    * get: validate the path, deserialize the body, serialize the output
    * patch: validate the path, deserialize the body, serialize the output
    * put: validate the path, deserialize the body, serialize the output
    * delete: validate the path

    The Serialization and Deserialization is done by the MarshMallow Schema.
    By default the schema is created by AnyBlok MarshMallow, but the schema
    can be overwritten

    * deactivate some access
      - has_collection_get: bool default True
      - has_collection_post: bool default True
      - has_collection_patch: bool default True
      - has_collection_put: bool default True
      - has_collection_delete: bool default True
      - has_get: bool default True
      - has_delete: bool default True
      - has_patch: bool default True
      - has_put: bool default True
    * get schema
      - default_schema: classmethod of AnyBlokMarshmallow schema, by default use
        model to defined it
    * get serialize schema
      - default_serialize_schema: method of AnyBlokMarshmallow schema, by
        default use default_schema
      - serialize_collection_get: method of AnyBlokMarshmallow schema,
                                  by default use default_serialize_schema
      - serialize_collection_post: method of AnyBlokMarshmallow schema
                                   by default use default_serialize_schema
      - serialize_collection_patch: method of AnyBlokMarshmallow schema
                                    by default use default_serialize_schema
      - serialize_collection_put: method of AnyBlokMarshmallow schema
                                  by default use default_serialize_schema
      - serialize_collection_delete: method of AnyBlokMarshmallow schema
                                     by default use default_serialize_schema
      - serialize_get: method of AnyBlokMarshmallow schema, by default use
                       default_serialize_schema
      - serialize_delete: method of AnyBlokMarshmallow schema, by default use
                          default_serialize_schema
      - serialize_patch: method of AnyBlokMarshmallow schema, by default use
                         default_serialize_schema
      - serialize_put: method of AnyBlokMarshmallow schema, by default use
                       default_serialize_schema
    * get serialize opts
      - get_serialize_opts: method return dict of option to use
    * get deserialize schema
      - default_deserialize_schema: method of AnyBlokMarshmallow schema, by
                                    default use default_schema
      - deserialize_collection_post: method of AnyBlokMarshmallow schema,
                                     by default use default_deserialize_schema
      - deserialize_collection_patch: method of AnyBlokMarshmallow schema,
                                      by default use default_deserialize_schema
      - deserialize_collection_put: method of AnyBlokMarshmallow schema,
                                    by default use default_deserialize_schema
      - deserialize_collection_delete: method of AnyBlokMarshmallow schema,
                                       by default use default_deserialize_schema
      - deserialize_patch: method of AnyBlokMarshmallow schema,
                           by default use default_deserialize_schema
      - deserialize_put: method of AnyBlokMarshmallow schema,
                         by default use default_deserialize_schema
    * get deserialize opts
      - get_deserialize_opts: method return dict of option to use
    * get path schema
      - default_path_schema: method of AnyBlokMarshmallow schema, by default use
                             default_schema
      - path_get: method of AnyBlokMarshmallow schema, by default use
                  default_serialize_schema
      - path_delete: method of AnyBlokMarshmallow schema, by default use
                     default_serialize_schema
      - path_patch: method of AnyBlokMarshmallow schema, by default use
                    default_serialize_schema
      - path_put: method of AnyBlokMarshmallow schema, by default use
                  default_serialize_schema
      - path_execute: method of AnyBlokMarshmallow schema, by default use
                      default_serialize_schema
    * get path opts
      - get_path_opts: method return dict of option to use
    * update_collection_get_filter: method to improve query to filter
    * create
    * update
    * collection_update
    * delete_entry
    * delete_entries
    * get_model_name:

    You can update the querystring to add an adapter in the resource::

        @resource(...)
        class MyResource(CrudResource):
            ...

            class adapter_cls(Adapter):
                # See the adapter definition

    Some http post action can be added with the decorator execute::

        @resource(...)
        class MyResource(CrudResource):
            ...

            @CrudResource.execute('action_name')  # schema is optional
            def post_foo_bar(self):
                # path/execute/action_name
                querystring = self.get_querystring('action_name')
                body = self.body
                ...

            @CrudResource.execute('other_action_name',
                                  collection=True)  # schema is optional
            def post_foo_bar(self):
                # collection_path/execute/other_action_name
                body = self.body
                Model = self.get_model('other_action_name')
                item = get_item(self.request, Model)
                ...
    """

    model = None
    adapter_cls = None
    cache_default_schema = True  # TODO
    has_collection_get = True
    has_collection_post = True
    has_collection_patch = True
    has_collection_put = True
    has_collection_delete = True
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

    def view_is_activated(self, condition):
        if not condition:
            raise HTTPNotFound()

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
        if rest_action in ('collection_get',
                           'collection_post',
                           'collection_put',
                           'collection_patch'):
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
        if rest_action == 'collection_patch':
            opts['partial'] = True
            opts['many'] = True
        elif rest_action in ('collection_put', 'collection_post'):
            opts['many'] = True
        elif rest_action == 'collection_delete':
            opts['many'] = True
            opts['context'] = {'only_primary_key': True}
        elif rest_action == 'patch':
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

    @property
    def body(self):
        return self.request.validated.get('body', self.request.validated)

    def get_querystring(self, rest_action):
        Model = self.get_model(rest_action)
        query = self.update_collection_get_filter(Model.query())
        query = update_from_query_string(
            self.request, Model, query, self.adapter)
        return query

    @cornice_view(validators=(collection_get_validator,), permission="read")
    def collection_get(self):
        self.view_is_activated(self.has_collection_get)
        if not self.request.errors:
            query = self.get_querystring('collection_get')
            if not query.count():
                return []

            return self.serialize('collection_get', query.all())

    def create(self, Model, params):
        return Model.insert(**params)

    @cornice_view(validators=(collection_post_validator,), permission="create")
    def collection_post(self):
        self.view_is_activated(self.has_collection_post)
        if not self.request.errors:
            items = []
            Model = self.get_model('collection_post')
            for params in self.body:
                with saved_errors_in_request(self.request):
                    items.append(self.create(Model, params=params))

            if items and not self.request.errors:
                return self.serialize('collection_post', items)

    def collection_update(self, Model, body):
        items = []
        for params in body:
            try:
                pks = {x: params[x] for x in Model.get_primary_keys()}
            except KeyError as e:
                self.request.errors.add(
                    'body', 'Validation Error',
                    'No primary key found %r to get the item on %s' % (
                        e.args, Model))
                self.request.errors.status = 400
            else:
                item = Model.from_primary_keys(**pks)
                if item:
                    self.update(item, params=params)
                    items.append(item)
                else:
                    self.request.errors.add(
                        'body', 'Validation Error',
                        'The primary key found %r does not exist on %s' % (
                            pks, Model))
                    self.request.errors.status = 400

        return items

    @cornice_view(validators=(collection_patch_validator,), permission="update")
    def collection_patch(self):
        self.view_is_activated(self.has_collection_patch)
        if not self.request.errors:
            items = []
            Model = self.get_model('collection_patch')
            with saved_errors_in_request(self.request):
                items = self.collection_update(Model, self.body)

            return self.serialize('collection_patch', items)

    @cornice_view(validators=(collection_put_validator,), permission="update")
    def collection_put(self):
        self.view_is_activated(self.has_collection_put)
        if not self.request.errors:
            items = []
            Model = self.get_model('collection_put')
            with saved_errors_in_request(self.request):
                items = self.collection_update(Model, self.body)

            return self.serialize('collection_put', items)

    def delete_entries(self, Model, body):
        for params in body:
            try:
                pks = {x: params[x] for x in Model.get_primary_keys()}
            except KeyError as e:
                self.request.errors.add(
                    'body', 'Validation Error',
                    'No primary key found %r to get the item on %s' % (
                        e.args, Model))
                self.request.errors.status = 400
                return 0
            else:
                item = Model.from_primary_keys(**pks)
                if item:
                    self.delete_entry(item)
                else:
                    self.request.errors.add(
                        'body', 'Validation Error',
                        'The primary key found %r does not exist on %s' % (
                            pks, Model))
                    self.request.errors.status = 400
                    return 0

        return len(body)

    @cornice_view(validators=(collection_delete_validator,),
                  permission="delete")
    def collection_delete(self):
        self.view_is_activated(self.has_collection_delete)
        count = 0
        if not self.request.errors:
            Model = self.get_model('collection_delete')
            with saved_errors_in_request(self.request):
                count = self.delete_entries(Model, self.body)

        return count

    @cornice_view(validators=(get_validator,), permission="read")
    def get(self):
        self.view_is_activated(self.has_get)
        if not self.request.errors:
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
        self.view_is_activated(self.has_delete)
        if not self.request.errors:
            Model = self.get_model('delete')
            item = get_item(self.request, Model)
            if item:
                with saved_errors_in_request(self.request):
                    self.delete_entry(item)

            return {}

    def update(self, item, params=None):
        if params:
            item.update(**params)

    @cornice_view(validators=(patch_validator,), permission="update")
    def patch(self):
        """
        """
        self.view_is_activated(self.has_patch)
        if not self.request.errors:
            Model = self.get_model('patch')
            item = get_item(self.request, Model)
            if item:
                with saved_errors_in_request(self.request):
                    self.update(item, params=self.body)

                return self.serialize('patch', item)

    @cornice_view(validators=(put_validator,), permission="update")
    def put(self):
        """
        """
        self.view_is_activated(self.has_put)
        if not self.request.errors:
            Model = self.get_model('put')
            item = get_item(self.request, Model)
            if item:
                with saved_errors_in_request(self.request):
                    self.update(item, params=self.body)

                return self.serialize('put', item)

    @classmethod
    def service(cls, name, permission=None, collection=False, path=None,
                **kwargs):
        if permission is None:
            permission = name

        def wrapper(method):
            method.crud_resource_execute_name = name
            method.crud_resource_execute_path = path

            if collection:
                method.is_a_crud_resource_execute_on_collection = True
                validators = (collection_execute_validator,)
            else:
                method.is_a_crud_resource_execute = True
                validators = (execute_validator,)

            add_view(method, validators=validators, permission=permission,
                     **kwargs)
            return method

        return wrapper
