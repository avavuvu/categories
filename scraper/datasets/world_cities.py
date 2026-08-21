import csv
from pathlib import Path

from country_continents import COUNTRY_TO_CONTINENT
from registry import register

SCRAPER_DIR = Path(__file__).parent.parent


@register("world_cities")
def world_cities(entry: dict) -> list[dict]:
    path = SCRAPER_DIR / entry["source"]
    population_min = entry.get("population_min", 0)

    seen_missing = set()
    results = []
    with path.open(encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            population_raw = row.get("population", "").strip()
            if not population_raw:
                continue
            try:
                population = float(population_raw)
            except ValueError:
                continue
            if population < population_min:
                continue

            country = row.get("country", "").strip()
            if country not in COUNTRY_TO_CONTINENT and country not in seen_missing:
                seen_missing.add(country)
                print(f"no continent mapping for: {country}")

            results.append(
                {
                    "name": row.get("city", ""),
                    "country": country,
                    "continent": COUNTRY_TO_CONTINENT.get(country, ""),
                    "population": int(population),
                }
            )

    return results
