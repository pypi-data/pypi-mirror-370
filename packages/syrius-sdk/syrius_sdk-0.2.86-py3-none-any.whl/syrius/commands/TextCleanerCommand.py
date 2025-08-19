from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class TextCleanerCommand(Command):
    id: int = 48
    text: str | AbstractCommand | loopType
    remove: list[str] | AbstractCommand | loopType
