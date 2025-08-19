"""
XML and its subtype detection (HTML, SVG).
"""
import re
from typing import List, Optional
from .base_detector import BaseDetector
# Attempt to import lxml for more robust parsing, fallback to regex
try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

class XMLDetector(BaseDetector):
    @property
    def content_type_name(self) -> str:
        return "xml"

    XML_DECLARATION = r"^\s*<\?xml\s+version="
    BASIC_TAG_PAIR = r"<(\w+)\b[^>]*>.*?</\1\s*>" # Non-greedy match

    def detect(self, content_sample, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> float:
        """Return confidence score for XML-based content."""
        # Accept both str and bytes for content_sample
        if isinstance(content_sample, bytes):
            try:
                content_sample = content_sample.decode('utf-8', errors='replace')
            except Exception:
                return 0.0
        confidence = 0.0
        if file_extension == ".xml":
            confidence = max(confidence, 0.9) # Strong hint

        if re.match(self.XML_DECLARATION, first_line, re.IGNORECASE):
            confidence = max(confidence, 0.95) # Very strong indicator
        
        # Basic check for tags
        if '<' in content_sample and '>' in content_sample and '</' in content_sample:
            confidence = max(confidence, 0.5)
            if re.search(self.BASIC_TAG_PAIR, content_sample, re.DOTALL | re.IGNORECASE):
                 confidence = max(confidence, 0.7)

        # If lxml is available, try parsing for higher confidence
        if LXML_AVAILABLE and confidence > 0.4: # Only try if basic checks pass
            try:
                etree.fromstring(content_sample.encode('utf-8', errors='replace'))
                confidence = max(confidence, 0.98) # Successfully parsed
            except etree.XMLSyntaxError:
                if confidence > 0.8: confidence = 0.6
            except Exception:
                pass
        if "<!DOCTYPE html" in content_sample[:200].lower():
            if confidence > 0.3: confidence -= 0.4
        return max(0.0, min(confidence, 1.0))

    def get_mime_type(self, content_sample, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> str:
        """Return the most likely MIME type for XML-based content."""
        # Accept both str and bytes for content_sample
        if isinstance(content_sample, bytes):
            try:
                content_sample = content_sample.decode('utf-8', errors='replace')
            except Exception:
                return 'application/octet-stream'
        if file_extension == ".xml":
            return "application/xml"
        if '<svg' in content_sample.lower():
            return 'image/svg+xml'
        if '<html' in content_sample.lower() or '<!doctype html' in content_sample.lower():
            return 'text/html'
        if content_sample.strip().startswith('<?xml') or re.match(self.XML_DECLARATION, first_line, re.IGNORECASE):
            return 'application/xml'
        if '<' in content_sample and '>' in content_sample and '</' in content_sample:
            return 'application/xml'
        return 'text/plain'

        confidence = 0.0
        if file_extension == ".xml":
            confidence = max(confidence, 0.9) # Strong hint

        if re.match(self.XML_DECLARATION, first_line, re.IGNORECASE):
            confidence = max(confidence, 0.95) # Very strong indicator
        
        # Basic check for tags
        if '<' in content_sample and '>' in content_sample and '</' in content_sample:
            confidence = max(confidence, 0.5)
            if re.search(self.BASIC_TAG_PAIR, content_sample, re.DOTALL | re.IGNORECASE):
                 confidence = max(confidence, 0.7)

        # If lxml is available, try parsing for higher confidence
        if LXML_AVAILABLE and confidence > 0.4: # Only try if basic checks pass
            try:
                # lxml expects bytes for parsing
                etree.fromstring(content_sample.encode('utf-8', errors='replace'))
                confidence = max(confidence, 0.98) # Successfully parsed
            except etree.XMLSyntaxError:
                # Parsing failed, might reduce confidence if it was high
                if confidence > 0.8: confidence = 0.6
            except Exception: # Other errors
                pass
        
        # Negative: if it looks like HTML (common doctype)
        if "<!DOCTYPE html" in content_sample[:200].lower():
            if confidence > 0.3: confidence -= 0.4

        return max(0.0, min(confidence, 1.0))