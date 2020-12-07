# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice.validators import extract_cstruct
from marshmallow import ValidationError, INCLUDE
import warnings
from logging import getLogger
import re

logger = getLogger(__name__)


FILTER_OPERATORS = [
    'eq', 'like', 'ilike', 'lt', 'lte', 'gt', 'gte',
    'in', 'or-like', 'or-ilike', 'or-lt', 'or-lte', 'or-gt', 'or-gte'
]
ORDER_BY_OPERATORS = ['asc', 'desc']


def parse_key_with_two_elements(filter_):
    pattern = ".*\\[(.*)\\]\\[(.*)\\]"
    return re.match(pattern, filter_).groups()


def parse_key_with_one_element(filter_):
    pattern = ".*\\[(.*)\\]"
    return re.match(pattern, filter_).groups()[0]


def get_order_by(k, v):
    key = parse_key_with_one_element(k)
    if key in ('asc', 'desc') and v not in ('asc', 'desc'):
        warnings.warn((
            "deprecated: replace order_by[%(key)s]=%(op)s by"
            "order_by[%(op)s]=%(key)s") % dict(key=key, op=v),
            DeprecationWarning)
        return dict(key=v, op=key)

    return dict(key=key, op=v)


def deserialize_querystring_composite_filters(key, op, value, mode=None):
    filters = []
    keys = key.split(':')
    ops = []
    if op is not None:
        ops = op.split(':')
        if len(keys) != len(ops):
            raise ValueError(
                f'len of key {keys} is different than len of op {ops}')

    for values in value.split(','):
        v = values.split(':')
        composite_filters = []
        if len(keys) != len(v):
            raise ValueError(
                f'len of key {keys} is different than len of value {v}')

        for i, k in enumerate(keys):
            filter_ = dict(key=k, value=v[i])
            if op is not None:
                filter_['op'] = ops[i]
            composite_filters.append(filter_)

        filters.append(composite_filters)

    return {
        'filters': filters,
        'mode': mode,
    }


def deserialize_querystring(params=None):  # noqa C901
    """
    Given a querystring parameters dict, returns a new dict that will be used
    to build query filters.
    The logic is to keep everything but transform some key, values to build
    database queries.
    Item whose key starts with 'filter[*' will be parsed to a key, operator,
    value dict (filter_by).
    Item whose key starts with 'order_by[*' will be parse to a key, operator
    dict(order_by).
    'limit' and 'offset' are kept as is.
    All other keys are added to 'filter_by' with 'eq' as default operator.

    # TODO: Use marshmallow pre-validation feature
    # TODO: Evaluate 'webargs' python module to see if it can helps

    :param params: A dict that represent a querystring (request.params)
    :type params: dict
    :return: A suitable dict for building a filtering query
    :rtype: dict
    """
    filter_by = []
    composite_filter_by = []
    filter_by_primary_keys = {}
    order_by = []
    tags = []
    context = {}
    limit = None
    offset = 0
    for param in params.items():
        k, v = param
        # TODO  better regex or something?
        if k.startswith("filter[") or k.startswith("~filter["):
            key, op = parse_key_with_two_elements(k)
            filter_by.append(dict(
                key=key, op=op, value=v,
                mode=("exclude" if k[0] == '~' else "include")))
        elif k.startswith("primary-keys[") or k.startswith("~primary-keys["):
            key = parse_key_with_one_element(k)
            filter_by_primary_keys = deserialize_querystring_composite_filters(
                key, None, v, mode=("exclude" if k[0] == '~' else "include"))
        elif (
            k.startswith("composite-filter[") or
            k.startswith("~composite-filter[")
        ):
            key, op = parse_key_with_two_elements(k)
            composite_filter_by.append(
                deserialize_querystring_composite_filters(
                    key, op, v, mode=("exclude" if k[0] == '~' else "include")
                ))
        elif k.startswith("context["):
            key = parse_key_with_one_element(k)
            context[key] = v
        elif k == "tag":
            tags.append(v)
        elif k == "tags":
            tags.extend(v.split(','))
        elif k.startswith("order_by["):
            # Ordering
            order_by.append(get_order_by(k, v))
        elif k == 'limit':
            # TODO check to allow positive integer only if value
            limit = int(v) if v else None
        elif k == 'offset':
            # TODO check to allow positive integer only
            offset = int(v)
        else:
            raise KeyError('Bad querystring : %s=%s' % (k, v))

    return dict(filter_by=filter_by, composite_filter_by=composite_filter_by,
                order_by=order_by, limit=limit, offset=offset,
                filter_by_primary_keys=filter_by_primary_keys,
                tags=tags, context=context)


