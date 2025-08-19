from typing import Literal
from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ElevenlabsVoiceCloneCommand(Command):
    id: int = 67
    text: str | AbstractCommand | loopType
    voice_id: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType