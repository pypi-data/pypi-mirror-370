from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class GoogleImagenCommand(Command):
    id: int = 97
    prompt: str | AbstractCommand | loopType
    model: str | AbstractCommand | loopType = "imagen-3.0-generate-002"
    num_images: int | AbstractCommand | loopType = 1
    aspect_ratio: Literal["1:1", "16:9", "2:3", "3:2", "4:5", "5:4", "9:16", "3:4", "4:3", "21:9", "9:21"] | AbstractCommand | loopType = "16:9"
    mimetype: str | AbstractCommand | loopType = 'image/png'

