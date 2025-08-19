from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class GetFileNameCommand(Command):
    """ """
    id: int = 46
    folder: str | AbstractCommand | loopType
    filename: str | AbstractCommand | loopType
    extension: str | AbstractCommand | loopType
