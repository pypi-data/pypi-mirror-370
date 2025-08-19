from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class OpenAITextToSpeechCommand(Command):
    """ """
    id: int = 37
    api_key: str | AbstractCommand | loopType
    model: str | AbstractCommand | loopType
    speed: str | AbstractCommand | loopType
    message: str | AbstractCommand | loopType
    voice: str | AbstractCommand | loopType
    output_format: str | AbstractCommand | loopType
