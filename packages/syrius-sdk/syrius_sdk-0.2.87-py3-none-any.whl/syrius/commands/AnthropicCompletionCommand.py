from typing import Any

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class AnthropicCompletionCommand(Command):
    """ """
    id: int = 36
    messages: list[dict[str, Any]] | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType
    model: str | AbstractCommand | loopType
    max_tokens: int | AbstractCommand | loopType
    temperature: float | AbstractCommand | loopType
    tools: dict[str, Any] | AbstractCommand | loopType
    extract: str | AbstractCommand | loopType
