# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice.resource import resource
from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import CrudResource
from .schema import CustomerSchema, AddressSchema


@resource(
    collection_path='/customers/v3',
    path='/customers/v3/{id}',
    installed_blok=current_blok()
)
class CustomerResourceV3(CrudResource):
    model = 'Model.Customer'
    default_schema = CustomerSchema


@resource(
    collection_path='/addresses/v3',
    path='/addresses/v3/{id}',
    installed_blok=current_blok()
)
class AddressResourceV3(CrudResource):
    model = 'Model.Address'
    default_schema = AddressSchema
