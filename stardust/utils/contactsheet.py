import shutil
import subprocess
from itertools import groupby
from os.path import dirname
from pathlib import Path

import stardust.utils.heliologger as log
from stardust.apps.models_app import ContactSheetModel
from stardust.config.settings import get_setting
from stardust.utils.timer import AppTimerSync


def get_folders():
    contactsheet_dir = get_setting().DIR_PROCESS_CONTACTSHEET
    folders = [path_ for path_ in contactsheet_dir.iterdir()]

    return folders


def get_videos():
    streamer = get_setting().DIR_PROCESS_CONTACTSHEET
    log.info(f"{streamer}")
    paths = [
        path_.resolve()
        for path_ in streamer.rglob("**/*")
        if path_.suffix in {".mp4", ".mkv"}
    ]
    paths.sort()
    video_paths = [list(g) for _, g in groupby(paths, dirname)]

    return video_paths


def get_video_duration(video_path: list[list[Path]]):
    log.info("calculating video durations")
    video_duration_seconds = 0
    new_dir = get_setting().DIR_VIDEO_SHORT
    video_durations: list[ContactSheetModel] = []
    video_data: list[list[ContactSheetModel]] = []

    for v_path in video_path:
        for path_ in v_path:
            new_location = Path(new_dir / path_.name)

            fs = path_.stat().st_size
            file_size = round(fs / (1024**2), 4)

            # auto remove files less than 10 Mib
            if file_size < 10:
                shutil.move(path_, new_location)
                log.moved(f"Tiny file: {path_.name} to {str(new_dir)}")

                continue

            output_file: Path = path_.with_suffix(".webp")

            if output_file.exists():
                continue

            path_str = str(path_)

            ffmpeg_args = [
                "ffprobe",
                "-hide_banner",
                "-show_entries",
                "format=DURATION",
                "-v",
                "quiet",
                "-i",
                path_str,
                "-of",
                "default=noprint_wrappers=1:nokey=1",
            ]

            try:
                video_seconds: str = subprocess.check_output(ffmpeg_args).decode("utf8")
                video_duration_seconds: int = round(float(video_seconds))

                # short video is <= 300 seconds (5 min)
                if video_duration_seconds <= 300:
                    shutil.move(path_, new_location)
                    log.moved(f"Moved {path_.name} to {str(new_dir)}")
                    continue

                interval = max_image(video_duration_seconds)

                video_durations.append(
                    ContactSheetModel(
                        input_path=path_, interval=interval, output_path=output_file
                    )
                )
            except (subprocess.CalledProcessError, ValueError):
                shutil.move(path_, new_location)
                log.failure(f"Broken file: {path_}\n**ffprobe read error")

        if len(video_durations) > 0:
            video_data.append(video_durations)
            video_durations = []

    return video_data


def max_image(seconds):
    max_images: int = round(seconds / 30)

    if max_images < 1:
        max_images = 1

    return max_images


@AppTimerSync
def create_contactsheet(data: ContactSheetModel):
    input_file = str(data.input_path)
    output_file = str(data.output_path)
    horizontal: int = 5
    vertical: int = 6
    frames = horizontal * vertical

    # ***************************************
    # contact sheet config
    # https://ffmpeg.org/ffmpeg-filters.html
    # **************************************

    # section 11.78 https://ffmpeg.org/ffmpeg-filters.html#drawtext-1
    time_stamp = "drawtext=text='%{pts\\:gmtime\\:0\\:%H\\\\\\:%M\\\\\\:%S}':x=(main_w-text_w):y=(main_h-text_h):fontcolor=White:fontsize=(main_h/8)"

    # section 18.17 https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect
    screen_shot = (
        f"select=isnan(prev_selected_t)+gte(t-prev_selected_t\\,{data.interval})"
    )

    # section 11.257 https://ffmpeg.org/ffmpeg-filters.html#tile
    sheet_features = f"scale=640:-1,tile={horizontal}x{vertical}:nb_frames={frames}:padding=7:margin=2 "

    sheet_attributes = [time_stamp, screen_shot, sheet_features]
    contact_sheet = ",".join(sheet_attributes)

    ff_args = [
        "ffmpeg",
        "-hide_banner",
        "-n",
        "-threads",
        "1",
        "-skip_frame",
        "nokey",
        "-i",
        input_file,
        "-filter:v",
        contact_sheet,
        "-vsync",
        "0",
        "-update",
        "1",
        "-quality",
        "85",
        "-compression_level",
        "0",
        output_file,
    ]

    with subprocess.Popen(
        ff_args,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        start_new_session=True,
        encoding="utf8",
    ) as sheet:
        # using communicate() as a hack to wait for process to finish

        _ = sheet.returncode


def loop_contactsheet_list(video_data):
    for files in video_data:
        for q, a in enumerate(files, 1):
            log.success(
                f"\rprocessing {q} of {len(files)} for {a.input_path.parts[-2]}"
            )
            create_contactsheet(a)


@AppTimerSync
def manage_contactsheet():
    log.created("Generating contact sheet(s)")
    videos = get_videos()
    video_data = get_video_duration(videos)
    loop_contactsheet_list(video_data)


if __name__ == "__main__":
    manage_contactsheet()
