from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class JoinAudioCommand(Command):
    """ """
    id: int = 38
    audio: list[str] | AbstractCommand | loopType
    format: str | loopType
