# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from marshmallow import fields, Schema

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
        strict = True
        model = 'Model.Address'


class AddressRequestSchema(FullRequestSchema):
    """Request validation for AddressSchema
    """
    body = fields.Nested(AddressSchema(
        partial=('tags', 'addresses')))
    path = fields.Nested(AddressSchema(only=('id',)))


class AddressFullSchema(Schema):
    post_collection = fields.Nested(AddressRequestSchema(only='body'))
    get_collection = fields.Nested(AddressRequestSchema(only='querystring'))
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

    class Meta:
        strict = True
        model = 'Model.Customer'
        # optionally attach an AnyBlok registry
        # to use for serialization, desarialization and validation
        # registry = registry
        # optionally return an AnyBlok model instance
        # post_load_return_instance = True


class CustomerRequestSchema(FullRequestSchema):
    """Request validation for CustomerSchema
    """
    body = fields.Nested(CustomerSchema(
        partial=('name', 'tags', 'addresses')))
    path = fields.Nested(CustomerSchema(only=('id',)))
    querystring = fields.Nested(CustomerSchema(partial=True))


class CustomerFullSchema(Schema):
    post_collection = fields.Nested(CustomerRequestSchema(only='body'))
    get_collection = fields.Nested(CustomerRequestSchema(only='querystring'))
    get = fields.Nested(CustomerRequestSchema(only='path'))
    put = fields.Nested(CustomerRequestSchema(only=('body', 'path')))
    patch = fields.Nested(CustomerRequestSchema(only=('body', 'path')))
    delete = fields.Nested(CustomerRequestSchema(only='path'))
