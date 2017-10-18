# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
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
