import json
from pathlib import Path

from registry import register

SCRAPER_DIR = Path(__file__).parent.parent


@register("json_array")
def json_array(entry: dict) -> list[dict]:
    path = SCRAPER_DIR / entry["source"]
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    items = data if entry.get("flat") else data[entry["array"]]
    properties = entry["properties"]
    return [{prop: item.get(prop) for prop in properties} for item in items]
