# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from datetime import datetime
from uuid import uuid1

from anyblok import Declarations
from anyblok.column import Integer, String, DateTime, Password, UUID
from anyblok.relationship import Many2One


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


@Declarations.register(Model)
class Thing():
    uuid = UUID(primary_key=True, default=uuid1, binary=False)
    name = String(label="Name", unique=True, nullable=False)
    create_date = DateTime(default=datetime.now, nullable=False)
    edit_date = DateTime(default=datetime.now, nullable=False)
    secret = Password(
        crypt_context={'schemes': ['pbkdf2_sha512']}, nullable=False)
    example = Many2One(
        label="Example", model=Model.Example, one2many="things",
        nullable=False)

    def __str__(self):
        return ('{self.name}').format(self=self)

    def __repr__(self):
        msg = ('<Thing: {self.name}, {self.uuid}>')
        return msg.format(self=self)
