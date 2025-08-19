from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateMinimaxVideo01DirectorCommand(Command):
    id: int = 94
    prompt: str | AbstractCommand | loopType
    first_frame_image: str | None | AbstractCommand | loopType = None
    prompt_optimizer: bool | AbstractCommand | loopType = True
    api_key: str | AbstractCommand | loopType