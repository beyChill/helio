import asyncio
from datetime import datetime, timedelta
import os
from pathlib import Path
from random import uniform
from string import ascii_lowercase, ascii_uppercase, digits

from rnet import Client, Response

import stardust
from stardust.apps import __apps__ as helio_apps
from stardust.apps.chaturbate.handleurls import NetActions
from stardust.apps.manage_app_db import HelioDB
from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.apps.myfreecams.helper import parse_profile
from stardust.config.settings import get_setting
from stardust.utils.applogging import HelioLogger, loglvl
from stardust.utils.handle_m3u8 import HandleM3u8

log = HelioLogger()
IMG_PATH = get_setting().DIR_IMG_PATH



def chk_streamer_name(name_: str,site:str):
    valid_all =   "".join([ascii_lowercase, ascii_uppercase, digits, "_"])
    valid_lower = "".join([ascii_lowercase, digits, "_"])

    valid_characters={'all':valid_all,'lower':valid_lower}

    if site=='CB':
        valid_char=valid_characters.get('all',"")
        return all(chars in valid_char for chars in name_)
    
    if site=='CB':
        valid_char=valid_characters.get('lower',"")
        return all(chars in valid_char for chars in name_)

def get_all_app_names():
    app_names = []
    for app in dir(helio_apps):
        if app.startswith("app_"):
            app_data = getattr(helio_apps, app)
            app_names.append(app_data[1])
    return app_names


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
        log.app(loglvl.SUCCESS, "Helio is current")

    return True


def calc_size(file_data: list[int]):
    raw_total = sum(file_data)
    giga = round(raw_total / (1024**3), 4)
    return giga


def calc_video_size(name_: str, file: Path, site: str):
    raw_size = os.stat(file).st_size
    file_size = calc_size([raw_size])
    values = (file_size, name_)
    HelioDB(site).write_video_size(values)


def get_url(name_, site):
    if site == "chaturbate":
        results = asyncio.run(NetActions().get_ajax_url([name_]))

        if not results[0]["url"]:
            log.app(loglvl.STOPPED, f"{name_} [{site}] {results[0]['room_status']}")
            return None

        url = results[0]["url"]
        return HandleM3u8(url).new_cb_m3u8()

    if site == "myfreecams":
        json_ = asyncio.run(MfcNetActions().get_user_profile([name_]))
        url_ = parse_profile(json_[0])

        if isinstance(url_,tuple):
            url_=None

        DbMfc("myfreecams").write_url((url_, name_))
        return url_
