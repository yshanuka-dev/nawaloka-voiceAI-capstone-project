#!/usr/bin/env python3
"""
Clean Qdrant vector database - drops collections (nawaloka, cag_cache, cag_cache_local).
"""

import sys
from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from infrastructure.config import QDRANT_COLLECTION_NAME
from infrastructure.db.qdrant_client import get_qdrant_client
from infrastructure.log import setup_logging


def clean_qdrant():
    client = get_qdrant_client()
    try:
        collections_response = client.get_collections()
        existing_names = [c.name for c in collections_response.collections]
    except Exception as e:
        logger.error(f"Failed to fetch Qdrant collections: {e}")
        return 1

    targets = [QDRANT_COLLECTION_NAME, "cag_cache", "cag_cache_local"]
    deleted = []

    for name in targets:
        if name in existing_names:
            try:
                client.delete_collection(name)
                deleted.append(name)
            except Exception as e:
                logger.error(f"Failed to delete collection {name}: {e}")

    if deleted:
        logger.info(f"Successfully deleted Qdrant collections: {', '.join(deleted)}")
    else:
        logger.info("No matching Qdrant collections found to delete.")
    return 0


def main():
    setup_logging()
    return clean_qdrant()


if __name__ == "__main__":
    sys.exit(main())

