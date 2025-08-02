from stardust.ffmpeg_files.ffmpeg_data import FFmpegConfig
from stardust.ffmpeg_files.ffmpeg_saver import CaptureStreamer
import stardust.utils.heliologger as log


def start_capture(data: set | list | tuple):
    """
    Compile data for capture using ffmpeg
    """
    if isinstance(data, list | set):
        if not data:
            for name_, x, y in data:
                if name_:
                    log.error(f"Invalid streamer data for {name_} ")
            return

        config_list = [
            FFmpegConfig(name_, slug, url_).return_data
            for name_, slug, url_ in data
            if url_ is not None
        ]

        _ = [CaptureStreamer(result) for result in config_list]
        return True

    name_, slug, url = data

    if url is None:
        return None

    config = FFmpegConfig(name_, slug, url).return_data
    CaptureStreamer(config)
    return True
