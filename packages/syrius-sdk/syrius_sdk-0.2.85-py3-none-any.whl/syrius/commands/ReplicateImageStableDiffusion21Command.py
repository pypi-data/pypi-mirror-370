from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateImageStableDiffusion21Command(Command):
    id: int = 85
    prompt: str | AbstractCommand | loopType
    negative_prompt: str | AbstractCommand | loopType = "worst quality, low quality"
    width: int | AbstractCommand | loopType = 512
    height: int | AbstractCommand | loopType = 512
    num_outputs: int | AbstractCommand | loopType = 1
    scheduler: str | AbstractCommand | loopType = "K_EULER"
    num_inference_steps: int | AbstractCommand | loopType = 50
    guidance_scale: float | AbstractCommand | loopType = 7.5
    api_key: str | AbstractCommand | loopType