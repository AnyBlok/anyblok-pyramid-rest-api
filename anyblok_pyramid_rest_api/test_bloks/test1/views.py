from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api import CrudRessource
from cornice import resource


@resource(
    collection_path='/bloks',
    path='/blok/{name}',
    installed_blok=current_blok()
)
class CrudBlok(CrudRessource):
    Model = 'Model.System.Blok'


@resource(
    collection_path='/columns',
    path='/column/{model}/{name}',
    installed_blok=current_blok()
)
class CrudColumn(CrudRessource):
    Model = 'Model.System.Column'