def base_validator(request, schema, deserializer, only, unknown=INCLUDE):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    logger.debug('base receipt: %r', base)
    if schema is None:
        request.validated = base
        return

    schema = schema(context={'registry': request.anyblok.registry},
                    only=only, unknown=unknown)

    try:
        result = schema.load(base)
        request.validated = result
    except ValidationError as err:
        errors = err.messages
        logger.exception(errors)
        for k, v in errors.items():
            request.errors.add(
                k, 'Validation error for %s' % k,
                v)


def service_collection_get_validator(request, schema=None,
                                     deserializer=None, **kwargs):
    base_validator(request, schema, deserializer, only=['querystring'])


def service_post_validator(request, schema=None, deserializer=None, **kwargs):
    base_validator(request, schema, deserializer, only=['body'])


def service_get_validator(request, schema=None, deserializer=None, **kwargs):
    base_validator(request, schema, deserializer, only=['path'])


def service_put_validator(request, schema=None, deserializer=None, **kwargs):
    base_validator(request, schema, deserializer, only=['path', 'body'])


service_patch_validator = service_put_validator


def service_delete_validator(request, schema=None, deserializer=None, **kwargs):
    base_validator(request, schema, deserializer, only=['path'])


def collection_get_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    deserializer(request)
    # I don't know how validate the query string


def collection_post_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the body
    model_name = klass.get_model_name(request, base)
    schema = klass.get_validator_schema(
        request, 'deserialize', 'collection_post', model_name)
    klass.apply_validator_schema(request, 'body', schema, base)


def collection_patch_validator(request, deserializer=None, klass=None,
                               **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the body
    model_name = klass.get_model_name(request, base)
    schema = klass.get_validator_schema(
        request, 'deserialize', 'collection_patch', model_name)
    klass.apply_validator_schema(request, 'body', schema, base)


def collection_put_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the body
    model_name = klass.get_model_name(request, base)
    schema = klass.get_validator_schema(
        request, 'deserialize', 'collection_put', model_name)
    klass.apply_validator_schema(request, 'body', schema, base)


def collection_delete_validator(request, deserializer=None, klass=None,
                                **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the body
    model_name = klass.get_model_name(request, base)
    schema = klass.get_validator_schema(
        request, 'deserialize', 'collection_delete', model_name)
    klass.apply_validator_schema(request, 'body', schema, base)


def get_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    schema = klass.get_validator_schema(request, 'path', 'get', None)
    klass.apply_validator_schema(request, 'path', schema, base)


def delete_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    schema = klass.get_validator_schema(request, 'path', 'get', None)
    klass.apply_validator_schema(request, 'path', schema, base)


def patch_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    model_name = klass.get_model_name(request, base)
    # validate the path
    schema = klass.get_validator_schema(
        request, 'path', 'patch', model_name)
    klass.apply_validator_schema(request, 'path', schema, base)
    # validate the body
    schema = klass.get_validator_schema(
        request, 'deserialize', 'patch', model_name)
    klass.apply_validator_schema(request, 'body', schema, base)


def put_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    schema = klass.get_validator_schema(request, 'path', 'put', None)
    klass.apply_validator_schema(request, 'path', schema, base)
    # validate the body
    model_name = klass.get_model_name(request, base)
    schema = klass.get_validator_schema(
        request, 'deserialize', 'put', model_name)
    klass.apply_validator_schema(request, 'body', schema, base)


def execute_validator(request, deserializer=None, klass=None, schema=None,
                      **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    schema_ = klass.get_validator_schema(request, 'path', 'execute', None)
    klass.apply_validator_schema(request, 'path', schema_, base)
    # validate the body
    if schema:
        klass.apply_validator_schema(request, 'body', schema(), base)
    else:
        request.validated['body'] = base['body']


def collection_execute_validator(request, deserializer=None, klass=None,
                                 schema=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    if schema:
        klass.apply_validator_schema(request, 'body', schema(), base)
    else:
        request.validated['body'] = base['body']
