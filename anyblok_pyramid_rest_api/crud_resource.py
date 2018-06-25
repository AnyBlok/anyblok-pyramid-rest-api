# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
""" A set of methods for crud resource manipulation
# TODO: Add a get_or_create_item method
# TODO: Manage relationship
# TODO: Response objects serialization
"""
from cornice.resource import view as cornice_view
from anyblok.registry import RegistryManagerException
from .querystring import QueryString
from .validator import base_validator
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import Deny, Allow, Everyone, ALL_PERMISSIONS
from json import dumps
from anyblok_marshmallow import ModelSchema
try:
    from anyblok_jsonschema import AnyBlokJSONSchema
except ImportError:
    AnyBlokJSONSchema = None


def get_model(registry, modelname):
    try:
        model = registry.get(modelname)
    except RegistryManagerException:
        raise RegistryManagerException(
            "The model %r does not exists" % modelname)

    return model


def get_item(registry, modelname, path={}):
    """Given a a modelname and a path returns a single record.
    Path must match a primary key column.
    """
    model = get_model(registry, modelname)
    model_pks = model.get_primary_keys()
    pks = {x: path[x] for x in model_pks}
    item = model.from_primary_keys(**pks)
    return item


def get_path(request):
    """Ensure we get a valid path
    """
    if 'path' in request.validated.keys():
        return request.validated.get('path')
    else:
        return request.matchdict


def get_dschema(request, key='dschema'):
    """Try to return a deserialization schema
    for body response
    """
    dschema = None
    if hasattr(request.current_service, 'schema'):
        if key in request.current_service.schema.fields:
            dschema = request.current_service.schema.fields.get(key, None)
        elif 'body' in request.current_service.schema.fields:
            dschema = request.current_service.schema.fields.get('body', None)
    if dschema and hasattr(dschema, 'nested'):
        return dschema.nested
    else:
        return None


def collection_get(request, modelname, collection_get_callback=None):
    """Parse request.params, deserialize it and then build an sqla query

    Default behaviour is to search for equal matches where key is a column
    name
    Two special keys are available ('filter[*' and 'order_by[*')

    Filter must be something like 'filter[key][operator]=value' where key
    is mapped to an sql column and operator is one of (eq, ilike, like, lt,
    lte, gt, gte, in, not)

    Order_by must be something like 'order_by[operator]=value' where
    'value' is mapped to an sql column and operator is one of (asc, desc)

    Limit will limit the records quantity
    Offset will apply an offset on records
    """
    model = get_model(request.anyblok.registry, modelname)
    query = model.query()

    headers = request.response.headers

    if request.params:
        # TODO: Implement schema validation to use request.validated
        querystring = QueryString(request, model)
        total_query = querystring.update_sqlalchemy_query(
            query, only_filter=True)
        query = querystring.update_sqlalchemy_query(query)
        if collection_get_callback:
            query = collection_get_callback(query)
        # TODO: Advanced pagination with Link Header
        # Link: '<https://api.github.com/user/repos?page=3&per_page=100>;
        # rel="next",
        # <https://api.github.com/user/repos?page=50&per_page=100>;
        # rel="last"'
        headers['X-Count-Records'] = str(query.count())
        headers['X-Total-Records'] = str(total_query.count())
        # TODO: Etag / timestamp / 304 if no changes
        # TODO: Cache headers
        return query.all() if query.count() > 0 else None
    else:
        # no querystring, returns all records (maybe we will want to apply
        # some default filters values
        headers['X-Count-Records'] = str(query.count())
        headers['X-Total-Records'] = str(query.count())
        return query.all() if query.count() > 0 else None


def collection_post(request, modelname, collection_post_callback=None):
    """
    """
    if request.errors:
        return

    model = get_model(request.anyblok.registry, modelname)
    if 'body' in request.validated.keys():
        if request.validated.get('body'):
            if collection_post_callback:
                item = collection_post_callback(
                    model, params=request.validated['body']
                )
            else:
                item = model.insert(**request.validated['body'])
        else:
            request.errors.add(
                'body', '400 bad request',
                'You can not post an empty body')
            request.errors.status = 400
            item = None
    else:
        if request.validated:
            if collection_post_callback:
                item = collection_post_callback(
                    model, params=request.validated
                )
            else:
                item = model.insert(**request.validated)
        else:
            request.errors.add(
                'body', '400 bad request',
                'You can not post an empty body')
            request.errors.status = 400
            item = None
    return item


def get(request, modelname):
    """return a model instance based on path
    """
    if request.errors:
        return

    item = get_item(
        request.anyblok.registry,
        modelname,
        get_path(request)
    )
    if item:
        return item
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (modelname, path))
        request.errors.status = 404


