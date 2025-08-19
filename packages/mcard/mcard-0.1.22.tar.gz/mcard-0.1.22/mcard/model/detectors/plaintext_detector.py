from typing import List, Optional
from .base_detector import BaseDetector

# Assuming ContentTypeInterpreter.IMAGE_EXTENSIONS and PDF_EXTENSIONS are accessible
# For simplicity, we'll redefine them here or pass them if needed.
# This is a slight break in perfect encapsulation if not passed.
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
PDF_EXTENSIONS = {'.pdf'}

class PlainTextDetector(BaseDetector):
    def get_mime_type(self, content_sample: str, lines, first_line: str, file_extension: str = None) -> str:
        return 'text/plain'
    @property
    def content_type_name(self) -> str:
        return "text"

    def detect(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> float:
        # This detector provides a baseline confidence if no other specific text type is found.
        # It should have low confidence so more specific detectors can override it.
        
        if not content_sample and not lines: # Empty content
            return 0.1 # Empty is still considered 'text' by default

        if content_sample:
            # If it has a known binary extension, it's not plain text.
            if file_extension and (file_extension in IMAGE_EXTENSIONS or file_extension in PDF_EXTENSIONS):
                return 0.0
                
            # Special case: Detect ambiguous CSV-like content (has commas but lacks proper CSV structure)
            # This helps prevent ambiguous content from being misclassified as YAML or CSV
            if ',' in content_sample and len(lines) < 5:
                comma_lines = sum(1 for line in lines if ',' in line)
                if comma_lines > 0 and comma_lines == len(lines):
                    # All lines have commas, but not enough structure for CSV
                    delimiter_counts = [line.count(',') for line in lines[:3] if line.strip()]
                    if delimiter_counts and all(count <= 2 for count in delimiter_counts):
                        return 0.8  # High confidence for ambiguous comma-separated content
            
            # For normal text content, give a small base confidence
            return 0.15 
        return 0.0