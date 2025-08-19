"""Card collection module for MCard."""
import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional, TypeVar, List, Tuple, Callable, Any

from mcard.config.env_parameters import EnvParameters
from mcard.model.card import MCard
from mcard.model.event_producer import generate_collision_event
from mcard.model.pagination import Page
from mcard.engine.sqlite_engine import SQLiteEngine, SQLiteConnection
import sys

logger = logging.getLogger(__name__)

# Initialize environment parameters
env_params = EnvParameters()

# Database paths are imported from config_constants

# Type variable for generic type hints
T = TypeVar('T')

# Type variable for MCard instances
MCardT = TypeVar('MCardT', bound='MCard')

class CardCollection:
    """High-level interface for card collection operations
    
    This class provides a simple interface for working with MCard collections.
    It handles database initialization automatically if no engine is provided.
    """
    
    @staticmethod
    def print_all_cards(db_path: Optional[str] = None, page_size: int = 10) -> None:
        """Print all cards in the database in a formatted table.
        
        Args:
            db_path: Path to the database file. If None, uses the default from environment.
            page_size: Number of items to process per page (default: 10).
        """
        from mcard.file_utility import FileUtility  # Import here to avoid circular import
        try:
            # Use the default collection which is already initialized with the correct path
            collection = CardCollection() if not db_path else CardCollection(db_path=db_path)
            
            print("Fetching MCards from the database...")
            
            # Get database path for display
            db_path_str = 'default'
            if hasattr(collection, 'engine') and hasattr(collection.engine, 'db_path'):
                db_path_str = collection.engine.db_path
            
            # Print the header with database path
            print(f"\nDATABASE: {db_path_str}")
            print('=' * 100)
            print(f"{'Hash':<10} | {'Content':<40} | {'Created':<17} | {'Type':<15}")
            print('-' * 100)
            
            # Get all cards directly without pagination
            all_cards = collection.get_all_mcards_raw()
            total_cards = len(all_cards)
            
            # Print all cards
            for card in all_cards:
                # Process each card for display using FileUtility.process_mcard
                processed = FileUtility.process_mcard(card)
                if processed:
                    # Shorten hash to 7 characters with ellipsis
                    short_hash = f"{processed['hash'][:7]}..." if len(processed['hash']) > 7 else processed['hash']
                    # Shorten content preview to fit in 40 chars
                    preview = str(processed['content_preview'])[:37] + '...' if len(str(processed['content_preview'])) > 40 else str(processed['content_preview'])
                    # Shorten created_at and content_type if needed
                    created = str(processed['created_at'])[:14]
                    ctype = processed['content_type'].split('/')[-1][:12]  # Just take the subtype and limit length
                    print(f"{short_hash:<10} | {preview:<40} | {created:<17} | {ctype:<15}")
            
            # Print summary
            print(f"\n{'=' * 100}")
            print(f"Displaying all {total_cards} MCards in database")
            print(f"Database path: {db_path_str}")
            
            if total_cards == 0:
                print("No MCards found in the database.")
                
        except Exception as e:
            print(f"Error accessing the database: {e}", file=sys.stderr)
            sys.exit(1)
    
    def __init__(self, engine=None, engine_type: str = 'sqlite', db_path: str = None):
        """Initialize the card collection.
        
        Args:
            engine: Optional pre-configured database engine. If None, a new one will be created.
            engine_type: Type of database engine to use ('sqlite' is the only supported option).
            db_path: Path to the database file. If None, defaults to 'data/mcard.db'.
            
        Raises:
            ValueError: If the provided engine is not a valid database engine instance.
            ValueError: If db_path is not a string when engine is None.
        """
        # Input validation for engine
        if engine is not None:
            if not hasattr(engine, 'add') or not callable(engine.add):
                raise ValueError(
                    "Invalid engine provided. Engine must implement the StorageEngine interface "
                    "with required methods (add, get, delete, etc.)"
                )
            self.engine = engine
            logger.debug(f"Using provided engine, db path: {getattr(engine, 'db_path', 'unknown')}")
            return
            
        # If no engine provided, initialize a new one
        if db_path is not None and not isinstance(db_path, (str, Path)):
            raise ValueError(f"db_path must be a string or Path, got {type(db_path).__name__}")
            
        # Set up database path using environment variable or default if none provided
        if db_path is None:
            logger.debug("No db_path provided, getting from env_params")
            db_path = env_params.get_db_path()
        else:
            logger.debug(f"Using provided db_path: {db_path}")
        
        # Ensure the directory exists
        abs_db_path = os.path.abspath(str(db_path))
        db_dir = os.path.dirname(abs_db_path) or '.'
        logger.debug(f"Ensuring directory exists: {db_dir}")
        
        try:
            os.makedirs(db_dir, exist_ok=True)
            
            logger.debug(f"Initializing SQLite connection to: {abs_db_path}")
            connection = SQLiteConnection(abs_db_path)
            self.engine = SQLiteEngine(connection)
            logger.info(f"Initialized SQLite database at {abs_db_path}")
            logger.debug(f"Engine initialized with db_path: {getattr(self.engine, 'db_path', 'unknown')}")
            
        except (OSError, sqlite3.Error) as e:
            logger.error(f"Failed to initialize database at {abs_db_path}: {e}")
            raise ValueError(f"Failed to initialize database at {abs_db_path}: {e}") from e
        
    def add(self, card: MCard) -> str:
        """Add a card to the collection.
        
        In a content-addressable scheme, we first check if there's an existing card
        with the same hash. If found, we compare the content to determine if it's
        a duplicate (same content) or a collision (different content).
        
        Args:
            card: The MCard to add
            
        Returns:
            str: The hash of the card
            
        Raises:
            ValueError: If card is None
        """
        logger.debug(f"Attempting to add card with content: {card.content}")
        if card is None:
            raise ValueError("Card cannot be None")
        
        # Get the hash of the incoming card
        hash_value = card.hash
        
        # Check if a card with this hash already exists
        existing_card = self.get(hash_value)
        if existing_card:
            logger.debug(f"Card with hash {hash_value} already exists")
            # Compare content to determine if it's a duplicate or collision
            if existing_card.content == card.content:
                logger.debug(f"Duplicate card found with content: {card.content}")
                # Duplicate detected - create duplicate event and add directly via engine
                logger.info(f"Duplicate detected for hash {hash_value}; creating duplicate event.")
                from mcard.model.event_producer import generate_duplication_event
                duplicate_event_content_str = generate_duplication_event(card)
                duplicate_event_card = MCard(duplicate_event_content_str)
                try:
                    self.engine.add(duplicate_event_card)
                    return duplicate_event_card.hash
                except Exception:
                    # If event creation fails, return existing hash
                    logger.warning(f"Failed to create duplicate event for {hash_value}; returning existing hash.")
                    return hash_value
            else:
                logger.debug(f"Collision detected for card with content: {card.content}")
                # Create collision event card and store the new card with new hash function
                collision_event_content_str = generate_collision_event(card)
                contentDict = json.loads(collision_event_content_str)
                # Different content = collision, upgrade hash function to stronger level
                collision_content_card = MCard(card.content, contentDict["upgraded_function"])  # Use the new hash function (upgraded_function)
                collision_event_card = MCard(collision_event_content_str)
                logger.debug(f"Collision event: {collision_event_content_str}")
                # Add via engine directly to avoid recursive duplicate handling
                try:
                    self.engine.add(collision_event_card)
                except Exception as e:
                    logger.debug(f"Collision event already exists or failed to add: {e}")
                try:
                    self.engine.add(collision_content_card)
                except Exception as e:
                    logger.debug(f"Collision content already exists or failed to add: {e}")
                logger.debug(f"Added collision event card with hash: {collision_event_card.hash}")
                return collision_event_card.hash
        
        # No existing card with this hash or content, add the new card
        self.engine.add(card)
        logger.debug(f"Successfully added card with hash {hash_value}")
        return hash_value
        
    def get(self, hash_value: str) -> Optional[MCard]:
        """Retrieve a card by its hash"""
        return self.engine.get(hash_value)
        
    def delete(self, hash_value: str) -> bool:
        """Delete a card by its hash"""
        return self.engine.delete(hash_value)
        
    def get_page(self, page_number: int = 1, page_size: int = None) -> Page:
        """Get a page of cards"""
        if page_size is None:
            page_size = env_params.get_default_page_size()
        return self.engine.get_cards_by_page(page_number=page_number, page_size=page_size)
        
    def search_by_string(self, search_string: str, page_number: int = 1, page_size: int = None) -> Page:
        """Search for cards containing the given string.
        
        Args:
            search_string: The string to search for in card content
            page_number: The page number to return (1-based)
            page_size: Number of items per page (defaults to env setting)
            
        Returns:
            Page: A page of matching cards
        """
        if page_size is None:
            page_size = env_params.get_default_page_size()
        # Delegate the search to the engine's search_by_string method
        return self.engine.search_by_string(search_string, page_number, page_size)
        
    def search_by_hash(self, hash_value: str, page_number: int = 1, page_size: int = None) -> Page:
        """Search for cards by hash value
        
        Args:
            hash_value: The hash value to search for
            page_number: The page number to return (1-based)
            page_size: Number of items per page (defaults to env setting)
            
        Returns:
            Page: A page of matching cards
        """
        if page_size is None:
            page_size = env_params.get_default_page_size()
        if page_number < 1:
            raise ValueError("Page number must be greater than 0")
        if page_size < 1:
            raise ValueError("Page size must be greater than 0")
        
        # Get all cards and filter by hash
        all_cards_page = self.engine.get_all_cards()
        matching_cards = [card for card in all_cards_page.items if str(card.hash) == hash_value]
        
        # Calculate pagination
        total_items = len(matching_cards)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        items = matching_cards[start_idx:end_idx]
        
        # Create page object
        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=end_idx < total_items,
            has_previous=page_number > 1,
            total_pages=(total_items + page_size - 1) // page_size if page_size > 0 else 0
        )
        
    def search_by_content(self, search_string: str, page_number: int = 1, page_size: int = None) -> Page:
        """Search for cards by content string
        
        Args:
            search_string: The string to search for in card content
            page_number: The page number to return (1-based)
            page_size: Number of items per page (defaults to env setting)
            
        Returns:
            Page: A page of matching cards
        """
        if page_size is None:
            page_size = env_params.get_default_page_size()
        return self.engine.search_by_content(search_string, page_number, page_size)

        
    def clear(self) -> None:
        """Remove all cards"""
        self.engine.clear()
        
    def count(self) -> int:
        """Return total number of cards"""
        return self.engine.count()

    def get_all_mcards_raw(self) -> List[MCard]:
        """Retrieve all MCard objects directly from the database without pagination or callbacks.
        
        This method is more efficient than get_all_cards when you need all cards and don't need
        pagination or processing callbacks.
        
        Returns:
            list: A list of MCard objects
        """
        page = self.engine.get_all_cards()
        return page.items if page and hasattr(page, 'items') else []
        
    def get_all_cards(self, page_size: int = 10, process_callback: Optional[Callable[[MCard], Any]] = None) -> Tuple[List[MCard], int]:
        """Retrieve all cards from the database with pagination support.
    
        Args:
            page_size: Number of items per page. Defaults to 10.
            process_callback: Optional callback function to process each card.
                           Signature: (card) -> processed_card
                            
        Returns:
            tuple: (list of all cards, total count of cards)
        """
        all_cards = []
        page_number = 1
        total_cards = 0
        
        while True:
            # Get a page of cards
            page = self.get_mcards_at_page(page_number=page_number, page_size=page_size)
            
            # If no items on this page, we're done
            if not page or not page.items:
                break
                
            # Process cards if callback is provided
            processed_cards = [
                process_callback(card) if process_callback and callable(process_callback) else card
                for card in page.items 
                if card is not None
            ]
            all_cards.extend(processed_cards)
                
            # Update total cards count
            total_cards += len(page.items)
            
            # If there are no more pages, we're done
            if not page.has_next:
                break
                
            # Move to the next page
            page_number += 1
            
        return all_cards, total_cards

    def get_mcards_at_page(self, page_number: int = 1, page_size: int = 10) -> Page:
        """Get a single page of MCards.
        
        Args:
            page_number: Page number to retrieve (1-based)
            page_size: Number of items per page
            
        Returns:
            Page: A Page object containing the MCards for the requested page
            
        Raises:
            ValueError: If page_number < 1 or page_size < 1
        """
        return self.engine.get_cards_by_page(page_number=page_number, page_size=page_size)
        