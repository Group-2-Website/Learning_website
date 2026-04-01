from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("learning.db")


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    try:
        tables = [
            name
            for (name,) in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        print("Tables:")
        for table in tables:
            print(f"- {table}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
