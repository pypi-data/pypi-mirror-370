from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class RunwayImageToVideoCommand(Command):
    id: int = 70
    model: str | AbstractCommand | loopType = "gen3a_turbo"
    prompt: str | AbstractCommand | loopType
    image: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType
    duration: int
    api_key: str | AbstractCommand | loopType