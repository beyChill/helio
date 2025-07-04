from cmd2 import CommandSet


class StripChat(CommandSet):
    prompt = "SC-->"

    def __init__(self):
        super().__init__()

    def do_b(self, _):
        print("hello stripchat")
