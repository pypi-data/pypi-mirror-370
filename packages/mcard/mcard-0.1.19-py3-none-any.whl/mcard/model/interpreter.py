"""
Content type detection and validation service.
"""
import json
import re
import xml.etree.ElementTree as ET
from typing import Union

try:
    from lxml import etree
except ImportError:
    etree = None
# Import detector modules
from mcard.model.detectors.binary_detector import BinarySignatureDetector
from mcard.model.detectors.language_detector import ProgrammingLanguageDetector
from mcard.model.detectors.text_format_detector import TextFormatDetector
from mcard.model.detectors.xml_detector import XMLDetector

# Backward compatibility shims for legacy tests
# Only import and set up these if needed for public API or legacy tests
try:
    setattr(TextFormatDetector, '_is_mermaid', staticmethod(lambda text_content: any(
        re.search(pattern, text_content, re.MULTILINE)
        for pattern in [
            r'^\s*graph\s+(TB|TD|BT|RL|LR)\b',
            r'^\s*sequenceDiagram\b',
            r'^\s*classDiagram\b',
            r'^\s*stateDiagram(-v2)?\b',
            r'^\s*erDiagram\b',
            r'^\s*gantt\b',
            r'^\s*pie\b',
            r'^\s*flowchart\s+(TB|TD|BT|RL|LR)\b',
            r'^\s*journey\b',
            r'^\s*gitGraph\b',
            r'^\s*mermaid\b'
        ]
    )))
    setattr(TextFormatDetector, '_is_tex', staticmethod(lambda text_content, lines: any([
        text_content.startswith('\\documentclass'),
        '\\documentclass{' in text_content,
        text_content.startswith('\\begin{document}'),
        '\\begin{document}' in text_content,
        '\\begin{abstract}' in text_content,
        '\\begin{figure}' in text_content,
        '\\begin{table}' in text_content,
        '\\begin{equation}' in text_content,
        '\\begin{align}' in text_content,
        '\\tableofcontents' in text_content,
        '\\section{' in text_content,
        '\\subsection{' in text_content,
        '\\chapter{' in text_content,
        '\\usepackage{' in text_content,
    ])))
except ImportError:
    pass

try:
    from .detectors.xml_detector import XMLDetector
    def _xml_detect_from_bytes(content: bytes) -> str:
        try:
            text_content = content.decode('utf-8', errors='ignore')
            return XMLDetector().get_mime_type(text_content, text_content.split('\n'), text_content.split('\n')[0] if text_content else '', None)
        except Exception:
            return 'text/plain'
    setattr(XMLDetector, 'detect_from_bytes', staticmethod(_xml_detect_from_bytes))
except ImportError:
    pass

def _xml_detect_from_string(content: str) -> str:
    """Detect XML-based format from string content with hierarchical subtype detection."""
    # Check for specialized XML subtypes first
    if content.strip().startswith('<'):
        content_lower = content.lower()
        # Check for SVG content
        if '<svg' in content_lower and ('xmlns' in content_lower and 'svg' in content_lower or 'viewbox' in content_lower):
            return 'image/svg+xml'
            
        # Check for HTML content
        if ('<!doctype html' in content_lower or '<html' in content_lower or 
            ('<head' in content_lower and '<body' in content_lower)):
            return 'text/html'
            
        # Check if it's valid XML
        try:
            ET.fromstring(content.encode('utf-8'))
            return 'application/xml'
        except Exception:
            pass
    
    return 'text/plain'

