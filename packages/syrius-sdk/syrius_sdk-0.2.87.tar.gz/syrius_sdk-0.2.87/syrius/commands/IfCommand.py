from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Logical


class IfCommand(Logical):
    """ """
    id: int = 1
    condition: Any | loopType
    then: list[Any]
