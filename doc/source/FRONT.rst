.. This file is a part of the AnyBlok / Pyramid project
..
..    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

Front Matter
============

Information about the AnyBlok / Pyramid project.

Project Homepage
----------------

AnyBlok is hosted on `github <http://github.com>`_ - the main project
page is at https://github.com/AnyBlok/anyblok-pyramid-rest-api. Source code is
tracked here using `GIT <https://git-scm.com>`_.

Releases and project status are available on Pypi at
https://pypi.org/project/anyblok_pyramid_rest_api.

The most recent published version of this documentation should be at
https://anyblok-pyramid-rest-api.readthedocs.io/en/latest/.

Project Status
--------------

AnyBlok with Pyramid and cornice is currently in beta status and is expected to be fairly
stable.   Users should take care to report bugs and missing features on an as-needed
basis.  It should be expected that the development version may be required
for proper implementation of recently repaired issues in between releases;

Installation
------------

Install released versions of AnyBlok from the Python package index with
`pip <http://pypi.python.org/pypi/pip>`_ or a similar tool::

    pip install anyblok_pyramid_rest_api

Installation via source distribution is via the ``setup.py`` script::

    python setup.py install

Installation will add the ``anyblok`` commands to the environment.

Unit Test
---------

Run the test with ``pytest``::

    pip install pytest
    # export the paramter needed for test
    export ANYBLOK_DATABASE_NAME=anyblok_rest_api
    export ANYBLOK_DATABASE_DRIVER=postgresql
    pytest anyblok_pyramid_rest_api/tests

Dependencies
------------

AnyBlok works with **Python 3.4** and later. The install process will
ensure that `AnyBlok <http://doc.anyblok.org>`_,
`Pyramid <http://pyramid.readthedocs.org/>`_, 
`cornice <https://cornice.readthedocs.io/en/latest/>`_ are installed, in addition to
other dependencies. The latest version of them is strongly recommended.


Contributing (hackers needed!)
------------------------------

Anyblok / Pyramid is at a very early stage, feel free to fork, talk with core
dev, and spread the word!

License
-------

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file,You can
obtain one at http://mozilla.org/MPL/2.0/.

Copyright (c) 2017, Franck Bret

Author
------

Franck Bret

Contributors
------------

`Anybox <http://anybox.fr>`_ team:

* Jean-Sébastien Suzanne

`Sensee <http://sensee.com>`_ team:

* Franck Bret
* Jean-Sébastien Suzanne


Bugs
----

Bugs and feature enhancements to AnyBlok should be reported on the `Issue
tracker <https://github.com/AnyBlok/anyblok-pyramid-rest-api/issues>`_.
