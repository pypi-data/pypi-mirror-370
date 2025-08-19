from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateMinimaxVideo01LiveCommand(Command):
    id: int = 93
    prompt: str | AbstractCommand | loopType
    first_frame_image: str | None | AbstractCommand | loopType
    prompt_optimizer: bool | AbstractCommand | loopType = True
    api_key: str | AbstractCommand | loopType