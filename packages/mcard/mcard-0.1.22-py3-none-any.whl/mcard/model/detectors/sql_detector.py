from typing import List, Optional
from .base_detector import BaseDetector

class SQLDetector(BaseDetector):
    """Detects SQL files based on common SQL keywords and structure."""
    SQL_KEYWORDS = [
        'SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE ', 'DROP ', 'ALTER ',
        'FROM ', 'WHERE ', 'JOIN ', 'TABLE ', 'INTO ', 'VALUES ', 'SET ', 'PRIMARY KEY',
    ]

    def get_mime_type(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> str:
        if self.detect(content_sample, lines, first_line, file_extension) > 0.5:
            return 'text/x-sql'
        return 'text/plain'

    @property
    def content_type_name(self) -> str:
        return "sql"

    def detect(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> float:
        # If file extension is .sql, high confidence
        if file_extension and file_extension.lower() == '.sql':
            return 0.95
        # Look for SQL keywords in the first few lines
        keyword_hits = 0
        for line in lines[:10]:
            for kw in self.SQL_KEYWORDS:
                if kw in line.upper():
                    keyword_hits += 1
        if keyword_hits >= 2:
            return 0.85
        if keyword_hits == 1:
            return 0.6
        return 0.0
