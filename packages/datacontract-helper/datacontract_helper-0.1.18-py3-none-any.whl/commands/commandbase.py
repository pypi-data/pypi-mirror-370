import logging





log = logging.getLogger("").getChild(__name__)




class CommandBase:

    def __init__(
        self, *args, **kwargs
    ) -> None:
        ...


    def do_run(self):

        self.run()

    def run(self):
        pass

