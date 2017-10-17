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
