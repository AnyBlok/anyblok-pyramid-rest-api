# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import DBTestCase
from anyblok.column import Integer, String
from anyblok_pyramid_rest_api.schema import ModelSchema


def add_model():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        number = Integer()


class ExempleSchema(ModelSchema):
    model = 'Model.Exemple'


class TestMarshmallow(DBTestCase):

    def test_dump_simple_schema(self):
        exemple_schema = ExempleSchema()
        registry = self.init_registry(add_model)
        exemple_schema.generate_marsmallow_instance(registry)
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(data, {'number': None, 'id': 1, 'name': 'test'})

    def test_load_simple_schema_1(self):
        exemple_schema = ExempleSchema()
        registry = self.init_registry(add_model)
        exemple_schema.generate_marsmallow_instance(registry)
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id})
        self.assertEqual(data, {'id': exemple.id})
        self.assertEqual(
            errors, {'name': ["Missing data for required field."]})

    def test_load_simple_schema_2(self):
        exemple_schema = ExempleSchema(partial=('name',))
        registry = self.init_registry(add_model)
        exemple_schema.generate_marsmallow_instance(registry)
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id})
        self.assertFalse(errors)
        self.assertEqual(data, {'number': None, 'id': exemple.id, 'name': None})
