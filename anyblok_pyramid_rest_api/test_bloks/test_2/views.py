from anyblok_pyramid import current_blok
from cornice.resource import resource
from anyblok_pyramid_rest_api.crud_resource import CrudResource


@resource(
    collection_path='/bloks',
    path='/blok/{name}',
    installed_blok=current_blok()
)
class CrudBlok(CrudResource):
    Model = 'Model.System.Blok'


@resource(
    collection_path='/columns',
    path='/column/{model}/{name}',
    installed_blok=current_blok()
)
class CrudColumn(CrudResource):
    Model = 'Model.System.Column'
