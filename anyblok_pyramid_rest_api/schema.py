# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""A set of reusable basic schemas"""
from marshmallow import Schema, fields, post_load
from marshmallow_sqlalchemy.schema import ModelSchema as MS
from marshmallow_sqlalchemy.convert import ModelConverter as MC
from anyblok.common import anyblok_column_prefix


def format_fields(x):
    if x.startswith(anyblok_column_prefix):
        return x[len(anyblok_column_prefix):]

    return x


class ModelConverter(MC):

    def fields_for_model(self, model, include_fk=False, fields=None,
                         exclude=None, base_fields=None, dict_cls=dict):
        res = super(ModelConverter, self).fields_for_model(
            model, include_fk=include_fk, fields=fields, exclude=exclude,
            base_fields=base_fields, dict_cls=dict_cls)

        res = {format_fields(x): y for x, y in res.items()}
        return res


class ModelSchema(Schema):
    """A marshmallow schema based on the AnyBlok Model"""
    ANYBLOK_MODEL = None

    def __init__(self, *args, **kwargs):
        super(ModelSchema, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self._schema = None

    def generate_marsmallow_instance(self):
        registry = self.context.get('registry')

        class Schema(self.__class__, MS):

            load = MS.load
            dump = MS.dump
            validate = MS.validate

            class Meta:
                model = registry.get(self.ANYBLOK_MODEL)
                sqla_session = registry.Session
                model_converter = ModelConverter

            @post_load
            def make_instance(self, data):
                return data

        self._schema = Schema(*self.args, **self.kwargs)
        return self._schema

    @property
    def schema(self):
        if not self._schema:
            return self.generate_marsmallow_instance()

        return self._schema

    def load(self, *args, **kwargs):
        return self.schema.load(*args, **kwargs)

    def dump(self, *args, **kwargs):
        return self.schema.dump(*args, **kwargs)

    def validate(self, *args, **kwargs):
        return self.schema.validate(*args, **kwargs)


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
