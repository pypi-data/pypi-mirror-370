from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateMinimaxSpeechCommand(Command):
    id: int = 99
    model: str | AbstractCommand | loopType = "minimax/speech-02-hd"
    text: str | AbstractCommand | loopType
    voice_id: str | AbstractCommand | loopType
    speed: int | AbstractCommand | loopType = 1
    volume: int | AbstractCommand | loopType = 1
    pitch: int | AbstractCommand | loopType = 0
    emotion: str | AbstractCommand | loopType = "neutral"
    english_normalization: bool | AbstractCommand | loopType = False
    sample_rate: int | AbstractCommand | loopType = 32000
    bitrate: int | AbstractCommand | loopType = 12800
    channel: str | AbstractCommand | loopType = "stereo"
    language_boost: str | AbstractCommand | loopType = "None"
    api_key: str | AbstractCommand | loopType