from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("learning.db")


def list_tables(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return [name for (name,) in rows]


def print_table_preview(connection: sqlite3.Connection, table_name: str, limit: int = 5) -> None:
    columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table_name}")').fetchall()]
    print(f"TABLE: {table_name}")
    print("COLUMNS:", columns)
    rows = connection.execute(f'SELECT * FROM "{table_name}" LIMIT {limit}').fetchall()
    if not rows:
        print("ROWS: <empty>")
    else:
        print("ROWS:")
        for row in rows:
            print(row)
    print()


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    try:
        tables = list_tables(connection)
        print("TABLES:")
        for table in tables:
            print(f"- {table}")
        print()

        for table in tables:
            print_table_preview(connection, table)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
