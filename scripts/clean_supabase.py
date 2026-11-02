#!/usr/bin/env python3
"""
Clean Supabase database - removes rows from CRM and memory tables.
"""

import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from sqlalchemy import text
from infrastructure.db import get_session, get_sql_engine
from infrastructure.log import setup_logging

TABLES = [
    "bookings",
    "patients",
    "doctors",
    "specialties",
    "locations",
    "mem_facts",
    "mem_episodes",
    "mem_procedures",
    "st_turns",
]


def clean_supabase_data():
    """Truncate or delete all rows from Supabase tables."""
    session = get_session()
    engine = get_sql_engine()
    cleared = []

    try:
        # Check which tables exist in public schema
        with engine.connect() as conn:
            existing = conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname='public'"
            )).scalars().all()

        existing_set = set(existing)
        tables_to_clear = [t for t in TABLES if t in existing_set]

        if not tables_to_clear:
            logger.info("No matching tables found to clear.")
            return

        for table in tables_to_clear:
            session.execute(text(f"DELETE FROM {table}"))
            cleared.append(table)

        session.commit()
        logger.info(f"Successfully cleared {len(cleared)} tables in Supabase: {', '.join(cleared)}")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to clear Supabase data: {e}")
        raise
    finally:
        session.close()


def drop_supabase_tables():
    """Drop all tables (destructive)."""
    engine = get_sql_engine()
    try:
        with engine.connect() as conn:
            for table in reversed(TABLES):
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                conn.commit()
        logger.info(f"Successfully dropped tables in Supabase: {', '.join(TABLES)}")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Clean Supabase database tables")
    parser.add_argument("--drop", action="store_true", help="Drop tables completely instead of just deleting rows")
    args = parser.parse_args()

    try:
        if args.drop:
            drop_supabase_tables()
        else:
            clean_supabase_data()
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())

