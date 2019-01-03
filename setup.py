#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck BRET <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Setup script for anyblok-pyramid-rest-api"""

from setuptools import setup, find_packages
from os.path import abspath, dirname, join

version = '0.4.0'
here = abspath(dirname(__file__))

with open(join(here, 'README.rst'), 'r',
          encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(join(here, 'CHANGELOG.rst'), 'r',
          encoding='utf-8') as changelog_file:
    changelog = changelog_file.read()

requirements = [
    'anyblok',
    'anyblok_pyramid',
    'cornice',
    'anyblok-marshmallow',
]

test_requirements = [
    # TODO: put package test requirements here
]

anyblok_pyramid_includeme = [
    'pyramid_cornice=anyblok_pyramid_rest_api.pyramid_config:pyramid_cornice',
]
test_bloks = [
    'test_rest_api_1=anyblok_pyramid_rest_api.test_bloks.test_1:TestBlok1',
    'test_rest_api_2=anyblok_pyramid_rest_api.test_bloks.test_2:TestBlok2',
    'test_rest_api_3=anyblok_pyramid_rest_api.test_bloks.test_3:TestBlok3',
    'test_rest_api_4=anyblok_pyramid_rest_api.test_bloks.test_4:TestBlok4',
    'test_rest_api_5=anyblok_pyramid_rest_api.test_bloks.test_5:TestBlok5',
    'test_rest_api_6=anyblok_pyramid_rest_api.test_bloks.test_6:TestBlok6',
    'test_rest_api_7=anyblok_pyramid_rest_api.test_bloks.test_7:TestBlok7',
    'test_rest_api_8=anyblok_pyramid_rest_api.test_bloks.test_8:TestBlok8',
    'test_rest_api_9=anyblok_pyramid_rest_api.test_bloks.test_9:TestBlok9',
    'test_rest_api_10=anyblok_pyramid_rest_api.test_bloks.test_10:TestBlok10',
]

setup(
    name='anyblok_pyramid_rest_api',
    version=version,
    description="Tools to build rest api's",
    long_description=readme + '\n\n' + changelog,
    author="Franck Bret",
    author_email='franckbret@gmail.com',
    url='https://github.com/franckbret/anyblok-pyramid-rest-api',
    packages=find_packages(),
    entry_points={
        'anyblok_pyramid.includeme': anyblok_pyramid_includeme,
        'test_bloks': test_bloks,
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='anyblok-pyramid-rest-api',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
