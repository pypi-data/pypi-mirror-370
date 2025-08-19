from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateRecraftCommand(Command):
    id: int = 76
    prompt: str | AbstractCommand | loopType
    size: (Literal["1024x1024", "1365x1024",
    "1024x1365", "1365x1024", "1365x1024", "1536x1024", "1024x1536", "1820x1024", "1024x1820", "1024x2048"
    , "2048x1024", "1434x1024", "1024x1434", "1024x1280", "1280x1024", "1024x1707", "1707x1024"]
           | AbstractCommand | loopType) =  "1024x1024"
    style: str | AbstractCommand | loopType = "any"
    api_key: str | AbstractCommand | loopType