from __future__ import annotations

import logging
from typing import Any, Dict, List

from config import Config
from client.tiktok_api_client import TikTokApiClient

logger = logging.getLogger(__name__)

def run(config: Config, client: TikTokApiClient) -> List[Dict[str, Any]]:
    if not config.hashtag_url:
        raise ValueError("HASHTAG mode requires `hashtag_url` to be set")

    logger.info("Executing HASHTAG mode with url='%s'", config.hashtag_url)
    items = client.fetch_hashtag(
        hashtag_url=config.hashtag_url,
        max_items=config.max_items,
        is_unlimited=config.is_unlimited,
    )
    return items