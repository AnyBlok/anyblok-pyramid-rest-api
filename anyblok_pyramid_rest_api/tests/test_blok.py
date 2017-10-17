# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidDBTestCase


class CrudTestCase(PyramidDBTestCase):

    blok_entry_points = ('bloks', 'test_bloks')

    def setUp(self):
        super(CrudTestCase, self).setUp()
        self.registry = self.init_registry(None)
        self.registry.upgrade(install=('test_rest_api_2',))


class TestCrudBlok(CrudTestCase):

    def test_current_blok(self):
        resp = self.webserver.get('/bloks', status=200)
        self.assertEqual(
            resp.json_body,
            self.registry.System.Blok.query().all().to_dict()
        )
