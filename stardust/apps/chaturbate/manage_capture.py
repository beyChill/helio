from stardust.apps.chaturbate.ffmpeg_config import FFmpegData
from stardust.apps.chaturbate.ffmpeg_saver import CaptureStreamer


def start_capture(list: list):
    """
    Compile data for capture

    Capture using ffmpeg
    """
    data = [FFmpegData(name_, url_).return_data for name_, url_ in list]

    _ = [CaptureStreamer(result) for result in data]

    return None
