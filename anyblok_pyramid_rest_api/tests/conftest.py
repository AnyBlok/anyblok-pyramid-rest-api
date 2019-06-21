# This file is a part of the AnyBlok project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Denis VIVIÈS <dvivies@geoblink.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import logging
import pytest
from anyblok.tests.conftest import *  # noqa
from anyblok.tests.conftest import init_registry_with_bloks


logger = logging.getLogger(__name__)


# Pyramid
from webtest import TestApp  # noqa
from anyblok_pyramid.pyramid_config import Configurator  # noqa


@pytest.fixture(scope="class")
def webserver(request):
    config = Configurator()
    config.include_from_entry_point()
    # No param here # for includeme in self.includemes:
    # No param here #     config.include(includeme)

    config.load_config_bloks()
    app = config.make_wsgi_app()
    return TestApp(app)


# rest api


@pytest.fixture(scope="class")
def registry_rest_api_1(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_1'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_2(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_2'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_3(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_3'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_4(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_4'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_5(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_5'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_5_logged(request, testbloks_loaded):
    registry = init_registry_with_bloks(
        ['test_rest_api_5', 'auth-password'], None)
    request.addfinalizer(registry.close)

    registry.User.insert(
        login='jssuzanne', first_name='js', last_name='Suzanne')
    registry.User.CredentialStore.insert(
        login='jssuzanne', password='mypassword')
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_6(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_6'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_7(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_7'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_8(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_8'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_9(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_9'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_rest_api_10(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_rest_api_10'], None)
    request.addfinalizer(registry.close)
    return registry
