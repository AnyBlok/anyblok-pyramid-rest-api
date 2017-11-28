# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase

from ..test_bloks.test_3.schema import CustomerFullSchema
from ..test_bloks.test_4.schema import CustomerApiSchema


class SchemaBase:
    blok_entry_points = ('bloks', 'test_bloks',)

    def test_customer_schema_collection_post_load(self):
        """
        """
        body = {'body': {'name': 'bob', 'tags': [{'id': 1, 'name': 'awesome'}]}}
        data, error = self.customer_schema.load({'collection_post': body})
        self.assertEqual(len(error), 0)
        self.assertEqual(len(data['collection_post'].keys()), 1)
        body = data['collection_post']['body']
        self.assertEqual(body['name'], "bob")
        self.assertEqual(body['tags'], [{'id': 1, 'name': 'awesome'}])

    def test_customer_schema_get_load(self):
        """
        """
        data, error = self.customer_schema.load({'get': {'path': {'id': 1}}})
        self.assertEqual(len(error), 0)
        self.assertEqual(len(data['get'].keys()), 1)
        self.assertEqual(data['get']['path']['id'], 1)

    def test_customer_schema_put_load(self):
        """
        """
        data, error = self.customer_schema.load(
            {'put': {'path': {'id': 1}, 'body': {'name': 'pop'}}})
        self.assertEqual(len(error), 0)
        self.assertEqual(len(data['put'].keys()), 2)
        self.assertEqual(data['put']['path']['id'], 1)
        self.assertEqual(data['put']['body']['name'], "pop")

    def test_customer_schema_delete_load(self):
        """
        """
        data, error = self.customer_schema.load({'delete': {'path': {'id': 1}}})
        self.assertEqual(len(error), 0)
        self.assertEqual(len(data['delete'].keys()), 1)
        self.assertEqual(data['delete']['path']['id'], 1)


class TestModelSchema(SchemaBase, DBTestCase):

    def setUp(self):
        super(TestModelSchema, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_3',))
        self.customer_schema = CustomerFullSchema(
            context={'registry': self.registry})


class TestAnySchema(SchemaBase, DBTestCase):

    def setUp(self):
        super(TestAnySchema, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_4',))
        self.customer_schema = CustomerApiSchema(
            context={'registry': self.registry})
