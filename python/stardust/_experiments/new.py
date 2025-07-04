import json
from pathlib import Path
from typing import NamedTuple

from pydantic import BaseModel


class url_data(NamedTuple):
    nm: str
    sid: int
    uid: int
    vs: int
    pid: int
    lv: int
    camserv: int
    phase: str


class mm(NamedTuple):
    chat_color: int
    chat_font: int
    chat_opt: int
    creation: int
    avatar: int
    profile: int
    photos: str
    blurb: int
    new_model: int
    missmfc: int
    camscore: float
    continent: str
    flags: int
    rank: int
    rc: str
    topic: int
    hidecs: int


# Get the current script's folder
base_dir = Path(__file__).parent

# Form the complete file path
file_path = base_dir / "j.json"
with open(file_path) as j:
    w = json.load(j)
q: list[list] = w["rdata"][1:3]
j = w["rdata"]

# print(*w['rdata'][1:3],sep='\n')
# t={url_data(*x[0:8]) for x in w['rdata'][1:-1]}
# mh={mm(*x[9:26])for x in w['rdata'][1:-1]}
# for x in q:
#     print(type(q))

# print(w['rdata'][1])

t = [x[0:8] for x in j[1:4]]
p = [[x[0], x[11], *x[16:22]] for x in j[1:4]]
# j = sum(p, [])
# b = [item for sublist in j for item in sublist]
# c = [sum(x, []) for x in b]

print(p)
# print(j)
# print(b)
# print(c)
# print(len(mh))

# e="00025681 0 329620393 14 256 %sfgsgr rgtr%4534%sfg"
# g=e.split()[0]
# print(g)
