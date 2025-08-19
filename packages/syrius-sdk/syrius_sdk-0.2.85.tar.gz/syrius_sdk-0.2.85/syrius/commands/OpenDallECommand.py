from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class OpenDallECommand(Command):
    id: int = 49
    prompt: str | AbstractCommand | loopType
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] | AbstractCommand | loopType = "1024x1024"
    quality: Literal['standard', 'hd'] | AbstractCommand | loopType = "standard"
    api_key: str | AbstractCommand | loopType