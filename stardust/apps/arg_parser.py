from cmd2 import Cmd2ArgumentParser

S_NAME = "Streamer's name"


def get_streamer():
    usage = "get [streamer_name]"
    desc = "Initiate video capture or view stored data"
    epilog = "Capture is the default argument, it can be ommitted."
    parser = Cmd2ArgumentParser(description=desc, usage=usage, epilog=epilog)
    parser.add_argument("name", nargs="?", help=S_NAME, default="--capture")
    parser.add_argument("-c", "--capture", action="store_true", help="capture video")
    parser.add_argument("-d", "--data", action="store_true", help="display data")

    return parser


def block_reason():
    usage = "block [streamer_name] [reason]"
    desc = "Prevent capture of a streamer"
    parser = Cmd2ArgumentParser(usage=usage, description=desc)
    parser.add_argument("name", nargs=1, help=S_NAME)
    parser.add_argument("reason", nargs="+", help="Reason for block")

    return parser


def cap_status():
    usage = "cap data"
    desc = "Display stats for active captures"
    epilog = "Name is the default sort field"
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
    usage = "long [number of days]"
    desc = "Lable streamer inactive based on input number of days\n Compares last broadcast with input of number of days"
    parser = Cmd2ArgumentParser(usage=usage, description=desc)
    parser.add_argument(
        "days",
        type=int,
        choices=[0, 7, 14, 31, 60, 90, 120, 180, 365, 730],
        help="Use one option",
    )

    return parser


def set_logs():
    usage = "log [debug] / log [info] on"
    desc = "Control visibility of Helio's logging messages"
    epilog = "Off is the default argument, it can be ommitted."
    parser = Cmd2ArgumentParser(usage=usage, description=desc, epilog=epilog)

    parser.add_argument(
        "level",
        type=str,
        help="",
        choices=[
            "notset",
            "created",
            "moved",
            "timer",
            "offline",
            "stopped",
            "debug",
            "maxtime",
            "info",
            "success",
            "capturing",
            "warning",
            "error",
            "failure",
        ],
    )

    parser.add_argument(
        "value",
        type=str,
        nargs="?",
        help="Activate / deactivate (default)",
        default="off",
        choices=["on", "off"],
    )
    return parser


def stop_streamer():
    usage = "get [streamer_name]"
    desc = "Stop video capture and remove from seek capture status"
    epilog = "Capture is the default argument, it can be ommitted."
    parser = Cmd2ArgumentParser(description=desc, usage=usage, epilog=epilog)
    parser.add_argument("name", nargs="?", help=S_NAME, default="--capture")
    parser.add_argument("-s", "--seek", action="store_true", help="capture video")
    parser.add_argument("-c", "--capture", action="store_true", help="display data")
    parser.add_argument(
        "-a",
        "-all",
        default="-a",
        action="store_true",
        help="display data"
    )

    return parser
