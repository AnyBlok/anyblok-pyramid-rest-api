# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_pyramid_rest_api.query import (
    update_query_filter_by_add_filter, update_query_filter_by,
    update_query_order_by)
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


class TestQuery(DBTestCase):

    def test_update_query_filter_by_add_filter_eq(self):
        registry = self.init_registry(None)
        request = None
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'eq'
        value = 'anyblok-core'
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_update_query_filter_by_add_filter_like(self):
        registry = self.init_registry(None)
        request = None
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'like'
        value = 'yblok-c'
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_update_query_filter_by_add_filter_ilike(self):
        registry = self.init_registry(None)
        request = None
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'ilike'
        value = 'yBlOk-c'
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_update_query_filter_by_add_filter_lt(self):
        registry = self.init_registry(add_integer_class)
        request = None
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'lt'
        value = 10
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 1)

    def test_update_query_filter_by_add_filter_lte(self):
        registry = self.init_registry(add_integer_class)
        request = None
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'lte'
        value = 10
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 2)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 2)

    def test_update_query_filter_by_add_filter_gt(self):
        registry = self.init_registry(add_integer_class)
        request = None
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'gt'
        value = 10
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 1)

    def test_update_query_filter_by_add_filter_gte(self):
        registry = self.init_registry(add_integer_class)
        request = None
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'gte'
        value = 10
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        self.assertEqual(len(Q.all()), 0)
        model.insert(number=9)
        self.assertEqual(len(Q.all()), 0)
        model.insert(number=10)
        self.assertEqual(len(Q.all()), 1)
        model.insert(number=11)
        self.assertEqual(len(Q.all()), 2)

    def test_update_query_filter_by_add_filter_in_1(self):
        registry = self.init_registry(None)
        request = None
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'in'
        value = 'anyblok-core'
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        obj = Q.all()
        self.assertEqual(obj.name, ['anyblok-core'])

    def test_update_query_filter_by_add_filter_in_2(self):
        registry = self.init_registry(None)
        request = None
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'in'
        value = 'anyblok-core,anyblok-io'
        Q = update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        obj = Q.all()
        self.assertEqual(obj.name, ['anyblok-core', 'anyblok-io'])

    def test_update_query_filter_by_add_filter_in_3(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'in'
        value = ''
        update_query_filter_by_add_filter(
            request, query, model, key, op, value)

        self.assertIn("Filter 'in' except a comma separated string value",
                      request.errors.messages)

    def test_update_query_filter_by_ok(self):
        registry = self.init_registry(None)
        request = None
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'eq'
        value = 'anyblok-core'
        Q = update_query_filter_by(
            request, query, model, [dict(key=key, op=op, value=value)])

        obj = Q.one()
        self.assertEqual(obj.name, 'anyblok-core')

    def test_update_query_filter_by_with_relationship(self):
        registry = self.init_registry(add_many2one_class)
        request = None
        model = registry.Test2
        query = model.query()
        key = 'test.name'
        op = 'eq'
        value = 'test'
        Q = update_query_filter_by(
            request, query, model, [dict(key=key, op=op, value=value)])

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

    def test_update_query_filter_by_ko_bad_op(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'unknown'
        value = 'anyblok-core'
        update_query_filter_by(
            request, query, model, [dict(key=key, op=op, value=value)])

        self.assertIn("Filter 'unknown' does not exist.",
                      request.errors.messages)

    def test_update_query_filter_by_bad_key(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'badkey'
        op = 'eq'
        value = 'anyblok-core'
        update_query_filter_by(
            request, query, model, [dict(key=key, op=op, value=value)])

        self.assertIn("Filter 'badkey': 'badkey' not exist in model "
                      "<class 'anyblok.model.system_blok'>.",
                      request.errors.messages)

    def test_update_query_filter_by_with_relationship_bad_key(self):
        registry = self.init_registry(add_many2one_class)
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.badkey'
        op = 'eq'
        value = 'test'
        update_query_filter_by(
            request, query, model, [dict(key=key, op=op, value=value)])

        self.assertIn("Filter 'test.badkey': 'badkey' not exist in model "
                      "<class 'anyblok.model.test'>.",
                      request.errors.messages)

    def test_update_query_order_by_ok(self):
        registry = self.init_registry(None)
        request = None
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'asc'
        Q = update_query_order_by(
            request, query, model, [dict(key=key, op=op)])

        self.assertEqual(
            Q.all().name,
            query.order_by(model.name.asc()).all().name)

    def test_update_query_order_by_ko_bad_op(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'unknown'
        update_query_order_by(
            request, query, model, [dict(key=key, op=op)])

        self.assertIn("ORDER_by operator 'unknown' does not exist.",
                      request.errors.messages)

    def test_update_query_order_by_bad_key(self):
        registry = self.init_registry(None)
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'badkey'
        op = 'asc'
        update_query_order_by(
            request, query, model, [dict(key=key, op=op)])

        self.assertIn("Key 'badkey' does not exist in model",
                      request.errors.messages)
