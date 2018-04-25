# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice import Service
from cornice.resource import resource

from anyblok_pyramid_rest_api.crud_resource import (
    CrudResource,
    collection_get,
    collection_post,
    get,
    put,
    delete
)
from anyblok_pyramid_rest_api.validator import (
    body_validator,
    full_validator
)
from .schema import (
    ExampleSchema,
    AnotherSchema,
    ThingSchema,
    ThingRequestSchema
)


@resource(collection_path='/examples', path='/examples/{id}')
class ExampleResource(CrudResource):
    """CrudResource basic example. No validator, no schema
    """
    model = 'Model.Example'


@resource(collection_path='/basevalidator/examples',
          path='/basevalidator/examples/{id}',
          validators=(full_validator,))
class ExampleResourceBaseValidator(CrudResource):
    """CrudResource basic example with base validator
    """
    model = 'Model.Example'


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


@another_service.put(
    validators=(full_validator,),
    schema=AnotherSchema())
def another_service_put(request):
    """ full_validator + AnotherSchema
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.query().get(request.validated.get('path').get('id'))
    item.update(**request.validated.get('body'))
    return item.to_dict()


@another_collection_service.post(
    validators=(body_validator,),
    schema=ExampleSchema(partial=('id',)))
def another_service_post(request):
    """ body_validator + schema
    As it is a POST, exclude 'id' from validation with the `partial` arg
    on schema instantiation
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.insert(**request.validated)
    return item.to_dict()


# thing endpoint through a service with the same model
thing_service = Service(name='thing_service', path='/things/{uuid}')

# thing collection endpoint through a service with the same model
thing_collection_service = Service(
    name='thing_collection_service',
    path='/things')


@thing_service.get(
    validators=(full_validator,),
    schema=ThingRequestSchema(only=('path',)))
def thing_service_get(request):
    """ Use Full validator with a request schema but Validate
    only the path
    """
    schema = ThingSchema()
    item = get(request, 'Model.Thing')
    return schema.dump(item)


@thing_service.put(
    validators=(full_validator,),
    schema=ThingRequestSchema(only=('path', 'body')))
def thing_service_put(request):
    """ full_validator + RequestSchema
    """
    item = put(request, 'Model.Thing')
    schema = ThingSchema()
    return schema.dump(item)


@thing_service.delete(
    validators=(full_validator,),
    schema=ThingRequestSchema(only=('path',)))
def thing_service_delete(request):
    """ full_validator + AnotherSchema
    """
    item = delete(request, 'Model.Thing')
    return item


@thing_collection_service.post(
    validators=(body_validator,),
    schema=ThingSchema(exclude=('uuid',)))
def thing_service_post(request):
    """ body_validator + schema
    As it is a POST, exclude 'id' from validation with the `partial` arg
    on schema instantiation
    """
    item = collection_post(request, 'Model.Thing')
    schema = ThingSchema()
    return schema.dump(item)


@thing_collection_service.get(
    validators=(full_validator,),
    schema=ThingRequestSchema(only=('querystring')))
def thing_service_get_collection(request):
    """ full_validator + querystring schema validation + schema validation
    for response data
    """
    schema = ThingSchema(many=True)
    collection = collection_get(request, 'Model.Thing')
    return schema.dump(collection)
