import os
from pathlib import Path

import psycopg

OUTPUT_DIR = Path(__file__).parent / "output"
SCHEMA_PATH = OUTPUT_DIR / "schema.sql"
EXTENSIONS_PATH = Path(__file__).parent / "extensions.sql"
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/scattergories"


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def load_schema(conn: psycopg.Connection) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.execute(sql)


def load_table(conn: psycopg.Connection, csv_path: Path) -> None:
    table = csv_path.stem
    with conn.cursor() as cur:
        with cur.copy(f"COPY {table} FROM STDIN WITH (FORMAT CSV, HEADER)") as copy:
            with csv_path.open("rb") as f:
                while chunk := f.read(8192):
                    copy.write(chunk)


def run() -> None:
    database_url = get_database_url()
    with psycopg.connect(database_url, autocommit=True) as conn:
        print("loading extensions...")
        conn.execute(EXTENSIONS_PATH.read_text(encoding="utf-8"))

        print("loading schema...")
        load_schema(conn)

        for csv_path in sorted(OUTPUT_DIR.glob("*.csv")):
            print(f"loading {csv_path.stem}...")
            load_table(conn, csv_path)

    print("done")


if __name__ == "__main__":
    run()
