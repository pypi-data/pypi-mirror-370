import logging


from commands.commandbase import CommandBase


log = logging.getLogger("").getChild(__name__)




class Validate(CommandBase):

    def __init__(
        self,
    ):

        super(Validate, self).__init__()

    def run(self):
        print("its Validate")
