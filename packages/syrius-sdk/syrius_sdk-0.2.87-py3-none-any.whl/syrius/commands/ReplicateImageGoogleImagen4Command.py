from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateImageGoogleImagen4Command(Command):
    id: int = 101
    prompt: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType = "1:1"
    safety_filter_level: str | AbstractCommand | loopType = "block_only_high"
    api_key: str | AbstractCommand | loopType