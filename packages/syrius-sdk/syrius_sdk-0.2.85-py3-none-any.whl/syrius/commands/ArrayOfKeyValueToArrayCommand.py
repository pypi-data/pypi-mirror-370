from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArrayOfKeyValueToArrayCommand(Command):
    """ """
    id: int = 28
    array: list[Any] | AbstractCommand | loopType
    filtered_by: str | AbstractCommand | loopType
