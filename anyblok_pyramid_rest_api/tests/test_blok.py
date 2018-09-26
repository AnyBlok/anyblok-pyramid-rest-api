# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidDBTestCase
from anyblok.registry import RegistryManagerException


class TestCrudBlok(PyramidDBTestCase):

    blok_entry_points = ('bloks', 'test_bloks')

    def test_predicate(self):
        registry = self.init_registry(None)
        self.webserver.get('/bloks1', status=404)
        self.webserver.get('/bloks2', status=200)
        registry.upgrade(install=('test_rest_api_2',))
        self.webserver.get('/bloks1', status=200)
        self.webserver.get('/bloks2', status=200)

    def test_multi_primary_keys(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_rest_api_2',))
        resp = self.webserver.get(
            '/column/Model.System.Model/name', status=200)
        self.assertEqual(resp.json_body, {
            'autoincrement': False,
            'code': 'system_model.name',
            'entity_type': 'Model.System.Column',
            'foreign_key': None,
            'ftype': 'String',
            'label': 'Name',
            'model': 'Model.System.Model',
            'name': 'name',
            'nullable': False,
            'primary_key': True,
            'remote_model': None,
            'unique': None
        })

    def test_bad_model(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test_rest_api_2',))
        with self.assertRaises(RegistryManagerException):
            self.webserver.get('/bad/model')


class CrudResourceBlok:

    blok_entry_points = ('bloks', 'test_bloks')

    def test_model_schema_validator_get(self):
        response = self.webserver.get(self.path % 'anyblok-core')
        self.assertEqual(response.status_code, 200)
        # self.maxDiff = None
        self.assertEqual(
            response.json_body,
            {
                'author': 'Suzanne Jean-Sébastien',
                'name': 'anyblok-core',
                'order': 0,
                'state': 'installed',
            }
        )


class TestCrudResourceBlokModelSchemaValidator(CrudResourceBlok,
                                               PyramidDBTestCase):
    """Test Customers and Addresses from
    test_bloks/test_5/views.py
    """

    def setUp(self):
        super(TestCrudResourceBlokModelSchemaValidator, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_5',))
        self.collection_path = '/bloks/v5'
        self.path = '/bloks/v5/%s'
