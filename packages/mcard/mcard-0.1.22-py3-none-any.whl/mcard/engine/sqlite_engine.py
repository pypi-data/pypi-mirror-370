import sqlite3
from typing import Optional, Union
import logging
import os
from mcard.model.card import MCard, MCardFromData
from mcard.model.pagination import Page
from mcard.engine.base import StorageEngine, DatabaseConnection
from mcard.config.config_constants import DEFAULT_PAGE_SIZE, MCARD_TABLE_SCHEMA, TRIGGERS

logger = logging.getLogger(__name__)

class SQLiteConnection(DatabaseConnection):
    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)  # Ensure it's an absolute path
        self.conn: Optional[sqlite3.Connection] = None
        self.setup_database()  # Call the setup method during initialization
        
    def setup_database(self):
        """Check if the database file exists; if not, create it."""
        try:
            # Resolve the absolute path for the database
            if not os.path.isabs(self.db_path):
                # Get the absolute path of the project's base directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                self.db_path = os.path.normpath(os.path.join(base_dir, self.db_path))
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to the database (creates the file if it doesn't exist)
            self.conn = sqlite3.connect(self.db_path)
            
            # Check if the card table exists
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='card'
            """)
            
            # Only create tables if they don't exist
            if not cursor.fetchone():
                logger.debug(f"Creating new database schema at {self.db_path}")
                from mcard.model.schema import CARD_TABLE_SCHEMA
                cursor.execute(CARD_TABLE_SCHEMA)
                self.conn.commit()
            else:
                logger.debug(f"Using existing database at {self.db_path}")
                
        except PermissionError as e:
            logger.error(f"Permission error: {e}")
            logger.error(f"Unable to access or create database at {self.db_path}")
            raise
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error setting up database: {e}")
            raise
        
    def connect(self) -> None:
        logger.debug(f"Connecting to database at {self.db_path}")
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            logger.debug(f"Connection established to {self.db_path}")
            logger.debug(f"Database connection details: {self.conn}")
            # Check if the database is empty and initialize schema if necessary
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if not tables:
                # Drop existing tables and triggers
                self.conn.execute("DROP TABLE IF EXISTS card")
                self.conn.execute("DROP TABLE IF EXISTS documents")
                for table_name, schema in MCARD_TABLE_SCHEMA.items():
                    logging.info(f"Executing SQL: {schema}")
                    self.conn.execute(schema)
                self.conn.commit()  # Ensure the schema is committed
                logger.debug("Database schema created successfully")
                for trigger in TRIGGERS:
                    logging.info(f"Executing SQL: {trigger}")
                    self.conn.execute(trigger)
                    self.conn.commit()  # Ensure the triggers are committed
        except sqlite3.Error as e:
            logger.error(f"Database error connecting to {self.db_path}: {e}")
            raise
        
    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def commit(self) -> None:
        if self.conn:
            self.conn.commit()
            
    def rollback(self) -> None:
        if self.conn:
            self.conn.rollback()

class SQLiteEngine(StorageEngine):
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection
        self.connection.connect()
        
    def __del__(self):
        self.connection.disconnect()
        
    def add(self, card: MCard) -> str:
        hash_value = str(card.hash)
        try:
            cursor = self.connection.conn.cursor()
            # Ensure content is bytes
            content_bytes = card.content if isinstance(card.content, bytes) else card.content.encode('utf-8')
            cursor.execute(
                "INSERT INTO card (hash, content, g_time) VALUES (?, ?, ?)",
                (hash_value, content_bytes, str(card.g_time))
            )
            self.connection.commit()
            logger.debug(f"Added card with hash {hash_value}")
            return hash_value
        except sqlite3.IntegrityError:
            raise ValueError(f"Card with hash {hash_value} and {str(card.g_time)} already exists, \n Content: {card.content[:20]}")


    def get(self, hash_value: str) -> Optional[MCard]:
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT content, g_time, hash FROM card WHERE hash = ?", (str(hash_value),))
        row = cursor.fetchone()
        
        if not row:
            return None
            
        content, g_time, hash = row
        # Make sure content is bytes
        if not isinstance(content, bytes):
            logger.warning(f"Content from database is not bytes but {type(content)}: {content[:20]}...")
            content_bytes = content.encode('utf-8') if isinstance(content, str) else bytes(content)
        else:
            content_bytes = content
            
        card = MCardFromData(content_bytes, hash, g_time) 
        return card
    
    def delete(self, hash_value: str) -> bool:
        cursor = self.connection.conn.cursor()
        cursor.execute("DELETE FROM card WHERE hash = ?", (str(hash_value),))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_page(self, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Get a page of cards from the database.
        
        This is a convenience method that calls get_cards_by_page() with the same arguments.
        It's maintained for backward compatibility.
        
        Args:
            page_number: The page number (1-based).
            page_size: Number of items per page.
            
        Returns:
            A Page object containing the requested cards.
            
        Raises:
            ValueError: If page_number < 1 or page_size < 1
        """
        return self.get_cards_by_page(page_number, page_size)
    
    
    
    def search_by_string(self, search_string: str, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Search for cards by string in content, hash, or g_time"""
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")

        offset = (page_number - 1) * page_size
        cursor = self.connection.conn.cursor()

        # Get total count of matching items
        cursor.execute("""
            SELECT COUNT(*) FROM card 
            WHERE hash LIKE ? OR g_time LIKE ? OR content LIKE ?
        """, (f"%{search_string}%", f"%{search_string}%", f"%{search_string}%"))
        total_items = cursor.fetchone()[0]

        # Get the actual items for the current page
        cursor.execute("""
            SELECT content, g_time, hash FROM card 
            WHERE hash LIKE ? OR g_time LIKE ? OR content LIKE ?
            ORDER BY g_time DESC LIMIT ? OFFSET ?
        """, (f"%{search_string}%", f"%{search_string}%", f"%{search_string}%", page_size, offset))

        items = []
        for row in cursor.fetchall():
            content, g_time, hash = row  # Assuming the row contains these values
            # Make sure content is bytes
            if not isinstance(content, bytes):
                logger.warning(f"Content from database is not bytes but {type(content)}: {content[:20]}...")
                content_bytes = content.encode('utf-8') if isinstance(content, str) else bytes(content)
            else:
                content_bytes = content
                
            card = MCardFromData(content_bytes, hash, g_time) 
            items.append(card)

        has_next = total_items > (page_number * page_size)
        has_previous = page_number > 1

        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous, total_pages=(total_items + page_size - 1) // page_size if page_size > 0 else 0
        )

    def search_by_content(self, search_string: Union[str, bytes], page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Search for cards by string or binary pattern in content.
        
        Args:
            search_string: The string or binary pattern to search for
            page_number: The page number (1-based)
            page_size: Number of items per page
            
        Returns:
            A Page object containing the matching cards
        """
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")
            
        if not search_string:
            raise ValueError("Search string cannot be empty")

        offset = (page_number - 1) * page_size
        cursor = self.connection.conn.cursor()

        # Convert search string to bytes if it's a string
        if isinstance(search_string, str):
            search_bytes = search_string.encode('utf-8')
        else:
            search_bytes = search_string
            
        # For binary search, we need to use the INSTR function to find the pattern
        cursor.execute("""
            SELECT COUNT(*) FROM card 
            WHERE INSTR(content, ?) > 0
        """, (search_bytes,))
        total_items = cursor.fetchone()[0]

        # Get the actual items for the current page
        cursor.execute("""
            SELECT content, g_time, hash FROM card 
            WHERE INSTR(content, ?) > 0
            ORDER BY g_time DESC
            LIMIT ? OFFSET ?
        """, (search_bytes, page_size, offset))

        items = []
        for row in cursor.fetchall():
            content, g_time, hash = row  # Assuming the row contains these values
            content_bytes = content if isinstance(content, bytes) else content.encode('utf-8')
            card = MCardFromData(content_bytes, hash, g_time) 
            items.append(card)

        has_next = total_items > (page_number * page_size)
        has_previous = page_number > 1

        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous, total_pages=(total_items + page_size - 1) // page_size if page_size > 0 else 0
        )

    def clear(self) -> None:
        cursor = self.connection.conn.cursor()
        cursor.execute("DELETE FROM card")
        self.connection.commit()
    
    def count(self) -> int:
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM card")
        return cursor.fetchone()[0]

    def get_all_cards(self) -> Page:
        """Get all cards from the database in a single page.
        
        Returns:
            A Page object containing all cards.
        """
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT content, hash, g_time FROM card")
        rows = cursor.fetchall()
        
        items = []
        for content, hash, g_time in rows:
            content_bytes = content if isinstance(content, bytes) else content.encode('utf-8')
            card = MCardFromData(content_bytes, hash, g_time)
            items.append(card)
            
        # Return a single page with all items
        return Page(
            items=items,
            total_items=len(items),
            page_number=1,
            page_size=len(items) if items else 1,
            has_next=False,
            has_previous=False,
            total_pages=1
        )
        
    def get_cards_by_page(self, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Get a page of cards from the database.
        
        Args:
            page_number: The page number (1-based).
            page_size: Number of items per page.
            
        Returns:
            A Page object containing the requested cards.
            
        Raises:
            ValueError: If page_number < 1 or page_size < 1
        """
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")
            
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM card")
        total_items = cursor.fetchone()[0]
        
        offset = (page_number - 1) * page_size
        cursor.execute(
            "SELECT content, g_time, hash FROM card ORDER BY g_time DESC LIMIT ? OFFSET ?",
            (page_size, offset)
        )
        
        items = []
        for row in cursor.fetchall():
            content, g_time, hash = row
            content_bytes = content if isinstance(content, bytes) else content.encode('utf-8')
            card = MCardFromData(content_bytes, hash, g_time)
            items.append(card)
                
        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=offset + len(items) < total_items,
            has_previous=page_number > 1,
            total_pages=(total_items + page_size - 1) // page_size if page_size > 0 else 0
        )
