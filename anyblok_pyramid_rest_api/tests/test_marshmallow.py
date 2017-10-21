# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import DBTestCase
from anyblok.column import Integer, String
from anyblok.relationship import Many2One
from anyblok_pyramid_rest_api.schema import ModelSchema
from marshmallow import fields


def add_simple_model():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        number = Integer()


def add_complexe_model():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class City:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        zipcode = String(nullable=False)

    @Declarations.register(Declarations.Model)
    class Customer:
        id = Integer(primary_key=True)
        name = String(nullable=False)

    @Declarations.register(Declarations.Model)
    class Address:
        id = Integer(primary_key=True)
        street = String(nullable=False)
        city = Many2One(model=Declarations.Model.City, nullable=False)
        customer = Many2One(
            model=Declarations.Model.Customer, nullable=False,
            one2many="addresses")


class ExempleSchema(ModelSchema):
    ANYBLOK_MODEL = 'Model.Exemple'


class CitySchema(ModelSchema):
    ANYBLOK_MODEL = 'Model.City'


class AddressSchema(ModelSchema):
    ANYBLOK_MODEL = 'Model.Address'
    city = fields.Nested(CitySchema)


class CustomerSchema(ModelSchema):
    ANYBLOK_MODEL = 'Model.Customer'
    addresses = fields.Nested(AddressSchema, many=True, exclude=('customer', ))


class TestMarshmallow(DBTestCase):

    def test_dump_simple_schema(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.dump(exemple)
        self.assertFalse(errors)
        self.assertEqual(data, {'number': None, 'id': 1, 'name': 'test'})

    def test_load_simple_schema_1(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load(
            {'id': exemple.id, 'name': exemple.name})
        self.assertEqual(data, {'id': exemple.id, 'name': exemple.name})
        self.assertFalse(errors)

    def test_load_simple_schema_2(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id})
        self.assertEqual(data, {'id': exemple.id})
        self.assertEqual(
            errors, {'name': ["Missing data for required field."]})

    def test_load_simple_schema_3(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id})
        self.assertFalse(errors)
        self.assertEqual(data, {'id': exemple.id})

    def test_load_simple_schema_4(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(
            partial=('name',), context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        data, errors = exemple_schema.load({'id': exemple.id, 'name': None})
        self.assertEqual(errors, {'name': ['Field may not be null.']})
        self.assertEqual(data, {'id': exemple.id})

    def test_validate_simple_schema(self):
        registry = self.init_registry(add_simple_model)
        exemple_schema = ExempleSchema(context={'registry': registry})
        exemple = registry.Exemple.insert(name="test")
        errors = exemple_schema.validate(
            {'id': exemple.id, 'name': exemple.name, 'number': 'test'})
        self.assertEqual(errors, {'number': ['Not a valid integer.']})

    def test_dump_complexe_schema(self):
        registry = self.init_registry(add_complexe_model)
        customer_schema = CustomerSchema(context={'registry': registry})
        customer = registry.Customer.insert(name="C1")
        city = registry.City.insert(name="Rouen", zipcode="76000")
        address = registry.Address.insert(
            customer=customer, city=city, street="Somewhere")
        data, errors = customer_schema.dump(customer)
        self.assertFalse(errors)
        self.assertEqual(
            data,
            {
                'id': customer.id,
                'name': customer.name,
                'addresses': [
                    {
                        'id': address.id,
                        'street': address.street,
                        'city': {
                            'id': city.id,
                            'name': city.name,
                            'zipcode': city.zipcode,
                        },
                    },
                ],
            }
        )
