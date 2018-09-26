# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""A set of reusable basic schemas"""
from marshmallow import Schema, fields


class FullRequestSchema(Schema):
    """A base marshmallow schema to validate the entire request
    :Example:
        >>> from marshmallow import Schema, fields
        >>> from anyblok_pyramid_rest_api.schema import FullRequestSchema
        >>> class ModelSchema(Schema):
        >>>     id = fields.Int(required=True)
        >>>     name = fields.Str(required=True)
        >>> class RequestModelSchema(FullRequestSchema):
        >>>     body = fields.Nested(ModelSchema(partial=('id',)))
        >>>     path = fields.Nested(ModelSchema(partial=('name',)))
    """
    body = fields.Dict()
    url = fields.Str()
    path = fields.Dict()
    method = fields.Str()
    querystring = fields.Dict()
    headers = fields.Dict()
    cookies = fields.Dict()
