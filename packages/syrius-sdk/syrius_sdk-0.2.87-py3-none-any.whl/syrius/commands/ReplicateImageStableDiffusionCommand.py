from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateStableDiffusionCommand(Command):
    id: int = 58
    prompt: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType = "1:1"
    guidance_scale: int | AbstractCommand | loopType = 7
    steps: int | AbstractCommand | loopType = 40
    output_format: str | AbstractCommand | loopType = "png"
    quality: int | AbstractCommand | loopType = 90
    api_key: str | AbstractCommand | loopType