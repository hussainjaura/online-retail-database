"""Rebuild database/online_retail.db from sql/schema.sql and sql/seed.sql.

Usage (from the project root):
    python scripts/rebuild_db.py
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "database" / "online_retail.db"
SQL_DIR = ROOT / "sql"


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    for name in ("schema.sql", "seed.sql"):
        conn.executescript((SQL_DIR / name).read_text(encoding="utf-8"))
        print(f"ran {name}")
    conn.commit()

    for table in ("Suppliers", "Products", "Customers", "Orders", "OrderItems", "Inventory"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<11} {count} rows")
    conn.close()
    print(f"database rebuilt at {DB_PATH}")


if __name__ == "__main__":
    main()
