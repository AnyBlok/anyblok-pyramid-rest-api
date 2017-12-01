# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""A set of reusable basic schemas"""
from marshmallow import Schema, fields
from anyblok_marshmallow.schema import ModelSchema
from anyblok_marshmallow.fields import Nested
from marshmallow.schema import SchemaOpts, SchemaMeta
from marshmallow.compat import with_metaclass


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


class ApiSchemaOptions(SchemaOpts):

    def __init__(self, meta, *a, **kw):
        super(ApiSchemaOptions, self).__init__(meta, *a, **kw)
        self.model = getattr(meta, 'model', None)
        # serialization opts
        self.serialization_model_schema = getattr(
            meta, 'serialization_model_schema', None)
        self.dschema_opts = getattr(meta, 'dschema_opts', {})
        self.dschema_collection_opts = getattr(
            meta, 'dschema_collection_opts', {'many': True})

        # deserialization : request
        self.deserialization_request_schema = getattr(
            meta, 'deserialization_request_schema', None)
        self.collection_post_opts = getattr(
            meta, 'collection_post_opts', {'only': ('body',)})
        self.collection_get_opts = getattr(
            meta, 'collection_get_opts', {'only': ('querystring',)})
        self.get_opts = getattr(meta, 'get_opts', {'only': ('path',)})
        self.putt_opts = getattr(meta, 'put_opts', {'only': ('body', 'path')})
        self.patch_opts = getattr(
            meta, 'patch_opts', {'only': ('body', 'path')})
        self.delete_opts = getattr(
            meta, 'delete_opts', {'only': ('path',)})

        # deserialization : model
        self.deserialization_model_schema = getattr(
            meta, 'deserialization_model_schema', None)
        self.request_fields = getattr(
            meta, 'request_fields', ['path', 'body', 'querystring'])
        if not isinstance(self.request_fields, (list, tuple)):
            raise Exception("bad type")

        self.path_opts = getattr(
            meta, 'path_opts', {'only_primary_key': True})
        self.body_opts = getattr(
            meta, 'body_opts', {'partial': True})
        self.querystring_opts = getattr(
            meta, 'querystring_opts', {'partial': True})


class ApiSchemaMeta(SchemaMeta):

    @classmethod
    def get_declared_fields(cls, klass, cls_fields, inherited_fields,
                            dict_cls):
        base_fields = super(ApiSchemaMeta, cls).get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls)
        declared_fields = cls.get_fields(klass.opts, base_fields, dict_cls)
        declared_fields.update(base_fields)
        return declared_fields

    @classmethod
    def get_fields(cls, opts, base_fields, dict_cls):
        declared_fields = dict_cls()
        known_fields = [x[0] for x in base_fields]

        deserialization_fields = [
            x
            for x in ('collection_get', 'collection_post', 'get', 'put',
                      'patch', 'delete')
            if x not in known_fields
        ]
        deserialization_request_schema = opts.deserialization_request_schema
        if not deserialization_request_schema and opts.model:
            deserialization_request_schema = (
                cls.getDeserializationRequestSchema(opts)
            )

        serialization_fields = [
            x
            for x in ('dschema', 'dschema_collection')
            if x not in known_fields
        ]
        serialization_model_schema = opts.serialization_model_schema
        if not serialization_model_schema and opts.model:
            serialization_model_schema = cls.getSerializationModelSchema(opts)

        if deserialization_request_schema:
            for field in deserialization_fields:
                declared_fields[field] = Nested(
                    deserialization_request_schema(
                        **getattr(opts, field + '_opts', {})
                    )
                )

        if serialization_model_schema:
            for field in serialization_fields:
                declared_fields[field] = Nested(
                    serialization_model_schema(
                        **getattr(opts, field + '_opts', {})
                    )
                )

        return declared_fields

    @classmethod
    def getDeserializationModelSchema(cls, opts):
        name = "Deserialization.Model.Schema." + opts.model
        properties = {
            'Meta': type('Meta', tuple(), dict(model=opts.model))
        }
        return type(name, (ModelSchema,), properties)

    @classmethod
    def getDeserializationRequestSchema(cls, opts):
        name = "Deserialization.Schema." + opts.model
        properties = {}
        deserialization_model_schema = opts.deserialization_model_schema
        if not deserialization_model_schema and opts.model:
            deserialization_model_schema = (
                cls.getDeserializationModelSchema(opts)
            )

        if deserialization_model_schema:
            for field in opts.request_fields:
                properties[field] = Nested(
                    deserialization_model_schema(
                        **getattr(opts, field + '_opts', {})
                    )
                )

        return type(name, (FullRequestSchema,), properties)

    @classmethod
    def getSerializationModelSchema(cls, opts):
        name = "Serialization.Model.Schema." + opts.model
        properties = {
            'Meta': type('Meta', tuple(), dict(model=opts.model))
        }
        return type(name, (ModelSchema,), properties)


class ApiSchema(with_metaclass(ApiSchemaMeta, Schema)):
    OPTIONS_CLASS = ApiSchemaOptions
