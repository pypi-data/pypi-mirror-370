from typing import Union
import json
import logging
from mcard.model.hash.validator import HashValidator, HashAlgorithm
from mcard.model.g_time import GTime


class MCard:
    """A simple data container for content with computed hash and timestamp."""

    def __init__(self, content: Union[str, bytes], hash_function: Union[str, HashAlgorithm] = HashAlgorithm.get_default()):
        """Initialize an MCard with content.
        
        Args:
            content: The content to store. Can be string or bytes.
            
        Raises:
            ValueError: If content is None or empty
        """
        if content is None:
            raise ValueError("Content cannot be None")

        if hash_function is None:
            raise ValueError("hash_function cannot be None")    
            
        if isinstance(content, (str, bytes)) and len(content) == 0:
            raise ValueError("Content cannot be empty")
            
        self.content = content if isinstance(content, bytes) else content.encode('utf-8')

        self.hash_function = HashAlgorithm(hash_function)

        # Compute and log the hash
        self.hash = HashValidator.compute_hash(content, self.hash_function)
        logging.debug(f"Computed hash for content: {self.hash}")

        self.g_time = GTime.stamp_now(self.hash_function)
        
        # Cache the content type
        from mcard.model.interpreter import ContentTypeInterpreter
        interpreter = ContentTypeInterpreter()
        self._content_type, _ = interpreter.detect_content_type(self.content)

    def get_content(self, as_text: bool = False) -> Union[bytes, str]:
        """Get the content.
        
        Args:
            as_text: If True, returns the content as a string (decoded from UTF-8).
                    If False (default), returns raw bytes.
                    
        Returns:
            The content as either bytes (default) or string, depending on the as_text parameter.
            
        Note:
            The default behavior returns bytes for backward compatibility with existing code.
            To get content as text, explicitly use get_content(as_text=True).
        """
        if as_text and isinstance(self.content, bytes):
            try:
                return self.content.decode('utf-8')
            except UnicodeDecodeError:
                # If content is not valid UTF-8, return as bytes
                return self.content
        return self.content

    def get_hash(self) -> str:
        """Compute and return the hash of the content."""
        return self.hash

    def get_g_time(self) -> str:
        """Get the current GTime string computed from the current time."""
        return self.g_time

    def get_content_type(self):
        """Get the content type of the MCard content."""
        return self._content_type

    def to_dict(self):
        """Convert the MCard to a dictionary.
        
        Returns:
            dict: A dictionary representation of the MCard with content as string.
        """
        content = self.get_content()
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                # If content is not valid UTF-8, keep as bytes
                pass
                
        return {
            'content': content,
            'hash': self.get_hash(),
            'g_time': self.get_g_time(),
            'content_type': self.get_content_type()
        }

class MCardFromData(MCard):
    """An MCard subclass that initializes from existing hash and g_time."""

    def __init__(self, content: bytes, hash_value: str, g_time_str: str):
        """Initialize an MCard from pre-existing hash and g_time.

        Args:
            content: The content (must be bytes).
            hash_value: The pre-computed hash value.
            g_time_str: The pre-existing g_time string.
            hash_function: The hash function used.
        
        Raises:
            TypeError: if content is not bytes
            ValudeError: If hash_value or g_time_str are None or empty.
        """
        if not isinstance(content, bytes):
            raise TypeError("Content must be bytes when initializing from existing data.")
            
        if not hash_value:
            raise ValueError("Hash value cannot be None or empty")
            
        if not g_time_str:
            raise ValueError("g_time string cannot be None or empty")

        self.content = content
        self.hash = hash_value
        self.g_time = g_time_str  # Directly assign the provided g_time string
        self.hash_function = GTime.get_hash_function(self.g_time)
        
        # Cache the content type
        from mcard.model.interpreter import ContentTypeInterpreter
        interpreter = ContentTypeInterpreter()
        self._content_type, _ = interpreter.detect_content_type(self.content)
        
        logging.debug(f"Initialized MCard from existing data: {self.hash}")
