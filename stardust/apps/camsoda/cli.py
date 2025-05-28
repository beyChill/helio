from cmd2 import CommandSet


class CamSoda(CommandSet):
    prompt = "SC-->"

    def __init__(self):
        super().__init__()

    def do_cs(self, _):
        print("hello camsoda")