setattr(XMLDetector, 'detect_from_string', staticmethod(_xml_detect_from_string))

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ContentTypeInterpreter:
    """Unified service for content type detection and validation.
    
    This class leverages specialized detector modules from the detectors package
    to provide a comprehensive content type detection system.
    """
    
    # Collection of text-based MIME types
    TEXT_MIME_TYPES = {
        # Basic text formats
        'text/plain',
        'text/html',
        'text/xml',
        'text/csv',
        'text/css',
        'text/javascript',
        'text/markdown',
        'text/x-python',
        'text/x-java',
        'text/x-c',
        'text/x-c++',
        'text/x-sql',
        'text/jsx',
        'text/typescript',
        
        # Application text formats
        'application/json',
        'application/xml',
        'application/x-yaml',
        'application/javascript',
        'application/x-httpd-php',
        'application/x-sh',
        'application/x-tex',
        'application/3d-obj',
        
        # Diagram formats
        'text/vnd.graphviz',
        'text/x-mermaid',
        'text/x-plantuml',
        
        # Configuration formats
        'application/x-properties',
        'application/toml',
    }

    @staticmethod
    def detect_content_type(content: Union[str, bytes], file_extension: str = None):
        """
        Detect content type and suggested extension.
        Returns tuple of (mime_type, extension).

        This method leverages the centralized DetectorRegistry for modular and maintainable content type detection.
        """
        # First check for binary content using binary signatures if content is bytes
        if isinstance(content, bytes):
            # Check for binary signatures first
            from mcard.model.detectors.binary_detector import BinarySignatureDetector
            detector = BinarySignatureDetector()
            content_sample = content
            lines = []
            first_line = ""
            mime_type = detector.get_mime_type(content_sample, lines, first_line)

            # If we detected a specific binary format, return it
            if mime_type != 'application/octet-stream':
                ext = ContentTypeInterpreter.get_extension(mime_type)
                return mime_type, ext

            # Try to decode as text if no binary signature matched
            try:
                content_sample = content.decode('utf-8', errors='replace')
            except Exception:
                # If we can't decode as UTF-8, it's likely binary
                ext = ContentTypeInterpreter.get_extension('application/octet-stream')
                return 'application/octet-stream', ext
        else:
            # For string content, use it directly
            content_sample = content

        # Process as text content
        # Optimize for files with very long lines by limiting line processing
        if isinstance(content_sample, str):
            # For very large content or content with extremely long lines, use a sample
            if len(content_sample) > 64 * 1024:  # 64KB limit for line processing
                content_for_lines = content_sample[:64 * 1024]
            else:
                content_for_lines = content_sample
            lines = content_for_lines.split('\n')[:100]  # Limit to first 100 lines
            first_line = lines[0] if lines else ''
        else:
            lines = []
            first_line = ''

        # Use the centralized registry for detection
        from mcard.model.detectors.registry import registry as detector_registry
        mime_type = detector_registry.detect(content_sample, lines, first_line, file_extension)
        ext = ContentTypeInterpreter.get_extension(mime_type)
        return mime_type, ext

    @staticmethod
    def _detect_by_signature(content: bytes) -> str:
        """Backward compatibility method that delegates to BinarySignatureDetector."""
        # Create necessary parameters for the BinarySignatureDetector.detect method
        content_sample = content
        lines = []
        first_line = ""
        
        # Get the mime type instead of using detect directly
        from mcard.model.detectors.binary_detector import BinarySignatureDetector
        detector = BinarySignatureDetector()
        return detector.get_mime_type(content_sample, lines, first_line)

    @staticmethod
    def _detect_bytes_content(content: bytes) -> str:
        """Detect content type from bytes input."""
        # First try binary signature detection using BinarySignatureDetector
        detector = BinarySignatureDetector()
        content_sample = content
        lines = []
        first_line = ""
        mime_type = detector.get_mime_type(content_sample, lines, first_line)
        if mime_type != 'application/octet-stream':
            return mime_type
            
        # Try to decode as text if no binary signature matched
        try:
            text_content = content.decode('utf-8', errors='ignore')
            
            # Check for XML-based formats (including SVG) using XMLDetector
            if text_content.lstrip().startswith('<'):
                xml_type = XMLDetector.detect_from_string(text_content)
                if xml_type != 'text/plain':
                    return xml_type
                
            # Try detecting programming languages
            lang_type = ProgrammingLanguageDetector.detect(text_content)
            if lang_type != 'text/plain':
                return lang_type
                
            # Then try other text formats
            format_type = TextFormatDetector.detect(text_content)
            return format_type
            
        except UnicodeDecodeError:
            # If we can't decode as UTF-8, it's likely binary
            return 'application/octet-stream'

    def validate_content(self, content: Union[str, bytes]) -> None:
        """Validate content based on its detected type."""
        if not content:
            raise ValidationError("Empty content")

        # Ensure that the content is not just random bytes
        if isinstance(content, bytes) and not content.strip():
            raise ValidationError("Invalid content: empty byte array")

        try:
            mime_type, _ = self.detect_content_type(content)

            # Validate binary formats
            if mime_type.startswith('image/') or mime_type.startswith('audio/') or mime_type.startswith('video/') or \
               mime_type in ['application/pdf', 'application/zip', 'application/octet-stream']:
                # For binary content, verify it has enough data
                if isinstance(content, bytes):
                    # PNG files need more than just the 8-byte header
                    if mime_type == 'image/png' and len(content) <= 8:
                        raise ValidationError("Invalid PNG content: truncated file")
                    # JPEG files need more than just the header
                    elif mime_type == 'image/jpeg' and len(content) <= 3:
                        raise ValidationError("Invalid JPEG content: truncated file")
                    # GIF files need more than just the header
                    elif mime_type == 'image/gif' and len(content) <= 6:
                        raise ValidationError("Invalid GIF content: truncated file")
                    # Generic check for other binary formats
                    elif len(content) < 8:
                        raise ValidationError(f"Invalid {mime_type} content: too small")
                return
                
            # For text content, validate that it's proper UTF-8 and meaningful content
            if mime_type == 'text/plain':
                if isinstance(content, bytes):
                    # Check if it might be binary content first
                    if self.is_binary_content(content):
                        return
                    try:
                        text_content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        raise ValidationError("Invalid content: not valid UTF-8")
                else:
                    text_content = content

                # Check if content is just random bytes, invalid characters, or too short
                if not text_content.strip():
                    raise ValidationError("Invalid content: empty text")
                if len(text_content.strip()) < 3:  # Require at least 3 meaningful characters
                    raise ValidationError("Invalid content: too short")
                if all(ord(c) < 32 for c in text_content.strip()):
                    raise ValidationError("Invalid content: contains only control characters")

                # Validate text content structure
                lines = text_content.strip().split('\n')
                if len(lines) < 1:
                    raise ValidationError("Invalid content: no lines")
                
                # Check for meaningful content structure
                has_valid_structure = False
                
                # Try JSON validation
                if text_content.strip().startswith('{') and text_content.strip().endswith('}'):
                    try:
                        json.loads(text_content)
                        print(f"JSON content validated successfully.")
                        has_valid_structure = True
                    except json.JSONDecodeError:
                        raise ValidationError("Invalid JSON content")

                # Try XML validation
                elif text_content.strip().startswith('<'):
                    try:
                        ET.fromstring(text_content)
                        print(f"XML content validated successfully.")
                        has_valid_structure = True
                    except ET.ParseError:
                        raise ValidationError("Invalid XML content")

                # For plain text, ensure it contains meaningful content
                if not has_valid_structure:
                    # Check if content looks like a valid text document
                    words = text_content.strip().split()
                    if len(words) < 2:  # Require at least 2 words for meaningful text
                        raise ValidationError("Invalid content: insufficient text content")
                    
                    # Check if content has a reasonable distribution of characters
                    char_counts = {}
                    total_chars = 0
                    for c in text_content:
                        if c.isprintable():
                            char_counts[c] = char_counts.get(c, 0) + 1
                            total_chars += 1
                    
                    if total_chars == 0:
                        raise ValidationError("Invalid content: no printable characters")
                    
                    # Check character distribution (no single character should dominate)
                    for count in char_counts.values():
                        if count / total_chars > 0.5:  # No character should be more than 50% of content
                            raise ValidationError("Invalid content: suspicious character distribution")

                    # Check for reasonable text patterns
                    if not any(c.isspace() for c in text_content):
                        raise ValidationError("Invalid content: no whitespace found")
                    if not any(c.isalpha() for c in text_content):
                        raise ValidationError("Invalid content: no letters found")
                    
                    # Check for proper sentence structure
                    sentences = [s.strip() for s in text_content.split('.') if s.strip()]
                    if not sentences:
                        raise ValidationError("Invalid content: no proper sentences found")
                    
                    # Each sentence should:
                    # 1. Start with an uppercase letter
                    # 2. Have at least 2 words
                    # 3. End with proper punctuation
                    for sentence in sentences:
                        if not sentence[0].isupper():
                            raise ValidationError("Invalid content: sentence must start with uppercase letter")
                        words = sentence.split()
                        if len(words) < 2:
                            raise ValidationError("Invalid content: sentence must have at least 2 words")
                        if not any(sentence.strip().endswith(p) for p in ['.', '!', '?']):
                            raise ValidationError("Invalid content: sentence must end with proper punctuation")

            # Handle text-based content types
            elif mime_type == 'application/json':
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                try:
                    # Check for comments before attempting to parse
                    lines = content.split('\n')
                    if any(line.strip().startswith('//') for line in lines):
                        raise ValidationError("Invalid JSON content")
                    json.loads(content)
                    pass
                except (json.JSONDecodeError, UnicodeDecodeError):
                    raise ValidationError("Invalid JSON content")
                # Add a check for invalid content
                if not content:
                    raise ValidationError("Invalid content: empty content")

            elif mime_type == 'application/xml' or mime_type == 'image/svg+xml':
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                try:
                    ET.fromstring(content)
                    pass
                except (ET.ParseError, UnicodeDecodeError):
                    raise ValidationError("Invalid XML content")
                # Check for mixed content (XML + binary)
                if isinstance(content, str):
                    content = content.encode('utf-8')
                for signature in BinarySignatureDetector.SIGNATURES:
                    if signature in content and not content.startswith(signature):
                        raise ValidationError("Invalid XML content")

            # Handle binary content types
            elif mime_type.startswith('image/'):
                # Basic validation for image formats
                if mime_type == 'image/png' and len(content) <= 8:  # PNG header is 8 bytes
                    raise ValidationError("Invalid content: truncated PNG file")
                elif mime_type == 'image/jpeg' and len(content) <= 3:  # JPEG header is 3 bytes
                    raise ValidationError("Invalid content: truncated JPEG file")
                elif mime_type == 'image/gif' and len(content) <= 6:  # GIF header is 6 bytes
                    raise ValidationError("Invalid content: truncated GIF file")
                elif not any(content.startswith(sig) for sig, mime in BinarySignatureDetector.SIGNATURES.items() if mime == mime_type):
                    raise ValidationError(f"Invalid {mime_type} content: missing proper header")
                pass

            elif mime_type == 'application/pdf':
                if not content.startswith(b'%PDF-'):
                    raise ValidationError("Invalid PDF content")
                pass

            elif mime_type == 'application/zip':
                if len(content) <= 4:  # ZIP header is 4 bytes
                    raise ValidationError("Invalid ZIP content")
                pass

            pass

        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Validation failed: {str(e)}")

    @staticmethod
    def is_binary_content(content: Union[str, bytes]) -> bool:
        """
        Determine if content should be treated as binary.
        
        This method uses multiple heuristics:
        1. If content is already a string, it's not binary
        2. For bytes content:
           - Check for known binary signatures
           - Try UTF-8 decoding
           - Analyze content patterns
        """
        # Delegate to BinarySignatureDetector's is_binary_content method
        # If content is already a string, it's not binary
        if isinstance(content, str):
            return False
            
        # Check for binary signatures
        for signature, _ in BinarySignatureDetector.SIGNATURES.items():
            if content.startswith(signature):
                return True
                
        # Try to decode as UTF-8
        try:
            # If content has null bytes, it's likely binary
            if b'\x00' in content:
                return True
                
            # Attempt to decode as UTF-8
            content.decode('utf-8', errors='strict')
            
            # If we get here, the content can be decoded as UTF-8
            # Check for high concentration of non-printable chars (indicating binary)
            sample = content[:4096] if len(content) > 4096 else content
            non_text_chars = sum(1 for b in sample if b < 9 or (b > 13 and b < 32) or b > 126)
            text_ratio = 1 - (non_text_chars / len(sample))
            
            # If more than 30% non-printable characters, consider it binary
            return text_ratio < 0.7
            
        except UnicodeDecodeError:
            # If it can't be decoded as UTF-8, it's binary
            return True

    @staticmethod
    def is_xml_content(content: Union[str, bytes]) -> bool:
        """Check if content is valid XML."""
        # Delegate to XMLDetector's is_valid_xml method
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')

            # Try to parse the XML without requiring XML declaration
            ET.fromstring(content)
            print(f"Valid XML content detected.")  # Debug statement
            return True
        except Exception as e:
            print(f"Invalid XML content detected: {str(e)}")  # Debug statement
            return False

    @staticmethod
    def is_svg_content(content: Union[str, bytes]) -> bool:
        """Check if content is SVG."""
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        
        # First check if it's valid XML
        if not ContentTypeInterpreter.is_xml_content(content):
            return False
        
        try:
            # Parse XML and check for SVG namespace
            tree = ET.fromstring(content)
            return (
                tree.tag == 'svg' or
                tree.tag.endswith('}svg') or
                any(attr.endswith('xmlns') and 'svg' in value
                    for attr, value in tree.attrib.items())
            )
        except Exception:
            return False

    @staticmethod
    def is_mermaid_content(content: str) -> bool:
        """Check if content is Mermaid diagram."""
        content = content.strip().lower()
        mermaid_keywords = [
            'graph ', 'sequencediagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'gantt',
            'pie', 'flowchart', 'journey'
        ]
        return any(content.startswith(keyword.lower()) for keyword in mermaid_keywords)

    @staticmethod
    def is_diagram_content(content: str) -> bool:
        """Check if content is a diagram format."""
        content = content.strip().lower()
        # Check for PlantUML
        if content.startswith('@startuml') and content.endswith('@enduml'):
            return True
        # Check for Graphviz
        if content.startswith(('digraph', 'graph', 'strict')):
            return True
        # Check for Mermaid
        return ContentTypeInterpreter.is_mermaid_content(content)

    @staticmethod
    def get_extension(mime_type: str) -> str:
        """Get file extension from MIME type."""
        extension = {
            # Images
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'image/bmp': 'bmp',
            'image/x-icon': 'ico',
            'image/svg+xml': 'svg',
            'image/djvu': 'djvu',
            'image/webp': 'webp',
            # Audio/Video
            'audio/wav': 'wav',
            'audio/x-wav': 'wav',  # Alternative MIME type for WAV
            'video/mp4': 'mp4',
            
            # Documents
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            'application/vnd.ms-powerpoint': 'ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
            
            # Archives
            'application/zip': 'zip',
            'application/gzip': 'gz',
            'application/x-rar-compressed': 'rar',
            'application/x-7z-compressed': '7z',
            
            # Database
            'application/x-sqlite3': 'db',
            'application/x-parquet': 'parquet',
            
            # Text formats
            'text/plain': 'txt',
            'text/html': 'html',
            'text/xml': 'xml',
            'text/csv': 'csv',
            'text/css': 'css',
            'text/javascript': 'js',
            'text/markdown': 'md',
            'text/x-python': 'py',
            'text/x-java': 'java',
            'text/x-c': 'c',
            'text/x-sql': 'sql',
            
            # Application formats
            'application/json': 'json',
            'application/xml': 'xml',
            'application/x-yaml': 'yaml',
            'application/javascript': 'js',
            'application/x-httpd-php': 'php',
            'application/x-sh': 'sh',
            'application/x-tex': 'tex',
            
            # Diagram formats
            'text/vnd.graphviz': 'dot',
            'text/x-mermaid': 'mmd',
            'text/x-plantuml': 'puml',
            
            # 3D Object formats
            'application/3d-obj': 'obj',
            
            # Configuration formats
            'application/x-properties': 'properties',
            'application/toml': 'toml',
            # 'application/x-yaml': 'yaml',  # Duplicate entry - already defined above
        }.get(mime_type, '')
        
        # Return the extension without dot prefix 
        if extension and extension.startswith('.'):
            extension = extension[1:]
        return extension

    @staticmethod
    def get_default_extension(mime_type: str) -> str:
        """
        Return the default file extension for a given MIME type.
        """
        mime_to_extension = {
            # Images
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'image/bmp': 'bmp',
            'image/webp': 'webp',
            'image/svg+xml': 'svg',
            'image/vnd.djvu': 'djv',
            'image/vnd.dxf': 'dxf',
            
            # Document formats
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            
            # Spreadsheets
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            
            # Presentations
            'application/vnd.ms-powerpoint': 'ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
            
            # Text formats
            'text/plain': 'txt',
            'text/html': 'html',
            'text/csv': 'csv',
            'text/markdown': 'md',
            'text/x-python': 'py',
            'application/json': 'json',
            'application/xml': 'xml',
            'application/x-yaml': 'yaml',
            
            # Special formats
            'application/x-tex': 'tex',
            'application/3d-obj': 'obj',
            'text/x-mermaid': 'mmd',
            
            # Audio/Video
            'audio/wav': 'wav',
            'audio/x-wav': 'wav',
            'video/mp4': 'mp4',
            'video/quicktime': 'mov',
            
            # Archives
            'application/zip': 'zip',
            'application/gzip': 'gz',
            'application/x-rar-compressed': 'rar',
            
            # Add more mappings as needed
        }
        return mime_to_extension.get(mime_type, '')