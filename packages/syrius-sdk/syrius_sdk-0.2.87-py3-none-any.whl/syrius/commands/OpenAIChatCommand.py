from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class OpenAIChatCommand(Command):
    """ """
    id: int = 91
    prompt: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType
    model: str | AbstractCommand | loopType
    temperature: float | AbstractCommand | loopType
    instructions: str | AbstractCommand | loopType
    reasoning: str | AbstractCommand | loopType = "low"
    verbosity: str | AbstractCommand | loopType = "medium"
