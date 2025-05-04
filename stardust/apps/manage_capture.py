from stardust.ffmpeg_files.ffmpeg_data import FFmpegConfig
from stardust.ffmpeg_files.ffmpeg_saver import CaptureStreamer


def start_capture(data: list | tuple):
    """
    Compile data for capture

    Capture using ffmpeg
    """
    if isinstance(data, list):
        config_list = [
            FFmpegConfig(name_, slug, url_).return_data for name_, slug, url_ in data
        ]
        _ = [CaptureStreamer(result) for result in config_list]
        return True

    name_, slug, url = data

    config = FFmpegConfig(name_, slug, url).return_data
    CaptureStreamer(config)
    return True
