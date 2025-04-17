
from cmd2 import CommandSet


from stardust.utils.applogging import HelioLogger

log = HelioLogger()


class StripChat(CommandSet):
    prompt = "SC-->"
    def __init__(self):
        super().__init__()
        
    def do_b(self, _):
        print("hello stripchat")

