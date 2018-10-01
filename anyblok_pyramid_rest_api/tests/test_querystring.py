# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_pyramid_rest_api.querystring import QueryString
from anyblok.column import Integer, String
from anyblok.relationship import Many2One


def add_integer_class():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class Exemple:
        id = Integer(primary_key=True)
        number = Integer()


def add_many2one_class():

    from anyblok import Declarations

    @Declarations.register(Declarations.Model)
    class Test:
        id = Integer(primary_key=True)
        name = String()

    @Declarations.register(Declarations.Model)
    class Test2:
        id = Integer(primary_key=True)
        test = Many2One(model=Declarations.Model.Test)


class MockRequestError:

    def __init__(self, testcase):
        self.testcase = testcase
        self.messages = []

    def add(self, a1, a2, a3):
        self.testcase.assertEqual(a1, 'querystring')
        self.testcase.assertEqual(a2, '400 Bad Request')
        self.messages.append(a3)


class MockRequest:

    def __init__(self, testcase):
        self.errors = MockRequestError(testcase)
        self.params = None


class TestQueryString(DBTestCase):

    def test_querystring_update_filter_eq(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'eq'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_querystring_update_filter_like(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'like'
        value = 'yblok-c'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_querystring_update_filter_ilike(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'ilike'
        value = 'yBlOk-c'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_querystring_update_filter_or_ilike(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'or-ilike'
        value = 'core,test'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        Q = Q.order_by('name')
        obj = Q.all()
        self.assertEqual(obj.name, ['anyblok-core', 'anyblok-test'])

    def test_querystring_update_filter_or_without_value(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        key = 'name'
        op = 'or-ilike'
        value = None
        qs = QueryString(request, model)
        self.assertIsNone(qs.update_or_filter(model, key, op, value))

    def test_querystring_update_filter_lt(self):
        registry = self.init_registry(add_integer_class)
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'lt'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 1)

    def test_querystring_update_filter_lte(self):
        registry = self.init_registry(add_integer_class)
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'lte'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 2)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 2)

    def test_querystring_update_filter_gt(self):
        registry = self.init_registry(add_integer_class)
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'gt'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 1)

    def test_querystring_update_filter_gte(self):
        registry = self.init_registry(add_integer_class)
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'gte'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 2)

    def test_querystring_update_filter_in_1(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'in'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.all()
        self.assertEqual(obj.name, ['anyblok-core'])

    def test_querystring_update_filter_in_2(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'in'
        value = 'anyblok-core,anyblok-test'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        names = Q.all().name
        self.assertEqual(len(names), 2)
        self.assertIn('anyblok-core', names)
        self.assertIn('anyblok-test', names)

    def test_querystring_update_filter_in_3(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        key = 'name'
        op = 'in'
        value = ''
        qs = QueryString(request, model)
        qs.update_filter(model, key, op, value)
        self.assertIn("Filter 'in' except a comma separated string value",
                      request.errors.messages)

    def test_querystring_from_filter_by_ok(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'eq'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        Q = qs.from_filter_by(query)
        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_querystring_from_filter_by_without_key(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = None
        op = 'eq'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        self.assertEqual(len(request.errors.messages), 1)

    def test_querystring_from_filter_by_with_relationship(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.name'
        op = 'eq'
        value = 'test'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        Q = qs.from_filter_by(query)
        self.assertEqual(len(Q.all()), 0)
        t1 = registry.Test(name='test')
        t2 = registry.Test(name='other')
        model.insert(test=t1)
        self.assertEqual(len(Q.all()), 1)
        model.insert(test=t2)
        self.assertEqual(len(Q.all()), 1)
        model.insert(test=t2)
        self.assertEqual(len(Q.all()), 1)
        model.insert(test=t1)
        self.assertEqual(len(Q.all()), 2)

    def test_querystring_from_filter_by_ko_bad_op(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'unknown'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        self.assertIn("Filter 'unknown' does not exist.",
                      request.errors.messages)

    def test_querystring_from_filter_by_bad_key(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'badkey'
        op = 'eq'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        self.assertIn("Filter 'badkey': 'badkey' does not exist in model "
                      "<class 'anyblok.model.factory.ModelSystemBlok'>.",
                      request.errors.messages)

    def test_querystring_from_filter_by_with_relationship_bad_key(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.badkey'
        op = 'eq'
        value = 'test'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        self.assertIn("Filter 'test.badkey': 'badkey' does not exist in model "
                      "<class 'anyblok.model.factory.ModelTest'>.",
                      request.errors.messages)

    def test_querystring_from_order_by_ok(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        Q = qs.from_order_by(query)
        self.assertEqual(
            Q.all().name,
            query.order_by(model.name.asc()).all().name)

    def test_querystring_from_order_by_without_key(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = None
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        self.assertEqual(len(request.errors.messages), 1)

    def test_querystring_from_order_by_ok_with_relationship(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.name'
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        Q = qs.from_order_by(query)
        t1 = registry.Test(name='test')
        t2 = registry.Test(name='other')
        model.insert(test=t1)
        model.insert(test=t2)
        model.insert(test=t2)
        model.insert(test=t1)
        query = query.join(registry.Test2.test)
        query = query.order_by(registry.Test.name.asc())
        self.assertEqual(Q.all(), query.all())

    def test_querystring_from_order_by_ko_bad_op(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'unknown'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        self.assertIn("ORDER_by operator 'unknown' does not exist.",
                      request.errors.messages)

    def test_querystring_from_order_by_bad_key(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'badkey'
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        self.assertIn("Order 'badkey': 'badkey' does not exist in model "
                      "<class 'anyblok.model.factory.ModelSystemBlok'>.",
                      request.errors.messages)

    def test_querystring_from_order_by_bad_key_relationship(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.badkey'
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        self.assertIn("Order 'test.badkey': 'badkey' does not exist in model "
                      "<class 'anyblok.model.factory.ModelTest'>.",
                      request.errors.messages)

    def test_querystring_from_limit(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.limit = 1
        Q = qs.from_limit(query)
        self.assertEqual(len(Q.all()), 1)

    def test_querystring_from_limit_without_limit(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.limit = None
        Q = qs.from_limit(query)
        self.assertEqual(len(Q.all()), len(query.all()))

    def test_querystring_from_offset(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.offset = 3
        Q = qs.from_offset(query)
        self.assertEqual(len(Q.all()), len(query.offset(3).all()))

    def test_querystring_from_offset_without_offset(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.offset = None
        Q = qs.from_offset(query)
        self.assertEqual(len(Q.all()), len(query.all()))

    def test_querystring_get_remote_model_for(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        Model = qs.get_remote_model_for(registry.Test2, 'test')
        self.assertIs(Model, registry.Test)

    def test_querystring_get_remote_model_for_without_relationship(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        Model = qs.get_remote_model_for(registry.Test, 'name')
        self.assertIsNone(Model)

    def test_querystring_get_remote_model_for_unknown(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        Model = qs.get_remote_model_for(registry.Test, 'test')
        self.assertIsNone(Model)

    def test_querystring_get_model_and_key_from_relationship_1(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(query, model, ['name'])
        self.assertIs(res[1], model)
        self.assertEqual(res[2], 'name')

    def test_querystring_get_model_and_key_from_relationship_2(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(
            query, model, ['test', 'name'])
        self.assertIs(res[1], registry.Test)
        self.assertEqual(res[2], 'name')

    def test_querystring_get_model_and_key_from_relationship_3(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(
            query, model, ['test', 'number'])
        self.assertEqual(
            res,
            "'number' does not exist in model <class 'anyblok.model.factory."
            "ModelTest'>.")

    def test_querystring_get_model_and_key_from_relationship_4(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Column
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(
            query, model, ['model', 'name'])
        self.assertEqual(
            "'model' in model "
            "<class 'anyblok.model.factory.ModelSystemColumn'> is not "
            "a relationship.",
            res)

    def test_has_no_tag(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        self.assertFalse(qs.has_tag('unknown.tag'))
