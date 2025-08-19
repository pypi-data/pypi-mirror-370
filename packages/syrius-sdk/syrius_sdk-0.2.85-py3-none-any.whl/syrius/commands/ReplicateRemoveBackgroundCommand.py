from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateRemoveBackgroundCommand(Command):
    id: int = 65
    images: list[str] | AbstractCommand | loopType
    prompt: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType