from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class BriaProductShadowCommand(Command):
    """ """
    id: int = 66
    sku: str | AbstractCommand | loopType = ""
    image_url: str | AbstractCommand | loopType
    shadow_type: str | AbstractCommand | loopType = "regular"
    background_color: str | AbstractCommand | loopType = "#c0d6e4"
    shadow_color: str | AbstractCommand | loopType =  "#000000"
    shadow_offset: list[int] | AbstractCommand | loopType = [0,15]
    shadow_intensity: int | AbstractCommand | loopType = 60
    shadow_blur: int | AbstractCommand | loopType = 15
    shadow_width: int | AbstractCommand | loopType = 0
    shadow_height: int | AbstractCommand | loopType = 70
    api_key: str | AbstractCommand | loopType