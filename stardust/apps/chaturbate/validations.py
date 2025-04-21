from string import ascii_lowercase, digits

from stardust.utils.applogging import HelioLogger

log = HelioLogger()


def check_streamer_name(name_: str):
    valid_characters = ascii_lowercase + digits + "_"
    if not all(chars in valid_characters for chars in name_):
        log.error("Use lowercase letters, digits 0-9, and underscore ( _ ) in name")
        return None
    print(name_)
    return name_
