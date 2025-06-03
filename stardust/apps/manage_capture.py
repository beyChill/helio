from stardust.ffmpeg_files.ffmpeg_data import FFmpegConfig
from stardust.ffmpeg_files.ffmpeg_saver import CaptureStreamer


def start_capture(data: set | list | tuple):
    """
    Compile data for capture using ffmpeg
    """
    if isinstance(data, list | set):
        config_list = [
            FFmpegConfig(name_, slug, url_).return_data for name_, slug, url_ in data if url_ is not None
        ]

        _ = [CaptureStreamer(result) for result in config_list]
        return True

    name_, slug, url = data
    
    if url is None:
        return None

    config = FFmpegConfig(name_, slug, url).return_data
    CaptureStreamer(config)
    return True
