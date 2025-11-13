from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from parsers.helpers import normalize_region_code

logger = logging.getLogger(__name__)

class TikTokApiClient:
    """
    Local demo API client.

    This implementation does not perform real network scraping. Instead, it loads
    data from `data/sample_output.json` and simulates different modes by applying
    simple filters on the sample dataset. This keeps the project runnable out of
    the box while preserving realistic integration boundaries.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self._cache: Optional[List[Dict[str, Any]]] = None

    def _load_sample_data(self) -> List[Dict[str, Any]]:
        if self._cache is not None:
            return self._cache

        sample_path = self.project_root / "data" / "sample_output.json"
        if not sample_path.exists():
            logger.warning("Sample data file %s not found, returning empty dataset", sample_path)
            self._cache = []
            return self._cache

        try:
            with sample_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                logger.warning("Sample data is not a list; wrapping in list")
                data = [data]
            self._cache = data
            logger.debug("Loaded %d sample items from %s", len(self._cache), sample_path)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to load sample data: %s", exc)
            self._cache = []

        return self._cache

    # --- Public methods used by modes -------------------------------------------------

    def fetch_search(
        self, keyword: str, region: Optional[str], max_items: int, is_unlimited: bool
    ) -> List[Dict[str, Any]]:
        items = self._load_sample_data()
        region_norm = normalize_region_code(region) if region else None

        filtered: List[Dict[str, Any]] = []
        keyword_lower = keyword.lower()
        for item in items:
            desc = str(item.get("desc", "")).lower()
            if keyword_lower in desc:
                if region_norm and normalize_region_code(item.get("region")) != region_norm:
                    continue
                filtered.append(item)

        logger.info(
            "Search filter keyword=%s region=%s matched %d items",
            keyword,
            region_norm,
            len(filtered),
        )

        if is_unlimited:
            return filtered
        return filtered[:max_items]

    def fetch_trend(self, region: Optional[str], max_items: int, is_unlimited: bool) -> List[Dict[str, Any]]:
        items = self._load_sample_data()
        region_norm = normalize_region_code(region) if region else None

        if region_norm:
            items = [i for i in items if normalize_region_code(i.get("region")) == region_norm]
            logger.info("Trend filter region=%s matched %d items", region_norm, len(items))

        if not is_unlimited:
            items = items[:max_items]

        return items

    def fetch_hashtag(self, hashtag_url: str, max_items: int, is_unlimited: bool) -> List[Dict[str, Any]]:
        hashtag = self._extract_hashtag_from_url(hashtag_url)
        items = self._load_sample_data()
        hashtag_lower = hashtag.lower()

        filtered: List[Dict[str, Any]] = []
        for item in items:
            text_extra = item.get("text_extra") or []
            for entity in text_extra:
                if entity.get("type") == 1 and str(entity.get("hashtag_name", "")).lower() == hashtag_lower:
                    filtered.append(item)
                    break

        logger.info("Hashtag filter hashtag=%s matched %d items", hashtag, len(filtered))

        if is_unlimited:
            return filtered
        return filtered[:max_items]

    def fetch_user(self, user_url: str, max_items: int, is_unlimited: bool) -> List[Dict[str, Any]]:
        username = self._extract_username_from_url(user_url)
        items = self._load_sample_data()
        username_lower = username.lower()

        filtered: List[Dict[str, Any]] = []
        for item in items:
            author = item.get("author") or {}
            unique_id = str(author.get("unique_id", "")).lower()
            if unique_id == username_lower:
                filtered.append(item)

        logger.info("User filter username=%s matched %d items", username, len(filtered))

        if is_unlimited:
            return filtered
        return filtered[:max_items]

    def fetch_music(self, music_url: str, max_items: int, is_unlimited: bool) -> List[Dict[str, Any]]:
        """Simulate filtering videos by a music identifier in the URL."""
        music_token = self._extract_music_token_from_url(music_url)
        items = self._load_sample_data()
        token_lower = music_token.lower()

        filtered: List[Dict[str, Any]] = []
        for item in items:
            music = item.get("music") or {}
            music_id = str(music.get("id", "")).lower()
            if music_id and music_id == token_lower:
                filtered.append(item)

        logger.info("Music filter token=%s matched %d items", music_token, len(filtered))

        if is_unlimited:
            return filtered
        return filtered[:max_items]

    # --- Internal helpers -------------------------------------------------------------

    @staticmethod
    def _extract_hashtag_from_url(url: str) -> str:
        """
        Extract hashtag part from a TikTok hashtag URL.
        Example: https://www.tiktok.com/tag/cuocdoivandepsao -> cuocdoivandepsao
        """
        parts = url.rstrip("/").split("/")
        if parts:
            last = parts[-1]
            if last.startswith("tag/"):
                return last.split("tag/", 1)[1]
            return last.lstrip("#")
        return url

    @staticmethod
    def _extract_username_from_url(url: str) -> str:
        """
        Extract username from a TikTok profile URL.
        Example: https://www.tiktok.com/@vtvgiaitriofficial -> vtvgiaitriofficial
        """
        parts = url.rstrip("/").split("/")
        for part in reversed(parts):
            if part.startswith("@"):
                return part[1:]
        return url

    @staticmethod
    def _extract_music_token_from_url(url: str) -> str:
        """
        Extract a music token from a TikTok music URL.
        Example: https://www.tiktok.com/music/original-sound-123456 -> 123456
        """
        parts = url.rstrip("/").split("-")
        if parts:
            return parts[-1]
        return url