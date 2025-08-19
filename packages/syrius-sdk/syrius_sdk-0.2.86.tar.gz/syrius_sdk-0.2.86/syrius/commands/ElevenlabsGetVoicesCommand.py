from typing import Literal
from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ElevenlabsGetVoicesCommand(Command):
    id: int = 68
    api_key: str | AbstractCommand | loopType