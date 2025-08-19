from typing import Any

from syrius.commands.abstract import AbstractCommand
from syrius.commands.abstract import Loop


class ForCommand(Loop):
    """ """
    id: int = 1
    array: AbstractCommand | list[Any] = None
    then: list[Any] = []

    def add_array(self, array: list[Any] | AbstractCommand) -> None:
        self.array = array

    def add_to_then(self, then: AbstractCommand) -> None:
        self.then.append(then)
