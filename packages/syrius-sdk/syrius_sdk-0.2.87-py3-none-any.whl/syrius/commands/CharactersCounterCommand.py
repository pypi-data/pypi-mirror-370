from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class CharactersCounterCommand(Command):
    id: int = 52
    text: str | AbstractCommand | loopType