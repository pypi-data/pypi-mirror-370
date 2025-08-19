from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class SectionSplitterCommand(Command):
    """ """
    id: int = 20
    words: list[dict[str, Any]] | AbstractCommand | loopType
    text: str | AbstractCommand | loopType
