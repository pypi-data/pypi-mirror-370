from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class ArrayKeyValueCommand(Command):
    """ """
    id: int = 26
    kvstore: dict[str, Any] | AbstractCommand | loopType
