#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for anyblok-pyramid-rest-api"""

from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(os.path.join(here, 'CHANGELOG.rst'), 'r', encoding='utf-8') as changelog_file:
    changelog = changelog_file.read()

requirements = [
    'anyblok',
    'anyblok_pyramid',
    'cornice',
    'marshmallow',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='anyblok_pyramid_rest_api',
    version='0.1.0',
    description="A blok to build json rest api's",
    long_description=readme + '\n\n' + changelog,
    author="Franck Bret",
    author_email='franckbret@gmail.com',
    url='https://github.com/franckbret/anyblok-pyramid-rest-api',
    packages=find_packages(),
    entry_points={
        'bloks': [
            'rest_api_blok=anyblok_pyramid_rest_api.rest_api_blok:Rest_api_blok'
            ]
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
