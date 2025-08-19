from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class AzureTextToSpeechCommand(Command):
    """ """
    id: int = 43
    region: str | AbstractCommand | loopType
    api_key: str | AbstractCommand | loopType
    language_code: str | AbstractCommand | loopType
    output_format: str | AbstractCommand | loopType
    voice_name: str | AbstractCommand | loopType
    text: str | AbstractCommand | loopType
