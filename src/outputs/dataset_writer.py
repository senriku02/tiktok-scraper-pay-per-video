from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List

from parsers.video_parser import parse_video
from . import exporters

logger = logging.getLogger(__name__)

class DatasetWriter:
    """
    Write normalized video records to disk.

    For simplicity the primary format is a JSON array of normalized video records.
    Additional exporters (CSV, NDJSON) are available through `exporters`.
    """

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def write(self, items: Iterable[Dict[str, Any]]) -> None:
        normalized: List[Dict[str, Any]] = [parse_video(item) for item in items]
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.output_path.open("w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)

        logger.info("Wrote %d normalized records to %s", len(normalized), self.output_path)

    def export_csv(self, csv_path: Path) -> None:
        exporters.json_to_csv(self.output_path, csv_path)
        logger.info("Exported CSV dataset to %s", csv_path)