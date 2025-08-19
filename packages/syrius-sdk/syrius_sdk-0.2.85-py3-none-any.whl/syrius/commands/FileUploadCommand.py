from syrius.api import SyriusAPI
from syrius.commands.abstract import LocalCommand
from syrius.exceptions import FlowException


class FileUploadCommand(LocalCommand):
    """ """
    file_path: str

    def run(self) -> str:
        """ """
        try:
            api_client = SyriusAPI()
            response = api_client.upload_file(self.file_path)
            return response["file"]
        except FlowException as e:
            raise Exception(
                "Something goes wrong with flow upload file process")
