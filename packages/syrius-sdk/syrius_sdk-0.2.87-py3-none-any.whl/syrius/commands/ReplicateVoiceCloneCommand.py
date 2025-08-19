from typing import Literal
from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateVoiceCloneCommand(Command):
    id: int = 53
    text: str | AbstractCommand | loopType
    speaker: str | AbstractCommand | loopType
    language: Literal["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "hu", "ko",
                    "hi"] | AbstractCommand | loopType = "en"
    cleanup_voice: bool | AbstractCommand | loopType = False
    api_key: str | AbstractCommand | loopType