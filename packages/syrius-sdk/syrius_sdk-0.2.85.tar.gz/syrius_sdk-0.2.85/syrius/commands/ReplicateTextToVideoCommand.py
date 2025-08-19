from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateTextToVideoCommand(Command):
    id: int = 55
    prompt: str | AbstractCommand | loopType
    num_frames: int | AbstractCommand | loopType = 49
    guidance_scale: int | AbstractCommand | loopType = 9
    num_inference_steps: int | AbstractCommand | loopType = 9
    api_key: str | AbstractCommand | loopType