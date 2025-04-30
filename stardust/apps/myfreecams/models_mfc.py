from __future__ import annotations

from pydantic import BaseModel

from typing import Any, List, Optional


class Session(BaseModel):
    session_id: int
    vstate: int
    room_count: int
    vidserver_id: int
    room_topic: str
    platform_id: int
    continent: str
    server_name: str
    server_type: Optional[str]=None
    fcapp_type: Optional[int]=None
    video_server_type: Optional[str]=None
    server_is_webrtc: bool=False
    phase: str
    snap_url: str


class Profile(BaseModel):
    age: Optional[str]=None
    gender: Optional[str]=None
    birthdate: Optional[str]=None
    sexual_preference: Optional[str]=None
    marital_status: Optional[str]=None
    ethnicity: Optional[str]=None
    hair: Optional[str]=None
    eyes: Optional[str]=None
    weight: Optional[str]=None
    weight_units: Optional[str]=None
    height: Optional[str]=None
    height_units: Optional[str]=None
    body_type: Optional[str]=None
    smoke: Optional[str]=None
    drink: Optional[str]=None
    drugs: Optional[str]=None
    blurb: Optional[str]=None


class Share(BaseModel):
    albums: Optional[int]=None
    follows: Optional[int]=None
    clubs: Optional[int]=None
    tm_album: Optional[int]=None
    collections: Optional[int]=None
    stores: Optional[int]=None
    goals: Optional[int]=None
    polls: Optional[int]=None
    things: Optional[int]=None
    recent_album_tm: Optional[int]=None
    recent_club_tm: Optional[int]=None
    recent_collection_tm: Optional[int]=None
    recent_goal_tm: Optional[int]=None
    recent_item_tm: Optional[int]=None
    recent_poll_tm: Optional[int]=None
    recent_story_tm: Optional[int]=None
    recent_album_thumb: Optional[str]=None
    recent_club_thumb: Optional[str]=None
    recent_collection_thumb: Optional[str]=None
    recent_goal_thumb: Optional[str]=None
    recent_item_thumb: Optional[str]=None
    recent_poll_thumb: Optional[str]=None
    recent_story_thumb: Optional[str]=None
    recent_album_title: Optional[str]=None
    recent_club_title: Optional[str]=None
    recent_collection_title: Optional[str]=None
    recent_goal_title: Optional[str]=None
    recent_item_title: Optional[str]=None
    recent_poll_title: Optional[str]=None
    recent_story_title: Optional[str]=None
    recent_album_slug: Optional[str]=None
    recent_collection_slug: Optional[str]=None
    tipmenus: Optional[int]=None
    free_albums: Optional[int]=None


class Social(BaseModel):
    twitter_username: Optional[str]=None
    instagram_username: Optional[str]=None


class User(BaseModel):
    id: int
    username: str
    access_level: int
    active: int
    avatar: str
    sessions: Optional[List[Session]]=None
    cam_score: float
    camserv: Optional[int]=None
    chat_color: str
    chat_font: int
    chat_opts: int
    hide_cam_score: int
    last_login: str
    missmfc: Any
    profile: Profile
    rank: Optional[int]=None
    sid: Optional[int]=None
    share: Optional[Share]=None
    social: Optional[Social]=None
    tags: Optional[List[str]]=None
    user_id: int
    vs: Optional[int]=None


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