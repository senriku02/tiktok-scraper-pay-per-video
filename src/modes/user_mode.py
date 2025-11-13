from __future__ import annotations

import logging
from typing import Any, Dict, List

from config import Config
from client.tiktok_api_client import TikTokApiClient

logger = logging.getLogger(__name__)

def run(config: Config, client: TikTokApiClient) -> List[Dict[str, Any]]:
    if not config.user_url:
        raise ValueError("USER mode requires `user_url` to be set")

    logger.info("Executing USER mode with url='%s'", config.user_url)
    items = client.fetch_user(
        user_url=config.user_url,
        max_items=config.max_items,
        is_unlimited=config.is_unlimited,
    )
    return items