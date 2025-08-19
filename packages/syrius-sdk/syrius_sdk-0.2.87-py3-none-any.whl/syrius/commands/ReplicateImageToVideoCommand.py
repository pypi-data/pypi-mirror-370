from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateImageToVideoCommand(Command):
    id: int = 54
    prompt: str | AbstractCommand | loopType
    image: str | AbstractCommand | loopType
    num_frames: int | AbstractCommand | loopType = 49
    guidance_scale: int | AbstractCommand | loopType = 9
    num_inference_steps: int | AbstractCommand | loopType = 9
    api_key: str | AbstractCommand | loopType