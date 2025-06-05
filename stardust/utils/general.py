import os
from datetime import datetime, timedelta
from pathlib import Path
from random import uniform
from string import ascii_lowercase, digits

from rnet import Client, Response

import stardust
import stardust.utils.heliologger as log
from stardust.apps import __apps__ as helio_apps
from stardust.apps.manage_app_db import HelioDB
from stardust.apps.models_app import not200
from stardust.apps.myfreecams.json_models import Lookup
from stardust.config.settings import get_setting

IMG_PATH = get_setting().DIR_IMG_PATH


def chk_streamer_name(name_: str):
    valid_lower = "".join([ascii_lowercase, digits, "_"])

    return all(chars in valid_lower for chars in name_)


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


def get_app_slugs():
    all_slugs: list[str] = []
    for app in dir(helio_apps):
        if app.startswith("app_"):
            values = getattr(helio_apps, app)
            all_slugs.append(values[0])
    return all_slugs


def script_delay(min: float, max: float):
    delay = uniform(min, max)
    t1 = datetime.now() + timedelta(seconds=delay)
    time_ = datetime.strftime(t1, "%H:%M:%S")

    return (delay, time_)


def make_image_dir(name_: str, app_site) -> Path:
    """Image files are sorted / stored using first character in streamer's name"""
    characters = list(name_)
    folder_character = characters[0].upper()
    path_ = Path(IMG_PATH / app_site / folder_character)

    if not path_.exists():
        path_.mkdir(parents=True, exist_ok=True)

    return path_


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
        log.warning(f"This Helio version {stardust.__version__} is not current")
        log.warning(f"Consider updating to {latest_version}")
        log.warning("https://github.com/beyChill/helio")
        return False

    if stardust.__version__ >= latest_version:
        log.success("Helio is current")

    return True


def calc_size(file_data: list[int]):
    raw_total = sum(file_data)
    giga = round(raw_total / (1024**3), 4)
    return giga


def calc_video_size(name_: str, file: Path, slug: str):
    raw_size = os.stat(file).st_size
    file_size = calc_size([raw_size])
    values = (file_size, name_, slug)
    HelioDB().write_video_size(values)


def filter_not200(data):
    db = HelioDB()
    isnot200: list[not200] = []
    filtered_data = []

    for x in data:
        if isinstance(x, not200):
            isnot200.append(x)
            continue

        filtered_data.append(x)
    data = [(x.name_, x.site, x.code_, x.reason) for x in isnot200]
    db.write_not200(data)
    return filtered_data


def build_url_data(data: list[Lookup]):
    table_data = []

    for x in data:
        if not x.result.user.sessions:
            log.warning(f"{x.result.user.username} is offline")
            continue

        table_data.append(
            (
                x.result.user.username,
                x.result.user.sid,
                x.result.user.id,
                x.result.user.vs,
                x.result.user.sessions[-1].platform_id,
                x.result.user.access_level,
                x.result.user.camserv,
                x.result.user.sessions[-1].phase,
            )
        )
    return table_data
