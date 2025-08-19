from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class GrtCommand(Command):
    """ """
    id: int = 7
    number: int | AbstractCommand | loopType
    greater: int | AbstractCommand | loopType
