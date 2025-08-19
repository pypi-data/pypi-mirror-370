"""
File utility functions for handling file operations in MCard.
"""
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TypeVar, TYPE_CHECKING
import hashlib
import time

from mcard.model.interpreter import ContentTypeInterpreter
from mcard.config.env_parameters import EnvParameters
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
            
            # Skip extremely large files (>10MB) - likely problematic for processing
            if file_size > 10 * 1024 * 1024:
                logger.warning(f"Skipping extremely large file: {file_path} ({file_size} bytes)")
                return True
            
            # For small files, no need to check further
            if file_size <= 1024:
                return False
            
            # If it's a known type that can have long lines, be more permissive
            is_known_type = ContentTypeInterpreter._is_known_long_line_extension(file_extension)
            
            # For known types, still have size limits to prevent pathological cases
            if is_known_type and file_size > 1024 * 1024:  # 1MB limit for known types
                logger.warning(f"Skipping large file of known type: {file_path} ({file_size} bytes)")
                return True
            
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
                    if ContentTypeInterpreter._is_unstructured_binary(sample):
                        logger.warning(f"Skipping unstructured binary file: {file_path}")
                        return True
                    
                    # Check for pathological line patterns
                    if ContentTypeInterpreter._has_pathological_lines(sample, is_known_type):
                        logger.warning(f"Skipping file with pathological line structure: {file_path}")
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking file {file_path}: {e}")
            return True  # Skip files we can't check
    
    @staticmethod
    def _is_unstructured_binary(sample: bytes) -> bool:
        """Deprecated local implementation; delegates to ContentTypeInterpreter."""
        return ContentTypeInterpreter._is_unstructured_binary(sample)
    
    @staticmethod
    def _has_pathological_lines(sample: bytes, is_known_type: bool) -> bool:
        """Deprecated local implementation; delegates to ContentTypeInterpreter."""
        return ContentTypeInterpreter._has_pathological_lines(sample, is_known_type)
    
    @staticmethod
    def _soft_wrap_long_lines(text: str, max_line_length: int = 1000) -> str:
        """Insert newlines into very long single lines to prevent pathological processing.
        This is a safe text normalization step for minified or long-line content.
        """
        if max_line_length <= 0:
            return text
        out_lines: List[str] = []
        for line in text.splitlines() or [text]:
            if len(line) <= max_line_length:
                out_lines.append(line)
                continue
            # Chunk the long line
            for i in range(0, len(line), max_line_length):
                out_lines.append(line[i:i + max_line_length])
        # Preserve trailing newline if present in input
        result = "\n".join(out_lines)
        return result

    @staticmethod
    def _stream_read_normalized_text(file_path: Path, *, byte_cap: int, wrap_width: int) -> Dict[str, Any]:
        """Stream-read bytes up to byte_cap, decode with replacement, and insert soft wraps on the fly.
        Returns dict with keys: text, original_size, original_sha256_prefix.
        """
        sha = hashlib.sha256()
        total_size = 0
        produced_chars: list[str] = []
        current_len = 0
        with open(file_path, 'rb') as f:
            remaining = byte_cap
            while remaining > 0:
                chunk = f.read(min(8192, remaining))
                if not chunk:
                    break
                sha.update(chunk)
                total_size += len(chunk)
                remaining -= len(chunk)
                try:
                    s = chunk.decode('utf-8', errors='replace')
                except Exception:
                    s = chunk.decode('latin-1', errors='replace')
                for ch in s:
                    if ch == '\r':
                        # Normalize CR to nothing; let CRLF become just LF via the subsequent '\n'
                        continue
                    produced_chars.append(ch)
                    if ch == '\n':
                        current_len = 0
                    else:
                        current_len += 1
                        if wrap_width > 0 and current_len >= wrap_width:
                            produced_chars.append('\n')
                            current_len = 0
        return {
            'text': ''.join(produced_chars),
            'original_size': total_size,
            'original_sha256_prefix': sha.hexdigest()[:16],
        }

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
    def _read_file(file_path: Union[str, Path], allow_pathological: bool = False, max_bytes: Optional[int] = None) -> bytes:
        """
        Read file content with timeout protection and size limits.
        
        Args:
            file_path: Path to the file to read
            allow_pathological: If True, bypass long-line/pathological content checks
            max_bytes: If set, cap the number of bytes read to this value
            
        Returns:
            File content as bytes
            
        Raises:
            TimeoutError: If reading takes too long
            IOError: If file cannot be read
        """
        import threading
        
        # Check file size first
        file_size = file_path.stat().st_size
        max_file_size = 50 * 1024 * 1024  # 50MB limit
        
        if file_size > max_file_size:
            raise IOError(f"File too large: {file_size} bytes (max {max_file_size})")
        
        # Timeout configurable with a small bias for larger files
        env = EnvParameters()
        base_timeout = env.get_read_timeout_secs()
        timeout_seconds = 5.0 if file_size > 50 * 1024 and base_timeout >= 5 else base_timeout
        
        result = [None]
        exception = [None]
        
        def read_with_timeout():
            try:
                with open(file_path, 'rb') as file:
                    # For potentially problematic files, read in chunks with progress checking
                    if file_size > 50 * 1024 or max_bytes is not None:  # Files > 50KB or when capping
                        content = bytearray()
                        chunk_size = 8192
                        bytes_read = 0
                        start_time = time.time()
                        
                        to_read = max_bytes if max_bytes is not None else file_size
                        
                        while bytes_read < to_read:
                            if time.time() - start_time > timeout_seconds:
                                raise TimeoutError(f"Reading timeout exceeded for {file_path}")
                            
                            remaining = to_read - bytes_read
                            chunk = file.read(min(chunk_size, remaining))
                            if not chunk:
                                break
                            content.extend(chunk)
                            bytes_read += len(chunk)
                            
                            # Check for pathological content patterns during reading unless allowed
                            if (not allow_pathological) and len(content) > 32768 and b'\n' not in content and b'\r' not in content:
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
    def _process_file(cls, file_path: Union[str, Path], *, force_binary: bool = False, allow_pathological: bool = False, max_bytes: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a file and return its metadata and content.
        
        For text files, ensures the content is properly decoded to UTF-8 when possible.
        If force_binary is True, skip decoding and treat content as binary.
        """
        # Read file content as bytes
        content = cls._read_file(file_path, allow_pathological=allow_pathological, max_bytes=max_bytes)
        
        # Analyze the content to get MIME type and other metadata
        # For very large files or files with extremely long lines, use a sample
        content_sample = content
        if len(content) > 1024 * 1024:  # 1MB limit for content type detection
            content_sample = content[:1024 * 1024]
            logger.info(f"Using content sample for large file: {file_path}")
        
        analysis = cls._analyze_content(content_sample)
        mime_type = analysis["mime_type"]
        is_binary = analysis["is_binary"]
        
        # Force binary mode if requested
        if force_binary:
            is_binary = True
            # If detection thought it's text, override to a safe default
            if not mime_type or mime_type.startswith('text/'):
                mime_type = 'application/octet-stream'
        
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
    
    def _process_and_store_file(self, file_path: Union[str, Path], *, allow_problematic: bool = False, max_bytes_on_problem: Optional[int] = None, metadata_only: bool = False) -> Optional[Dict[str, Any]]:
        """Process a file, create an MCard, and store it in the collection.
        
        If a file is flagged as problematic and allow_problematic is True, process it as safe text
        by decoding with replacement and soft-wrapping long lines, rather than loading as a binary blob.
        Fallback to capped binary only if text coercion fails unexpectedly.
        """
        from mcard import MCard
        
        # Convert to Path object for consistency
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
            
        try:
            # Check if the file is problematic before processing
            if FileUtility._is_problematic_file(file_path):
                if not allow_problematic:
                    logger.warning(f"Skipping problematic file: {file_path}")
                    return None
                # Resolve environment-configured parameters
                env = EnvParameters()
                if max_bytes_on_problem is None:
                    max_bytes_on_problem = env.get_max_problem_text_bytes()
                is_known_type = ContentTypeInterpreter._is_known_long_line_extension(file_path.suffix.lower())
                wrap_width = env.get_wrap_width_known() if is_known_type else env.get_wrap_width_default()
                # Process as safe text via streaming normalization
                logger.warning(
                    f"Problematic file detected, processing as safe text with soft-wrap (cap {max_bytes_on_problem} bytes, wrap {wrap_width}): {file_path}"
                )
                try:
                    streamed = self._stream_read_normalized_text(file_path, byte_cap=max_bytes_on_problem, wrap_width=wrap_width)
                    text = streamed['text']
                    file_info = {
                        "content": text,
                        "filename": Path(file_path).name,
                        "mime_type": 'text/plain',
                        "extension": Path(file_path).suffix.lower(),
                        "is_binary": False,
                        "size": len(text),
                        "original_size": streamed['original_size'],
                        "original_sha256_prefix": streamed['original_sha256_prefix'],
                        "normalized": True,
                        "wrap_width": wrap_width,
                    }
                except Exception as _e:
                    # Last-resort fallback: capped binary
                    logger.warning(
                        f"Safe text processing failed, falling back to capped binary ({max_bytes_on_problem} bytes): {file_path}"
                    )
                    file_info = self._process_file(
                        file_path,
                        force_binary=True,
                        allow_pathological=True,
                        max_bytes=max_bytes_on_problem,
                    )
            else:
                logger.info(f"PROCESSING FILE: {file_path}")
                # Process the file
                logger.info(f"Reading file content: {file_path}")
                file_info = self._process_file(file_path)
                if not file_info:
                    logger.warning(f"No file info returned for: {file_path}")
                    return None
                logger.info(f"File processed - Type: {file_info.get('mime_type')}, Size: {file_info.get('size')} bytes")
            
            # Optionally skip storing content for problematic files if metadata_only is requested
            if metadata_only and FileUtility._is_problematic_file(file_path):
                mcard = None
            else:
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
            # Surface original bytes metadata if present
            if "original_size" in file_info:
                result["original_size"] = file_info["original_size"]
            if "original_sha256_prefix" in file_info:
                result["original_sha256_prefix"] = file_info["original_sha256_prefix"]
            if metadata_only and FileUtility._is_problematic_file(file_path):
                result["metadata_only"] = True
            
            logger.info(f"COMPLETED processing file: {file_path}")
            return result
            
        except (TimeoutError, ValueError) as e:
            logger.warning(f"Skipping problematic file {file_path}: {e}")
            return None
        except Exception as _e:
            logger.error(f"Error processing {file_path}", exc_info=True)
            return None
    
    @classmethod
    def _load_files(cls, directory: Union[str, Path], recursive: bool = False) -> List[Path]:
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
    
def load_file_to_collection(path: Union[str, Path], 
                         collection: CardCollection, 
                         recursive: bool = False,
                         include_problematic: bool = False,
                         max_bytes_on_problem: int = 2 * 1024 * 1024,
                         metadata_only: bool = False) -> List[Dict[str, Any]]:
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
        include_problematic: If True, files flagged as problematic are processed with safe text streaming
        max_bytes_on_problem: Cap the number of bytes read for problematic files
        metadata_only: If True and file is problematic, store only metadata (no MCard content)
        
    Returns:
        List of dictionaries with processing information for each processed file
    """
    path = Path(path) if isinstance(path, str) else path
    utility = FileUtility(collection)
    results = []
    
    if path.is_file():
        # Process a single file
        result = utility._process_and_store_file(path, allow_problematic=include_problematic, max_bytes_on_problem=max_bytes_on_problem, metadata_only=metadata_only)
        if result:
            results.append(result)
    elif path.is_dir():
        # Process all files in the directory
        file_paths = utility._load_files(path, recursive=recursive)
        logger.info(f"About to process {len(file_paths)} files")
        for i, file_path in enumerate(file_paths):
            logger.info(f"Processing file {i+1}/{len(file_paths)}: {file_path}")
            result = utility._process_and_store_file(file_path, allow_problematic=include_problematic, max_bytes_on_problem=max_bytes_on_problem, metadata_only=metadata_only)
            if result:
                results.append(result)
            logger.info(f"Completed file {i+1}/{len(file_paths)}: {file_path}")
    else:
        raise FileNotFoundError(f"Path '{path}' does not exist or is not accessible")
            
    return results
