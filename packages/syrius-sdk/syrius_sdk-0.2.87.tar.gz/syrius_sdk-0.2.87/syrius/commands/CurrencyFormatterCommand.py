from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class CurrencyFormatterCommand(Command):
    """ """
    id: int = 9
    quantity: str | AbstractCommand | loopType
