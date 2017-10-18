from anyblok_pyramid.tests.testcase import PyramidBlokTestCase, PyramidDBTestCase


class TestCrudRestApi(PyramidDBTestCase):
    """ Test pyramid routes with PyramidBlokTestCase"""

    blok_entry_points = ('bloks', 'test_bloks',)

    def setUp(self):
        super(TestCrudRestApi, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_1',))

    def create_example(self, name="plop"):
        """Create a dummy example record"""
        example = self.registry.Example.insert(name=name)
        return example

    def test_example_get(self):
        """Example GET /examples/{id}"""
        ex = self.create_example()
        response = self.webserver.get('/examples/%s' % ex.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plop")

    def test_example_collection_post(self):
        """Example POST /examples/"""
        response = self.webserver.post_json('/examples', {'name': 'plip'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plip")

    def test_example_put(self):
        """Example PUT /examples/{id}"""
        ex = self.create_example()
        response = self.webserver.put_json(
                '/examples/%s' % ex.id, {'name': 'plip'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plip")

        fail = self.webserver.put_json('/examples/0', {'name': 'plip'}, status=404)
        self.assertEqual(fail.status_code, 404)

    def test_example_delete(self):
        """Example DELETE /examples/{id}"""
        ex = self.create_example()
        response = self.webserver.delete('/examples/%s' % ex.id)
        self.assertEqual(response.status_code, 200)
        response = self.webserver.get('/examples')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 0)

    def test_example_collection_get(self):
        """Example collection GET /examples"""
        ex = self.create_example()
        response = self.webserver.get('/examples')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "plop")

    def test_example_collection_get_order_by_asc(self):
        """Example collection GET /examples?order_by[asc]=field"""
        names = ['air', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?order_by[asc]=name')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 2)
        self.assertEqual(response.json_body[0].get('name'), "air")

    def test_example_collection_get_order_by_desc(self):
        """Example collection GET /examples?order_by[desc]=field"""
        names = ['air', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?order_by[desc]=name')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 2)
        self.assertEqual(response.json_body[0].get('name'), "zen")

    def test_example_collection_get_filter_eq(self):
        """Example collection GET /examples?filter[name][eq]=term"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][eq]=air')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 5)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "air")

    def test_example_collection_get_filter_like(self):
        """Example collection GET /examples?filter[name][like]=term"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][like]=a')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 5)
        self.assertEqual(len(response.json_body), 3)
        self.assertEqual(response.json_body[0].get('name'), "air")

    def test_example_collection_get_filter_ilike(self):
        """Example collection GET /examples?filter[name][ilike]=TeRm"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][ilike]=A')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 5)
        self.assertEqual(len(response.json_body), 3)
        self.assertEqual(response.json_body[0].get('name'), "air")

    def test_example_collection_get_limit(self):
        """Example collection GET /examples?limit=limit"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?limit=4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 5)
        self.assertEqual(len(response.json_body), 4)
        self.assertEqual(response.json_body[0].get('name'), "air")

    def test_example_collection_get_offset(self):
        """Example collection GET /examples?offset=offset"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?offset=3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 5)
        self.assertEqual(len(response.json_body), 2)
        self.assertEqual(response.json_body[0].get('name'), "dot")

    def test_example_service_get(self):
        """Example GET /anothers/{id}"""
        ex = self.create_example()
        response = self.webserver.get('/anothers/%s' % ex.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plop")
