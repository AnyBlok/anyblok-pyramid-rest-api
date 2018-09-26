# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_marshmallow import SchemaWrapper
from marshmallow import validates_schema, ValidationError
from anyblok_marshmallow.fields import Nested


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

        @validates_schema(pass_original=True)
        def check_unknown_fields(self, data, original_data):
            unknown = set(original_data) - set(self.fields)
            if unknown:
                raise ValidationError('Unknown field', unknown)
