from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateDeepseekCommand(Command):
    id: int = 81
    prompt: str | AbstractCommand | loopType
    system_prompt: str | AbstractCommand | loopType = ""
    max_tokens: int | AbstractCommand | loopType = 20480
    api_key: str | AbstractCommand | loopType