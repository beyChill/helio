__all__ = [
    "sum_as_string",
    "get_env_data",
    "format_streamer_name",
    "parse_streamer_name",
]

def sum_as_string(a: int, b: int): ...
def get_env_data(): ...
def format_streamer_name(name_: str) -> str:
    """Tranfrom streamer's name to lowercase\n
    Check for valid charcters in name\n

    :return: valid streamer name as string
    """
    ...

def parse_streamer_name(name: str) -> str: ...
