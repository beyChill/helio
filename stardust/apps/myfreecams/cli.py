from cmd2 import CommandSet, categorize
from argparse import Namespace
from stardust.utils.applogging import HelioLogger

log = HelioLogger()


class MyFreeCams(CommandSet):
    # prompt = "MFC-->"
    def __init__(self):
        super().__init__()

    def do_get(self,ns:Namespace):
        """Capture a streamer

        example:
        MFC--> get my_fav_girl
        """
        pass


    def do_stop(self,ns:Namespace):
        """Stop Streamer Capture
        MFC--> get my_fav_girl
        """
        pass

    def do_block(self,ns:Namespace):
        """Block streamer from long captures
        MFC--> get my_fav_girl
        """
        pass

    categorize((do_get, do_stop, do_block), "MyFreeCams Streamer")