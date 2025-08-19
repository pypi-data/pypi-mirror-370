from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArraysMergeByKeyCommand(Command):
    """ """
    id: int = 1
    initial: list[dict[str, Any]] | AbstractCommand | loopType
    to_combine: list[dict[str, Any]] | AbstractCommand | loopType
    key: str | AbstractCommand | loopType
