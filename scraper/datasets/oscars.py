import csv
from pathlib import Path

from registry import register

SCRAPER_DIR = Path(__file__).parent.parent


@register("oscars")
def oscars(entry: dict) -> list[dict]:
    path = SCRAPER_DIR / entry["source"]
    delimiter = entry.get("delimiter", ",")

    has_won: dict[str, bool] = {}
    with path.open(encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            won = (row.get("Winner") or "").strip() == "True"
            for film in (row.get("Film") or "").split("|"):
                film = film.strip()
                if not film:
                    continue
                has_won[film] = has_won.get(film, False) or won

    return [{"name": film, "has_won": won} for film, won in has_won.items()]
