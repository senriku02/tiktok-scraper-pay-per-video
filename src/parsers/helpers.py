from __future__ import annotations

from typing import Any, Optional

def normalize_region_code(region: Optional[Any]) -> Optional[str]:
    if region is None:
        return None
    region_str = str(region).strip().upper()
    return region_str or None

def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default