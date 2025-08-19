from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class TemplateCommand(Command):
    """ """
    id: int = 21
    variables: dict[str, Any] | AbstractCommand | loopType
    text: str | AbstractCommand | loopType
