from typing import Annotated, Literal

from pydantic import TypeAdapter

from syrius.commands.abstract import LocalCommand


class LoopInputCommand(LocalCommand):
    """ """

    def run(self) -> str:
        """ """
        return "ref@index"


loopindex = "ref@index"
loopType = Literal["ref@index"]


