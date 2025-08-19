from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateMinimaxVoiceCloningCommand(Command):
    id: int = 100
    voice_file: str | AbstractCommand | loopType
    need_noise_reduction: bool | AbstractCommand | loopType = False
    model: str | AbstractCommand | loopType = "minimax/speech-02-hd"
    accuracy: float | AbstractCommand | loopType = 0.7
    need_volume_normalization: bool | AbstractCommand | loopType = False
    api_key: str | AbstractCommand | loopType