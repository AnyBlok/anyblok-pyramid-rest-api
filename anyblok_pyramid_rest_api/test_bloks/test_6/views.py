# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice.resource import resource
from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import CrudResource
from anyblok_pyramid_rest_api.adapter import Adapter as Adapter
from .schema import CustomerSchema
from sqlalchemy import or_


@resource(
    collection_path='/customers/v6',
    path='/customers/v6/{id}',
    installed_blok=current_blok()
)
class CustomerResourceV6(CrudResource):
    model = 'Model.Customer'
    default_schema = CustomerSchema

    class adapter_cls(Adapter):

        @Adapter.filter('addresses.city', ['ilike'])
        def filter_by_location_and_children(self, querystring, query, operator,
                                            value, mode):
            query = query.join(self.registry.Customer.addresses, aliased=True)
            query = query.join(self.registry.Address.city, aliased=True)
            query = query.filter(or_(
                self.registry.City.name.ilike(value),
                self.registry.City.zipcode.ilike(value)))
            return query

        @Adapter.tag('green')
        def tag_is_green(self, querystring, query):
            query = query.join(self.registry.Customer.tags, aliased=True)
            query = query.filter(self.registry.Tag.name == 'green')
            return query

        @Adapter.tag('orange')
        def tag_is_orange(self, querystring, query):
            query = query.join(self.registry.Customer.tags, aliased=True)
            query = query.filter(self.registry.Tag.name == 'orange')
            return query

        @Adapter.tag('colors')
        def tag_color_depend_of_context(self, querystring, query):
            colors = querystring.context.get('colors')
            if colors:
                colors = colors.split(',')
                query = query.join(self.registry.Customer.tags, aliased=True)
                query = query.filter(self.registry.Tag.name.in_(colors))

            return query

        @Adapter.tag('wrong')
        def wrong_tag(self, querystring, query):
            raise Exception('Wrong tags')

        @Adapter.filter('addresses.other', ['ilike'])
        def wrong_filter(self, querystring, query, operator,
                         value, mode):
            raise Exception('Wrong filters')

        @Adapter.order_by('address')
        def order_by_city(self, querystring, query, operator):
            query = query.join(self.registry.Customer.addresses, aliased=True)
            query = query.join(self.registry.Address.city, aliased=True)
            return query.order_by(self.registry.City.zipcode)
