from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class PdfHighlighterCommand(Command):
    """ """
    id: int = 27
    filename: str | AbstractCommand | loopType
    bucket: str | AbstractCommand | loopType
    access_key: str | AbstractCommand | loopType
    secret_key: str | AbstractCommand | loopType
    texts: list[str] | AbstractCommand | loopType
