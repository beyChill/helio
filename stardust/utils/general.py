from datetime import datetime, timedelta
from random import uniform
from typing import Any

import m3u8
from rnet import Client, Response

import stardust
from stardust.apps import __apps__ as helio_apps
from stardust.apps.chaturbate.db_write import write_m3u8
from stardust.utils.applogging import HelioLogger, loglvl

log = HelioLogger()


def get_app_name(app_tag: str):
    """
    Dynamically generate a dict then return value
    """
    APP_DICT = {}
    for app in dir(helio_apps):
        if app.startswith("app_"):
            app_data = getattr(helio_apps, app)
            APP_DICT[app_data[0]] = app_data

    if not (data := APP_DICT.get(app_tag)):
        return None

    return data


def script_delay(min: float, max: float):
    delay = uniform(min, max)
    t1 = datetime.now() + timedelta(seconds=delay)
    time_ = datetime.strftime(t1, "%H:%M:%S")

    return (delay, time_)


def process_hls(results: list[Any]):
    streamer_url: list[tuple[str, str]] = []

    for url_, m3u8_ in results:
        m3u8_file = m3u8.loads(m3u8_)

        if not m3u8_file.playlists[-1]:
            continue

        best_quality = m3u8_file.playlists[-1].uri
        new_url = url_.replace("playlist.m3u8", str(best_quality))
        streamer_name = new_url.split("amlst:")[-1].split("-sd-")[0]
        streamer_url.append((streamer_name, new_url))
        write_data = [(v, k) for k, v in streamer_url]
        write_m3u8(write_data)

    return streamer_url


async def check_helio_github_version():
    """Check Helio version currency"""

    log.info("Checking Helio version")
    repo_path = stardust.__repo_path__
    client = Client()
    latest_version = ""
    try:
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        resp: Response = await client.get(
            f"https://api.github.com/repos/{repo_path}/releases/latest",
            headers=headers,
        )

        github_json = await resp.json()
        latest_version = github_json["name"]

    except Exception as e:
        log.error("Helio version check failed")
        log.error(e)
        return False

    if stardust.__version__ < latest_version:
        log.warning(f"Helio version {stardust.__version__} is not current")
        log.warning(f"Consider updating to {latest_version}")
        return False

    if stardust.__version__ >= latest_version:
        log.app(loglvl.SUCCESS, "Helio is current")

    return True
