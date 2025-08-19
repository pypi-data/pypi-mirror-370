"""
File utility functions for handling file operations in MCard.
"""
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TypeVar, TYPE_CHECKING

from mcard.model.interpreter import ContentTypeInterpreter
from mcard.model.card_collection import CardCollection

# Import MCard type for type hints
if TYPE_CHECKING:
    from mcard.model.mcard import MCard
else:
    MCard = TypeVar('MCard')  # For runtime type checking

# Set up logger
logger = logging.getLogger(__name__)

class FileUtility:
    """
    Internal utility class for file operations in MCard.
    This class is not meant to be used directly. Use the standalone functions instead.
    """
    
    def __init__(self, collection: CardCollection):
        """Initialize with a CardCollection for storing MCards."""
        self.collection = collection
    
    @staticmethod
    def process_mcard(mcard: MCard) -> Optional[Dict[str, Any]]:
        """Process a single MCard into a displayable format.
        
        This function takes an MCard object and converts it into a dictionary with
        display-friendly fields including a content preview and formatted timestamps.
        
        Args:
            mcard: An instance of MCard or MCardFromData.
            
        Returns:
            dict: A dictionary with processed card data for display, or None if mcard is None.
            The dictionary contains the following keys:
                - hash: The card's unique hash
                - content_type: The type of content in the card
                - created_at: Formatted creation timestamp
                - content_preview: A preview of the card's content (first 50 chars)
                - card_class: The class name of the card (for debugging)
        """
        if mcard is None:
            return None
        
        try:
            # Safely get attributes with defaults using appropriate getter methods
            card_hash = getattr(mcard, 'hash', 'N/A')
            content = getattr(mcard, 'content', None)
            # Use getter methods instead of direct attribute access
            content_type = mcard.get_content_type() if hasattr(mcard, 'get_content_type') else 'unknown'
            created_at = mcard.get_g_time() if hasattr(mcard, 'get_g_time') else None
            
            # Create a preview of the content
            content_str = str(content) if content is not None else ''
            content_preview = content_str[:50] + ('...' if len(content_str) > 50 else '')
            
            # Format the creation time
            created_at_str = str(created_at)[:19] if created_at is not None else 'N/A'
            
            # Get the class name for debugging
            card_class = mcard.__class__.__name__
            
            return {
                'hash': card_hash,
                'content_type': content_type,
                'created_at': created_at_str,
                'content_preview': content_preview,
                'card_class': card_class  # For debugging
            }
        except Exception as e:
            logger.error("Error processing card: %s", str(e))
            return None
    
    @staticmethod
    def _is_problematic_file(file_path: Path) -> bool:
        """
        Check if a file is likely to cause processing issues.
        
        This method distinguishes between:
        1. Truly problematic files (corrupted, binary with no structure, etc.)
        2. Legitimate files with long lines (minified JS/CSS, optimized files)
        
        Returns True only for files that are genuinely problematic.
        """
        try:
            file_size = file_path.stat().st_size
            file_extension = file_path.suffix.lower()
            
            # Skip extremely large files (>500MB) - likely media or database files
            if file_size > 500 * 1024 * 1024:
                logger.warning(f"Skipping extremely large file: {file_path} ({file_size} bytes)")
                return True
            
            # For small files, no need to check further
            if file_size <= 1024:
                return False
            
            # Known file types that commonly have long lines but are legitimate
            legitimate_long_line_extensions = {
                '.js', '.mjs', '.min.js', '.bundle.js',
                '.css', '.min.css',
                '.json', '.jsonl',
                '.xml', '.svg',
                '.html', '.htm',
                '.map',  # source maps
                '.wasm'  # WebAssembly text format
            }
            
            # If it's a known type that can have long lines, be more permissive
            is_known_type = file_extension in legitimate_long_line_extensions
            
            with open(file_path, 'rb') as f:
                # Sample from beginning, middle, and end for large files
                sample_size = min(32 * 1024, file_size)  # 32KB sample
                samples = []
                
                if file_size > 100 * 1024:  # For files > 100KB, check multiple positions
                    positions = [0, file_size // 2, max(0, file_size - sample_size)]
                else:
                    positions = [0]
                
                for pos in positions:
                    f.seek(pos)
                    sample = f.read(sample_size)
                    if sample:
                        samples.append(sample)
                
                for sample in samples:
                    # Check for binary content that's not structured
                    if FileUtility._is_unstructured_binary(sample):
                        logger.warning(f"Skipping unstructured binary file: {file_path}")
                        return True
                    
                    # Check for pathological line patterns
                    if FileUtility._has_pathological_lines(sample, is_known_type):
                        logger.warning(f"Skipping file with pathological line structure: {file_path}")
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking file {file_path}: {e}")
            return True  # Skip files we can't check
    
    @staticmethod
    def _is_unstructured_binary(sample: bytes) -> bool:
        """Check if sample appears to be unstructured binary data."""
        if len(sample) < 512:
            return False
        
        # Count null bytes and control characters
        null_count = sample.count(b'\x00')
        control_chars = sum(1 for b in sample if b < 32 and b not in (9, 10, 13))  # Exclude tab, LF, CR
        
        # If more than 10% null bytes or 20% control chars, likely binary
        null_ratio = null_count / len(sample)
        control_ratio = control_chars / len(sample)
        
        return null_ratio > 0.1 or control_ratio > 0.2
    
    @staticmethod
    def _has_pathological_lines(sample: bytes, is_known_type: bool) -> bool:
        """
        Check for pathological line patterns that indicate problematic files.
        
        Args:
            sample: Byte sample from the file
            is_known_type: Whether this is a known file type that can have long lines
        """
        # More lenient thresholds for known types
        max_line_length = 200000 if is_known_type else 100000  # 200KB vs 100KB
        max_avg_line_length = 50000 if is_known_type else 10000  # 50KB vs 10KB
        
        # Check if there are any newlines at all in a reasonable sample
        if b'\n' not in sample and b'\r' not in sample and len(sample) >= 16384:
            # No line breaks in 16KB+ suggests a single massive line
            # But be more permissive for known types
            if not is_known_type or len(sample) >= 64 * 1024:
                return True
        
        # Split on any line ending
        lines = sample.replace(b'\r\n', b'\n').replace(b'\r', b'\n').split(b'\n')
        
        if not lines:
            return False
        
        # Check for extremely long individual lines
        for line in lines:
            if len(line) > max_line_length:
                return True
        
        # Check average line length only if we have multiple lines
        if len(lines) > 1:
            avg_line_length = sum(len(line) for line in lines) / len(lines)
            if avg_line_length > max_avg_line_length:
                return True
        
        return False
    
    @staticmethod
    def _load_files(directory: Union[str, Path], recursive: bool = False) -> List[Path]:
        """
        Load all files from the specified directory.
        
        Args:
            directory: The directory to load files from (can be str or Path)
            recursive: If True, recursively load files from subdirectories
            
        Returns:
            A list of Path objects for all files in the directory
        """
        dir_path = Path(directory) if isinstance(directory, str) else directory
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory '{dir_path}' does not exist.")
            
        if recursive:
            all_files = [f for f in dir_path.rglob("*") if f.is_file()]
        else:
            all_files = [f for f in dir_path.glob("*") if f.is_file()]
        
        # Filter out problematic files
        safe_files = []
        for file_path in all_files:
            if not FileUtility._is_problematic_file(file_path):
                safe_files.append(file_path)
        
        logger.info(f"Found {len(all_files)} files, filtered to {len(safe_files)} safe files")
        return safe_files
    
    @staticmethod
    def _analyze_content(content: bytes) -> Dict[str, Any]:
        """Analyze content using ContentTypeInterpreter and return metadata."""
        mime_type, extension = ContentTypeInterpreter.detect_content_type(content)
        is_binary = ContentTypeInterpreter.is_binary_content(content)
        
        return {
            "mime_type": mime_type,
            "extension": extension,
            "is_binary": is_binary,
            "size": len(content)
        }
    
    @staticmethod
    def _read_file(file_path: Union[str, Path]) -> bytes:
        """
        Read file content with timeout protection and size limits.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as bytes
            
        Raises:
            TimeoutError: If reading takes too long
            IOError: If file cannot be read
        """
        import threading
        import time
        
        # Check file size first
        file_size = file_path.stat().st_size
        max_file_size = 50 * 1024 * 1024  # 50MB limit
        
        if file_size > max_file_size:
            raise IOError(f"File too large: {file_size} bytes (max {max_file_size})")
        
        # For very large single-line files, use a more aggressive timeout
        timeout_seconds = 5 if file_size > 50 * 1024 else 30  # 5 seconds for files > 50KB
        
        result = [None]
        exception = [None]
        
        def read_with_timeout():
            try:
                with open(file_path, 'rb') as file:
                    # For potentially problematic files, read in chunks with progress checking
                    if file_size > 50 * 1024:  # Files > 50KB
                        content = bytearray()
                        chunk_size = 8192
                        bytes_read = 0
                        start_time = time.time()
                        
                        while bytes_read < file_size:
                            if time.time() - start_time > timeout_seconds:
                                raise TimeoutError(f"Reading timeout exceeded for {file_path}")
                            
                            chunk = file.read(chunk_size)
                            if not chunk:
                                break
                            content.extend(chunk)
                            bytes_read += len(chunk)
                            
                            # Check for pathological content patterns during reading
                            if len(content) > 32768 and b'\n' not in content and b'\r' not in content:
                                raise IOError(f"File appears to be a single massive line: {file_path}")
                        
                        result[0] = bytes(content)
                    else:
                        result[0] = file.read()
            except Exception as e:
                exception[0] = e
        
        # Use threading for timeout since signal doesn't work well on all platforms
        thread = threading.Thread(target=read_with_timeout)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout_seconds)
        
        if thread.is_alive():
            # Thread is still running, reading is taking too long
            logger.warning(f"File reading timed out after {timeout_seconds}s: {file_path}")
            raise TimeoutError(f"File reading timed out for {file_path}")
        
        if exception[0]:
            logger.error(f"Error reading file {file_path}: {exception[0]}")
            raise exception[0]
        
        if result[0] is None:
            raise IOError(f"Failed to read file: {file_path}")
        
        return result[0]
    
    @classmethod
    def _process_file(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a file and return its metadata and content.
        
        For text files, ensures the content is properly decoded to UTF-8 when possible.
        """
        # Read file content as bytes
        content = cls._read_file(file_path)
        
        # Analyze the content to get MIME type and other metadata
        # For very large files or files with extremely long lines, use a sample
        content_sample = content
        if len(content) > 1024 * 1024:  # 1MB limit for content type detection
            content_sample = content[:1024 * 1024]
            logger.info(f"Using content sample for large file: {file_path}")
        
        analysis = cls._analyze_content(content_sample)
        mime_type = analysis["mime_type"]
        is_binary = analysis["is_binary"]
        
        # For text files, try to decode the content
        if not is_binary and mime_type.startswith('text/'):
            try:
                # Decode the content as UTF-8 for text files
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 fails, try with error replacement
                try:
                    content = content.decode('utf-8', errors='replace')
                except Exception as e:
                    logger.warning(f"Failed to decode content for {file_path} as UTF-8: {e}")
        
        return {
            "content": content,
            "filename": Path(file_path).name,
            "mime_type": mime_type,
            "extension": analysis["extension"],
            "is_binary": is_binary,
            "size": len(content)  # Use original content size, not sample
        }
        
    def _process_and_store_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Process a file, create an MCard, and store it in the collection."""
        from mcard import MCard
            
        try:
            logger.info(f"PROCESSING FILE: {file_path}")
            
            # Process the file
            logger.info(f"Reading file content: {file_path}")
            file_info = self._process_file(file_path)
            if not file_info:
                logger.warning(f"No file info returned for: {file_path}")
                return None
                
            logger.info(f"File processed - Type: {file_info.get('mime_type')}, Size: {file_info.get('size')} bytes")
            
            # Create MCard with just the content bytes
            try:
                logger.info(f"Creating MCard for: {file_path}")
                mcard = MCard(content=file_info["content"])
                logger.info(f"Created MCard with hash: {mcard.get_hash()}")
            except Exception as _e:
                logger.error(f"Failed to create MCard for {file_path}", exc_info=True)
                return None
            
            # Add to collection
            try:
                logger.info(f"Adding MCard to collection for: {file_path}")
                self.collection.add(mcard)
                logger.info(f"Successfully added MCard to collection for: {file_path}")
            except Exception as _e:
                logger.error(f"Failed to add MCard to collection for {file_path}", exc_info=True)
                return None
            
            # Prepare and return processing info
            result = {
                "hash": mcard.get_hash(),
                "content_type": file_info.get("mime_type"),
                "is_binary": file_info.get("is_binary"),
                "filename": file_info.get("filename"),
                "size": file_info.get("size"),
                "file_path": str(file_path)
            }
            
            logger.info(f"COMPLETED processing file: {file_path}")
            return result
            
        except (TimeoutError, ValueError) as e:
            logger.warning(f"Skipping problematic file {file_path}: {e}")
            return None
        except Exception as _e:
            logger.error(f"Error processing {file_path}", exc_info=True)
            return None

def load_file_to_collection(path: Union[str, Path], 
                         collection: CardCollection, 
                         recursive: bool = False) -> List[Dict[str, Any]]:
    """
    Load a file or directory of files into the specified collection.
    
    This function handles the entire process of:
    1. If path is a file: Process that single file
    2. If path is a directory: Process all files in the directory (optionally recursively)
    3. Store the processed files in the collection
    4. Return processing information
    
    Args:
        path: Path to a file or directory to process
        collection: CardCollection to store the MCards in
        recursive: If True and path is a directory, recursively process files in subdirectories (default: False)
        
    Returns:
        List of dictionaries with processing information for each processed file
        
    Example:
        ```python
        from mcard import CardCollection
        from mcard.file_utility import load_file_to_collection
        
        # Create or load a collection
        collection = CardCollection()
        
        # Load a single file
        results = load_file_to_collection('/path/to/file.txt', collection)
        
        # Load files from a directory (non-recursive)
        results = load_file_to_collection('/path/to/files', collection)
        
        # Load files recursively from a directory
        results = load_file_to_collection('/path/to/files', collection, recursive=True)
        ```
    """
    path = Path(path) if isinstance(path, str) else path
    utility = FileUtility(collection)
    results = []
    
    if path.is_file():
        # Process a single file
        result = utility._process_and_store_file(path)
        if result:
            results.append(result)
    elif path.is_dir():
        # Process all files in the directory
        file_paths = utility._load_files(path, recursive=recursive)
        logger.info(f"About to process {len(file_paths)} files")
        for i, file_path in enumerate(file_paths):
            logger.info(f"Processing file {i+1}/{len(file_paths)}: {file_path}")
            result = utility._process_and_store_file(file_path)
            if result:
                results.append(result)
            logger.info(f"Completed file {i+1}/{len(file_paths)}: {file_path}")
    else:
        raise FileNotFoundError(f"Path '{path}' does not exist or is not accessible")
            
    return results
