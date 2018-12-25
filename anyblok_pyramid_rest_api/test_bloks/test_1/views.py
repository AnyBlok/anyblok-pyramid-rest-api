# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice import Service
from cornice.resource import resource
from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.validator import (
    service_collection_get_validator,
    service_post_validator,
    service_get_validator,
    service_put_validator,
    service_delete_validator,
)
from anyblok_pyramid_rest_api.crud_resource import (
    CrudResource,
    get_items,
    post_item,
    get_item,
    put_item,
    delete_item,
)
from .schema import (ExampleSchema, ExamplePathSchema, ThingSchema,
                     ThingRequestSchema, AnotherSchema)


@resource(collection_path='/examples', path='/examples/{id}',
          installed_blok=current_blok())
class ExampleResource(CrudResource):
    model = 'Model.Example'


@resource(collection_path='/with/default/schema/examples',
          path='/with/default/schema/examples/{id}',
          installed_blok=current_blok())
class ExampleResourceWithDefaultSchema(CrudResource):
    model = 'Model.Example'
    default_schema = ExampleSchema
    default_path_schema = ExamplePathSchema


# another endpoint through a service with the same model
another_service = Service(name='another_service', path='/anothers/{id}')


# another collection endpoint through a service with the same model
another_collection_service = Service(
    name='another_collection_service',
    path='/anothers')


@another_service.get()
def another_service_get(request):
    """ No validator, no schema
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.query().get(request.matchdict['id'])
    return item.to_dict()


@another_service.put(validators=(service_put_validator,), schema=AnotherSchema)
def another_service_put(request):
    """ full_validator + AnotherSchema
    """
    registry = request.anyblok.registry
    Model = registry.get('Model.Example')
    item = Model.query().get(request.validated.get('path').get('id'))
    item.update(**request.validated.get('body'))
    return item.to_dict()


@another_collection_service.post(validators=(service_post_validator,),
                                 schema=AnotherSchema)
def another_service_post(request):
    """ body_validator + schema
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.insert(**request.validated['body'])
    return item.to_dict()


# thing endpoint through a service with the same model
thing_service = Service(name='thing_service', path='/things/{uuid}')

# thing collection endpoint through a service with the same model
thing_collection_service = Service(
    name='thing_collection_service',
    path='/things')


@thing_service.get(validators=(service_get_validator,),
                   schema=ThingRequestSchema)
def thing_service_get(request):
    """ Use Full validator with a request schema but Validate
    only the path
    """
    schema = ThingSchema()
    item = get_item(request, 'Model.Thing')
    return schema.dump(item)


@thing_service.put(validators=(service_put_validator,),
                   schema=ThingRequestSchema)
def thing_service_put(request):
    """ full_validator + RequestSchema
    """
    item = put_item(request, 'Model.Thing')
    schema = ThingSchema()
    return schema.dump(item)


@thing_service.delete(validators=(service_delete_validator,),
                      schema=ThingRequestSchema)
def thing_service_delete(request):
    """ full_validator + AnotherSchema
    """
    item = delete_item(request, 'Model.Thing')
    return item


@thing_collection_service.post(validators=(service_post_validator,),
                               schema=ThingRequestSchema)
def thing_service_post(request):
    """ body_validator + schema
    """
    item = post_item(request, 'Model.Thing')
    schema = ThingSchema()
    return schema.dump(item)


@thing_collection_service.get(validators=(service_collection_get_validator,),
                              schema=ThingRequestSchema)
def thing_service_get_collection(request):
    """ full_validator + querystring schema validation + schema validation
    for response data
    """
    schema = ThingSchema(many=True)
    collection = get_items(request, 'Model.Thing')
    return schema.dump(collection)


@resource(collection_path='/examples/with/errors',
          path='/examples/with/error/{id}',
          installed_blok=current_blok())
class ExampleResourceWithError(CrudResource):
    model = 'Model.Example'

    def add_error(self):
        self.request.errors.add('body', '500 Internal Server Error', 'test')
        self.request.errors.status = 500

    def create(self, Model, params):
        item = super(ExampleResourceWithError, self).create(Model, params)
        self.add_error()
        return item

    def update(self, item, params=None):
        super(ExampleResourceWithError, self).update(item, params=params)
        self.add_error()

    def delete_entry(self, item):
        super(ExampleResourceWithError, self).delete_entry(item)
        self.add_error()

    def collection_update(self, querystring, params=None):
        items = super(ExampleResourceWithError, self).collection_update(
            querystring, params=params)
        self.add_error()
        return items

    def delete_entries(self, querystring):
        count = super(ExampleResourceWithError, self).delete_entries(
            querystring)
        self.add_error()
        return count
