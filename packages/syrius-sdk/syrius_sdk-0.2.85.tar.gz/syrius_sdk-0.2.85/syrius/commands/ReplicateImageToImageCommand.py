from typing import Literal
from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateImageToImageCommand(Command):
    id: int = 59
    prompt: str | AbstractCommand | loopType
    image: str | AbstractCommand | loopType
    guidance_scale: int | AbstractCommand | loopType = 7
    steps: int | AbstractCommand | loopType = 40
    output_format: str | AbstractCommand | loopType = "png"
    quality: int | AbstractCommand | loopType = 90
    prompt_strength: float | AbstractCommand | loopType = 0.50
    api_key: str | AbstractCommand | loopType