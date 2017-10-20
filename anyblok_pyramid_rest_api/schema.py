# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
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


class ModelSchema:
    model = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def generate_marsmallow_instance(self, registry):

        class Schema(MS):
            class Meta:
                model = registry.get(self.model)
                sqla_session = registry.Session
                model_converter = ModelConverter

        self.schema = Schema(*self.args, **self.kwargs)
        return self.schema

    def load(self, *args, **kwargs):
        data, errors = self.schema.load(*args, **kwargs)
        if not isinstance(data, dict):
            data = self.dump(data, *args[1:], **kwargs).data

        return data, errors

    def dump(self, *args, **kwargs):
        return self.schema.dump(*args, **kwargs)
