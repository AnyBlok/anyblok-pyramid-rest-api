# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from marshmallow import Schema, fields, validates_schema, ValidationError

from anyblok_marshmallow.schema import ModelSchema
from anyblok_pyramid_rest_api.schema import (
    FullRequestSchema,
)


class CitySchema(ModelSchema):

    class Meta:
        model = 'Model.City'


class TagSchema(ModelSchema):

    class Meta:
        model = 'Model.Tag'


class AddressSchema(ModelSchema):

    # follow the relationship Many2One and One2One
    city = fields.Nested(CitySchema)

    class Meta:
        model = 'Model.Address'


class AddressRequestSchema(FullRequestSchema):
    """Request validation for AddressSchema
    """
    body = fields.Nested(AddressSchema(
        partial=('tags', 'addresses')))
    path = fields.Nested(AddressSchema(only_primary_key=True))


class AddressFullSchema(Schema):
    collection_post = fields.Nested(AddressRequestSchema(only='body'))
    collection_get = fields.Nested(AddressRequestSchema(only='querystring'))
    get = fields.Nested(AddressRequestSchema(only='path'))
    put = fields.Nested(AddressRequestSchema(only=('body', 'path')))
    patch = fields.Nested(AddressRequestSchema(only=('body', 'path')))
    delete = fields.Nested(AddressRequestSchema(only='path'))


class CustomerSchema(ModelSchema):
    """Schema for 'Model.Customer'
    """

    # follow the relationship One2Many and Many2Many
    # - the many=True is required because it is *2Many
    # - exclude is used to forbid the recurse loop
    addresses = fields.Nested(AddressSchema, many=True, exclude=('customer', ))
    tags = fields.Nested(TagSchema, many=True)

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        unknown = set(original_data) - set(self.fields)
        if unknown:
            raise ValidationError('Unknown field', unknown)

    class Meta:
        model = 'Model.Customer'


class CustomerRequestSchema(FullRequestSchema):
    """Request validation for CustomerSchema
    """
    body = fields.Nested(CustomerSchema(partial=True))
    path = fields.Nested(CustomerSchema(only_primary_key=True))
    querystring = fields.Nested(CustomerSchema(partial=True))


class CustomerFullSchema(Schema):
    # fields for incoming request validation
    collection_post = fields.Nested(CustomerRequestSchema(only=('body',)))
    collection_get = fields.Nested(CustomerRequestSchema(only=('querystring',)))
    get = fields.Nested(CustomerRequestSchema(only=('path',)))
    put = fields.Nested(CustomerRequestSchema(only=('body', 'path',)))
    patch = fields.Nested(CustomerRequestSchema(only=('body', 'path',)))
    delete = fields.Nested(CustomerRequestSchema(only=('path',)))
    # fields for response deserialization
    dschema = fields.Nested(CustomerSchema())
    dschema_collection = fields.Nested(CustomerSchema(many=True))
