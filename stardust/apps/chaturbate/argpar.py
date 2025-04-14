from cmd2 import Cmd2ArgumentParser

def get_parser():
    cb_get = Cmd2ArgumentParser(description='capture streamer or show data')
    cb_get.add_argument("-c", "--capture", action="store_true", help="Capture streamer")
    cb_get.add_argument("-d", "--data", action="store_true", help="Display streamer data")
    cb_get.add_argument("streamer", nargs="?", help="Streamer name", default="--capture")

    return cb_get
    
