from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class AWSS3SaveObjectCommand(Command):
    """ """
    id: int = 39
    region: str | AbstractCommand | loopType
    access_key: str | AbstractCommand | loopType
    secret_key: str | AbstractCommand | loopType
    bucket: str | AbstractCommand | loopType
    filename: str | AbstractCommand | loopType
    file_content: str | AbstractCommand | loopType
