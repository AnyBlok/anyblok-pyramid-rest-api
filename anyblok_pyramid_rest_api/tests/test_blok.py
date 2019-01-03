# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok.registry import RegistryManagerException
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request


class TestBlokApi2:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_2):
        transaction = registry_rest_api_2.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_predicate(self, registry_rest_api_2, webserver):
        webserver.get('/bloks1', status=200)
        webserver.get('/bloks2', status=200)

    def test_multi_primary_keys(self, webserver):
        resp = webserver.get(
            '/column/Model.System.Model/name', status=200)
        assert resp.json_body == {
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
        }

    def test_bad_model(self, webserver):
        with pytest.raises(RegistryManagerException):
            webserver.get('/bad/model')


class TestBlok:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_testblok):
        transaction = registry_testblok.begin_nested()

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        return

    def test_predicate(self, webserver):
        webserver.get('/bloks1', status=404)
        webserver.get('/bloks2', status=200)

    def test_saved_errors_in_request(self, registry_testblok):
        registry = registry_testblok

        class Error:
            def __init__(self):
                self._errors = []
                self.status = 0

            def add(self, *a):
                self._errors.append(a)

        class A:
            def __init__(self):
                self.registry = registry

        class Request:
            anyblok = A()
            errors = Error()

        request = Request()
        with saved_errors_in_request(request):
            raise Exception()

        assert request.errors.status == 500


class TestCrudResourceBlokModelSchemaValidator:
    """Test Customers and Addresses from
    test_bloks/test_5/views.py
    """
    collection_path = '/bloks/v5'
    path = '/bloks/v5/%s'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_5):
        transaction = registry_rest_api_5.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_model_schema_validator_get(self, registry_rest_api_5, webserver):
        response = webserver.get(self.path % 'anyblok-core')
        assert response.status_code == 200
        assert response.json_body == {
            'author': 'Suzanne Jean-Sébastien',
            'name': 'anyblok-core',
            'order': 0,
            'state': 'installed',
        }
