from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent
RAW_CSV = BASE_DIR.parent / "raw" / "nature" / "merge_wikipages_wikidata_vars_B_FINAL_ORANGE.csv"
OUTPUT_DIR = BASE_DIR.parent / "output"

VISIBILITY_RANK_CUTOFF = 100_000

COLUMNS = [
    "name",
    "gender",
    "birth",
    "area1_of_rattachment",
    "area2_of_rattachment",
    "ranking_visib_5criteria",
]


def normalize_value(value: str) -> str:
    value = value.replace("_", " ")
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"\[[^\]]*\]", "", value)
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def clean_field(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text in ("", "Missing"):
        return ""
    return normalize_value(text)


def load_people() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV, usecols=COLUMNS, encoding_errors="replace")
    return df[df["ranking_visib_5criteria"] <= VISIBILITY_RANK_CUTOFF]


def build_people(df: pd.DataFrame) -> list[dict]:
    results = []
    for record in df.to_dict("records"):
        name = clean_field(record["name"])
        if not name:
            continue
        results.append(
            {
                "name": name,
                "is_female": str(clean_field(record["gender"]) == "female").lower(),
                "birth": int(record["birth"]) if pd.notna(record["birth"]) else None,
                "country1": clean_field(record["area1_of_rattachment"]),
                "country2": clean_field(record["area2_of_rattachment"]),
            }
        )
    return results


def save_table(name: str, rows: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{name}.csv"
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    df = load_people()
    rows = build_people(df)
    save_table("people", rows)
    print(f"people: {len(rows)} rows")


if __name__ == "__main__":
    run()
