import json
import sqlite3
from pathlib import Path

import pandas as pd
import yaml

SCRAPER_DIR = Path(__file__).parent
REPO_DIR = SCRAPER_DIR.parent
CATEGORIES_YAML = SCRAPER_DIR / "categories.yaml"
CATEGORIES_JSON = REPO_DIR / "panettone" / "src" / "lib" / "assets" / "categories.json"
OUTPUT_DIR = SCRAPER_DIR / "output"

ALLOWED_LETTERS = [c for c in "abcdefghijklmnopqrstuvwxyz" if c not in "quvxyz"]


def load_table(table: str) -> pd.DataFrame | None:
    path = OUTPUT_DIR / f"{table}.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


def valid_letters_for(table: str, query: str | None) -> list[str] | None:
    df = load_table(table)
    if df is None:
        return None

    conn = sqlite3.connect(":memory:")
    df.to_sql(table, conn, index=False)

    sql = f"SELECT DISTINCT LOWER(SUBSTR(name, 1, 1)) AS letter FROM {table}"
    if query:
        sql += f" WHERE {query}"

    try:
        cursor = conn.execute(sql)
        letters = {row[0] for row in cursor.fetchall() if row[0]}
    except sqlite3.OperationalError as e:
        print(f"query failed for table '{table}': {e}")
        return []
    finally:
        conn.close()

    return sorted(letter for letter in letters if letter in ALLOWED_LETTERS)


def build_categories() -> list[dict]:
    with CATEGORIES_YAML.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    categories = []
    for entry in data["categories"]:
        table = entry["table"]
        query = entry.get("query")
        letters = valid_letters_for(table, query)

        if letters is None:
            print(f"skip: no data file for table '{table}'")
            continue

        categories.append({**entry, "valid_letters": letters})

    return categories


def run() -> None:
    categories = build_categories()
    CATEGORIES_JSON.write_text(
        json.dumps({"categories": categories}, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(categories)} categories to {CATEGORIES_JSON}")


if __name__ == "__main__":
    run()
