from pathlib import Path

from registry import register

SCRAPER_DIR = Path(__file__).parent.parent

VOWELS = set("aeiou")


@register("dictionary")
def dictionary(entry: dict) -> list[dict]:
    path = SCRAPER_DIR / entry["source"]
    results = []

    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            word = line.strip()
            if not word:
                continue

            letters = [c for c in word if c.isalpha()]
            unique_letters = set(letters)

            results.append(
                {
                    "name": word,
                    "length": len(word),
                    "ends_in_n": word.endswith("n"),
                    "contains_ing_not_ending_in_ing": "ing" in word and not word.endswith("ing"),
                    "has_double_letter": any(a == b for a, b in zip(word, word[1:])),
                    "is_palindrome": word == word[::-1],
                    "contains_q": "q" in word,
                }
            )

    return results
