from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class AWSPollyGenerateCommand(Command):
    """ """
    id: int = 41
    engine: str | AbstractCommand | loopType
    access_key: str | AbstractCommand | loopType
    secret_key: str | AbstractCommand | loopType
    language_code: str | AbstractCommand | loopType
    output_format: str | AbstractCommand | loopType
    voice_name: str | AbstractCommand | loopType
    text: str | AbstractCommand | loopType
