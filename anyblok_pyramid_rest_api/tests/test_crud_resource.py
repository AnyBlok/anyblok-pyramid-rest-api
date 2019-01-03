# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok.tests.testcase import LogCapture


class TestCrudResourceBase:
    """Test CrudResource class from test_bloks/test_1/views.py:ExampleResource
    This is the basic case, no validators(except the default one,
    base_validator), no schema.
    """

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_1, webserver):
        transaction = registry_rest_api_1.begin_nested()
        self.registry = registry_rest_api_1

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return

    def create_example(self, name="plop"):
        """Create a dummy example record"""
        example = self.registry.Example.insert(name=name)
        return example

    def test_example_get(self):
        """Example GET /examples/{id}"""
        ex = self.create_example()
        response = self.webserver.get('/examples/%s' % ex.id)
        assert response.status_code == 200
        assert response.json_body.get('name') == "plop"

    def test_example_get_bad_value_in_path(self):
        """Example FAILED GET /examples/{id}"""
        self.create_example()
        fail = self.webserver.get('/examples/0', status=404)
        assert fail.status_code == 404

    def test_example_collection_post(self):
        """Example POST /examples/"""
        response = self.webserver.post_json('/examples', [{'name': 'plip'}])
        assert response.status_code == 200
        assert response.json_body[0]['name'] == "plip"

    def test_example_collection_post_with_errors(self):
        """Example POST /examples/with/errors"""
        with LogCapture() as logs:
            fail = self.webserver.post_json(
                '/examples/with/errors', [{'name': 'plip'}], status=500)

        assert fail.status_code == 500
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'
        assert fail.json_body.get('errors')[0].get('description') == 'test'

        assert ('Request error found: rollback the registry'
                in logs.get_debug_messages())

    def test_example_put(self):
        """Example PUT /examples/{id}"""
        ex = self.create_example()
        response = self.webserver.put_json(
            '/examples/%s' % ex.id, {'name': 'plip'})
        assert response.status_code == 200
        assert response.json_body.get('name') == "plip"

    def test_example_put_with_errors(self):
        """Example PUT /examples/with/error/{id}"""
        ex = self.create_example()
        with LogCapture() as logs:
            self.webserver.put_json(
                '/examples/with/error/%s' % ex.id,
                {'name': 'plip'}, status=500)

        assert ('Request error found: rollback the registry'
                in logs.get_debug_messages())

    def test_example_patch_with_errors(self):
        """Example PATCH /examples/with/error/{id}"""
        ex = self.create_example()
        with LogCapture() as logs:
            self.webserver.patch_json(
                '/examples/with/error/%s' % ex.id, {'name': 'plip'},
                status=500)

        assert ('Request error found: rollback the registry'
                in logs.get_debug_messages())

    def test_example_collection_put_with_errors(self):
        """Example PUT /examples/with/errors"""
        ex = self.create_example()
        with LogCapture() as logs:
            response = self.webserver.put_json(
                '/examples/with/errors',
                [{'id': ex.id, 'name': 'plip'}], status=500)

        assert response.status_code == 500
        assert ex.name != "plip"
        assert ('Request error found: rollback the registry'
                in logs.get_debug_messages())

    def test_example_collection_patch_with_errors(self):
        """Example PATCH /examples/with/errors"""
        ex = self.create_example()
        with LogCapture() as logs:
            response = self.webserver.patch_json(
                '/examples/with/errors',
                [{'id': ex.id, 'name': 'plip'}], status=500)

        assert response.status_code == 500
        assert ex.name != "plip"
        assert ('Request error found: rollback the registry'
                in logs.get_debug_messages())

    def test_example_put_bad_value_in_path(self):
        """Example FAILED PUT /examples/{id}"""
        self.create_example()
        fail = self.webserver.put_json(
            '/examples/0', {'name': 'plip'}, status=404)
        assert fail.status_code == 404

    def test_example_delete(self):
        """Example DELETE /examples/{id}"""
        ex = self.create_example()
        response = self.webserver.delete('/examples/%s' % ex.id)
        assert response.status_code == 200
        response = self.webserver.get('/examples')
        assert response.status_code == 200
        assert response.json_body == []

    def test_example_delete_with_errors(self):
        """Example DELETE /examples/with/error/{id}"""
        ex = self.create_example()
        with LogCapture() as logs:
            response = self.webserver.delete(
                '/examples/with/error/%s' % ex.id, status=500)

        assert response.status_code == 500
        assert ('Request error found: rollback the registry'
                in logs.get_debug_messages())

    def test_example_collection_delete_with_errors(self):
        """Example DELETE /examples/with/errors"""
        ex = self.create_example()
        with LogCapture() as logs:
            response = self.webserver.delete_json(
                '/examples/with/errors',
                [{'id': ex.id}], status=500)

        assert response.status_code == 500
        assert ('Request error found: rollback the registry'
                in logs.get_debug_messages())

    def test_example_delete_bad_value_in_path(self):
        """Example FAILED DELETE /examples/{id}"""
        self.create_example()
        fail = self.webserver.delete('/examples/0', status=404)
        assert fail.status_code == 404

    def test_example_collection_get(self):
        """Example collection GET /examples"""
        self.create_example()
        response = self.webserver.get('/examples')
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "plop"

    def test_example_collection_get_order_by_asc(self):
        """Example collection GET /examples?order_by[asc]=field"""
        names = ['air', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?order_by[asc]=name')
        assert response.status_code == 200
        assert len(response.json_body) == 2
        assert response.json_body[0].get('name') == "air"

    def test_example_collection_get_order_by_desc(self):
        """Example collection GET /examples?order_by[desc]=field"""
        names = ['air', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?order_by[desc]=name')
        assert response.status_code == 200
        assert len(response.json_body) == 2
        assert response.json_body[0].get('name') == "zen"

    def test_example_collection_get_filter_eq(self):
        """Example collection GET /examples?filter[name][eq]=term"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][eq]=air')
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 1
        assert int(response.headers.get('X-Count-Records')) == 1
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "air"

    def test_example_collection_get_not_filter_eq(self):
        """Example collection GET /examples?~filter[name][eq]=term"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?~filter[name][eq]=air')
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 4
        assert int(response.headers.get('X-Count-Records')) == 4
        assert len(response.json_body) == 4

    def test_example_collection_get_filter_like(self):
        """Example collection GET /examples?filter[name][like]=term"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][like]=a')
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 3
        assert int(response.headers.get('X-Count-Records')) == 3
        assert len(response.json_body) == 3
        assert response.json_body[0].get('name') == "air"

    def test_example_collection_get_filter_ilike(self):
        """Example collection GET /examples?filter[name][ilike]=TeRm"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?filter[name][ilike]=A')
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 3
        assert int(response.headers.get('X-Count-Records')) == 3
        assert len(response.json_body) == 3
        assert response.json_body[0].get('name') == "air"

    def test_example_collection_get_limit(self):
        """Example collection GET /examples?limit=limit"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?limit=4')
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 5
        assert len(response.json_body) == 4
        assert response.json_body[0].get('name') == "air"

    def test_example_collection_get_offset(self):
        """Example collection GET /examples?offset=offset"""
        names = ['air', 'bar', 'car', 'dot', 'zen']
        for name in names:
            self.create_example(name)
        response = self.webserver.get('/examples?offset=3')
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 5
        assert len(response.json_body) == 2
        assert response.json_body[0].get('name') == "dot"


class TestCrudResourceWithDefaultSchema:
    """Test CrudResource class from
    test_bloks/test_1/views.py:ExampleResourceBaseValidator.

    This is the basic case, no validators(except the default one,
    base_validator), no schema.
    """

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_1, webserver):
        transaction = registry_rest_api_1.begin_nested()
        self.registry = registry_rest_api_1

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return

    def create_example(self, name="plop"):
        """Create a dummy example record"""
        example = self.registry.Example.insert(name=name)
        return example

    def test_example_get(self):
        """Example GET /with/default/schema/examples/{id}"""
        ex = self.create_example()
        response = self.webserver.get(
            '/with/default/schema/examples/%s' % ex.id)
        assert response.status_code == 200
        assert response.json_body.get('name') == "plop"

    def test_example_get_bad_value_in_path(self):
        """Example FAILED GET /with/default/schema/examples/{id}"""
        self.create_example()
        fail = self.webserver.get('/with/default/schema/examples/0', status=404)
        assert fail.status_code == 404


class CrudResourceSchema:

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
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "bob"
        assert len(response.json_body[0].get('addresses')) == 1
        assert response.json_body[0].get('addresses')[0].get('city').get(
            'zipcode') == "000"

    def test_customer_get(self):
        """Customer GET /customers/{id}"""
        cu = self.create_customer()
        response = self.webserver.get(self.path % cu.id)
        assert response.status_code == 200
        assert response.json_body.get('name') == "bob"
        assert len(response.json_body.get('addresses')) == 1
        assert response.json_body.get('addresses')[0].get('city').get(
            'zipcode') == "000"

    def test_customer_get_bad_value_in_path(self):
        """Customer FAILED GET /customers/{id}"""
        fail = self.webserver.get(self.path % '0', status=404)
        assert fail.status_code == 404

    def test_customer_collection_post(self):
        """Customer POST /customers"""
        response = self.webserver.post_json(self.collection_path,
                                            [{'name': 'plip'}])
        assert response.status_code == 200
        assert response.json_body[0]['name'] == "plip"

    def test_customer_collection_post_partial(self):
        """Customer POST partial /customers"""
        response = self.webserver.post_json(self.collection_path,
                                            [{'name': 'plip'}])
        assert response.status_code == 200
        assert response.json_body[0]['name'] == "plip"

    def test_customer_collection_post_empty_body(self):
        """Customer POST empty body /customers"""
        fail = self.webserver.post_json(
            self.collection_path, [{}], status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'
        assert fail.json_body.get('errors')[0].get('description') == {
            '0': {'name': ['Missing data for required field.']}}

    def test_customer_collection_post_bad_key_in_body(self):
        """Customer POST bad key in body /customers"""
        fail = self.webserver.post_json(
            self.collection_path, [{'unexistingkey': 'plip'}], status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('status') == 'error'
        assert fail.json_body.get('errors')[0].get('location') == 'body'
        assert fail.json_body.get('errors')[0].get(
            'name') == 'Validation error for body'
        assert fail.json_body['errors'][0]['description'] == {
            '0': {
                'name': ['Missing data for required field.'],
                'unexistingkey': [
                    'Unknown field.',
                    "Unknown fields {'unexistingkey'} on Model "
                    "Model.Customer"
                ]
            }
        }

    def test_customer_put(self):
        """Customer PUT /customers/{id}"""
        ex = self.create_customer()
        response = self.webserver.head(self.path % ex.id)  # fix headers
        response = self.webserver.put_json(
            self.path % ex.id, {'name': 'bobby'})
        assert response.status_code == 200
        assert response.json_body.get('name') == "bobby"

    def test_customer_patch(self):
        """Customer PATCH /customers/{id}"""
        ex = self.create_customer()
        response = self.webserver.head(self.path % ex.id)  # fix headers
        response = self.webserver.patch_json(
            self.path % ex.id, {'name': 'bobby'})
        assert response.status_code == 200
        assert response.json_body.get('name') == "bobby"

    def test_customer_put_bad_value_in_path(self):
        """Customer FAILED PUT /customers/{id}"""
        self.create_customer()
        fail = self.webserver.put_json(
            self.path % '0', {'name': 'plip'}, status=404)
        assert fail.status_code == 404

    def test_customer_delete(self):
        """Customer DELETE /customers/{id}"""
        ex = self.create_customer()
        response = self.webserver.delete(self.path % ex.id)
        assert response.status_code == 200
        response = self.webserver.get(self.collection_path)
        assert response.status_code == 200
        assert response.json_body == []

    def test_customer_delete_bad_value_in_path(self):
        """Customer FAILED DELETE /customers/{id}"""
        fail = self.webserver.get(self.path % '0', status=404)
        assert fail.status_code == 404

    def test_customer_collection_put(self):
        """Customer PUT /customers"""
        ex = self.create_customer()
        response = self.webserver.head(self.collection_path)  # fix headers
        response = self.webserver.put_json(
            self.collection_path, [{'id': ex.id, 'name': 'bobby'}])
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "bobby"

    def test_customer_collection_patch(self):
        """Customer PATCH /customers"""
        ex = self.create_customer()
        response = self.webserver.head(self.collection_path)  # fix headers
        response = self.webserver.patch_json(
            self.collection_path, [{'id': ex.id, 'name': 'bobby'}])
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "bobby"

    def test_customer_collection_put_no_entry_found(self):
        """Customer FAILED PUT /customers (no id)"""
        response = self.webserver.put_json(
            self.collection_path, [{'name': 'plip'}], status=400)
        assert response.status_code == 400

    def test_customer_collection_put_no_entry_found2(self):
        """Customer FAILED PUT /customers (id=0)"""
        response = self.webserver.put_json(
            self.collection_path, [{'id': 0, 'name': 'plip'}], status=400)
        assert response.status_code == 400

    def test_customer_collection_delete(self):
        """Customer DELETE /customers"""
        ex = self.create_customer()
        path = self.collection_path + '?filter[id][eq]=%d' % ex.id

        response = self.webserver.get(path)
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 1
        assert int(response.headers.get('X-Count-Records')) == 1

        response = self.webserver.delete_json(
            self.collection_path, [{'id': ex.id}])
        assert response.status_code == 200
        assert response.json_body == 1

        response = self.webserver.get(path)
        assert response.status_code == 200
        assert int(response.headers.get('X-Total-Records')) == 0
        assert int(response.headers.get('X-Count-Records')) == 0

    def test_customer_collection_delete_no_entry_found(self):
        """Customer FAILED DELETE /customers (no id)"""
        response = self.webserver.delete_json(
            self.collection_path, [{}], status=400)
        assert response.status_code == 400

    def test_customer_collection_delete_no_entry_found2(self):
        """Customer FAILED DELETE /customers (id=0)"""
        response = self.webserver.delete_json(
            self.collection_path, [{'id': 0}], status=400)
        assert response.status_code == 400


class TestCrudResourceModelSchema(CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_3/views.py
    """
    collection_path = '/customers/v3'
    path = '/customers/v3/%s'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_3, webserver):
        transaction = registry_rest_api_3.begin_nested()
        self.registry = registry_rest_api_3

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class CrudResourceAdapter:

    def create_adapter_customers(self):
        self.create_customer()
        self.create_customer(name="robert", tag_name="orange", zipcode="001")

    def test_adapter_get_all_without_tag_or_custom_filter(self):
        self.create_adapter_customers()
        response = self.webserver.get(self.collection_path)
        assert response.status_code == 200
        assert len(response.json_body) == 2

    def test_adapter_tag(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=green"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "bob"

    def test_adapter_unexisting_tag(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=unexisting"
        response = self.webserver.get(path, status=400)
        assert response.status_code == 400

    def test_adapter_wrong_tag(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=wrong"
        response = self.webserver.get(path, status=400)
        assert response.status_code == 400
        assert len(response.json_body) == 2

    def test_adapter_tags_1(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tags=green"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "bob"

    def test_adapter_tags_2(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tags=green,orange"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert len(response.json_body) == 0

    def test_adapter_tags_3(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tags=orange"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "robert"

    def test_adapter_tags_and_context_1(self):
        self.create_adapter_customers()
        path = self.collection_path + "?tag=colors&context[colors]=orange"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "robert"

    def test_adapter_tags_and_context_2(self):
        self.create_adapter_customers()
        path = self.collection_path
        path += "?tag=colors&context[colors]=green,orange"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert len(response.json_body) == 2

    def test_adapter_customer_filter(self):
        self.create_adapter_customers()
        path = self.collection_path + "?filter[addresses.city][ilike]=001"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert response.json_body[0].get('name') == "robert"

    def test_adapter_wrong_filter(self):
        self.create_adapter_customers()
        path = self.collection_path + "?filter[addresses.other][ilike]=001"
        response = self.webserver.get(path, status=400)
        assert response.status_code == 400
        assert len(response.json_body) == 2

    def test_adapter_wrong_order_by(self):
        self.create_adapter_customers()
        path = self.collection_path + "?order_by[asc]=wrong"
        response = self.webserver.get(path, status=400)
        assert response.status_code == 400
        assert len(response.json_body) == 2

    def test_adapter_order_by(self):
        self.create_adapter_customers()
        path = self.collection_path + "?order_by[asc]=address"
        response = self.webserver.get(path)
        assert response.status_code == 200
        assert response.json_body[0].get('name') == "bob"


class TestCrudResourceWithAdapter(CrudResourceAdapter, CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_4/views.py
    """
    collection_path = '/customers/v4'
    path = '/customers/v4/%s'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_4, webserver):
        transaction = registry_rest_api_4.begin_nested()
        self.registry = registry_rest_api_4

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class TestCrudResourceWithAdapter2(CrudResourceAdapter, CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_6/views.py
    """
    collection_path = '/customers/v6'
    path = '/customers/v6/%s'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_6, webserver):
        transaction = registry_rest_api_6.begin_nested()
        self.registry = registry_rest_api_6

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class TestCrudResourceModelSchemaValidator(CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_5/views.py
    """
    collection_path = '/customers/v5'
    path = '/customers/v5/%s'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_5, webserver):
        transaction = registry_rest_api_5.begin_nested()
        self.registry = registry_rest_api_5

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class CrudResourceAction:

    def create_customer(self, name="bob", tag_name="green", zipcode="000"):
        """Create a dummy customer record"""
        tag = self.registry.Tag.insert(name=tag_name)
        customer = self.registry.Customer.insert(name=name)
        customer.tags.append(tag)
        city = self.registry.City.insert(name="nowhere", zipcode=zipcode)
        self.registry.Address.insert(
            customer=customer, city=city, street="Dead end street")
        return customer

    def test_collection_action(self):
        """Example collection GET /customers/v*/execute/action1"""
        response = self.webserver.get(self.collection_service_path)
        assert response.status_code == 200
        assert response.json_body == 'test'

    def test_collection_action_post_on_path(self):
        """Example collection POST /customers/v*/{id}/execute/action1"""
        cu = self.create_customer()
        service_path = self.path + '/execute/action1'
        fail = self.webserver.get(service_path % cu.id, status=404)
        assert fail.status_code == 404

    def test_collection_action_post(self):
        """Example collection GET /customers/v*/execute/action1"""
        fail = self.webserver.post(self.collection_service_path, status=405)
        assert fail.status_code == 405

    def test_collection_action_put(self):
        """Example collection PUT /customers/v*/execute/action1"""
        fail = self.webserver.put(self.collection_service_path, status=405)
        assert fail.status_code == 405

    def test_collection_action_patch(self):
        """Example collection PATCH /customers/v*/execute/action1"""
        fail = self.webserver.patch(self.collection_service_path, status=405)
        assert fail.status_code == 405

    def test_collection_action_delete(self):
        """Example collection DELETE /customers/v*/execute/action1"""
        fail = self.webserver.delete(self.collection_service_path, status=405)
        assert fail.status_code == 405

    def test_action(self):
        """Example POST /customers/v*/{id}/execute/action2"""
        cu = self.create_customer()
        response = self.webserver.post_json(
            self.service_path % cu.id, {'name': 'test'})
        assert response.status_code == 200
        assert response.json_body == 'test'

    def test_action_missing_name(self):
        """Example FAIL POST /customers/v*/{id}/execute/action2"""
        cu = self.create_customer()
        fail = self.webserver.post_json(
            self.service_path % cu.id, {}, status=400)
        assert fail.status_code == 400
        assert fail.json_body.get('errors')[0].get('location') == 'body'
        assert fail.json_body.get('errors')[0].get(
            'name') == 'Validation error for body'

    def test_action_post_on_collection_path(self):
        """Example collection POST /customers/v*/execute/action2"""
        path = self.collection_path + '/execute/action2'
        fail = self.webserver.get(path, status=404)
        assert fail.status_code == 404

    def test_action_get(self):
        """Example GET /customers/v*/{id}/execute/action2"""
        cu = self.create_customer()
        fail = self.webserver.get(self.service_path % cu.id, status=405)
        assert fail.status_code == 405

    def test_action_put(self):
        """Example PUT /customers/v*/{id}/execute/action2"""
        cu = self.create_customer()
        fail = self.webserver.put(self.service_path % cu.id, status=405)
        assert fail.status_code == 405

    def test_action_patch(self):
        """Example PATCH /customers/v*/{id}/execute/action2"""
        cu = self.create_customer()
        fail = self.webserver.patch(self.service_path % cu.id, status=405)
        assert fail.status_code == 405

    def test_action_delete(self):
        """Example DELETE /customers/v*/{id}/execute/action2"""
        cu = self.create_customer()
        fail = self.webserver.delete(self.service_path % cu.id, status=405)
        assert fail.status_code == 405


class TestCrudResourceExecute1(CrudResourceAction, CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_7/views.py
    """
    collection_path = '/customers/v7'
    path = '/customers/v7/%s'
    collection_service_path = '/customers/v7/execute/action1'
    service_path = '/customers/v7/%s/execute/action2'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_7, webserver):
        transaction = registry_rest_api_7.begin_nested()
        self.registry = registry_rest_api_7

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class TestCrudResourceExecute2(CrudResourceAction, CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_8/views.py
    """
    collection_path = '/customers/v8'
    path = '/customers/v8/%s'
    collection_service_path = '/customers/v8/execute/action1'
    service_path = '/customers/v8/%s/execute/action2'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_8, webserver):
        transaction = registry_rest_api_8.begin_nested()
        self.registry = registry_rest_api_8

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class TestCrudResourceExecute3(CrudResourceAction, CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_9/views.py
    """
    collection_path = '/customers/v9'
    path = '/customers/v9/%s'
    collection_service_path = '/customers/v9/other/action1'
    service_path = '/customers/v9/%s/other/action2'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_9, webserver):
        transaction = registry_rest_api_9.begin_nested()
        self.registry = registry_rest_api_9

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class TestCrudResourceExecute4(CrudResourceAction, CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_10/views.py
    """
    collection_path = '/customers/v10'
    path = '/customers/v10/%s'
    collection_service_path = '/foo/bar'
    service_path = '/customers/v10/%s/execute/action2'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_10, webserver):
        transaction = registry_rest_api_10.begin_nested()
        self.registry = registry_rest_api_10

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        return


class TestCrudResourceModelSchemaValidatorAndAuth(CrudResourceSchema):
    """Test Customers and Addresses from
    test_bloks/test_5/views.py
    """
    collection_path = '/customers/v5'
    path = '/customers/v5/%s'

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_rest_api_5_logged, webserver):
        transaction = registry_rest_api_5_logged.begin_nested()
        self.registry = registry_rest_api_5_logged

        def rollback():
            try:
                transaction.rollback()
            except Exception:
                pass

        request.addfinalizer(rollback)
        self.webserver = webserver
        webserver.post_json(
            '/login', {'login': 'jssuzanne', 'password': 'mypassword'},
            status=302)
        return

    def test_customer_get_logout(self):
        """Customer GET /customers/{id} [UNLOGGED]"""
        cu = self.create_customer()
        self.webserver.post_json('/logout', {}, status=302)
        self.webserver.get(self.path % cu.id, status=403)
