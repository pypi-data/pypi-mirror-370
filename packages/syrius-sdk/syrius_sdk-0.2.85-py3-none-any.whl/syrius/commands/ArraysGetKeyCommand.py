from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArraysGetKeyCommand(Command):
    """ """
    id: int = 44
    array: dict[str, Any] | AbstractCommand | loopType
    key: str | AbstractCommand | loopType
