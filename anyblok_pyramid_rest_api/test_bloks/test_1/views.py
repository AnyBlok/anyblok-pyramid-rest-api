# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice import Service
from cornice.resource import resource

from marshmallow import Schema, fields

from anyblok_pyramid_rest_api.crud_resource import CrudResource
from anyblok_pyramid_rest_api.validator import (
    # base_validator,
    body_validator,
    full_validator
)


class ExampleSchema(Schema):
    """A basic marshmallow schema example
    """
    id = fields.Int(required=True)
    name = fields.Str(required=True)


@resource(collection_path='/examples', path='/examples/{id}')
class ExampleResource(CrudResource):
    """ CrudResource basic example. No validator, no schema
    """
    model = 'Model.Example'


@resource(collection_path='/basevalidator/examples',
          path='/basevalidator/examples/{id}',
          validators=(full_validator,))
class ExampleResourceBaseValidator(CrudResource):
    """ CrudResource basic example with base validator
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
    schema=ExampleSchema())
def another_service_put(request):
    """ full_validator + full schema
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.query().get(request.validated['path']['id'])
    item.update(**request.validated['body'])
    return item.to_dict()


@another_collection_service.post(
    validators=(body_validator,),
    schema=ExampleSchema(partial=('id',)))
def another_service_post(request):
    """ body_validator + schema.
    As it is a POST, exclude 'id' from validation with the `partial` arg
    on schema instantiation
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.insert(**request.validated)
    return item.to_dict()
