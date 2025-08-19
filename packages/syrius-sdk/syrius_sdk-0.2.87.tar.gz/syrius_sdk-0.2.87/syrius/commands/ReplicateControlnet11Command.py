from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateControlnet11Command(Command):
    id: int = 86
    prompt: str | AbstractCommand | loopType
    image: str | AbstractCommand | loopType
    negative_prompt: str | AbstractCommand | loopType = "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck"
    max_width: int | AbstractCommand | loopType = 612
    max_height: int | AbstractCommand | loopType = 612
    strength: float | AbstractCommand | loopType = 0.5
    steps: int | AbstractCommand | loopType = 20
    guidance_scale: float | AbstractCommand | loopType = 10
    api_key: str | AbstractCommand | loopType