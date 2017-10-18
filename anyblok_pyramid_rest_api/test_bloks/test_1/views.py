from cornice import Service
from cornice.resource import resource

from anyblok_pyramid_rest_api.crud_resource import CrudResource


@resource(collection_path='/examples', path='/examples/{id}')
class ExampleResource(CrudResource):
    """ CrudResource example
    """
    model = 'Model.Example'

# another endpoint with the same model
example_service = Service(name='example_service', path='/anothers/{id}')

@example_service.get()
def example_service_get(request):
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.query().get(request.matchdict['id'])
    return item.to_dict()
