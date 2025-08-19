from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArrayReduceByKeyCommand(Command):
    """ """
    id: int = 32
    array: list[Any] | AbstractCommand | loopType
    key: str | AbstractCommand | loopType
    value: str | AbstractCommand | loopType
