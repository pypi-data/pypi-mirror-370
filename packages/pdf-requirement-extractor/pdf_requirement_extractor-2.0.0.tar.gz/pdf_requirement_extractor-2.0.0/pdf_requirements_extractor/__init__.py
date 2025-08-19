"""
PDF Requirement Extractor - Extract structured brand requirements from PDF documents.

This package provides tools to extract and parse brand requirements, guidelines,
and specifications from PDF documents using PyMuPDF and optional GPT integration.
"""

from .extractor import PDFRequirementExtractor, ExtractionResult
from .utils import validate_pdf, clean_text, extract_patterns

try:
    from .gpt_parser import GPTParser, GPTRequirementParser
    GPT_AVAILABLE = True
except ImportError:
    GPT_AVAILABLE = False
    GPTParser = None
    GPTRequirementParser = None

__version__ = "2.0.0"
__author__ = "S M Asiful Islam Saky"
__email__ = "saky.aiu22@gmail.com"
__description__ = "Extract structured brand requirements from PDF documents"

__all__ = [
    "PDFRequirementExtractor",
    "ExtractionResult", 
    "validate_pdf",
    "clean_text",
    "extract_patterns",
    "GPTParser",
    "GPTRequirementParser",
    "GPT_AVAILABLE",
]
