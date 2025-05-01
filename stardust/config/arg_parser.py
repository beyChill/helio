from cmd2 import Cmd2ArgumentParser

def get_parser():
    cli_get_cmd = Cmd2ArgumentParser(description='capture streamer or show data')
    cli_get_cmd.add_argument("-c", "--capture", action="store_true", help="Capture streamer")
    cli_get_cmd.add_argument("-d", "--data", action="store_true", help="Display streamer data")
    cli_get_cmd.add_argument("streamer", nargs="?", help="Streamer name", default="--capture")

    return cli_get_cmd