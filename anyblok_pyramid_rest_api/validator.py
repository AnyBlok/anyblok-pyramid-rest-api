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


def deserialize_querystring(params=None):
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
    order_by = []
    tags = []
    context = {}
    limit = None
    offset = 0
    for param in params.items():
        k, v = param
        # TODO  better regex or something?
        if k.startswith("filter["):
            # Filtering (include)
            key, op = parse_key_with_two_elements(k)
            filter_by.append(dict(key=key, op=op, value=v, mode="include"))
        elif k.startswith("~filter["):
            # Filtering (exclude)
            # TODO check for errors into string pattern
            key, op = parse_key_with_two_elements(k)
            filter_by.append(dict(key=key, op=op, value=v, mode="exclude"))
        elif k.startswith("context["):
            key = parse_key_with_one_element(k)
            context[key] = v
        elif k == "tag":
            tags.append(v)
        elif k == "tags":
            tags.extend(v.split(','))
        elif k.startswith("order_by["):
            # Ordering
            op = parse_key_with_one_element(k)
            order_by.append(dict(key=v, op=op))
        elif k == 'limit':
            # TODO check to allow positive integer only if value
            limit = int(v) if v else None
        elif k == 'offset':
            # TODO check to allow positive integer only
            offset = int(v)
        else:
            raise KeyError('Bad querystring : %s=%s' % (k, v))

    return dict(filter_by=filter_by, order_by=order_by, limit=limit,
                offset=offset, tags=tags, context=context)


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
    Schema = klass.get_deserialize_schema('collection_post', model_name)
    opts = klass.get_deserialize_opts('collection_post')
    klass.apply_validator_schema(request, 'body', Schema, opts, base)


def collection_patch_validator(request, deserializer=None, klass=None,
                               **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the body
    model_name = klass.get_model_name(request, base)
    Schema = klass.get_deserialize_schema('collection_patch', model_name)
    opts = klass.get_deserialize_opts('collection_patch')
    klass.apply_validator_schema(request, 'body', Schema, opts, base)


def collection_put_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the body
    model_name = klass.get_model_name(request, base)
    Schema = klass.get_deserialize_schema('collection_put', model_name)
    opts = klass.get_deserialize_opts('collection_put')
    klass.apply_validator_schema(request, 'body', Schema, opts, base)


def collection_delete_validator(request, deserializer=None, klass=None,
                                **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the body
    model_name = klass.get_model_name(request, base)
    Schema = klass.get_deserialize_schema('collection_delete', model_name)
    opts = klass.get_deserialize_opts('collection_delete')
    klass.apply_validator_schema(request, 'body', Schema, opts, base)


def get_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    Schema = klass.get_path_schema('get')
    opts = klass.get_path_opts('get')
    klass.apply_validator_schema(request, 'path', Schema, opts, base)


def delete_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    Schema = klass.get_path_schema('get')
    opts = klass.get_path_opts('get')
    klass.apply_validator_schema(request, 'path', Schema, opts, base)


def patch_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    Schema = klass.get_path_schema('patch')
    opts = klass.get_path_opts('patch')
    klass.apply_validator_schema(request, 'path', Schema, opts, base)
    # validate the body
    model_name = klass.get_model_name(request, base)
    Schema = klass.get_deserialize_schema('patch', model_name)
    opts = klass.get_deserialize_opts('patch')
    klass.apply_validator_schema(request, 'body', Schema, opts, base)


def put_validator(request, deserializer=None, klass=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    Schema = klass.get_path_schema('put')
    opts = klass.get_path_opts('put')
    klass.apply_validator_schema(request, 'path', Schema, opts, base)
    # validate the body
    model_name = klass.get_model_name(request, base)
    Schema = klass.get_deserialize_schema('put', model_name)
    opts = klass.get_deserialize_opts('put')
    klass.apply_validator_schema(request, 'body', Schema, opts, base)


def execute_validator(request, deserializer=None, klass=None, schema=None,
                      **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    # validate the path
    Schema = klass.get_path_schema('execute')
    opts = klass.get_path_opts('execute')
    klass.apply_validator_schema(request, 'path', Schema, opts, base)
    # validate the body
    if schema:
        klass.apply_validator_schema(request, 'body', schema, {}, base)
    else:
        request.validated['body'] = base['body']


def collection_execute_validator(request, deserializer=None, klass=None,
                                 schema=None, **kwargs):
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    if schema:
        klass.apply_validator_schema(request, 'body', schema, {}, base)
    else:
        request.validated['body'] = base['body']
