import re
import json
from typing import List, Optional
from .base_detector import BaseDetector

class MarkdownDetector(BaseDetector):
    def get_mime_type(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> str:
        conf = self.detect(content_sample, lines, first_line, file_extension)
        return 'text/markdown' if conf > 0.5 else 'text/plain'

    @property
    def content_type_name(self) -> str:
        return "markdown"

    MD_PATTERNS = [
        r"^#{1,6}\s+\S+",             # ATX Headers
        r"^\s*[\*\+\-]\s+\S+",        # List items
        r"^\s*\d+\.\s+\S+",           # Ordered list items
        r"`{1,3}[^`]+`{1,3}",         # Inline code
        r"\[[^\]]+\]\([^\)]+\)",      # Links
        r"!\[[^\]]+\]\([^\)]+\)",     # Images
        r"^\s*>.*"                    # Blockquotes
    ]
    SETEXT_HEADER_PATTERN = r"^.*\n(?:={3,}|-{3,})\s*$" # Needs multiline search on sample

    def detect(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> float:
        confidence = 0.0
        if file_extension in [".md", ".markdown"]:
            confidence = max(confidence, 0.95)

        md_features = 0
        if re.search(self.SETEXT_HEADER_PATTERN, content_sample, re.MULTILINE):
            md_features += 2 # Strong indicator

        for line in lines[:20]:
            if any(re.search(p, line) for p in self.MD_PATTERNS):
                md_features += 1
        
        # Check for fenced code blocks specifically
        has_code_fence = "```" in content_sample
        if has_code_fence:
            md_features += 1

        # Boost confidence if headers and code fences are present
        if md_features > 1 and has_code_fence:
            confidence = max(confidence, 0.85)
        if md_features > 3 and has_code_fence:
            confidence = max(confidence, 0.95)
        elif md_features > 1:
            confidence = max(confidence, 0.6)
        elif md_features > 3:
            confidence = max(confidence, 0.8)
        elif md_features > 5:
            confidence = max(confidence, 0.9)
        
        # Negative: if it looks like well-formed Python/JSON/XML
        if (content_sample.strip().startswith('{') and content_sample.strip().endswith('}')) or \
           (content_sample.strip().startswith('[') and content_sample.strip().endswith(']')):
            try:
                json.loads(content_sample) # if it's valid JSON
                if confidence > 0.3:
                    confidence -= 0.4
            except Exception:
                pass
        
        if content_sample.strip().startswith('<') and '<?xml' in content_sample[:100]:
            if confidence > 0.3:
                confidence -= 0.4


        return max(0.0, min(confidence, 1.0))