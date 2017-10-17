from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api import CrudRessource, validator
from cornice import resource


@resource(
    collection_path='/bloks',
    path='/blok/{name}',
    installed_blok=current_blok()
)
class CrudBlok(CrudRessource):
    Model = 'Model.System.Blok'

    collection_get = CrudRessource.property_collection_get()
    collection_post = CrudRessource.property_collection_post()
    get = CrudRessource.property_get()
    put = CrudRessource.property_put()
    delete = CrudRessource.property_delete()


@resource(
    collection_path='/bloks/ro',
    path='/blok/ro/{name}',
    installed_blok=current_blok()
)
class CrudBlokRO(CrudRessource):
    Model = 'Model.System.Blok'

    collection_get = CrudRessource.property_collection_get()
    get = CrudRessource.property_get()


@resource(
    collection_path='/models',
    path='/model/{name}',
    installed_blok=current_blok()
)
class CrudModel(CrudRessource):
    Model = 'Model.System.Model'

    collection_get = CrudRessource.property_collection_get(
        validators=(validator.base_validator,))

    collection_post = CrudRessource.property_collection_post(
        validators=(validator.base_validator,))

    get = CrudRessource.property_get(
        validators=(validator.base_validator,))

    put = CrudRessource.property_put(
        validators=(validator.base_validator,))

    delete = CrudRessource.property_delete(
        validators=(validator.base_validator,))


@resource(
    collection_path='/columns',
    path='/column/{model}/{name}',
    installed_blok=current_blok()
)
class CrudColumn(CrudRessource):
    Model = 'Model.System.Blok'

    collection_get = CrudRessource.property_collection_get()
    collection_post = CrudRessource.property_collection_post()
    get = CrudRessource.property_get()
    put = CrudRessource.property_put()
    delete = CrudRessource.property_delete()
