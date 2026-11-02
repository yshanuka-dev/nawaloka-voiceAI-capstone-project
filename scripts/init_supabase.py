#!/usr/bin/env python3
"""
Initialize Supabase schema - creates all Memory + CRM tables + Chat Sessions.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from loguru import logger
from infrastructure.log import setup_logging
from infrastructure.db.supabase_client import init_supabase_schema
import init_chat_sessions


def main():
    setup_logging()
    try:
        init_supabase_schema()
        init_chat_sessions.main()
        return 0
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