def put(request, modelname, put_callback=None):
    """
    """
    if request.errors:
        return

    item = get_item(
        request.anyblok.registry,
        modelname,
        get_path(request)
    )

    if item:
        if put_callback:
            put_callback(item, params=request.validated['body'])
        else:
            item.update(**request.validated['body'])
        return item
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (modelname, path))
        request.errors.status = 404


def patch(request, modelname, patch_callback=None):
    """
    """
    if request.errors:
        return

    item = get_item(
        request.anyblok.registry,
        modelname,
        get_path(request)
    )

    if item:
        if patch_callback:
            patch_callback(item, params=request.validated['body'])
        else:
            item.update(**request.validated['body'])
        return item
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (modelname, path))
        request.errors.status = 404


def delete(request, modelname, delete_callback=None):
    """
    """
    if request.errors:
        return

    item = get_item(
        request.anyblok.registry,
        modelname,
        get_path(request)
    )
    if item:
        if delete_callback:
            delete_callback(item)
        else:
            item.delete()
        request.status = 204
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (modelname, path))
        request.errors.status = 404


def getJsonSchema(request, schema):
    if AnyBlokJSONSchema:
        headers = request.response.headers
        json_schema = AnyBlokJSONSchema()
        schema = schema.schema if isinstance(schema, ModelSchema) else schema
        headers['X-Json-Schema'] = dumps(json_schema.dump(schema))


class CrudResource(object):
    """ A class that add to cornice resource CRUD abilities on Anyblok models.

    :Example:

    >>> @resource(collection_path='/examples', path='/examples/{id}')
    >>> class ExampleResource(CrudResource):
    >>>     model = 'Model.Example'

    """
    model = None
    QueryString = QueryString

    def __init__(self, request, **kwargs):
        self.request = request
        self.registry = self.request.anyblok.registry

        if not self.model:
            raise ValueError(
                "You must provide a 'model' to use CrudResource class")

    def __acl__(self):
        if not hasattr(self, 'registry'):
            raise HTTPUnauthorized("ACL have not get AnyBlok registry")

        Blok = self.registry.System.Blok
        if not Blok.is_installed('auth'):
            return [(Allow, Everyone, ALL_PERMISSIONS)]

        userid = self.request.authenticated_userid
        if userid:
            return self.registry.User.get_acl(
                userid, self.model, params=dict(self.request.matchdict)
            )

        return [(Deny, Everyone, ALL_PERMISSIONS)]

    def collection_get_filter(self, query):
        """Allow to update the query to add some filter"""
        return query

    @cornice_view(validators=(base_validator,), permission="read")
    def collection_get(self):
        """
        """
        collection = collection_get(
            self.request, self.model,
            collection_get_callback=self.collection_get_filter)
        if not collection:
            return
        dschema = get_dschema(self.request, key='dschema_collection')
        if dschema:
            dschema.context['registry'] = self.registry
            getJsonSchema(self.request, dschema)
            return dschema.dump(collection)
        else:
            return collection.to_dict()

    def create(self, Model, params=None):
        if params is None:
            params = {}

        return Model.insert(**params)

    @cornice_view(validators=(base_validator,), permission="create")
    def collection_post(self):
        """
        """
        collection = collection_post(self.request, self.model,
                                     collection_post_callback=self.create)
        if not collection:
            return
        dschema = get_dschema(self.request)
        if dschema:
            return dschema.dump(collection, registry=self.registry)
        else:
            return collection.to_dict()

    @cornice_view(validators=(base_validator,), permission="read")
    def get(self):
        """
        """
        item = get(self.request, self.model)
        if not item:
            return
        dschema = get_dschema(self.request)
        if dschema:
            dschema.context['registry'] = self.registry
            getJsonSchema(self.request, dschema)
            return dschema.dump(item)
        else:
            return item.to_dict()

    def update(self, item, params=None):
        if params is None:
            return item

        item.update(**params)

    @cornice_view(validators=(base_validator,), permission="update")
    def put(self):
        """
        """
        item = put(self.request, self.model, put_callback=self.update)
        if not item:
            return

        dschema = get_dschema(self.request)
        if dschema:
            return dschema.dump(item, registry=self.registry)
        else:
            return item.to_dict()

    @cornice_view(validators=(base_validator,), permission="update")
    def patch(self):
        """
        """
        item = patch(self.request, self.model, patch_callback=self.update)
        if not item:
            return
        dschema = get_dschema(self.request)
        if dschema:
            return dschema.dump(item, registry=self.registry)
        else:
            return item.to_dict()

    def delete_entry(self, item):
        item.delete()

    @cornice_view(validators=(base_validator,), permission="delete")
    def delete(self):
        """
        """
        delete(self.request, self.model, delete_callback=self.delete_entry)
        return {}
