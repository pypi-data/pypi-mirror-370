from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class LumaImageToVideoCommand(Command):
    id: int = 56
    prompt: str | AbstractCommand | loopType
    image: str | AbstractCommand | loopType
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"] | AbstractCommand | loopType = "1:1"
    api_key: str | AbstractCommand | loopType