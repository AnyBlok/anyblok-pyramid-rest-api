from cornice.resource import resource
from anyblok_pyramid_rest_api.rest_api_blok.crud_resource import CrudResource


@resource(collection_path='/examples', path='/examples/{id}')
class ExampleResource(CrudResource):

    def __init__(self, request, context=None):
        CrudResource.__init__(self, request)
        self.request = request
        self.context = context
        self.model = 'Example'

