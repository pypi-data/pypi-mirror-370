import logging


from commands.commandbase import CommandBase
from requests.auth import HTTPBasicAuth
import requests
import os


log = logging.getLogger("").getChild(__name__)


class PublishPackage(CommandBase):

    def __init__(
        self,
    ):

        super(PublishPackage, self).__init__()

    def run(self):
        print("its PublishPackage")

    def create_proto(self):
        create_proto: str = """
        echo "$(uv run datacontract export vertica_datacontract.yaml --format protobuf | perl -0777 -nle "print \$1 if /'protobuf':\s*'(.*?)'/s" )" > vertica_datacontract.proto
        """
        print(create_proto)

    def publish(self):
        q: str = """
        this is where the package is published to nexus
        example:
        https://gitlab.ostrovok.ru/an_dev/data-build-tool/-/blob/dbt_sandbox/python_scripts/generate_config_for_af.py#L27

        """
        # self.upload_to_nexus()

    def upload_to_nexus(
        self, file_path, nexus_url, nexus_repo_path, username, password
    ):
        with open(file_path, "rb") as file:
            nexus_full_url = f"{nexus_url}/repository/{nexus_repo_path}/{os.path.basename(file_path)}"
            response = requests.put(
                nexus_full_url,
                auth=HTTPBasicAuth(username, password),
                data=file,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logging.info(
                f"The file has been successfully uploaded to Nexus: {nexus_full_url}"
            )

        # print()
