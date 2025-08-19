from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class BriaLifeStyleProductShotImageCommand(Command):
    """ """
    id: int = 64
    sku: str | AbstractCommand | loopType = ""
    sync: bool | AbstractCommand | loopType = False
    image_url: str | AbstractCommand | loopType
    ref_image_urls: str | AbstractCommand | loopType
    placement_type: str | AbstractCommand | loopType = "original"
    padding_values: list[int] | AbstractCommand | loopType = []
    num_results: int | AbstractCommand | loopType = 4
    api_key: str | AbstractCommand | loopType