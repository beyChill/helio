from stardust.apps.chaturbate.ffmpeg_config import FFmpegData
from stardust.ffmpeg_files.ffmpeg_data import FFmpegConfig
from stardust.ffmpeg_files.ffmpeg_saver import CaptureStreamer


def start_capture(list: list):
    """
    Compile data for capture

    Capture using ffmpeg
    """
    data = [FFmpegConfig(name_, slug, url_).return_data for name_, slug, url_ in list]
    # data = [FFmpegData(name_, url_).return_data for name_, url_ in list]

    _ = [CaptureStreamer(result) for result in data]

    return None
