from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel


class _auto_null:
    def __repr__(self):
        return "_auto_null"


# _auto_null = _auto_null()


class auto:
    """
    Instances are replaced with an appropriate value in Enum class suites.
    """

    def __init__(self, value=_auto_null):
        self.value = value

    def __repr__(self):
        return "auto(%r)" % self.value


class CBajax(BaseModel):
    success: bool
    url: str
    room_status: str
    hidden_message: str
    cmaf_edge: bool


class CBRoom(BaseModel):
    display_age: Optional[int]
    # gender: str
    location: Optional[str]
    current_show: str
    username: str
    is_new: bool
    num_users: int
    num_followers: int
    tags: list[str]
    start_dt_utc: str
    country: Optional[str]
    # has_password: bool
    # is_gaming: bool
    # is_age_verified: bool
    # label: str
    # is_following: bool
    # source_name: str
    start_timestamp: int
    # img: str
    # subject: str


class CBModel(BaseModel):
    rooms: list[CBRoom]
    total_count: int
    all_rooms_count: int
    room_list_id: str


class PhotoSet(BaseModel):
    id: int
    name: str
    cover_url: str
    tokens: int
    is_video: bool
    video_has_sound: bool
    user_can_access: bool
    user_has_purchased: bool
    fan_club_only: bool
    label_text: str
    label_color: str
    video_ready: bool
    fan_club_unlock: bool


class SocialMedia(BaseModel):
    id: int
    title_name: str
    image_url: str
    link: str
    popup_link: bool
    tokens: int
    purchased: bool
    label_text: str
    label_color: str


class StreamerBio(BaseModel):
    name_: str
    follower_count: int
    # location: str
    # real_name: str
    # body_decorations: str
    last_broadcast: str
    # smoke_drink: str
    # body_type: str
    # display_birthday: str
    # about_me: str
    # wish_list: str
    # time_since_last_broadcast: str
    # fan_club_cost: int
    # performer_has_fanclub: bool
    # fan_club_is_member: bool
    # fan_club_join_url: str
    # needs_supporter_to_pm: bool
    # interested_in: list[str]
    display_age: int | None
    # sex: str
    # subgender: str
    room_status: str
    # photo_sets: list[PhotoSet]
    # social_medias: list[SocialMedia]
    # is_broadcaster_or_staff: bool


class RespNot200(BaseModel):
    name_: str
    status: int
    detail: str
    code: str
    ts_context: Any


class BioResults(BaseModel):
    success: list[StreamerBio]
    fail: list[RespNot200]


class PassNone(BaseModel):
    quit: list[str]


class ContactSheetModel(BaseModel):
    input_path: Path
    interval: int
    output_path: Path


class cb_tags(Enum):
    ANAL = auto()
    ASAIN = auto()
    BBW = auto()
    BIGBOOBS = auto()
    BIGTITS = auto()
    BIGPUSSYLIPS = auto()
    BIGCLIT = auto()
    CURVY = auto()
    FUCKMACHINE = auto()
    HAIRY = auto()
    JOI = auto()
    LATINA = auto()
    LESBIAN = auto()
    MATURE = auto()
    MILF = auto()
    MILK = auto()
    MISTRESS = auto()
    MUSCLE = auto()
    NEW = auto()
    NONE = ""
    PANTYHOSE = auto()
    PETITE = auto()
    PUFFNIPPLES = auto()
    REDHEAD = auto()
    SMALLTITS = auto()
    SQUIRT = auto()


class cb_param:
    COUPLES = "?genders=c"
    FEMALE = "?genders=f"
    NONE = "?"
    MALE = "?genders=m"
    TRANS = "?genders=t"
    TAG = cb_tags


class ChatSettings(BaseModel):
    font_size: str
    show_emoticons: bool
    emoticon_autocomplete_delay: int
    sort_users_key: str
    room_entry_for: str
    room_leave_for: str
    c2c_notify_limit: int
    silence_broadcasters: str
    allowed_chat: str
    collapse_notices: bool
    highest_token_color: str
    mod_expire: int
    max_pm_age: int
    font_family: str
    font_color: str
    tip_volume: int
    ignored_users: str


class SatisfactionScore(BaseModel):
    percent: Optional[int] = None
    up_votes: Optional[int] = None
    down_votes: Optional[int] = None
    max: Optional[int] = None


class Quality(BaseModel):
    quality: str
    rate: float
    stopped: bool


class ChatVideoContext(BaseModel):
    viewer_uid: Any
    is_age_verified: bool
    age: Any
    room_status: str
    num_viewers: int
    wschat_host: str
    viewer_username: str
    viewer_gender: str
    allow_anonymous_tipping: bool
    chat_username: str
    chat_password: str
    broadcaster_username: str
    room_pass: str
    last_pass: str
    chat_rules: str
    room_title: str
    room_uid: str
    broadcaster_uid: str
    broadcaster_gender: str
    apps_running: str
    hls_source: str
    cmaf_edge: bool
    dismissible_messages: list
    edge_auth: str
    is_widescreen: bool
    allow_private_shows: bool
    private_show_price: int
    private_min_minutes: int
    allow_show_recordings: bool
    spy_private_show_price: int
    private_show_id: str
    low_satisfaction_score: bool
    hidden_message: str
    following: bool
    follow_notification_frequency: str
    is_moderator: bool
    chat_settings: ChatSettings
    broadcaster_on_new_chat: bool
    token_balance: int
    is_supporter: bool
    needs_supporter_to_pm: bool
    server_name: str
    num_followed: int
    num_followed_online: int
    has_studio: bool
    is_mobile: bool
    ignored_emoticons: list
    tfa_enabled: bool
    satisfaction_score: Optional[SatisfactionScore] = None
    hide_satisfaction_score: bool
    tips_in_past_24_hours: int
    last_vote_in_past_24_hours: Any
    last_vote_in_past_90_days_down: bool
    show_mobile_site_banner_link: bool
    exploring_hashtag: str
    source_name: str
    performer_has_fanclub: bool
    opt_out: bool
    fan_club_is_member: bool
    asp_auth_url: str
    browser_id: str
    edge_region: str
    userlist_color: str
    active_password: bool
    summary_card_image: str
    fan_club_paid_with_tokens: bool
    fan_club_spy_private_show_price: Any
    premium_private_price: int
    premium_private_min_minutes: int
    premium_show_running: bool
    quality: Quality
    code: Optional[int]


class DataFFmpeg(BaseModel):
    """Data for capturing live stream"""

    name_: str
    url_: str
    file_: Path
    # parameters require for ffmpeg capture
    args: list


class StreamerWithPid(BaseModel):
    pid: int
    name_: str


class FailVideoContext(BaseModel):
    status: int
    detail: str
    code: str
    ts_context: str | None
    name_: str
