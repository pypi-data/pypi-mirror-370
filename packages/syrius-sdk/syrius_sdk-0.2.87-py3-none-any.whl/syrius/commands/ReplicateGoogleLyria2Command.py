from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateGoogleLyria2Command(Command):
    id: int = 102
    prompt: str | AbstractCommand | loopType
    negative_prompt: str | AbstractCommand | loopType = ""
    api_key: str | AbstractCommand | loopType