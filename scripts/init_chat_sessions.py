"""
Apply the ``chat_sessions`` DDL (sql/07_chat_sessions.sql) against the
configured Supabase Postgres. Idempotent — uses ``CREATE TABLE IF NOT
EXISTS`` so re-running is safe.

Usage:
    uv run python scripts/init_chat_sessions.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv(".env")

from sqlalchemy import text

from infrastructure.db import get_sql_engine


SQL_FILE = Path(__file__).resolve().parent.parent / "sql" / "07_chat_sessions.sql"


def main() -> None:
    ddl = SQL_FILE.read_text(encoding="utf-8")
    engine = get_sql_engine()

    print(f"Applying {SQL_FILE.name}...")

    # Strip line-comments first, then split on semicolons.
    cleaned_lines = [
        line for line in ddl.splitlines()
        if not line.lstrip().startswith("--")
    ]
    cleaned = "\n".join(cleaned_lines)

    with engine.begin() as conn:
        for stmt in [s.strip() for s in cleaned.split(";") if s.strip()]:
            conn.execute(text(stmt))

    # Sanity check
    with engine.connect() as conn:
        n = conn.execute(text("SELECT count(*) FROM chat_sessions")).scalar()
    print(f"[SUCCESS] chat_sessions table ready ({n} existing row(s)).")


if __name__ == "__main__":
    main()
