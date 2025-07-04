import asyncio
import shutil
from pathlib import Path
from PIL import Image
import pytesseract
import cv2

from stardust.apps.myfreecams.db_myfreemcams import DbMfc
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.apps.myfreecams.helper import HASH_REFS, calc_img_hash, mfc_server_offset
from stardust.utils.applogging import HelioLogger
from stardust.utils.general import make_image_dir
from stardust.utils.timer import AppTimer, AppTimerSync

iNet = MfcNetActions()
log = HelioLogger()

APP_SITE = "myfreecams"
db = DbMfc(APP_SITE)


@AppTimer
async def request_images(streamers: list[tuple[str, int, int]]):
    data = await iNet.get_all_jpg(streamers)

    results = [(streamer_name, image) for streamer_name, image in data if image]

    return results


@AppTimerSync
def process_results(results: list[tuple[str, bytes]]):
    next = []
    for streamer in results:
        name_, image = streamer
        img_dir = make_image_dir(name_, APP_SITE)
        next.append((image, name_, img_dir))
    return next


delete = []
move = []
online = []
words = ["MyFreeCams", "MyFreeGams", "currently", 'from', 'away']


@AppTimerSync
def process_imgs(next: list[tuple[bytes, str, Path]]):
    anoth = []
    for image, name_, img_dir in next:
        path_to_img = Path(img_dir, f"{name_}.jpg").joinpath()
        path_to_img.write_bytes(image)
        anoth.append((path_to_img, name_))
    return anoth


@AppTimerSync
def hash_n(anoth):
    hash_n = [(calc_img_hash(x), x, y) for x, y in anoth]
    return hash_n


@AppTimerSync
def do_checks(hash_n):
    we = []
    for hash, path, name_ in hash_n:
        # Image hash is fast but myfreecams has trickery.
        if str(hash) in HASH_REFS:
            # Delete ops are slow, delaying
            # them til after all imgs are hashed
            delete.append(path)
            continue
            # print(hash)
        we.append((path, name_))
    return we


@AppTimerSync
def do_text_check(we):
    for path, name_ in we:
        # Secondary check, text on image.
        # MFC streamers can blur live background
        # which makes img hash impractical.
        # However, MFC places a notice on screen
        image = Image.open(path)
        text = pytesseract.image_to_string(image, lang="eng", config="--psm 6").split()
        found = [word for word in words if word in text]
        # print(found)
        if found:
            # if "MyFreeCams" in text or "MyFreeGams" in text:
            log.warning(f"{name_} [MFC] is busy")
            move.append(path)

        online.append(name_)


@AppTimerSync
def status_seek_capture():
    streamers_list = db.query_for_img()
    if not streamers_list:
        log.warning("Zero MyFreeCams streamers for status query")
        return None

    # Data used to construct MFC img url
    url_data = [
        (name_, mfc_server_offset(server), id) for name_, id, server in streamers_list
    ]

    results = asyncio.run(request_images(url_data))

    next = process_results(results)
    anoth = process_imgs(next)
    almost = hash_n(anoth)
    we = do_checks(almost)
    do_text_check(we)

    dst = "/mnt/Alpha/_bey/uv/helio/stardust/aexper/review"
    dst1 = "/mnt/Alpha/_bey/uv/helio/stardust/aexper/good"

    # _ = [x.unlink() for x in delete]
    _ = [shutil.move(x, dst) for x in delete]
    _ = [shutil.move(x, dst1) for x in move]
    log.info(f"Secondary evals for {len(move)} steamer imgs")
    log.info(f"{len(streamers_list) - len(delete)} of {len(streamers_list)} are online")


if __name__ == "__main__":
    status_seek_capture()
