"""
Detectors package for content type interpretation.
"""
from .binary_detector import BinarySignatureDetector
from .base_detector import BaseDetector
from .python_detector import PythonDetector
from .yaml_detector import YAMLDetector
from .markdown_detector import MarkdownDetector
from .json_detector import JSONDetector
from .xml_detector import XMLDetector
from .plaintext_detector import PlainTextDetector
from .language_detector import ProgrammingLanguageDetector
from .text_format_detector import TextFormatDetector

__all__ = [
    "BinarySignatureDetector",
    "XMLDetector",
    "ProgrammingLanguageDetector",
    "TextFormatDetector",
]

# Order can matter if you have a strategy that picks the first match above a threshold.
# For a strategy that picks the highest confidence, order is less critical but can break ties.
# More specific/strict detectors might go before more general ones.
DETECTOR_CLASSES = [
    PythonDetector,
    JSONDetector,    # Often very specific structure
    XMLDetector,     # Also specific
    YAMLDetector,
    MarkdownDetector,
    PlainTextDetector # Fallback for general text
]