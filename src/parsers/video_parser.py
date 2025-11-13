from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from .helpers import normalize_region_code, safe_int

@dataclass
class AuthorInfo:
    uid: str
    unique_id: str
    nickname: str

@dataclass
class MusicInfo:
    id: Optional[str]
    title: Optional[str]
    author: Optional[str]

@dataclass
class VideoStats:
    play_count: int
    digg_count: int
    comment_count: int
    share_count: int
    collect_count: int

@dataclass
class VideoRecord:
    aweme_id: str
    region: Optional[str]
    desc: str
    author: AuthorInfo
    music: Optional[MusicInfo]
    statistics: VideoStats
    share_url: Optional[str]
    duration: Optional[int]

def _parse_author(raw: Dict[str, Any]) -> AuthorInfo:
    return AuthorInfo(
        uid=str(raw.get("uid", "")),
        unique_id=str(raw.get("unique_id", "")),
        nickname=str(raw.get("nickname", "")),
    )

def _parse_music(raw: Dict[str, Any]) -> Optional[MusicInfo]:
    if not raw:
        return None
    return MusicInfo(
        id=str(raw.get("id")) if raw.get("id") is not None else None,
        title=str(raw.get("title")) if raw.get("title") is not None else None,
        author=str(raw.get("author")) if raw.get("author") is not None else None,
    )

def _parse_statistics(raw: Dict[str, Any]) -> VideoStats:
    return VideoStats(
        play_count=safe_int(raw.get("play_count")),
        digg_count=safe_int(raw.get("digg_count")),
        comment_count=safe_int(raw.get("comment_count")),
        share_count=safe_int(raw.get("share_count")),
        collect_count=safe_int(raw.get("collect_count")),
    )

def _extract_share_url(raw: Dict[str, Any]) -> Optional[str]:
    share_info = raw.get("share_info") or {}
    return share_info.get("share_url")

def _extract_duration(raw: Dict[str, Any]) -> Optional[int]:
    video = raw.get("video") or {}
    return safe_int(video.get("duration")) if "duration" in video else None

def parse_video(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a raw TikTok video object into a normalized, flat dict suitable for analytics.
    """
    author_raw = raw.get("author") or {}
    music_raw = raw.get("music") or raw.get("added_sound_music_info") or {}
    stats_raw = raw.get("statistics") or {}

    record = VideoRecord(
        aweme_id=str(raw.get("aweme_id", "")),
        region=normalize_region_code(raw.get("region")),
        desc=str(raw.get("desc", "")),
        author=_parse_author(author_raw),
        music=_parse_music(music_raw),
        statistics=_parse_statistics(stats_raw),
        share_url=_extract_share_url(raw),
        duration=_extract_duration(raw),
    )

    # Flatten nested dataclasses into a single dict structure
    base = asdict(record)
    base["author_uid"] = base.pop("author")["uid"]
    base["author_unique_id"] = base.pop("author")["unique_id"]
    base["author_nickname"] = base.pop("author")["nickname"]

    music = base.pop("music", None)
    if music:
        base["music_id"] = music.get("id")
        base["music_title"] = music.get("title")
        base["music_author"] = music.get("author")
    else:
        base["music_id"] = None
        base["music_title"] = None
        base["music_author"] = None

    stats = base.pop("statistics")
    for key, value in stats.items():
        base[f"stats_{key}"] = value

    return base