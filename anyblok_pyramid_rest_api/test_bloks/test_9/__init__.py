# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from uuid import UUID
from datetime import datetime

from pyramid.renderers import JSON

from anyblok.blok import Blok
from anyblok_pyramid.adapter import uuid_adapter, datetime_adapter


class TestBlok9(Blok):

    version = '0.1.0'
    required = ['anyblok-core']

    @classmethod
    def import_declaration_module(cls):
        from . import model # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import model # noqa
        reload(model)

    @classmethod
    def pyramid_load_config(cls, config):
        json_renderer = JSON()
        json_renderer.add_adapter(UUID, uuid_adapter)
        json_renderer.add_adapter(datetime, datetime_adapter)
        config.add_renderer('json', json_renderer)
        config.scan(cls.__module__ + '.views')
