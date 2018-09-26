# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidDBTestCase


class TestCrudServiceBase(PyramidDBTestCase):
    """Test Service from test_bloks/test_1/views.py:example_service
    This is the basic case, no validators, no schema.
    """

    blok_entry_points = ('bloks', 'test_bloks',)

    def setUp(self):
        super(TestCrudServiceBase, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_1',))

    def create_example(self, name="plop"):
        """Create a dummy example record"""
        example = self.registry.Example.insert(name=name)
        return example

    def test_example_service_get(self):
        """Example GET /anothers/{id}"""
        ex = self.create_example()
        response = self.webserver.get('/anothers/%s' % ex.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plop")

    def test_example_service_put(self):
        """Example PUT /anothers/{id}"""
        ex = self.create_example()
        response = self.webserver.put_json(
            '/anothers/%s' % ex.id, {'name': 'plip'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plip")

    def test_example_service_put_schema_fail_bad_path(self):
        """Example PUT schema validation fail on invalid path /anothers/{id}
        """
        fail = self.webserver.put_json(
            '/anothers/x', {'name': 'plip'}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'path')

    def test_example_service_put_schema_fail_bad_value_type(self):
        """Example PUT schema validation fail on invalid value type in `body`
        /anothers/{id}
        """
        ex = self.create_example()
        fail = self.webserver.put_json(
            '/anothers/%s' % ex.id, {'name': 0}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')

    def test_example_service_post(self):
        """Example POST /anothers/"""
        response = self.webserver.post_json('/anothers', {'name': 'plip'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plip")

    def test_example_service_post_schema_fail_bad_column_name(self):
        """Example POST schema validation fail on invalid column name /anothers/
        """
        fail = self.webserver.post_json(
            '/anothers', {'badcolumn': 'plip'}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')

    def test_example_service_post_schema_fail_bad_value_type(self):
        """Example POST schema validation fail on invalid value type /anothers/
        """
        fail = self.webserver.post_json(
            '/anothers', {'name': 0}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')


class TestCrudServiceAdvanced(PyramidDBTestCase):
    """Test Service from test_bloks/test_1/views.py:thing_service
    This is the advanced case, validators and relationnal schema
    """

    blok_entry_points = ('bloks', 'test_bloks',)

    def setUp(self):
        super(TestCrudServiceAdvanced, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_1',))

    def create_example(self, name="plop"):
        """Create a dummy example record"""
        example = self.registry.Example.insert(name=name)
        return example

    def create_examples(self, examples=None):
        """Create a dummy example collection record"""
        res = []
        if examples is None:
            examples = [dict(name="car example"),
                        dict(name="apple example"),
                        dict(name="human example")]
        for example in examples:
            res.append(self.create_example(**example))
        return res

    def create_thing(self, name="car", secret="aaa", **kwargs):
        """Create a dummy thing record"""
        if 'example_id' not in kwargs.keys():
            example = self.create_example(name="%s example" % name)
            kwargs['example_id'] = example.id
        thing = self.registry.Thing.insert(name=name, secret=secret, **kwargs)
        return thing

    def create_things(self, things=None):
        """Create a dummy thing collection record"""
        res = []
        if things is None:
            exs = self.create_examples()
            things = [dict(name="car", secret="aaa", example_id=exs[0].id),
                      dict(name="apple", secret="bbb", example_id=exs[1].id),
                      dict(name="human", secret="ccc", example_id=exs[2].id)]
        for thing in things:
            res.append(self.create_thing(**thing))
        return res

    def test_thing_service_get(self):
        """Example GET /things/{uuid}"""
        ex = self.create_thing()
        response = self.webserver.get('/things/%s' % ex.uuid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "car")

    def test_thing_service_delete(self):
        """Example GET /things/{uuid}"""
        ex = self.create_thing()
        query = self.registry.Thing.query().filter_by(uuid=ex.uuid)
        self.assertEqual(query.count(), 1)
        response = self.webserver.delete('/things/%s' % ex.uuid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(query.count(), 0)

    def test_thing_service_put(self):
        """Example PUT /things/{uuid}"""
        ex = self.create_thing()
        msg = dict(
            name='plip',
            secret='other',
            example_id=ex.example_id,
        )
        response = self.webserver.put_json(
            '/things/%s' % ex.uuid, msg)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plip")

    def test_thing_service_put_schema_fail_bad_path(self):
        """Example PUT schema validation fail on invalid path /things/{uuid}
        """
        fail = self.webserver.put_json(
            '/things/x', {'name': 'plip'}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertIn(
            fail.json_body.get('errors')[0].get('location'), ['path', 'body'])

    def test_thing_service_put_schema_fail_bad_value_type(self):
        """Example PUT schema validation fail on invalid value type in `body`
        /things/{uuid}
        """
        ex = self.create_thing()
        fail = self.webserver.put_json(
            '/things/%s' % ex.uuid, {'name': 0}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')

    def test_thing_service_post(self):
        """Example POST /things/"""
        ex = self.create_example()
        response = self.webserver.post_json(
            '/things',
            {'name': 'book', 'secret': 'xxx', 'example_id': ex.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "book")

    def test_thing_service_post_schema_fail_bad_column_name(self):
        """Example POST schema validation fail on invalid column name /things/
        """
        fail = self.webserver.post_json(
            '/things', {'badcolumn': 'plip'}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')

    def test_thing_service_post_schema_fail_bad_value_type(self):
        """Example POST schema validation fail on invalid value type /things/
        """
        fail = self.webserver.post_json(
            '/things', {'name': 0}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')

    def test_thing_collection_get(self):
        """Thing collection GET /things"""
        self.create_things()
        response = self.webserver.get('/things')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 3)
        self.assertEqual(response.json_body[0].get('name'), "car")

    def test_thing_collection_get_unknown_querystring(self):
        """Thing collection GET /things"""
        self.create_things()
        with self.assertRaises(KeyError):
            self.webserver.get('/things?foo=bar')

    def test_thing_collection_get_with_querystring(self):
        """Thing collection GET /things?querystring"""
        self.create_things()
        response = self.webserver.get('/things?filter[name][like]=car')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 1)
        self.assertEqual(int(response.headers.get('X-Count-Records')), 1)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "car")

    def test_thing_collection_get_with_bad_querystring(self):
        """Thing collection GET fail on bad /things?badquerystring"""
        self.create_things()
        fail = self.webserver.get('/things?filter[name][oops]=car', status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'querystring')
