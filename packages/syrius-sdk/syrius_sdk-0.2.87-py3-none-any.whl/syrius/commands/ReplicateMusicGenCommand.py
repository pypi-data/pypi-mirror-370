from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateMusicGenCommand(Command):
    id: int = 89
    prompt: str | AbstractCommand | loopType
    model_version: str | AbstractCommand | loopType = "stereo-melody-large"
    duration: int | AbstractCommand | loopType = 8
    normalization_strategy: str | AbstractCommand | loopType = "loudness"
    top_k: int | AbstractCommand | loopType =  250
    input_audio: str | None | AbstractCommand | loopType = None
    top_p: float | AbstractCommand | loopType = 0
    temperature: int | AbstractCommand | loopType = 1
    output_format: str | AbstractCommand | loopType = "mp3"
    api_key: str | AbstractCommand | loopType