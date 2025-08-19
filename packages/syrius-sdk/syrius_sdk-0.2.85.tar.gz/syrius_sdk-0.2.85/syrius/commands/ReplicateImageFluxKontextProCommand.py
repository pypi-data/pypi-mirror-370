from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateImageFluxKontextProCommand(Command):
    id: int = 105
    prompt: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType = "1:1"
    input_image: str | AbstractCommand | loopType = ""
    api_key: str | AbstractCommand | loopType