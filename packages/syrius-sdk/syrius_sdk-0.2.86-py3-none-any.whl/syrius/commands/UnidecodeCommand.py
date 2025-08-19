from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class UnidecodeCommand(Command):
    """ """
    id: int = 47
    text: str | AbstractCommand | loopType