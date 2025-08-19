import re
from typing import List, Optional
from .base_detector import BaseDetector

class YAMLDetector(BaseDetector):
    def get_mime_type(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> str:
        conf = self.detect(content_sample, lines, first_line, file_extension)
        return 'application/x-yaml' if conf > 0.5 else 'text/plain'
    @property
    def content_type_name(self) -> str:
        return "yaml"

    YAML_START_PATTERNS = [r"^---\s*$", r"^%YAML"]
    KEY_VALUE_PATTERN = r"^\s*[\w.-]+:\s+(?![=\{\[])" # key: value (avoid dicts, type hints)
    LIST_ITEM_PATTERN = r"^\s*-\s+[\w\'\"]"

    def detect(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> float:
        confidence = 0.0
        if file_extension in [".yaml", ".yml"]:
            confidence = max(confidence, 0.95)

        if any(re.match(p, first_line) for p in self.YAML_START_PATTERNS):
            confidence = max(confidence, 0.9)
        
        yaml_features = 0
        if any(re.match(p, content_sample, re.MULTILINE) for p in self.YAML_START_PATTERNS):
             yaml_features +=2

        for line in lines[:20]: # Check first 20 lines
            stripped_line = line.strip()
            if re.match(self.KEY_VALUE_PATTERN, stripped_line):
                yaml_features += 1
            elif re.match(self.LIST_ITEM_PATTERN, stripped_line):
                yaml_features += 1
        
        # Only classify as YAML if YAML document start (---) is present
        # Only classify as YAML if the document starts with '---' on the first non-empty line
        first_nonempty = next((line for line in lines if line.strip()), "")
        if first_nonempty.strip() == '---':
            if yaml_features > 1:
                confidence = max(confidence, 0.5)
            if yaml_features > 3:
                confidence = max(confidence, 0.75)
            if yaml_features > 5:
                confidence = max(confidence, 0.9)
        else:
            confidence = 0.0
        
        # Negative: if python keywords are abundant
        python_keywords = ['def ', 'class ', 'import ']
        py_kw_hits = sum(1 for kw in python_keywords if kw in content_sample[:1024])
        if py_kw_hits > 1 and confidence > 0.3:
            confidence -= 0.3

        return max(0.0, min(confidence, 1.0))