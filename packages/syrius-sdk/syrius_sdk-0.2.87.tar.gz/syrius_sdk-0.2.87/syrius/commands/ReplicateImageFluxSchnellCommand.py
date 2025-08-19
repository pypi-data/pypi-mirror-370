from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateFluxSchnellCommand(Command):
    id: int = 88
    prompt: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType = "1:1"
    num_outputs: int | AbstractCommand | loopType = 1
    output_format: str | AbstractCommand | loopType = "png"
    quality: int | AbstractCommand | loopType = 80
    num_inference_steps: int | AbstractCommand | loopType = 4
    disable_safety_checker: bool | AbstractCommand | loopType = True
    go_fast: bool | AbstractCommand | loopType = True
    api_key: str | AbstractCommand | loopType