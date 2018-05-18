# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice.validators import extract_cstruct
from marshmallow import ValidationError
from .schema import ApiSchema


FILTER_OPERATORS = [
    'eq', 'like', 'ilike', 'lt', 'lte', 'gt', 'gte',
    'in', 'or-like', 'or-ilike', 'or-lt', 'or-lte', 'or-gt', 'or-gte'
]
ORDER_BY_OPERATORS = ['asc', 'desc']


def deserialize_querystring(params=dict()):
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
    limit = None
    offset = 0
    if params:
        for param in params.items():
            k, v = param
            # TODO  better regex or something?
            if k.startswith("filter["):
                # Filtering (include)
                # TODO check for errors into string pattern
                key = k.split("[")[1].split("]")[0]
                op = k.split("][")[1].split("]")[0]
                filter_by.append(dict(key=key, op=op, value=v, mode="include"))
            elif k.startswith("~filter["):
                # Filtering (exclude)
                # TODO check for errors into string pattern
                key = k.split("[")[1].split("]")[0]
                op = k.split("][")[1].split("]")[0]
                filter_by.append(dict(key=key, op=op, value=v, mode="exclude"))
            elif k.startswith("order_by["):
                # Ordering
                op = k.split("[")[1].split("]")[0]
                order_by.append(dict(key=v, op=op))
            elif k == 'limit':
                # TODO check to allow positive integer only if value
                limit = int(v) if v else None
            elif k == 'offset':
                # TODO check to allow positive integer only
                offset = int(v)
            else:
                # Unknown key, add it as a filter with 'eq' operator
                filter_by.append(dict(key=k, op='eq', value=v))

    return dict(filter_by=filter_by, order_by=order_by, limit=limit,
                offset=offset)


def base_validator(request, schema=None, deserializer=None, **kwargs):
    """ Validate the entire request through cornice.validators.extract_cstruct
    if no schema provided
    """
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)
    if schema is None:
        del base['body']
        request.validated.update(base)
    else:
        try:
            result = schema.load(base)
            request.validated.update(result)
        except ValidationError as err:
            errors = err.messages
            for k, v in errors.items():
                request.errors.add(
                    k,
                    'Validation error for %s' % k,
                    ''.join(map('{}.\n'.format, v)))


def body_validator(request, schema=None, deserializer=None, **kwargs):
    """ This validator will add the 'body'content to request.validated
    if any marshmallow instanciated schema is provided, otherwise it will do
    nothing.
    """
    if deserializer is None:
        deserializer = extract_cstruct

    if schema is None:
        return

    body = deserializer(request).get('body', {})
    if request.anyblok:
        schema.context['registry'] = request.anyblok.registry

    try:
        result = schema.load(body)
        request.validated.update(result)
    except ValidationError as err:
        errors = err.messages
        for k, v in errors.items():
            request.errors.add(
                'body',
                'Validation error for %s' % k,
                ''.join(map('{}.\n'.format, v)))


def full_validator(request, schema=None, deserializer=None, **kwargs):
    """ This validator will validate the entire request if any schema is provided.
    Note that in this case the schema should map it's fields to all the fields
    returned by the deserializer.
    """
    if deserializer is None:
        deserializer = extract_cstruct

    if schema is None:
        return

    full = deserializer(request)
    if request.anyblok:
        schema.context['registry'] = request.anyblok.registry

    try:
        result = schema.load(full)
        request.validated.update(result)
    except ValidationError as err:
        errors = err.messages
        for k, v in errors.items():
            request.errors.add(
                k, 'Validation error for %s' % k,
                ''.join(map('{}.\n'.format, v)))


def model_schema_validator(request, schema=None, deserializer=None, **kwargs):
    """
    """
    if schema is None:
        klass = kwargs.get('klass', None)
        if klass and getattr(klass, 'model', None):
            metaProperties = {}
            if hasattr(klass, 'apischema_properties'):
                klass.apischema_properties(metaProperties)

            metaProperties.update({'model': klass.model})
            if getattr(klass, 'schema_defined_by', None):
                if request.anyblok:
                    registry = request.anyblok.registry
                    Model = registry.get(klass.model)
                    schema = getattr(Model, klass.schema_defined_by)(
                        request=request, klass=klass,
                        metaProperties=metaProperties
                    )
                else:
                    # raise error we must have a schema
                    raise TypeError(
                        "No AnyBlok registry to define schema "
                        "`model_schema_validator`")

            else:
                schema = type(
                    'Api.Schema.%s' % klass.model,
                    (ApiSchema,),
                    {'Meta': type('Meta', tuple(), metaProperties)}
                )()

            # put the build schema in the request because the crud_resource
            # need a dschema and dschema_collection, it is the only way
            request.current_service.schema = schema
        else:
            # raise error we must have a schema
            raise TypeError(
                "You must provide a schema to your view when using "
                "`model_schema_validator`")

    if deserializer is None:
        deserializer = extract_cstruct

    if request.current_service.name.startswith("collection"):
        action = "collection_%s" % request.method.lower()
    else:
        action = request.method.lower()

    if action in schema.fields.keys() and schema.fields.get(action).nested:
        schema = schema.fields.get(action).nested

    return full_validator(request,
                          schema=schema,
                          deserializer=deserializer,
                          **kwargs)
