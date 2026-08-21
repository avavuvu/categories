from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

import yaml

import csv_columns  # noqa: F401
import dictionary  # noqa: F401
import json_array  # noqa: F401
import oscars  # noqa: F401
import world_cities  # noqa: F401
from registry import PARSERS

SCRAPER_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SCRAPER_DIR / "output"
CONFIG_PATH = Path(__file__).parent / "datasets.yaml"


def normalize_value(value: str) -> str:
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"\[[^\]]*\]", "", value)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def normalize_row(row: dict) -> list[dict]:
    expanded = [{}]
    for key, value in row.items():
        parts = [normalize_value(part) for part in str(value).split("/")]
        parts = [part for part in parts if part] or [""]
        expanded = [{**base, key: part} for base in expanded for part in parts]
    return expanded


def normalize_rows(rows: list[dict]) -> list[dict]:
    results = []
    for row in rows:
        results.extend(normalize_row(row))
    return results


def load_config() -> list[dict]:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("datasets", [])


def save_table(table_name: str, rows: list[dict]) -> None:
    if not rows:
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{table_name}.csv"
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(table_name: str | None = None) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}

    for entry in load_config():
        name = entry["table"]
        if table_name is not None and name != table_name:
            continue

        parser = PARSERS.get(entry["type"])
        if parser is None:
            print(f"skip: no parser registered for type '{entry['type']}'")
            continue

        rows = normalize_rows(parser(entry))
        save_table(name, rows)
        results[name] = rows

    return results


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else None
    output = run(target)
    for table, rows in output.items():
        print(f"{table}: {len(rows)} rows")
