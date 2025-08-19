from typing import Any, ClassVar

from syrius.commands.abstract import Command, AbstractCommand


class OpenAICompletionCommand(Command):
    """ """
    id: int = 18
    messages: list[dict[str, Any]] | AbstractCommand
    api_key: str | AbstractCommand
    model: str | AbstractCommand
    temperature: float | AbstractCommand
    tools: dict[str, Any] | AbstractCommand
    extract: str | AbstractCommand
