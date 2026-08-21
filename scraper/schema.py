import csv
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
SCHEMA_PATH = OUTPUT_DIR / "schema.sql"


def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def infer_type(values: list[str]) -> str:
    present = [v for v in values if v != ""]
    if not present:
        return "TEXT"
    if all(v in ("true", "false") for v in present):
        return "BOOLEAN"
    if all(is_int(v) for v in present):
        return "INTEGER"
    if all(is_float(v) for v in present):
        return "DOUBLE PRECISION"
    return "TEXT"


def table_schema(path: Path) -> str:
    table = path.stem
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    columns = []
    for col in reader.fieldnames or []:
        values = [row[col] for row in rows]
        columns.append(f"    {col} {infer_type(values)}")

    body = ",\n".join(columns)
    return f"DROP TABLE IF EXISTS {table};\nCREATE TABLE {table} (\n{body}\n);"


def build_schema() -> str:
    statements = [table_schema(path) for path in sorted(OUTPUT_DIR.glob("*.csv"))]
    return "\n\n".join(statements)


def run() -> None:
    schema = build_schema()
    SCHEMA_PATH.write_text(schema + "\n", encoding="utf-8")
    print(f"wrote schema to {SCHEMA_PATH}")


if __name__ == "__main__":
    run()
