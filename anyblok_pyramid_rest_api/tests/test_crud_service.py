# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest


class TestCrudServiceBase:
    """Test Service from test_bloks/test_1/views.py:example_service
    This is the basic case, no validators, no schema.
    """

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_1):
        transaction = registry_rest_api_1.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def create_example(self, registry, name="plop"):
        """Create a dummy example record"""
        return registry.Example.insert(name=name)

    def test_example_service_get(self, registry_rest_api_1, webserver):
        """Example GET /anothers/{id}"""
        ex = self.create_example(registry_rest_api_1)
        response = webserver.get('/anothers/%s' % ex.id)
        assert response.status_code == 200
        assert response.json_body.get('name') == "plop"

    def test_example_service_put(self, registry_rest_api_1, webserver):
        """Example PUT /anothers/{id}"""
        ex = self.create_example(registry_rest_api_1)
        response = webserver.put_json(
            '/anothers/%s' % ex.id, {'name': 'plip'})
        assert response.status_code == 200
        assert response.json_body.get('name') == "plip"

    def test_example_service_put_schema_fail_bad_path(
        self, registry_rest_api_1, webserver
    ):
        """Example PUT schema validation fail on invalid path /anothers/{id}
        """
        fail = webserver.put_json(
            '/anothers/x', {'name': 'plip'}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'path'

    def test_example_service_put_schema_fail_bad_value_type(
        self, registry_rest_api_1, webserver
    ):
        """Example PUT schema validation fail on invalid value type in `body`
        /anothers/{id}
        """
        ex = self.create_example(registry_rest_api_1)
        fail = webserver.put_json(
            '/anothers/%s' % ex.id, {'name': 0}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'

    def test_example_service_post(self, registry_rest_api_1, webserver):
        """Example POST /anothers/"""
        response = webserver.post_json('/anothers', {'name': 'plip'})
        assert response.status_code == 200
        assert response.json_body.get('name') == "plip"

    def test_example_service_post_schema_fail_bad_column_name(
        self, registry_rest_api_1, webserver
    ):
        """Example POST schema validation fail on invalid column name /anothers/
        """
        fail = webserver.post_json(
            '/anothers', {'badcolumn': 'plip'}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'

    def test_example_service_post_schema_fail_bad_value_type(
        self, registry_rest_api_1, webserver
    ):
        """Example POST schema validation fail on invalid value type /anothers/
        """
        fail = webserver.post_json(
            '/anothers', {'name': 0}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'


class TestCrudServiceAdvanced:
    """Test Service from test_bloks/test_1/views.py:thing_service
    This is the advanced case, validators and relationnal schema
    """

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_1):
        transaction = registry_rest_api_1.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def create_example(self, registry, name="plop"):
        """Create a dummy example record"""
        return registry.Example.insert(name=name)

    def create_examples(self, registry, examples=None):
        """Create a dummy example collection record"""
        res = []
        if examples is None:
            examples = [dict(name="car example"),
                        dict(name="apple example"),
                        dict(name="human example")]
        for example in examples:
            res.append(self.create_example(registry, **example))
        return res

    def create_thing(self, registry, name="car", secret="aaa", **kwargs):
        """Create a dummy thing record"""
        if 'example_id' not in kwargs.keys():
            example = self.create_example(registry, name="%s example" % name)
            kwargs['example_id'] = example.id
        thing = registry.Thing.insert(name=name, secret=secret, **kwargs)
        return thing

    def create_things(self, registry, things=None):
        """Create a dummy thing collection record"""
        res = []
        if things is None:
            exs = self.create_examples(registry)
            things = [dict(name="car", secret="aaa", example_id=exs[0].id),
                      dict(name="apple", secret="bbb", example_id=exs[1].id),
                      dict(name="human", secret="ccc", example_id=exs[2].id)]
        for thing in things:
            res.append(self.create_thing(registry, **thing))
        return res

    def test_thing_service_get(self, registry_rest_api_1, webserver):
        """Example GET /things/{uuid}"""
        ex = self.create_thing(registry_rest_api_1)
        response = webserver.get('/things/%s' % ex.uuid)
        assert response.status_code == 200
        assert response.json_body.get('name') == "car"

    def test_thing_service_delete(self, registry_rest_api_1, webserver):
        """Example GET /things/{uuid}"""
        ex = self.create_thing(registry_rest_api_1)
        query = registry_rest_api_1.Thing.query().filter_by(uuid=ex.uuid)
        assert query.count() == 1
        response = webserver.delete('/things/%s' % ex.uuid)
        assert response.status_code == 200
        assert query.count() == 0

    def test_thing_service_put(self, registry_rest_api_1, webserver):
        """Example PUT /things/{uuid}"""
        ex = self.create_thing(registry_rest_api_1)
        msg = dict(
            name='plip',
            secret='other',
            example_id=ex.example_id,
        )
        response = webserver.put_json(
            '/things/%s' % ex.uuid, msg)
        assert response.status_code == 200
        assert response.json_body.get('name') == "plip"

    def test_thing_service_put_schema_fail_bad_path(
        self, registry_rest_api_1, webserver
    ):
        """Example PUT schema validation fail on invalid path /things/{uuid}
        """
        fail = webserver.put_json(
            '/things/x', {'name': 'plip'}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') in [
            'path', 'body']

    def test_thing_service_put_schema_fail_bad_value_type(
        self, registry_rest_api_1, webserver
    ):
        """Example PUT schema validation fail on invalid value type in `body`
        /things/{uuid}
        """
        ex = self.create_thing(registry_rest_api_1)
        fail = webserver.put_json(
            '/things/%s' % ex.uuid, {'name': 0}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'

    def test_thing_service_post(self, registry_rest_api_1, webserver):
        """Example POST /things/"""
        ex = self.create_example(registry_rest_api_1)
        response = webserver.post_json(
            '/things',
            {'name': 'book', 'secret': 'xxx', 'example_id': ex.id}
        )
        assert response.status_code == 200
        assert response.json_body.get('name') == "book"

    def test_thing_service_post_schema_fail_bad_column_name(
        self, registry_rest_api_1, webserver
    ):
        """Example POST schema validation fail on invalid column name /things/
        """
        fail = webserver.post_json(
            '/things', {'badcolumn': 'plip'}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'

    def test_thing_service_post_schema_fail_bad_value_type(
        self, registry_rest_api_1, webserver
    ):
        """Example POST schema validation fail on invalid value type /things/
        """
        fail = webserver.post_json(
            '/things', {'name': 0}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'

    def test_thing_collection_get(
        self, registry_rest_api_1, webserver
    ):
        """Thing collection GET /things"""
        self.create_things(registry_rest_api_1)
        response = webserver.get('/things')
        assert response.status_code == 200
        assert len(response.json_body) == 3
        assert response.json_body[0].get('name') == "car"

    def test_thing_collection_get_unknown_querystring(
        self, registry_rest_api_1, webserver
    ):
        """Thing collection GET /things"""
        self.create_things(registry_rest_api_1)
        with pytest.raises(KeyError):
            webserver.get('/things?foo=bar')

    def test_thing_collection_get_with_querystring(
        self, registry_rest_api_1, webserver
    ):
        """Thing collection GET /things?querystring"""
        self.create_things(registry_rest_api_1)
        response = webserver.get('/things?filter[name][like]=car')
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 1
        assert int(response.headers.get('X-Count-Records')) == 1
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "car"

    def test_thing_collection_get_with_bad_querystring(
        self, registry_rest_api_1, webserver
    ):
        """Thing collection GET fail on bad /things?badquerystring"""
        self.create_things(registry_rest_api_1)
        fail = webserver.get('/things?filter[name][oops]=car', status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'querystring'
