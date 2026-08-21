from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from typing import Callable

import requests
import yaml
from bs4 import BeautifulSoup

CACHE_DIR = Path(__file__).parent / "cache"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
CONFIG_PATH = Path(__file__).parent / "wikipedia_tables.yaml"
USER_AGENT = "scattergories-scraper/0.1 (personal project)"

PARSERS: dict[str, Callable[[BeautifulSoup, dict], list[dict]]] = {}


def register(type_name: str):
    def wrapper(func: Callable[[BeautifulSoup, dict], list[dict]]):
        PARSERS[type_name] = func
        return func

    return wrapper


@register("simple_table")
def simple_table(soup: BeautifulSoup, entry: dict) -> list[dict]:
    tables = soup.select("table.wikitable")
    table = tables[entry["id"]]
    rows = table.find_all("tr")

    headers = [cell.get_text(strip=True) for cell in rows[0].find_all(["th", "td"])]
    cols = entry["cols"]
    source_cols = list(cols.keys())
    indexes = [headers.index(col) for col in source_cols]

    results = []
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        results.append(
            {cols[col]: cells[i].get_text(strip=True) for col, i in zip(source_cols, indexes)}
        )
    return results


def letter_sections(soup: BeautifulSoup) -> list:
    sections = []

    for section in soup.find_all("section"):
        label = section.get("aria-labelledby", "")

        if label in ["See_also", "Notes", "External_links", "References"]:
            print(label)

        if len(label) != 0 and label not in ["See_also", "Notes", "External_links", "References", "Culinary_herbs_and_spices_by_country,_region_and_culture"]:
            sections.append(section)

    return sections


@register("alphabetical_table")
def alphabetical_table(soup: BeautifulSoup, entry: dict) -> list[dict]:
    cols = entry["cols"]
    source_cols = list(cols.keys())
    results = []

    for section in letter_sections(soup):
        table = section.find("table")
        if table is None:
            continue

        rows = table.find_all("tr")

        if entry.get("number_index"):
            indexes = source_cols
        else:
            headers = [cell.get_text(strip=True) for cell in rows[0].find_all(["th", "td"])]
            indexes = [headers.index(col) for col in source_cols]

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            results.append(
                {cols[col]: cells[i].get_text(strip=True) for col, i in zip(source_cols, indexes)}
            )

    return results


def li_own_text(li) -> str:
    parts = []
    for child in li.children:
        if getattr(child, "name", None) == "ul":
            break
        parts.append(child.get_text() if hasattr(child, "get_text") else str(child))
    return "".join(parts).strip()


@register("alphabetical_list")
def alphabetical_list(soup: BeautifulSoup, entry: dict) -> list[dict]:
    results = []
    for section in letter_sections(soup):
        for li in section.find_all("li"):
            text = li_own_text(li)
            if text:
                results.append({"name": text})
    return results


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


def fetch_html(table_name: str, url: str, refresh: bool = False) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{table_name}.html"

    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding="utf-8")

    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    cache_path.write_text(response.text, encoding="utf-8")
    return response.text


def save_table(table_name: str, rows: list[dict]) -> None:
    if not rows:
        return
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{table_name}.csv"
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_config() -> list[dict]:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("wikipedia_tables", [])


def run(table_name: str | None = None, refresh: bool = False) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}

    for entry in load_config():
        name = entry["table"]
        if table_name is not None and name != table_name:
            continue

        parser = PARSERS.get(entry["type"])
        if parser is None:
            print(f"skip: no parser registered for type '{entry['type']}'")
            continue

        html = fetch_html(name, entry["url"], refresh=refresh)
        soup = BeautifulSoup(html, "html.parser")
        rows = normalize_rows(parser(soup, entry))
        save_table(name, rows)
        results[name] = rows

    return results


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else None
    output = run(target)
    for table, rows in output.items():
        print(f"{table}: {len(rows)} rows")
