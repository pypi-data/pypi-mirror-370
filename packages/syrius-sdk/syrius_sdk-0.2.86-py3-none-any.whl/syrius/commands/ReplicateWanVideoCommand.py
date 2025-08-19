from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateWanVideoCommand(Command):
    id: int = 84
    prompt: str | AbstractCommand | loopType
    frame_num: int | AbstractCommand | loopType = 81
    resolution: str | AbstractCommand | loopType = "480p"
    aspect_ratio: str | AbstractCommand | loopType = "16:9"
    sample_shift: int | AbstractCommand | loopType = 8
    sample_steps: int | AbstractCommand | loopType = 30
    sample_guide_scale: int | AbstractCommand | loopType = 6
    api_key: str | AbstractCommand | loopType