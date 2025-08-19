"""
Helper functions for PDF requirement extraction.

This module provides utility functions that support the main extraction process:
- PDF file validation
- Text cleaning and normalization  
- Pattern extraction utilities
- Color, dimension, and font extraction
- Contact information parsing
- Brand guideline detection
- Text filtering and validation

These utilities are used by the main PDFRequirementExtractor class but can
also be used independently for custom processing workflows.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)


def validate_pdf(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file is a valid PDF document.
    
    Performs multiple checks to ensure the file is a readable PDF:
    1. File exists and is accessible
    2. Has .pdf extension
    3. Contains PDF magic number (%PDF) at the beginning
    
    Args:
        file_path (Union[str, Path]): Path to the file to validate
        
    Returns:
        bool: True if the file is a valid PDF, False otherwise
        
    Example:
        >>> if validate_pdf("document.pdf"):
        ...     print("Valid PDF file")
        ... else:
        ...     print("Invalid or corrupted PDF")
        
    Note:
        This function only checks basic PDF validity, not whether
        the content is extractable or well-formed.
    """
    try:
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return False
        
        # Check file extension
        if not file_path.suffix.lower() == '.pdf':
            return False
        
        # Check PDF magic number (first 4 bytes should be '%PDF')
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
            
    except Exception as e:
        logger.warning(f"Error validating PDF {file_path}: {str(e)}")
        return False


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text from PDF documents.
    
    Performs comprehensive text cleaning to improve pattern matching:
    - Normalizes whitespace (removes extra spaces, tabs, newlines)
    - Removes control characters that can interfere with processing
    - Strips common PDF artifacts (page numbers, headers/footers)
    - Normalizes quotes to standard ASCII characters
    - Reduces excessive punctuation and line breaks
    
    Args:
        text (str): Raw extracted text from PDF
        
    Returns:
        str: Cleaned and normalized text ready for pattern extraction
        
    Example:
        >>> raw_text = "Brand   Guidelines\\n\\n\\n   Page 1\\n---"
        >>> clean_text(raw_text)
        "Brand Guidelines Page 1 ---"
        
    Note:
        This function is designed to be aggressive in cleaning while
        preserving meaningful content for brand requirement extraction.
    """
    if not text:
        return ""
    
    # Remove excessive whitespace (multiple spaces, tabs, etc.)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters that can cause issues
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
    
    # Remove standalone page numbers (common PDF artifact)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Replace repeated dashes or underscores with standardized separator
    text = re.sub(r'[-_]{3,}', '---', text)
    
    # Normalize quotation marks to standard ASCII quotes
    text = text.replace('"', '"').replace('"', '"')  # Smart quotes to straight quotes
    text = text.replace(''', "'").replace(''', "'")  # Smart apostrophes to straight quotes
    
    # Reduce excessive line breaks (3+ newlines become 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def extract_patterns(text: str, patterns: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Extract patterns from text using provided regex patterns.
    
    Args:
        text: Text to search in
        patterns: Dictionary of pattern names and regex patterns
        
    Returns:
        Dict[str, List[str]]: Dictionary of pattern names and matches
    """
    results = {}
    
    for pattern_name, pattern in patterns.items():
        try:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            results[pattern_name] = list(set(matches)) if matches else []
        except Exception as e:
            logger.warning(f"Error extracting pattern '{pattern_name}': {str(e)}")
            results[pattern_name] = []
    
    return results


def extract_colors(text: str) -> List[str]:
    """
    Extract color specifications from text.
    
    Args:
        text: Text to search for colors
        
    Returns:
        List[str]: List of color specifications found
    """
    color_patterns = [
        r'#[0-9A-Fa-f]{6}',  # Hex colors
        r'#[0-9A-Fa-f]{3}',   # Short hex colors
        r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',  # RGB
        r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)',  # RGBA
        r'hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)',  # HSL
        r'cmyk\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',  # CMYK
        r'pantone\s+\d+\s*[cu]?',  # Pantone colors
    ]
    
    colors = []
    for pattern in color_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        colors.extend(matches)
    
    return list(set(colors))


