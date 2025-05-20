from cmd2 import Cmd2ArgumentParser

h_name = "Streamer's name"


def get_streamer():
    usage = "get [streamer_name]"
    desc = "Initiate video capture or view stored data"
    epilog = "capture is the default argument, it can be ommitted."
    parser = Cmd2ArgumentParser(description=desc, usage=usage, epilog=epilog)
    parser.add_argument("name", nargs="?", help=h_name, default="--capture")
    parser.add_argument("-c", "--capture", action="store_true", help="capture video")
    parser.add_argument("-d", "--data", action="store_true", help="display data")

    return parser


def block_reason():
    usage = "block [streamer_name] [reason]"
    desc = "Prevent capture of a streamer"
    parser = Cmd2ArgumentParser(usage=usage, description=desc)
    parser.add_argument("name", nargs=1, help=h_name)
    parser.add_argument("reason", nargs="+", help="Reason for block")

    return parser


def cap_status():
    usage = "cap data"
    desc = "Display stats for active captures"
    epilog = "name is the default sort field"
    parser = Cmd2ArgumentParser(
        prog="hello", usage=usage, description=desc, epilog=epilog
    )
    parser.add_argument(
        "sort",
        nargs="?",
        default="name",
        choices=["date", "name", "site", "size"],
        help="Select one option",
    )

    return parser


def long_inactive():
    usage = "long [number]"
    desc = "Places streamer in an inactive status"
    parser = Cmd2ArgumentParser(usage=usage, description=desc)
    parser.add_argument(
        "days",
        type=int,
        choices=[0, 7, 14, 31, 60, 90, 120, 180, 365, 730],
        help="Use one option",
    )

    return parser
