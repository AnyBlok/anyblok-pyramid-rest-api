# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice.resource import resource

from anyblok_pyramid_rest_api.crud_resource import (
    CrudResource
)

from anyblok_pyramid_rest_api.validator import (
    full_validator,
    model_schema_validator
)

from .schema import (
    CustomerRequestSchema,
    AddressRequestSchema
)


@resource(collection_path='/customers',
          path='/customers/{id}',
          schema=CustomerRequestSchema(),
          validators=(model_schema_validator,))
class CustomerResource(CrudResource):
    model = 'Model.Customer'


@resource(collection_path='/addresses',
          path='/addresses/{id}',
          schema=AddressRequestSchema(),
          validators=(full_validator,))
class AddressResource(CrudResource):
    model = 'Model.Address'
