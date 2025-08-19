from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class GoogleGeminiCommand(Command):
    id: int = 96
    prompt: str | AbstractCommand | loopType
    system: str | AbstractCommand | loopType | None = None
    model: Literal["gemini-2.0-flash", "gemini-2.5-pro-preview-03-25", "gemini-2.0-flash-lite"] | AbstractCommand | loopType = "gemini-2.0-flash"
    temperature: float | AbstractCommand | loopType = 1
    max_token: int | AbstractCommand | loopType = 65536

