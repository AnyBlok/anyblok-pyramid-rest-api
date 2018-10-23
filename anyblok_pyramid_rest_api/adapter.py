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
from logging import getLogger

logger = getLogger(__name__)


class Adapter:

    def __init__(self, registry, Model):
        self.registry = registry
        self.Model = Model
        self.loaded = False
        self.filters = {}
        self.orders_by = {}
        self.tags = {}

    def load_decorators(self):
        for attr, value in self.__class__.__dict__.items():
            if hasattr(value, 'is_filter'):
                key, operators = value.is_filter
                self.filters[key] = {operator: attr for operator in operators}
            elif hasattr(value, 'is_order_by'):
                self.orders_by[value.is_order_by] = attr
            elif hasattr(value, 'is_tag'):
                self.tags[value.is_tag] = attr

    def has_filter_for(self, key, operator):
        return True if self.filters.get(key, {}).get(operator) else False

    def get_filter_for(self, key, operator):
        return getattr(self, self.filters[key][operator])

    def has_order_by_for(self, key):
        return True if self.orders_by.get(key) else False

    def get_order_by_for(self, key):
        return getattr(self, self.orders_by[key])

    def has_tag_for(self, tag):
        return True if self.tags.get(tag) else False

    def get_tag_for(self, tag):
        return getattr(self, self.tags[tag])

    @classmethod
    def filter(cls, key, operators):
        if not isinstance(operators, (list, tuple)):
            operators = [operators]

        def wrapper(method):
            method.is_filter = (key, operators)
            return method

        return wrapper

    @classmethod
    def order_by(cls, name):
        def wrapper(method):
            method.is_order_by = name
            return method

        return wrapper

    @classmethod
    def tag(cls, name):
        def wrapper(method):
            method.is_tag = name
            return method

        return wrapper
