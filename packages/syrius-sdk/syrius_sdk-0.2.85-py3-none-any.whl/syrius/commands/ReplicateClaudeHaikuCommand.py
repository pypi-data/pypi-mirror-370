from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateClaudeHaikuCommand(Command):
    id: int = 79
    prompt: str | AbstractCommand | loopType
    system_prompt: str | AbstractCommand | loopType = ""
    max_tokens: int | AbstractCommand | loopType = 8192
    api_key: str | AbstractCommand | loopType