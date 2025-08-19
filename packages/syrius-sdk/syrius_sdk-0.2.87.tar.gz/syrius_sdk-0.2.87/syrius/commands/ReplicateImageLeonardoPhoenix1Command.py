from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateImageLeonardoPhoenix1Command(Command):
    id: int = 103
    prompt: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType = "3:2"
    generation_mode: str | AbstractCommand | loopType = "quality"
    contrast: str | AbstractCommand | loopType = "medium"
    prompt_enhance: bool | AbstractCommand | loopType = True
    num_images: int | AbstractCommand | loopType = 1
    style: str | AbstractCommand | loopType = "none"
    api_key: str | AbstractCommand | loopType