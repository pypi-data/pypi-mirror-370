from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class RunwayStartEndImageToVideoCommand(Command):
    id: int = 71
    model: str | AbstractCommand | loopType = "gen3a_turbo"
    prompt: str | AbstractCommand | loopType
    image_start: str | AbstractCommand | loopType
    image_end: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType