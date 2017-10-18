# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String


Model = Declarations.Model


@Declarations.register(Model)
class Example():
    """ Example Model for tests purpose
    """
    id = Integer(primary_key=True)
    name = String(label="Name", unique=True, nullable=False)

    def __str__(self):
        return ('{self.name}').format(self=self)

    def __repr__(self):
        msg = ('<Example: {self.name}, {self.id}>')
        return msg.format(self=self)
