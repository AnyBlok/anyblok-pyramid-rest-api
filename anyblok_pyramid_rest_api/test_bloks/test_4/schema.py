# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sébastien Suzanne <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_marshmallow.schema import ModelSchema
from anyblok_marshmallow.fields import Nested
from anyblok_pyramid_rest_api.schema import AnySchema, ApiSchema


class CitySchema(ModelSchema):

    class Meta:
        model = 'Model.City'


class TagSchema(ModelSchema):

    class Meta:
        model = 'Model.Tag'


class AddressSchema(ModelSchema):

    # follow the relationship Many2One and One2One
    city = Nested(CitySchema)

    class Meta:
        model = 'Model.Address'


class AddressApiSchema(ApiSchema):

    class Meta:
        model = 'Model.Address'
        request_fields = ('body', 'path')
        deserialization_model_schema = AddressSchema
        serialization_model_schema = AddressSchema


class CustomerSchema(AnySchema):
    """Schema for 'Model.Customer'
    """

    # follow the relationship One2Many and Many2Many
    # - the many=True is required because it is *2Many
    # - exclude is used to forbid the recurse loop
    addresses = Nested(AddressSchema, many=True, exclude=('customer', ))
    tags = Nested(TagSchema, many=True)

    class Meta:
        model = 'Model.Customer'


class CustomerApiSchema(ApiSchema):

    class Meta:
        model = 'Model.Customer'
        deserialization_model_schema = CustomerSchema
        serialization_model_schema = CustomerSchema


class BlokApiSchema(ApiSchema):

    class Meta:
        model = 'Model.System.Blok'
