from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArrayFilterByCommand(Command):
    """ """
    id: int = 29
    array: dict[str, Any] | AbstractCommand | loopType
    filter_by: str | AbstractCommand | loopType
