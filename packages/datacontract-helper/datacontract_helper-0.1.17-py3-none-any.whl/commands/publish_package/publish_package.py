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
