

from cmd2 import  CommandSet, Statement

from stardust.utils.applogging import HelioLogger


log = HelioLogger()


class Chaturbate(CommandSet):
    """Interact with Chaturbate streamers"""

    prompt = "CB"

    def __init__(self):
        super().__init__()

    def do_a(self,_:Statement):
        log.warning('hello my dear chaturbate')