def extract_dimensions(text: str) -> List[str]:
    """
    Extract dimension specifications from text.
    
    Args:
        text: Text to search for dimensions
        
    Returns:
        List[str]: List of dimensions found
    """
    dimension_patterns = [
        r'\d+\s*(?:px|pt|mm|cm|in|em|rem|%)',  # Common units
        r'\d+\s*x\s*\d+\s*(?:px|pt|mm|cm|in)',  # Width x Height
        r'\d+\.?\d*\s*(?:inches?|feet?|ft)',  # Imperial units
    ]
    
    dimensions = []
    for pattern in dimension_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dimensions.extend(matches)
    
    return list(set(dimensions))


def extract_fonts(text: str) -> List[str]:
    """
    Extract font specifications from text.
    
    Args:
        text: Text to search for fonts
        
    Returns:
        List[str]: List of font specifications found
    """
    font_patterns = [
        r'(?:font-family|typeface|font):\s*([^;,\n]+)',
        r'(?:use|using)\s+([A-Za-z\s]+)\s+(?:font|typeface)',
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:font|typeface)',
        r'(?:Arial|Helvetica|Times|Calibri|Georgia|Verdana|Trebuchet|Impact)[^,\n]*',
    ]
    
    fonts = []
    for pattern in font_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        fonts.extend(matches)
    
    # Clean font names
    cleaned_fonts = []
    for font in fonts:
        font = font.strip().strip('"\'')
        if font and len(font) > 2:
            cleaned_fonts.append(font)
    
    return list(set(cleaned_fonts))


def extract_contact_info(text: str) -> Dict[str, List[str]]:
    """
    Extract contact information from text.
    
    Args:
        text: Text to search for contact info
        
    Returns:
        Dict[str, List[str]]: Dictionary with emails, phones, addresses
    """
    patterns = {
        'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phones': r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
        'websites': r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*)?',
    }
    
    return extract_patterns(text, patterns)


def is_brand_guideline_pdf(text: str) -> bool:
    """
    Check if PDF appears to be a brand guideline document.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        bool: True if appears to be brand guidelines
    """
    brand_keywords = [
        'brand guideline', 'brand guide', 'style guide', 'brand standard',
        'brand identity', 'corporate identity', 'visual identity',
        'logo usage', 'brand book', 'brand manual', 'design system'
    ]
    
    text_lower = text.lower()
    keyword_count = sum(1 for keyword in brand_keywords if keyword in text_lower)
    
    # If we find multiple brand-related keywords, likely a brand guide
    return keyword_count >= 2


def extract_requirements_summary(requirements: Dict[str, Any]) -> str:
    """
    Generate a summary of extracted requirements.
    
    Args:
        requirements: Dictionary of extracted requirements
        
    Returns:
        str: Human-readable summary
    """
    summary_parts = []
    
    # Count findings
    total_findings = sum(len(v) if isinstance(v, list) else (1 if v else 0) 
                        for v in requirements.values())
    
    summary_parts.append(f"Found {total_findings} total requirement elements:")
    
    for key, value in requirements.items():
        if isinstance(value, list) and value:
            summary_parts.append(f"  • {len(value)} {key.replace('_', ' ')}")
        elif value and not isinstance(value, list):
            summary_parts.append(f"  • {key.replace('_', ' ')}: {value}")
    
    return '\n'.join(summary_parts)


def filter_noise_text(text: str) -> str:
    """
    Remove common noise patterns from extracted text.
    
    Args:
        text: Text to filter
        
    Returns:
        str: Filtered text
    """
    # Remove common PDF artifacts
    noise_patterns = [
        r'\bPage \d+ of \d+\b',  # Page numbers
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # Dates
        r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\b',  # Times
        r'\bCopyright.*?\d{4}\b',  # Copyright notices
        r'\b(?:Confidential|Internal|Private|Proprietary)\b',  # Confidentiality markers
        r'\b(?:Draft|Version|Rev|v)\s*\d+(?:\.\d+)*\b',  # Version numbers
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return clean_text(text)


def validate_extraction_result(result: Dict[str, Any]) -> bool:
    """
    Validate that extraction result has required fields.
    
    Args:
        result: Extraction result to validate
        
    Returns:
        bool: True if valid result structure
    """
    required_fields = [
        'file_name', 'total_pages', 'raw_text_excerpt', 'extracted_requirements'
    ]
    
    return all(field in result for field in required_fields)
