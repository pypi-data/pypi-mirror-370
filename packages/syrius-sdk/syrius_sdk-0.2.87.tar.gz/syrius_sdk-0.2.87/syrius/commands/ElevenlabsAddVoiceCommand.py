from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ElevenlabsAddVoiceCommand(Command):
    id: int = 77
    speaker: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType