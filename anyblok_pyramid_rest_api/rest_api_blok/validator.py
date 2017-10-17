from cornice.validators import extract_cstruct


FILTER_OPERATORS = ['eq', 'like', 'ilike', 'lt', 'lte', 'gt', 'gte', 'in', 'not']
ORDER_BY_OPERATORS = ['asc', 'desc']


def deserialize_querystring(params=dict()):
    """
    Given a querystring parameters dict, returns a new dict that will be used to build
    query filters.
    The logic is to keep everything but transform some key, values to build database queries.
    Item whose key starts with 'filter[*' will be parsed to a key, operator, value dict (filter_by).
    Item whose key starts with 'order_by[*' will be parse to a key, operator dict(order_by).
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
                # Filtering
                # TODO check for errors into string pattern
                key = k.split("[")[1].split("]")[0]
                op = k.split("][")[1].split("]")[0]
                filter_by.append(dict(key=key, op=op, value=v))
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

    return dict(filter_by=filter_by, order_by=order_by, limit=limit, offset=offset)


def base_validator(request, schema=None, deserializer=None, **kwargs):
    """ This validator will validate the entire request through extract_cstruct if no schema
    provided
    """
    if deserializer is None:
        deserializer = extract_cstruct

    base = deserializer(request)

    if schema is None:
        request.validated.update(base)
    else:
        result, errors = schema.load(base)
        if errors:
            for k,v in errors.items():
                request.errors.add(
                        k, 'Validation error for %s' % k, ''.join(map('{}.\n'.format, v)))
        else:
            request.validated.update(result)


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
    result, errors = schema.load(body)
    if errors:
        for k,v in errors.items():
            request.errors.add('body',
                    'Validation error for %s' % k, ''.join(map('{}.\n'.format, v)))
    else:
        request.validated.update(result)

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
    result, errors = schema.load(full)
    if errors:
        for k,v in errors.items():
            request.errors.add(k, 'Validation error for %s' % k, ''.join(map('{}.\n'.format, v)))
    else:
        request.validated.update(result)
