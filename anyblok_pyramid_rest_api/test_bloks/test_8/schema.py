# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sébastien Suzanne <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_marshmallow import SchemaWrapper
from marshmallow.schema import Schema
from anyblok_marshmallow.fields import Nested, String


class CitySchema(SchemaWrapper):
    model = 'Model.City'


class TagSchema(SchemaWrapper):
    model = 'Model.Tag'


class AddressSchema(SchemaWrapper):
    model = 'Model.Address'

    class Schema:
        # follow the relationship Many2One and One2One
        city = Nested(CitySchema)


class CustomerSchema(SchemaWrapper):
    """Schema for 'Model.Customer'
    """
    model = 'Model.Customer'

    class Schema:
        # follow the relationship One2Many and Many2Many
        # - the many=True is required because it is *2Many
        # - exclude is used to forbid the recurse loop
        addresses = Nested(AddressSchema, many=True, exclude=('customer', ))
        tags = Nested(TagSchema, many=True)


class ActionSchema(Schema):
    name = String(required=True)
