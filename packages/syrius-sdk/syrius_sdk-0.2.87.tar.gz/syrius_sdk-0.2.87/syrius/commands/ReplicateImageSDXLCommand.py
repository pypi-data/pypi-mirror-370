from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateImageSDXLCommand(Command):
    id: int = 50
    prompt: str | AbstractCommand | loopType
    negative_prompt: str | AbstractCommand | loopType = "worst quality, low quality"
    width: int | AbstractCommand | loopType = 512
    height: int | AbstractCommand | loopType = 512
    num_outputs: int | AbstractCommand | loopType = 1
    scheduler: str | AbstractCommand | loopType = "K_EULER"
    num_inference_steps: int | AbstractCommand | loopType = 25
    guidance_scale: float | AbstractCommand | loopType = 7.5
    prompt_strength: float | AbstractCommand | loopType = 0.8
    refine: str | AbstractCommand | loopType = "expert_ensemble_refiner"
    high_noise_frac: float | AbstractCommand | loopType = 0.8
    lora_scale: float | AbstractCommand | loopType = 0.6
    disable_safety_checker: float | AbstractCommand | loopType = True
    api_key: str | AbstractCommand | loopType