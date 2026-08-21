import csv
from pathlib import Path

from registry import register

SCRAPER_DIR = Path(__file__).parent.parent


@register("csv_columns")
def csv_columns(entry: dict) -> list[dict]:
    path = SCRAPER_DIR / entry["source"]
    delimiter = entry.get("delimiter", ",")
    skip_rows = entry.get("skip_rows", 0)
    columns = entry["columns"]

    with path.open(encoding="utf-8", errors="replace") as f:
        for _ in range(skip_rows):
            next(f)
        reader = csv.DictReader(f, delimiter=delimiter)
        return [
            {out_name: row[col] for col, out_name in columns.items()} for row in reader
        ]
