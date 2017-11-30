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

from anyblok_pyramid_rest_api.validator import (
    full_validator,
    model_schema_validator
)

from .schema import (
    CustomerApiSchema,
    AddressApiSchema,
    BlokApiSchema
)


@resource(
    collection_path='/customers/v4',
    path='/customers/v4/{id}',
    schema=CustomerApiSchema(),
    validators=(model_schema_validator,),
    installed_blok=current_blok()
)
class CustomerResourceV4(CrudResource):
    model = 'Model.Customer'


@resource(
    collection_path='/addresses/v4',
    path='/addresses/v4/{id}',
    schema=AddressApiSchema(),
    validators=(full_validator,),
    installed_blok=current_blok()
)
class AddressResourceV4(CrudResource):
    model = 'Model.Address'


@resource(
    collection_path='/bloks/v4',
    path='/bloks/v4/{name}',
    schema=BlokApiSchema(),
    validators=(model_schema_validator,),
    installed_blok=current_blok()
)
class BlokResourceV4(CrudResource):
    model = 'Model.System.Blok'
