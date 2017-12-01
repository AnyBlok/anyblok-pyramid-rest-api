# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice.resource import resource
from anyblok_pyramid import current_blok

from anyblok_pyramid_rest_api.crud_resource import (
    CrudResource
)

from anyblok_pyramid_rest_api.validator import model_schema_validator

from .schema import (
    CustomerSchema,
    AddressSchema,
)


@resource(
    collection_path='/customers/v5',
    path='/customers/v5/{id}',
    validators=(model_schema_validator,),
    installed_blok=current_blok()
)
class CustomerResourceV5(CrudResource):
    model = 'Model.Customer'

    @classmethod
    def apischema_properties(cls, metaProperties):
        metaProperties.update({
            'deserialization_model_schema': CustomerSchema,
            'serialization_model_schema': CustomerSchema,
        })


@resource(
    collection_path='/addresses/v5',
    path='/addresses/v5/{id}',
    validators=(model_schema_validator,),
    installed_blok=current_blok()
)
class AddressResourceV5(CrudResource):
    model = 'Model.Address'

    @classmethod
    def apischema_properties(cls, metaProperties):
        metaProperties.update({
            'request_fields': ('path', 'body'),
            'deserialization_model_schema': AddressSchema,
            'serialization_model_schema': AddressSchema,
        })


@resource(
    collection_path='/bloks/v5',
    path='/bloks/v5/{name}',
    validators=(model_schema_validator,),
    installed_blok=current_blok()
)
class BlokResourceV5(CrudResource):
    model = 'Model.System.Blok'

    @classmethod
    def apischema_properties(cls, metaProperties):
        metaProperties.update({
            'dschema_opts': {
                'only': ['author', 'order', 'name', 'state']},
            'dschema_collection_opts': {
                'only': ['author', 'order', 'name', 'state']},
        })
