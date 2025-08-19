from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import Command, AbstractCommand


class OCRToMarkdownCommand(Command):
    id: int = 60
    prompt: str | AbstractCommand | loopType
    pdf_file: str | AbstractCommand | loopType
