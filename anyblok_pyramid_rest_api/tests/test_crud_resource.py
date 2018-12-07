# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidDBTestCase


class TestCrudResourceBase(PyramidDBTestCase):
    """Test CrudResource class from test_bloks/test_1/views.py:ExampleResource
    This is the basic case, no validators(except the default one,
    base_validator), no schema.
    """

    blok_entry_points = ('bloks', 'test_bloks',)

    def setUp(self):
        super(TestCrudResourceBase, self).setUp()
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

    def test_example_get_bad_value_in_path(self):
        """Example FAILED GET /examples/{id}"""
        self.create_example()
        fail = self.webserver.get('/examples/0', status=404)
        self.assertEqual(fail.status_code, 404)

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

    def test_example_put_bad_value_in_path(self):
        """Example FAILED PUT /examples/{id}"""
        self.create_example()
        fail = self.webserver.put_json(
            '/examples/0', {'name': 'plip'}, status=404)
        self.assertEqual(fail.status_code, 404)

    def test_example_delete(self):
        """Example DELETE /examples/{id}"""
        ex = self.create_example()
        response = self.webserver.delete('/examples/%s' % ex.id)
        self.assertEqual(response.status_code, 200)
        response = self.webserver.get('/examples')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body, [])

    def test_example_delete_bad_value_in_path(self):
        """Example FAILED DELETE /examples/{id}"""
        self.create_example()
        fail = self.webserver.delete('/examples/0', status=404)
        self.assertEqual(fail.status_code, 404)

    def test_example_collection_get(self):
        """Example collection GET /examples"""
        self.create_example()
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
        self.assertEqual(int(response.headers.get('X-Total-Records')), 1)
        self.assertEqual(int(response.headers.get('X-Count-Records')), 1)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "air")

    def test_example_collection_get_not_filter_eq(self):
        """Example collection GET /examples?~filter[name][eq]=term"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?~filter[name][eq]=air')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 4)
        self.assertEqual(int(response.headers.get('X-Count-Records')), 4)
        self.assertEqual(len(response.json_body), 4)

    def test_example_collection_get_filter_like(self):
        """Example collection GET /examples?filter[name][like]=term"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][like]=a')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 3)
        self.assertEqual(int(response.headers.get('X-Count-Records')), 3)
        self.assertEqual(len(response.json_body), 3)
        self.assertEqual(response.json_body[0].get('name'), "air")

    def test_example_collection_get_filter_ilike(self):
        """Example collection GET /examples?filter[name][ilike]=TeRm"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][ilike]=A')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.headers.get('X-Total-Records')), 3)
        self.assertEqual(int(response.headers.get('X-Count-Records')), 3)
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


class TestCrudResourceWithDefaultSchema(PyramidDBTestCase):
    """Test CrudResource class from
    test_bloks/test_1/views.py:ExampleResourceBaseValidator.

    This is the basic case, no validators(except the default one,
    base_validator), no schema.
    """

    blok_entry_points = ('bloks', 'test_bloks',)

    def setUp(self):
        super(TestCrudResourceWithDefaultSchema, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_1',))

    def create_example(self, name="plop"):
        """Create a dummy example record"""
        example = self.registry.Example.insert(name=name)
        return example

    def test_example_get(self):
        """Example GET /with/default/schema/examples/{id}"""
        ex = self.create_example()
        response = self.webserver.get(
            '/with/default/schema/examples/%s' % ex.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plop")

    def test_example_get_bad_value_in_path(self):
        """Example FAILED GET /with/default/schema/examples/{id}"""
        self.create_example()
        fail = self.webserver.get('/with/default/schema/examples/0', status=404)
        self.assertEqual(fail.status_code, 404)


class CrudResourceSchema:
    blok_entry_points = ('bloks', 'test_bloks',)

    def create_customer(self, name="bob", tag_name="green", zipcode="000"):
        """Create a dummy customer record"""
        tag = self.registry.Tag.insert(name=tag_name)
        customer = self.registry.Customer.insert(name=name)
        customer.tags.append(tag)
        city = self.registry.City.insert(name="nowhere", zipcode=zipcode)
        self.registry.Address.insert(
            customer=customer, city=city, street="Dead end street")
        return customer

    def test_example_collection_get(self):
        """Example collection GET /examples"""
        self.create_customer()
        response = self.webserver.get(self.collection_path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "bob")
        self.assertEqual(len(response.json_body[0].get('addresses')), 1)
        self.assertEqual(
            response.json_body[0].get('addresses')[0].get('city').get(
                'zipcode'), "000")

    def test_customer_get(self):
        """Customer GET /customers/{id}"""
        cu = self.create_customer()
        response = self.webserver.get(self.path % cu.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "bob")
        self.assertEqual(len(response.json_body.get('addresses')), 1)
        self.assertEqual(
            response.json_body.get('addresses')[0].get('city').get('zipcode'),
            "000")

    def test_customer_get_bad_value_in_path(self):
        """Customer FAILED GET /customers/{id}"""
        fail = self.webserver.get(self.path % '0', status=404)
        self.assertEqual(fail.status_code, 404)

    def test_customer_collection_post(self):
        """Customer POST /customers"""
        response = self.webserver.post_json(self.collection_path,
                                            {'name': 'plip'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plip")

    def test_customer_collection_post_partial(self):
        """Customer POST partial /customers"""
        response = self.webserver.post_json(self.collection_path,
                                            {'name': 'plip'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "plip")

    def test_customer_collection_post_empty_body(self):
        """Customer POST empty body /customers"""
        fail = self.webserver.post_json(
            self.collection_path, {}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')
        self.assertDictEqual(
            fail.json_body.get('errors')[0].get('description'),
            {'name': ['Missing data for required field.']}
        )

    def test_customer_collection_post_bad_key_in_body(self):
        """Customer POST bad key in body /customers"""
        fail = self.webserver.post_json(
            self.collection_path, {'unexistingkey': 'plip'}, status=400)
        self.assertEqual(fail.status_code, 400)
        self.assertEqual(fail.json_body.get('status'), 'error')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('location'), 'body')
        self.assertEqual(
            fail.json_body.get('errors')[0].get('name'),
            'Validation error for body')
        self.assertEqual(len(fail.json_body.get('errors')), 2)

    def test_customer_put(self):
        """Customer PUT /customers/{id}"""
        ex = self.create_customer()
        response = self.webserver.head(self.path % ex.id)  # fix headers
        response = self.webserver.put_json(
            self.path % ex.id, {'name': 'bobby'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "bobby")

    def test_customer_patch(self):
        """Customer PATCH /customers/{id}"""
        ex = self.create_customer()
        response = self.webserver.head(self.path % ex.id)  # fix headers
        response = self.webserver.patch_json(
            self.path % ex.id, {'name': 'bobby'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body.get('name'), "bobby")

    def test_customer_put_bad_value_in_path(self):
        """Customer FAILED PUT /customers/{id}"""
        self.create_customer()
        fail = self.webserver.put_json(
            self.path % '0', {'name': 'plip'}, status=404)
        self.assertEqual(fail.status_code, 404)

    def test_customer_delete(self):
        """Customer DELETE /customers/{id}"""
        ex = self.create_customer()
        response = self.webserver.delete(self.path % ex.id)
        self.assertEqual(response.status_code, 200)
        response = self.webserver.get(self.collection_path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json_body, [])

    def test_customer_delete_bad_value_in_path(self):
        """Customer FAILED DELETE /customers/{id}"""
        fail = self.webserver.get(self.path % '0', status=404)
        self.assertEqual(fail.status_code, 404)


class TestCrudResourceModelSchema(CrudResourceSchema, PyramidDBTestCase):
    """Test Customers and Addresses from
    test_bloks/test_3/views.py
    """

    def setUp(self):
        super(TestCrudResourceModelSchema, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_3',))
        self.collection_path = '/customers/v3'
        self.path = '/customers/v3/%s'


class TestCrudResourceWithAdapter(CrudResourceSchema, PyramidDBTestCase):
    """Test Customers and Addresses from
    test_bloks/test_3/views.py
    """

    def setUp(self):
        super(TestCrudResourceWithAdapter, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_4',))
        self.collection_path = '/customers/v4'
        self.path = '/customers/v4/%s'

    def create_adapter_customers(self):
        self.create_customer()
        self.create_customer(name="robert", tag_name="orange", zipcode="001")

    def test_adapter_get_all_without_tag_or_custom_filter(self):
        self.create_adapter_customers()
        response = self.webserver.get(self.collection_path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 2)

    def test_adapter_tag(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=green"
        response = self.webserver.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "bob")

    def test_adapter_unexisting_tag(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=unexisting"
        response = self.webserver.get(path, status=400)
        self.assertEqual(response.status_code, 400)

    def test_adapter_wrong_tag(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=wrong"
        response = self.webserver.get(path, status=400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json_body), 2)

    def test_adapter_tags_1(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tags=green"
        response = self.webserver.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "bob")

    def test_adapter_tags_2(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tags=green,orange"
        response = self.webserver.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 0)

    def test_adapter_tags_3(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tags=orange"
        response = self.webserver.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "robert")

    def test_adapter_tags_and_context_1(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=colors&context[colors]=orange"
        response = self.webserver.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "robert")

    def test_adapter_tags_and_context_2(self):
        self.create_adapter_customers()
        path = self.collection_path
        path += "?tag=colors&context[colors]=green,orange"
        response = self.webserver.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 2)

    def test_adapter_customer_filter(self):
        self.create_adapter_customers()
        path = self.collection_path + "?filter[addresses.city][ilike]=001"
        response = self.webserver.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json_body), 1)
        self.assertEqual(response.json_body[0].get('name'), "robert")

    def test_adapter_wrong_filter(self):
        self.create_adapter_customers()
        path = self.collection_path + "?filter[addresses.other][ilike]=001"
        response = self.webserver.get(path, status=400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json_body), 2)


class TestCrudResourceModelSchemaValidator(CrudResourceSchema,
                                           PyramidDBTestCase):
    """Test Customers and Addresses from
    test_bloks/test_5/views.py
    """

    def setUp(self):
        super(TestCrudResourceModelSchemaValidator, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_5',))
        self.collection_path = '/customers/v5'
        self.path = '/customers/v5/%s'


class TestCrudResourceModelSchemaValidatorAndAuth(
    CrudResourceSchema, PyramidDBTestCase
):
    """Test Customers and Addresses from
    test_bloks/test_5/views.py
    """

    def setUp(self):
        super(TestCrudResourceModelSchemaValidatorAndAuth, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_5', 'auth-password'))
        self.collection_path = '/customers/v5'
        self.path = '/customers/v5/%s'
        self.registry.User.insert(
            login='jssuzanne', first_name='js', last_name='Suzanne')
        self.registry.User.CredentialStore.insert(
            login='jssuzanne', password='mypassword')
        self.webserver.post_json(
            '/login', {'login': 'jssuzanne', 'password': 'mypassword'},
            status=302)

    def test_customer_get_logout(self):
        """Customer GET /customers/{id} [UNLOGGED]"""
        cu = self.create_customer()
        self.webserver.post_json('/logout', {}, status=302)
        self.webserver.get(self.path % cu.id, status=403)
