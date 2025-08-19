from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateGoogleVeo3Command(Command):
    id: int = 107
    prompt: str | AbstractCommand | loopType
    negative_prompt: str | AbstractCommand | loopType = ""
    enhance_prompt: bool | AbstractCommand | loopType = True
    api_key: str | AbstractCommand | loopType