from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateMinimaxImage01Command(Command):
    id: int = 95
    prompt: str | AbstractCommand | loopType
    aspect_ratio: Literal["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"] | None | AbstractCommand | loopType = "1:1"
    number_of_images: int | None | AbstractCommand | loopType = 1
    prompt_optimizer: bool | AbstractCommand | loopType = True
    api_key: str | AbstractCommand | loopType