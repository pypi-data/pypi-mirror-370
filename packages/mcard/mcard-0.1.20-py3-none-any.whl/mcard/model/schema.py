# mcard/model/schema.py
"""
Shared SQL schema definitions for MCard storage engines.
"""

CARD_TABLE_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS card (
        hash TEXT PRIMARY KEY,
        content TEXT NOT NULL,  -- Changed from BLOB to TEXT for human-readable storage
        g_time TEXT
    )
    """
)
