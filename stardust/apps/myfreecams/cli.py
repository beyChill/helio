from cmd2 import CommandSet

from stardust.utils.applogging import HelioLogger

log = HelioLogger()


class MyFreeCams(CommandSet):
    prompt = "MFC-->"
    def __init__(self):
        super().__init__()
        
    def do_mfc(self, _):
        print("hello MFC")
