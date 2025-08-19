from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class SectionRemoverCommand(Command):
    """ """
    id: int = 24
    words: list[dict[str, Any]] | AbstractCommand | loopType
    text: str | AbstractCommand | loopType
