"""CSV content type detector."""
import csv
import io
import re
from typing import List, Optional
from .base_detector import BaseDetector

class CSVDetector(BaseDetector):
    """Detects CSV (Comma-Separated Values) file content."""
    
    def get_mime_type(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> str:
        """Return the MIME type if content is detected as CSV."""
        if self.detect(content_sample, lines, first_line, file_extension) > 0.5:
            return 'text/csv'
        return 'text/plain'
    
    @property
    def content_type_name(self) -> str:
        """Return the detector name."""
        return "csv"
    
    def detect(self, content_sample: str, lines: List[str], first_line: str, file_extension: Optional[str] = None) -> float:
        """
        Detect if content is CSV format.
        
        Returns a confidence score between 0.0 and 1.0.
        """
        # If file extension is .csv, increase confidence
        if file_extension and file_extension.lower() == '.csv':
            # Still verify content
            if self._verify_csv_structure(lines):
                return 0.95
            return 0.6  # Extension matches but content doesn't look valid
        
        # No extension hint, check content
        return self._analyze_csv_content(lines)
    
    def _verify_csv_structure(self, lines: List[str]) -> bool:
        """Check if content has valid CSV structure."""
        if not lines or len(lines) == 0:
            return False
        
        # Check for consistent comma delimiters
        sample_lines = [line for line in lines[:10] if line.strip()]
        if not sample_lines or len(sample_lines) < 1:
            return False

        # All sample lines must contain at least one comma
        if not all(',' in line for line in sample_lines):
            return False

        # Check for consistent comma count
        comma_counts = [line.count(',') for line in sample_lines]
        
        # If all lines have the same number of commas (and > 0)
        if len(set(comma_counts)) == 1 and comma_counts[0] > 0:
            return True
            
        # Allow for a header row with a different number of commas
        if len(sample_lines) > 1:
            data_commas_set = set(comma_counts[1:])
            if len(data_commas_set) == 1 and list(data_commas_set)[0] > 0:
                return True
                
        return False
    
    def _analyze_csv_content(self, lines: List[str]) -> float:
        """Analyze content to determine if it's CSV format."""
        if not lines or len(lines) == 0:
            return 0.0
            
        # Check first few lines for consistent comma delimiters
        sample_lines = [line for line in lines[:10] if line.strip()]
        if not sample_lines:
            return 0.0

        # All sample lines must contain at least one comma
        if not all(',' in line for line in sample_lines):
            return 0.0

        # Check for consistent comma count
        comma_counts = [line.count(',') for line in sample_lines]
        
        # If all lines have the same number of commas (and > 0)
        if len(set(comma_counts)) == 1 and comma_counts[0] > 0:
            return 0.9
            
        # Allow for a header row with a different number of commas
        if len(sample_lines) > 1:
            data_commas_set = set(comma_counts[1:])
            if len(data_commas_set) == 1 and list(data_commas_set)[0] > 0:
                return 0.8
                
        # If we have commas but not consistent, lower confidence
        if all(count > 0 for count in comma_counts):
            return 0.5
            
        return 0.0
