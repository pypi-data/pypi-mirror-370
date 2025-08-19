from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class FileTextExtractCommand(Command):
    """ """
    id: int = 5
    file_type: Literal["local", "s3", "base64"] | loopType
    filepath: str | AbstractCommand | loopType
    bucket: str | AbstractCommand | loopType = ""
    access_key: str | AbstractCommand | loopType = ""
    secret_key: str | AbstractCommand | loopType = ""
    remove_breaks: bool | AbstractCommand | loopType = False
    remove_multi_whitespaces: bool | AbstractCommand | loopType = False
