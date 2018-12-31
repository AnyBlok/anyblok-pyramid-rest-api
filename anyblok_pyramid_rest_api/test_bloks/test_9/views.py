# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2018 Jean-Sébastien Suzanne <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import (
    CrudResource, resource)
from .schema import CustomerSchema, ActionSchema


@resource(
    collection_path='/customers/v9',
    path='/customers/v9/{id}',
    service_path='%(path)s/other/%(name)s',
    installed_blok=current_blok()
)
class CustomerResourceV9(CrudResource):
    model = 'Model.Customer'
    default_schema = CustomerSchema

    @CrudResource.service('action1', verb='GET', collection=True)
    def do_action_1(self):
        return 'test'

    @CrudResource.service('action2', schema=ActionSchema)
    def do_action_2(self):
        return self.body['name']
