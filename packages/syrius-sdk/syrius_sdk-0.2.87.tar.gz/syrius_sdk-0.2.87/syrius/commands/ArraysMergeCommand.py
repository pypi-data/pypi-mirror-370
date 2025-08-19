from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArraysMergeCommand(Command):
    """ """
    id: int = 4
    lists: list[list[Any]] | AbstractCommand | loopType
