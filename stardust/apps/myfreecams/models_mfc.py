from __future__ import annotations

from pydantic import BaseModel

from typing import Any, Optional


class MfcSession(BaseModel):
    session_id: int
    vstate: int
    room_count: int
    vidserver_id: int
    room_topic: str
    platform_id: int
    continent: str
    server_name: str
    server_type: Optional[str] = None
    fcapp_type: Optional[int] = None
    video_server_type: Optional[str] = None
    server_is_webrtc: bool = False
    phase: str
    snap_url: str


class Profile(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[str] = None
    sexual_preference: Optional[str] = None
    marital_status: Optional[str] = None
    ethnicity: Optional[str] = None
    hair: Optional[str] = None
    eyes: Optional[str] = None
    weight: Optional[str] = None
    weight_units: Optional[str] = None
    height: Optional[str] = None
    height_units: Optional[str] = None
    body_type: Optional[str] = None
    smoke: Optional[str] = None
    drink: Optional[str] = None
    drugs: Optional[str] = None
    blurb: Optional[str] = None


class Share(BaseModel):
    albums: Optional[int] = None
    follows: Optional[int] = None
    clubs: Optional[int] = None
    tm_album: Optional[int] = None
    collections: Optional[int] = None
    stores: Optional[int] = None
    goals: Optional[int] = None
    polls: Optional[int] = None
    things: Optional[int] = None
    recent_album_tm: Optional[int] = None
    recent_club_tm: Optional[int] = None
    recent_collection_tm: Optional[int] = None
    recent_goal_tm: Optional[int] = None
    recent_item_tm: Optional[int] = None
    recent_poll_tm: Optional[int] = None
    recent_story_tm: Optional[int] = None
    recent_album_thumb: Optional[str] = None
    recent_club_thumb: Optional[str] = None
    recent_collection_thumb: Optional[str] = None
    recent_goal_thumb: Optional[str] = None
    recent_item_thumb: Optional[str] = None
    recent_poll_thumb: Optional[str] = None
    recent_story_thumb: Optional[str] = None
    recent_album_title: Optional[str] = None
    recent_club_title: Optional[str] = None
    recent_collection_title: Optional[str] = None
    recent_goal_title: Optional[str] = None
    recent_item_title: Optional[str] = None
    recent_poll_title: Optional[str] = None
    recent_story_title: Optional[str] = None
    recent_album_slug: Optional[str] = None
    recent_collection_slug: Optional[str] = None
    tipmenus: Optional[int] = None
    free_albums: Optional[int] = None


class Social(BaseModel):
    twitter_username: Optional[str] = None
    instagram_username: Optional[str] = None


class User(BaseModel):
    id: int
    username: str
    access_level: int
    active: int
    avatar: str
    sessions: Optional[list[MfcSession]] = None
    cam_score: float
    camserv: Optional[int] = None
    chat_color: str
    chat_font: int
    chat_opts: int
    hide_cam_score: int
    last_login: str
    missmfc: Any
    profile: Profile
    rank: Optional[int] = None
    sid: Optional[int] = None
    share: Optional[Share] = None
    social: Optional[Social] = None
    tags: Optional[list[str]] = None
    user_id: int
    vs: Optional[int] = None


class Result(BaseModel):
    success: int
    message: str
    user: Optional[User] = None


class MFCModel(BaseModel):
    id: str
    responseVer: int
    method: str
    result: Result
    err: int


class AppProfile(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    birthdate: Optional[str] = None
    sexual_preference: Optional[str] = None
    marital_status: Optional[str] = None
    ethnicity: Optional[str] = None
    hair: Optional[str] = None
    eyes: Optional[str] = None
    weight: Optional[str] = None
    weight_units: Optional[str] = None
    height: Optional[str] = None
    height_units: Optional[str] = None
    body_type: Optional[str] = None
    smoke: Optional[str] = None
    drink: Optional[str] = None
    drugs: Optional[str] = None
    blurb: Optional[str] = None
    favorite_food: Optional[str] = None
    pets: Optional[str] = None
    automobile: Optional[str] = None
    perfect_mate: Optional[str] = None
    perfect_date: Optional[str] = None
    meaning_life: Optional[str] = None
    know_me: Optional[str] = None


class Attribute(BaseModel):
    title: str
    value: str
    order: int


class AppShare(BaseModel):
    follows: Optional[int]=None
    tipmenus: Optional[int]=None


class MFCAppModel(BaseModel):
    id: int
    username: str
    access_level: int
    active: int
    avatar: Optional[str] = None
    cam_score: Optional[float] = None
    camserv: Optional[int] = None
    chat_color: Optional[str] = None
    chat_font: Optional[int] = None
    chat_opts: Optional[int] = None
    hide_cam_score: Optional[int] = None
    last_login: Optional[str] = None
    missmfc: Optional[Any] = None
    profile: Optional[AppProfile] = None
    rank: Optional[Any] = None
    sid: Optional[int] = None
    social: Optional[Any] = None
    user_id: Optional[int] = None
    vs: Optional[int] = None
    attributes: Optional[list[Attribute]] = None
    tags: Optional[list[str]] = None
    share: Optional[AppShare] = None


class GetStreamerResult(BaseModel):
    name_: str
    data: Optional[MFCAppModel] = None
    status: Optional[int] = None


class MfcData(BaseModel):
    user_id: int
    username: str
    cam_score: int
    answer: str
    chat_text_color: str
    chat_text_font: int
    chat_text_font_flags: int
    style_string: str


class MfcResults(BaseModel):
    category: str
    order: str
    selection: str
    limit: str
    full_detail: str
    desc: str
    search: str
    expanded: str
    _: str
    offset: int
    total: int
    data: list[MfcData]


class AllModels(BaseModel):
    id: str
    responseVer: int
    method: str
    result: MfcResults
    err: int