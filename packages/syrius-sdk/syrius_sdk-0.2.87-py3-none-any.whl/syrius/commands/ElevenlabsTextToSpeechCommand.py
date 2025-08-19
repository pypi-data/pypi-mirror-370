from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ElevenlabsTextToSpeechCommand(Command):
    id: int = 69
    text: str | AbstractCommand | loopType
    voice: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType