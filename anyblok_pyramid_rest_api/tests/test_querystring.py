# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok_pyramid_rest_api.querystring import QueryString
from anyblok.column import Integer, String
from anyblok.relationship import Many2One
from .conftest import init_registry_with_bloks


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
        assert a1 == 'querystring'
        assert a2 == '400 Bad Request'
        self.messages.append(a3)


class MockRequest:

    def __init__(self, testcase):
        self.errors = MockRequestError(testcase)
        self.params = {}


class TestQueryString:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_blok):
        transaction = registry_blok.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_querystring_update_filter_eq(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'eq'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.one()
        assert obj.name == 'anyblok-core'

    def test_querystring_update_sqlalchemy_query(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.update_sqlalchemy_query(query)

    def test_querystring_update_filter_like(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'like'
        value = 'yblok-c'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.one()
        assert obj.name == 'anyblok-core'

    def test_querystring_update_filter_ilike(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'ilike'
        value = 'yBlOk-c'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.one()
        assert obj.name == 'anyblok-core'

    def test_querystring_update_filter_or_ilike(self, registry_blok):
        registry = registry_blok
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
        assert obj.name == ['anyblok-core', 'anyblok-test']

    def test_querystring_update_filter_or_without_value(self,
                                                        registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        key = 'name'
        op = 'or-ilike'
        value = None
        qs = QueryString(request, model)
        assert qs.update_or_filter(model, key, op, value) is None

    def test_querystring_update_filter_in_1(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'in'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        obj = Q.all()
        assert obj.name == ['anyblok-core']

    def test_querystring_update_filter_in_2(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'in'
        value = 'anyblok-core,anyblok-test'
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        names = Q.all().name
        assert len(names) == 2
        assert 'anyblok-core' in names
        assert 'anyblok-test' in names

    def test_querystring_update_filter_in_3(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        key = 'name'
        op = 'in'
        value = ''
        qs = QueryString(request, model)
        qs.update_filter(model, key, op, value)
        assert (
            "Filter 'in' except a comma separated string value" in
            request.errors.messages)

    def test_querystring_from_filter_by_ok(self, registry_blok):
        registry = registry_blok
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
        assert obj.name == 'anyblok-core'

    def test_querystring_from_filter_by_without_key(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = None
        op = 'eq'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        assert len(request.errors.messages) == 1

    def test_querystring_from_filter_by_ko_bad_op(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'unknown'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        assert (
            "Filter 'unknown' does not exist." in
            request.errors.messages)

    def test_querystring_from_filter_by_bad_key(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'badkey'
        op = 'eq'
        value = 'anyblok-core'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        assert (
            "Filter 'badkey': 'badkey' does not exist in model "
            "<class 'anyblok.model.factory.ModelSystemBlok'>." in
            request.errors.messages)

    def test_querystring_from_order_by_ok(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        Q = qs.from_order_by(query)
        assert Q.all().name == query.order_by(model.name.asc()).all().name

    def test_querystring_from_order_by_without_key(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = None
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        assert len(request.errors.messages) == 1

    def test_querystring_from_order_by_ko_bad_op(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'name'
        op = 'unknown'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        assert (
            "ORDER_by operator 'unknown' does not exist." in
            request.errors.messages)

    def test_querystring_from_order_by_bad_key(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        key = 'badkey'
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        assert (
            "Order 'badkey': 'badkey' does not exist in model "
            "<class 'anyblok.model.factory.ModelSystemBlok'>." in
            request.errors.messages)

    def test_querystring_from_limit(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.limit = 1
        Q = qs.from_limit(query)
        assert len(Q.all()) == 1

    def test_querystring_from_limit_without_limit(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.limit = None
        Q = qs.from_limit(query)
        assert len(Q.all()) == len(query.all())

    def test_querystring_from_offset(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.offset = 3
        Q = qs.from_offset(query)
        assert len(Q.all()) == len(query.offset(3).all())

    def test_querystring_from_offset_without_offset(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        qs.offset = None
        Q = qs.from_offset(query)
        assert len(Q.all()) == len(query.all())

    def test_querystring_get_model_and_key_from_relationship_1(self,
                                                               registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(query, model, ['name'])
        assert res[1] is model
        assert res[2] == 'name'

    def test_querystring_get_model_and_key_from_relationship_4(self,
                                                               registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Column
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(
            query, model, ['model', 'name'])
        assert (
            "'model' in model "
            "<class 'anyblok.model.factory.ModelSystemColumn'> is not "
            "a relationship." == res)

    def test_has_no_tag(self, registry_blok):
        registry = registry_blok
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        assert not (qs.has_tag('unknown.tag'))


@pytest.fixture(scope="class")
def registry_blok_with_integer(request, bloks_loaded):
    registry = init_registry_with_bloks([], add_integer_class)
    request.addfinalizer(registry.close)
    return registry


class TestQueryStringOnInteger:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_blok_with_integer):
        transaction = registry_blok_with_integer.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_querystring_update_filter_lt(self, registry_blok_with_integer):
        registry = registry_blok_with_integer
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'lt'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        assert len(Q.all()) == 0
        model.insert(number=9)
        assert len(Q.all()) == 1
        model.insert(number=10)
        assert len(Q.all()) == 1
        model.insert(number=11)
        assert len(Q.all()) == 1

    def test_querystring_update_filter_lte(self, registry_blok_with_integer):
        registry = registry_blok_with_integer
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'lte'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        assert len(Q.all()) == 0
        model.insert(number=9)
        assert len(Q.all()) == 1
        model.insert(number=10)
        assert len(Q.all()) == 2
        model.insert(number=11)
        assert len(Q.all()) == 2

    def test_querystring_update_filter_gt(self, registry_blok_with_integer):
        registry = registry_blok_with_integer
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'gt'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        assert len(Q.all()) == 0
        model.insert(number=9)
        assert len(Q.all()) == 0
        model.insert(number=10)
        assert len(Q.all()) == 0
        model.insert(number=11)
        assert len(Q.all()) == 1

    def test_querystring_update_filter_gte(self, registry_blok_with_integer):
        registry = registry_blok_with_integer
        request = MockRequest(self)
        model = registry.Exemple
        query = model.query()
        key = 'number'
        op = 'gte'
        value = 10
        qs = QueryString(request, model)
        Q = query.filter(qs.update_filter(model, key, op, value))
        assert len(Q.all()) == 0
        model.insert(number=9)
        assert len(Q.all()) == 0
        model.insert(number=10)
        assert len(Q.all()) == 1
        model.insert(number=11)
        assert len(Q.all()) == 2


@pytest.fixture(scope="class")
def registry_blok_with_m2o(request, bloks_loaded):
    registry = init_registry_with_bloks([], add_many2one_class)
    request.addfinalizer(registry.close)
    return registry


class TestQueryStringWithM2O:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_blok_with_m2o):
        transaction = registry_blok_with_m2o.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_querystring_from_filter_by_with_relationship(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.name'
        op = 'eq'
        value = 'test'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        Q = qs.from_filter_by(query)
        assert len(Q.all()) == 0
        t1 = registry.Test(name='test')
        t2 = registry.Test(name='other')
        model.insert(test=t1)
        assert len(Q.all()) == 1
        model.insert(test=t2)
        assert len(Q.all()) == 1
        model.insert(test=t2)
        assert len(Q.all()) == 1
        model.insert(test=t1)
        assert len(Q.all()) == 2

    def test_querystring_from_filter_by_with_relationship_bad_key(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.badkey'
        op = 'eq'
        value = 'test'
        qs = QueryString(request, model)
        qs.filter_by = [dict(key=key, op=op, value=value)]
        qs.from_filter_by(query)
        assert (
            "Filter 'test.badkey': 'badkey' does not exist in model "
            "<class 'anyblok.model.factory.ModelTest'>." in
            request.errors.messages)

    def test_querystring_from_order_by_ok_with_relationship(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
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
        assert Q.all() == query.all()

    def test_querystring_from_order_by_bad_key_relationship(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        key = 'test.badkey'
        op = 'asc'
        qs = QueryString(request, model)
        qs.order_by = [dict(key=key, op=op)]
        qs.from_order_by(query)
        assert (
            "Order 'test.badkey': 'badkey' does not exist in model "
            "<class 'anyblok.model.factory.ModelTest'>." in
            request.errors.messages)

    def test_querystring_get_remote_model_for(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        Model = qs.get_remote_model_for(registry.Test2, 'test')
        assert Model is registry.Test

    def test_querystring_get_remote_model_for_without_relationship(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        Model = qs.get_remote_model_for(registry.Test, 'name')
        assert Model is None

    def test_querystring_get_remote_model_for_unknown(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.System.Blok
        qs = QueryString(request, model)
        Model = qs.get_remote_model_for(registry.Test, 'test')
        assert Model is None

    def test_querystring_get_model_and_key_from_relationship_2(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(
            query, model, ['test', 'name'])
        assert res[1] is registry.Test
        assert res[2] == 'name'

    def test_querystring_get_model_and_key_from_relationship_3(
        self, registry_blok_with_m2o
    ):
        registry = registry_blok_with_m2o
        request = MockRequest(self)
        model = registry.Test2
        query = model.query()
        qs = QueryString(request, model)
        res = qs.get_model_and_key_from_relationship(
            query, model, ['test', 'number'])
        waiting = ("'number' does not exist in model <class 'anyblok.model."
                   "factory.ModelTest'>.")
        assert res == waiting
