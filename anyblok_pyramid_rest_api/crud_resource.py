""" A set of methods for crud resource manipulation
# TODO: Add a get_or_create_item method
# TODO: Manage relationship
# TODO: Response objects serialization
"""

from cornice.validators import extract_cstruct
from cornice.resource import view as cornice_view

from .rest_api_blok.validator import (
    deserialize_querystring, base_validator,
    FILTER_OPERATORS, ORDER_BY_OPERATORS)


class CrudResource(object):
    """ A class that add to cornice resource CRUD abilities on Anyblok models.

    :Example:

    >>> @resource(collection_path='/examples', path='/examples/{id}')
    >>> class ExampleResource(CrudResource):
    >>>     model = 'Model.Example'

    """
    model = None
    item_key = 'id'

    def __init__(self, request):
        self.request = request
        self.registry = self.request.anyblok.registry

    def get_model(self):
        if not self.model:
            raise ValueError("You must provide a 'model' to use CrudResource class")
        try:
            model = self.registry.get(self.model)
        except KeyError:
            raise KeyError("The model you set on CrudResource class does not exists")

        return model

    @cornice_view(validators=(base_validator,))
    def collection_get(self):
        """Parse request.params, deserialize it and then build an sqlalchemy query

        Default behaviour is to search for equal matches where key is a column name
        Two special keys are available ('filter[*' and 'order_by[*')

        Filter must be something like 'filter[key][operator]=value' where key is mapped to an sql
        column and operator is one of (eq, ilike, like, lt, lte, gt, gte, in, not)

        Order_by must be something like 'order_by[operator]=value' where 'value' is mapped to an sql
        column and operator is one of (asc, desc)

        Limit will limit the records quantity
        Offset will apply an offset on records
        """
        model = self.get_model()
        Q = model.query()

        headers = self.request.response.headers
        headers['X-Total-Records'] = str(Q.count())

        if self.request.params:
            # TODO: Implement schema validation to use request.validated
            parsed_params = deserialize_querystring(self.request.params)

            for item in parsed_params["filter_by"]:
                op = item.get('op')
                key = item.get('key')
                value = item.get('value')
                # Is operator valid?
                if op not in FILTER_OPERATORS:
                    self.request.errors.add('querystring',
                            '400 Bad Request', 'Filter %s does not exist.' % op)
                    self.request.errors.status = 400
                # Column exists?
                if key not in model.fields_description().keys():
                    self.request.errors.add('querystring',
                            '400 Bad Request', "Key '%s' does not exist in model" % key)
                    self.request.errors.status = 400
                    # set key to None to avoid making a query filter based on it
                    key = None

                if key:
                    if op == "eq":
                        Q = Q.filter(getattr(model, key) == value)
                    if op == "like":
                        Q = Q.filter(getattr(model, key).like("%" + value + "%"))
                    if op == "ilike":
                        Q = Q.filter(getattr(model, key).ilike("%" + value + "%"))
                    if op == "lt":
                        Q = Q.filter(getattr(model, key) < value)
                    if op == "lte":
                        Q = Q.filter(getattr(model, key) <= value)
                    if op == "gt":
                        Q = Q.filter(getattr(model, key) > value)
                    if op == "gte":
                        Q = Q.filter(getattr(model, key) >= value)
                    if op == "in":
                    # ensure we have a comma separated value string...
                        values = value.split(',')
                        if values:
                            Q = Q.filter(getattr(model, key) in values)
                        else:
                            self.request.errors.add('querystring', '400 Bad Request',
                                    'Filter %s except a comma separated string value' % op)
                            self.request.errors.status = 400
                    if op == "not":
                        # TODO: exclusion
                        self.request.errors.add('querystring',
                                '400 Bad Request', "'%s' filter not implemented yet" % op)
                        self.request.errors.status = 400

            # ORDER_BY
            for item in parsed_params["order_by"]:
                op = item.get('op')
                key = item.get('key')
                # Is operator valid?
                if op not in ORDER_BY_OPERATORS:
                    self.request.errors.add('querystring',
                            '400 Bad Request', "ORDER_by operator '%s' does not exist." % op)
                    self.request.errors.status = 400
                # Column exists?
                if key not in model.fields_description().keys():
                    self.request.errors.add('querystring',
                            '400 Bad Request', "Key '%s' does not exist in model" % key)
                    self.request.errors.status = 400

                if op == "asc":
                    Q = Q.order_by(getattr(model, key).asc())
                if op == "desc":
                    Q = Q.order_by(getattr(model, key).desc())
            # LIMIT
            if parsed_params.get('limit', None):
                Q = Q.limit(int(parsed_params['limit']))
            # OFFSET
            if parsed_params.get('offset', 0) > 0:
                Q = Q.offset(int(parsed_params['offset']))

            # TODO: Advanced pagination with Link Header
            #Link: '<https://api.github.com/user/repos?page=3&per_page=100>; rel="next", <https://api.github.com/user/repos?page=50&per_page=100>; rel="last"'
            headers['X-Count-Records'] = str(Q.count())
            # TODO: Etag / timestamp / 304 if no changes
            # TODO: Cache headers
            return Q.all().to_dict() if Q.count() > 0 else dict()
        else:
            # no querystring, returns all records (maybe we will want to apply some default filters
            # values
            headers['X-Count-Records'] = str(Q.count())
            return Q.all().to_dict() if Q.count() > 0 else dict()

    @cornice_view(validators=(base_validator,))
    def collection_post(self):
        """
        """
        model = self.get_model()
        item = model.insert(**self.request.validated['body'])

        return item.to_dict()

    @cornice_view(validators=(base_validator,))
    def get(self):
        """
        """
        model = self.get_model()
        item = model.query().get(self.request.matchdict[self.item_key])
        if item:
            return item.to_dict()
        else:
            self.request.errors.add('path', '404 not found',
                    'Resource %s with %s=%s does not exist.' % (
                        self.model, self.item_key, self.request.matchdict[self.item_key]))
            self.request.errors.status = 404

    @cornice_view(validators=(base_validator,))
    def put(self):
        """
        """
        model = self.get_model()
        path = self.request.validated.get('path').copy()
        key, value = path.popitem()
        item = model.query().filter(getattr(model, key) == value).first()
        if item:
            item.update(**self.request.validated['body'])
            return item.to_dict()
        else:
            self.request.errors.add('path', '404 not found',
                    'Resource %s with %s=%s does not exist.' % (model, key, value))
            self.request.errors.status = 404

    @cornice_view(validators=(base_validator,))
    def delete(self):
        """
        """
        model = self.get_model()
        item = model.query().get(self.request.matchdict[self.item_key])
        if item:
            item.delete()
            self.request.status = 204
            return {}
        else:
            self.request.errors.add('path',
                    '404 not found', 'Resource %s with %s=%s does not exist.' % (
                        self.model, self.item_key, self.request.matchdict[self.item_key]))
            self.request.errors.status = 404
