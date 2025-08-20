import logging


from commands.commandbase import CommandBase


log = logging.getLogger("").getChild(__name__)


class PublishPackage(CommandBase):

    def __init__(
        self,
    ):

        super(PublishPackage, self).__init__()

    def run(self):
        print("its PublishPackage")
        create_proto: str = """
        echo "$(uv run datacontract export vertica_datacontract.yaml --format protobuf | perl -0777 -nle "print \$1 if /'protobuf':\s*'(.*?)'/s" )" > vertica_datacontract.proto
        """
        print(create_proto)
