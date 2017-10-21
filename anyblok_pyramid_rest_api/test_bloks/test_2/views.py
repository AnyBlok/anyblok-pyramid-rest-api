# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid import current_blok
from cornice.resource import resource
from anyblok_pyramid_rest_api.crud_resource import CrudResource


@resource(
    collection_path='/bloks',
    path='/blok/{name}',
    installed_blok=current_blok()
)
class CrudBlok(CrudResource):
    ANYBLOK_MODEL = 'Model.System.Blok'


@resource(
    collection_path='/bloks2',
    path='/blok2/{name}',
)
class CrudBlok2(CrudResource):
    ANYBLOK_MODEL = 'Model.System.Blok'


@resource(
    collection_path='/columns',
    path='/column/{model}/{name}',
    installed_blok=current_blok()
)
class CrudColumn(CrudResource):
    ANYBLOK_MODEL = 'Model.System.Column'


@resource(
    collection_path='/bad/model',
    path='/bad/model/{id}',
)
class CrudBadModel(CrudResource):
    ANYBLOK_MODEL = 'Model.Bad.Model'
