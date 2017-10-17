from cornice.resource import resource
from anyblok_pyramid_rest_api.crud_resource import CrudResource


@resource(collection_path='/examples', path='/examples/{id}')
class ExampleResource(CrudResource):
    model = 'Model.Example'