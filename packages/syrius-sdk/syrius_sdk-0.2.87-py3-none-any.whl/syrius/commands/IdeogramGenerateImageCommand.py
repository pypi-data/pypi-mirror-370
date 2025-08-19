from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class IdeogramGenerateImageCommand(Command):
    id: int = 62
    prompt: str | AbstractCommand | loopType
    aspect_ratio: str | AbstractCommand | loopType = "1:1"
    model: str | AbstractCommand | loopType = "V_2"
    magic_prompt_option: str | AbstractCommand | loopType = "AUTO"
    style_type: str | AbstractCommand | loopType = "AUTO"
    negative_prompt: str | AbstractCommand | loopType = ""
    api_key: str | AbstractCommand | loopType