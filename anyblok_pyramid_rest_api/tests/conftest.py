# This file is a part of the AnyBlok project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Denis VIVIÈS <dvivies@geoblink.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import logging
from copy import deepcopy
import pytest
from anyblok.blok import BlokManager
from anyblok.config import Configuration
from anyblok.environment import EnvironmentManager
from anyblok.registry import RegistryManager
from copy import copy
import sqlalchemy
from sqlalchemy_utils.functions import database_exists, create_database, orm
import os

logger = logging.getLogger(__name__)


def init_registry_with_bloks(bloks, function, **kwargs):
    if bloks is None:
        bloks = []
    if isinstance(bloks, tuple):
        bloks = list(bloks)
    if isinstance(bloks, str):
        bloks = [bloks]

    anyblok_test_name = 'anyblok-test'
    if anyblok_test_name not in bloks:
        bloks.append(anyblok_test_name)

    loaded_bloks = deepcopy(RegistryManager.loaded_bloks)
    if function is not None:
        EnvironmentManager.set('current_blok', anyblok_test_name)
        try:
            function(**kwargs)
        finally:
            EnvironmentManager.set('current_blok', None)
    try:
        registry = RegistryManager.get(
            Configuration.get('db_name'),
            unittest=True)

        # update required blok
        registry_bloks = registry.get_bloks_by_states('installed', 'toinstall')
        toinstall = [x for x in bloks if x not in registry_bloks]
        toupdate = [x for x in bloks if x in registry_bloks]
        registry.upgrade(install=toinstall, update=toupdate)
    finally:
        RegistryManager.loaded_bloks = loaded_bloks

    return registry


def init_registry(function, **kwargs):
    return init_registry_with_bloks([], function, **kwargs)


def drop_database(url):
    url = copy(sqlalchemy.engine.url.make_url(url))
    database = url.database
    if url.drivername.startswith('postgresql'):
        url.database = 'postgres'
    elif not url.drivername.startswith('sqlite'):
        url.database = None

    engine = sqlalchemy.create_engine(url)
    if engine.dialect.name == 'sqlite' and url.database != ':memory:':
        os.remove(url.database)
    else:
        text = 'DROP DATABASE {0}'.format(orm.quote(engine, database))
        cnx = engine.connect()
        cnx.execute("ROLLBACK")
        cnx.execute(text)
        cnx.execute("commit")
        cnx.close()


@pytest.fixture(scope="session")
def base_loaded(request):
    url = Configuration.get('get_url')()
    if not database_exists(url):
        db_template_name = Configuration.get('db_template_name', None)
        create_database(url, template=db_template_name)

    BlokManager.load()
    registry = init_registry_with_bloks([], None)
    registry.commit()
    registry.close()
    BlokManager.unload()


@pytest.fixture(scope="module")
def bloks_loaded(request, base_loaded):
    request.addfinalizer(BlokManager.unload)
    BlokManager.load()


@pytest.fixture(scope="module")
def testbloks_loaded(request, base_loaded):
    request.addfinalizer(BlokManager.unload)
    BlokManager.load(entry_points=('bloks', 'test_bloks'))


@pytest.fixture(scope="class")
def registry_blok(request, bloks_loaded):
    registry = init_registry_with_bloks([], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_testblok(request, testbloks_loaded):
    registry = init_registry_with_bloks([], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="function")
def registry_testblok_func(request, testbloks_loaded):
    registry = init_registry_with_bloks([], None)
    request.addfinalizer(registry.close)
    return registry


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
