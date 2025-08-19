from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArrayLengthCommand(Command):
    """ """
    id: int = 2
    array: list[Any] | AbstractCommand | loopType
