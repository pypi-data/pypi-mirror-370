from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ElevenlabsDeleteVoiceCommand(Command):
    id: int = 78
    voice_id: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType