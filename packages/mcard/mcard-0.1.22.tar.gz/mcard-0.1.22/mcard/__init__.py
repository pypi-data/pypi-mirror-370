# MCard package initialization
__version__ = "0.1.22"

import os
from .config.logging_config import setup_logging, get_logger
from .model.card import MCard
from .model.card_collection import CardCollection
from .config.config_constants import DEFAULT_DB_PATH
from .engine.sqlite_engine import SQLiteConnection, SQLiteEngine
from .config.env_parameters import EnvParameters
from .file_utility import FileUtility

# Note: Do not initialize logging on import. Entry points should call
# mcard.config.logging_config.setup_logging() explicitly.

# Define the most commonly used classes in __all__
__all__ = [
    'MCard',
    'CardCollection',
    'SQLiteConnection',
    'SQLiteEngine',
    'EnvParameters',
    'FileUtility',
    'setup_logging',
    'get_logger',
    'default_collection'
]

# Get database path from environment or use default
db_path = os.environ.get('MCARD_DB_PATH')
if not db_path:
    # Create default data directory if it doesn't exist
    os.makedirs(os.path.dirname(DEFAULT_DB_PATH), exist_ok=True)
    db_path = DEFAULT_DB_PATH

# Create a default collection instance for quick access
default_collection = CardCollection(db_path=db_path)
