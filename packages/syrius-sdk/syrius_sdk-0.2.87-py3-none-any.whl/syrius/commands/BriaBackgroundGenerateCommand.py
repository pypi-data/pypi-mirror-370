from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class BriaBackgroundGenerateCommand(Command):
    """ """
    id: int = 63
    prompt: str | AbstractCommand | loopType
    image_url: str | AbstractCommand | loopType
    ref_image_url: str | AbstractCommand | loopType
    sync: bool | AbstractCommand | loopType = False
    fast: bool | AbstractCommand | loopType = False
    refine_prompt: bool | AbstractCommand | loopType = True
    original_quality: bool | AbstractCommand | loopType = False
    enhance_ref_image: bool | AbstractCommand | loopType = True
    num_results: int | AbstractCommand | loopType = 4
    negative_prompt: str | AbstractCommand | loopType = ""
    seed: int | AbstractCommand | loopType = 0
    api_key: str | AbstractCommand | loopType