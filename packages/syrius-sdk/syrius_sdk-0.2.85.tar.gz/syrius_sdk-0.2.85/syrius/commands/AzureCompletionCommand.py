from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class AzureCompletionCommand(Command):
    """ """
    id: int = 35
    messages: list[dict[str, Any]] | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType
    api_endpoint: str | AbstractCommand | loopType
    model: str | AbstractCommand | loopType
    temperature: float | AbstractCommand | loopType
    tools: dict[str, Any] | AbstractCommand | loopType
    extract: str | AbstractCommand | loopType
