# syrius/commands/abstract.py
"""Provide abstract class and base classes for Command, Loop and Logical.

The module contains the following classes:

- `AbstractCommand` - Abstract Class for Command, Loop and Logical.
- `Command` - Parent class for Commands.
- `Loop` - Parent class for Loops commands.
- `Logical` - Parent class for Logical commands.
"""
import abc
from typing import Literal

from pydantic import BaseModel


class LocalCommand(BaseModel, abc.ABC):
    """ """

    @abc.abstractmethod
    def run(self):
        """ """
        raise Exception("Not implemented")


class AbstractCommand(BaseModel):
    """Abstract Class for Commands"""
    id: int
    type: Literal["Main"]
    @classmethod
    def get_subclasses(cls):
        return tuple(cls.__subclasses__())


class Command(AbstractCommand):
    """Command parent class

    That class is the parent class for all the commands


    """
    type: Literal["Command"] = "Command"


class Loop(AbstractCommand):
    """Loop parent class

    That class is the parent class for all the Loop Commands


    """

    type: Literal["Loop"] = "Loop"


class Logical(AbstractCommand):
    """Logical parent class

    That class is the parent class for all the Logical Commands


    """

    type: Literal["Conditional"] = "Conditional"
