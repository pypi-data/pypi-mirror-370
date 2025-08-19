from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateVideoLeonardoMotion2Command(Command):
    id: int = 104
    prompt: str | AbstractCommand | loopType
    image: str | AbstractCommand | loopType = ""
    aspect_ratio: str | AbstractCommand | loopType = "16:9"
    frame_interpolation: bool | AbstractCommand | loopType = True
    prompt_enhance: bool | AbstractCommand | loopType = True
    negative_prompt: str | AbstractCommand | loopType = ""
    vibe_style: str | AbstractCommand | loopType = "None"
    lighting_style: str | AbstractCommand | loopType = "None"
    shot_type_style: str | AbstractCommand | loopType = "None"
    color_theme_style: str | AbstractCommand | loopType = "None"
    api_key: str | AbstractCommand | loopType