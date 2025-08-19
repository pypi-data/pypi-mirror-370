from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateAudioToVideoCommand(Command):
    id: int = 90
    prompt: str | AbstractCommand | loopType
    video: str | AbstractCommand | loopType
    negative_prompt: str | AbstractCommand | loopType = "music"
    duration: int | AbstractCommand | loopType = 8
    num_steps: int | AbstractCommand | loopType = 25
    cfg_strength: float | AbstractCommand | loopType = 4.5
    api_key: str | AbstractCommand | loopType