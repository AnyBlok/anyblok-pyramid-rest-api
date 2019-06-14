.. This file is a part of the AnyBlok / Pyramid / REST api project
..
..    Copyright (C) 2017 Franck BRET <franckbret@gmail.com>
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. image:: https://img.shields.io/pypi/pyversions/anyblok_pyramid_rest_api.svg?longCache=True
    :alt: Python versions

.. image:: https://travis-ci.org/AnyBlok/anyblok-pyramid-rest-api.svg?branch=master
    :target: https://travis-ci.org/AnyBlok/anyblok-pyramid-rest-api
    :alt: Build status

.. image:: https://coveralls.io/repos/github/AnyBlok/anyblok-pyramid-rest-api/badge.svg?branch=master
    :target: https://coveralls.io/github/AnyBlok/anyblok-pyramid-rest-api?branch=master
    :alt: Coverage

.. image:: https://img.shields.io/pypi/v/anyblok-pyramid-rest-api.svg
   :target: https://pypi.python.org/pypi/anyblok-pyramid-rest-api/
   :alt: Version status
   
.. image:: https://readthedocs.org/projects/anyblok-pyramid-rest-api/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://doc.anyblok-pyramid-rest-api.anyblok.org/en/latest/?badge=latest

Anyblok Pyramid Rest Api
========================

The main idea is to provide facilities for building restful api that interacts with AnyBlok_ models
through a CRUD like pattern.

As dependecy, it use Cornice_ for its validators and schema abilities and Marshmallow_ for
schema definition, serialization and deserialization (we have since split this work to
AnyBlok_Marshmallow_).

* Free software: Mozilla Public License Version 2.0
* Documentation: https://anyblok-pyramid-rest-api.readthedocs.io

Features
--------

* Incoming request validation through schema (validation before database query and ability to
  validate several parts of the request object)
* CRUD queries always with request.validated data
* Data deserialization for response through schema
* Easy CRUD resource declaration (map a model on an endpoint)
* Automatic schema generation based on models introspection
* Advanced collection filtering, ordering, paging (querystring validation through schema)

Todo
----

* Helpers for JsonSchema or Swagger
* Advanced introspection for api documentation generation

Request lifecyle
----------------

incoming request ::

    -> validators -> deserializer (json to dict) -> schema load -> request.validated -> request.errors

request.validated ::

    -> crud -> resulting records
    -> deserializer (records to schema dump)
    -> serializer (default pyramid / cornice dict to json serializer)
    -> response

Author
------

Franck Bret
~~~~~~~~~~~

* franckbret@gmail.com
* https://github.com/franckbret

Contributors
------------

Jean-Sébastien Suzanne
~~~~~~~~~~~~~~~~~~~~~~

* js.suzanne@gmail.com
* https://github.com/jssuzanne
* https://github.com/AnyBlok

Credits
-------

* Anyblok_
* Pyramid_
* Cornice_
* Marshmallow_
* AnyBlok_Marshmallow_

.. _Anyblok: https://github.com/AnyBlok/AnyBlok
.. _Pyramid: https://getpyramid.com
.. _Cornice: http://cornice.readthedocs.io/
.. _Marshmallow: http://marshmallow.readthedocs.io/
.. _AnyBlok_Marshmallow: https://github.com/AnyBlok/AnyBlok_Marshmallow

License
~~~~~~~

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file,You can
obtain one at http://mozilla.org/MPL/2.0/.

Copyright (c) 2017, Franck Bret
