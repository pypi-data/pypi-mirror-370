from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class PdfToExcellCommand(Command):
    """ """
    id: int = 61
    filename: str | AbstractCommand | loopType
