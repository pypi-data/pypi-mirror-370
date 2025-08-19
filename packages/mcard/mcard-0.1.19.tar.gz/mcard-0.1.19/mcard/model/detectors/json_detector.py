import json
import re
from typing import List, Optional
from .base_detector import BaseDetector

class JSONDetector(BaseDetector):
    """Detects JSON content."""
    
    def get_mime_type(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> str:
        """Return the MIME type if content is detected as JSON."""
        if self.detect(content_sample, lines, first_line, file_extension) > 0.5:
            return 'application/json'
        return 'text/plain'
    
    @property
    def content_type_name(self) -> str:
        """Return the detector name."""
        return "json"
    
    def detect(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> float:
        """
        Detect if content is JSON format.
        
        Returns a confidence score between 0.0 and 1.0.
        """
        # If file extension is .json, increase confidence
        if file_extension and file_extension.lower() == '.json':
            # Still verify content
            if self._verify_json_structure(content_sample):
                return 0.95
            return 0.6  # Extension matches but content doesn't look valid
        
        # Basic structural check
        if not ((content_sample.strip().startswith('{') and content_sample.strip().endswith('}')) or 
                (content_sample.strip().startswith('[') and content_sample.strip().endswith(']'))):
            return 0.0
            
        # Reject content with JavaScript/C-style comments, as pure JSON doesn't allow them
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('//') or stripped_line.startswith('/*'):
                # This is likely JavaScript, not JSON
                return 0.0

        # Try to parse as JSON
        try:
            json.loads(content_sample)
            return 0.9  # Successfully parsed
        except json.JSONDecodeError:
            return 0.0
    
    def _verify_json_structure(self, content_sample: str) -> bool:
        """Check if content has valid JSON structure."""
        try:
            json.loads(content_sample)
            return True
        except json.JSONDecodeError:
            return False