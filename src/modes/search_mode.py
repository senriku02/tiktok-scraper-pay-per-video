from __future__ import annotations

import logging
from typing import Any, Dict, List

from config import Config
from client.tiktok_api_client import TikTokApiClient

logger = logging.getLogger(__name__)

def run(config: Config, client: TikTokApiClient) -> List[Dict[str, Any]]:
    if not config.keyword:
        raise ValueError("SEARCH mode requires `keyword` to be set")

    logger.info("Executing SEARCH mode with keyword='%s'", config.keyword)
    items = client.fetch_search(
        keyword=config.keyword,
        region=config.region,
        max_items=config.max_items,
        is_unlimited=config.is_unlimited,
    )
    return items