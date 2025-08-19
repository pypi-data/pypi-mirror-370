from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class AWSSESSendEmailCommand(Command):
    """ """
    id: int = 40
    region: str | AbstractCommand | loopType
    access_key: str | AbstractCommand | loopType
    secret_key: str | AbstractCommand | loopType
    subject: str | AbstractCommand | loopType
    from_email: str | AbstractCommand | loopType
    recipient: str | AbstractCommand | loopType
    text_email: str | AbstractCommand | loopType
    html_email: str | AbstractCommand | loopType
