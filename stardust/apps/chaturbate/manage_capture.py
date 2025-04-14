from stardust.apps.chaturbate.set_streamer_data import FFmpegData
from stardust.apps.chaturbate.capture import CaptureStreamer


def start_capture(list: list):
    """
    Compile data for capture

    Capture using ffmpeg
    """
    data = [FFmpegData(name_, url_).return_data for name_, url_ in list]

    _ = [CaptureStreamer(result) for result in data]

    return None
