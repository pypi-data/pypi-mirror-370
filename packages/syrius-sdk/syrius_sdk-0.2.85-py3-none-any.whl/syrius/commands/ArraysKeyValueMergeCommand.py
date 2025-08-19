from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArraysKeyValueMergeCommand(Command):
    id: int = 3
    dictionaries: list[Any] | AbstractCommand | loopType
