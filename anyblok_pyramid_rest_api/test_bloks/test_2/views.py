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
    collection_path='/bloks1',
    path='/blok1/{name}',
    installed_blok=current_blok()
)
class CrudBlok(CrudResource):
    model = 'Model.System.Blok'


@resource(
    collection_path='/bloks2',
    path='/blok2/{name}',
)
class CrudBlok2(CrudResource):
    model = 'Model.System.Blok'


@resource(
    collection_path='/columns',
    path='/column/{model}/{name}',
    installed_blok=current_blok()
)
class CrudColumn(CrudResource):
    model = 'Model.System.Column'


@resource(
    collection_path='/bad/model',
    path='/bad/model/{id}',
)
class CrudBadModel(CrudResource):
    model = 'Model.Bad.Model'
