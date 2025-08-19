from collections import OrderedDict
from typing import Any, ClassVar

from pydantic import BaseModel

from syrius.api import SyriusAPI
from syrius.commands.abstract import AbstractCommand
from syrius.types import commands_union


class Flow(BaseModel):
    commands: list[commands_union] = []
    name: str
    api_client: ClassVar[SyriusAPI] = SyriusAPI()

    def add(self, command: AbstractCommand):
        self.commands.append(command)

    def check_status(self, runner_id: str, latest: bool = False) -> Any | None:
        """

        :param runner_id: str:
        :param latest: bool:  (Default value = False)

        """
        status_answer = self.api_client.check_flow_status(runner_id)
        status = status_answer["status"]
        context = status_answer["context"]
        if status == "COMPLETED":
            if latest:
                new_context = OrderedDict(context)
                tuple_context = new_context.popitem()
                if len(tuple_context) == 2:
                    status_answer["context"] = tuple_context[1]
            return status_answer
        return None

    def run(self) -> str:
        """ """
        # check if the following flow already exist
        response = self.api_client.add_flow(self.model_dump())
        runner_code = self.api_client.run(name=self.name, hash=response['hash'])
        return runner_code
