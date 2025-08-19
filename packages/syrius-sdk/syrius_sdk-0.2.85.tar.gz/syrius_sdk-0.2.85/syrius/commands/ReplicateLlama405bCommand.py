from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateLlama405bCommand(Command):
    id: int = 82
    prompt: str | AbstractCommand | loopType
    system_prompt: str | AbstractCommand | loopType = ""
    max_tokens: int | AbstractCommand | loopType = 1024
    api_key: str | AbstractCommand | loopType