"""
Core PDF extraction logic using PyMuPDF for extracting structured brand requirements.

This module provides the main PDFRequirementExtractor class that can:
- Extract text from PDF documents using PyMuPDF
- Apply regex patterns to identify brand elements
- Process and structure the extracted data
- Handle both file paths and byte streams
- Support custom extraction patterns

Classes:
    ExtractionResult: Data class for storing extraction results
    PDFRequirementExtractor: Main extraction engine
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError(
        "PyMuPDF is required. Install with: pip install pymupdf"
    )

from .utils import validate_pdf, clean_text, extract_patterns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """
    Data class for PDF extraction results.
    
    This class encapsulates all the information extracted from a PDF document,
    including metadata, raw text, and structured requirements.
    
    Attributes:
        file_name (str): Name of the processed PDF file
        total_pages (int): Number of pages in the PDF
        raw_text_excerpt (str): Truncated raw text from the PDF
        extracted_requirements (Dict[str, Any]): Structured requirements data
        metadata (Optional[Dict[str, Any]]): PDF metadata information
        
    Methods:
        to_dict(): Convert the result to a dictionary
        to_json(): Convert the result to a JSON string
    """
    
    file_name: str
    total_pages: int
    raw_text_excerpt: str
    extracted_requirements: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert extraction result to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the extraction result
        """
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert extraction result to JSON string.
        
        Args:
            indent (int): Number of spaces for JSON indentation
            
        Returns:
            str: JSON string representation of the extraction result
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class PDFRequirementExtractor:
    """
    Extract structured brand requirements from PDF documents.
    
    This class is the main engine for extracting brand guidelines, requirements,
    and specifications from PDF documents. It uses PyMuPDF for text extraction
    and applies regex patterns to identify specific brand elements.
    
    Key Features:
    - Text extraction from PDF pages
    - Pattern-based requirement identification  
    - Support for custom extraction patterns
    - Metadata extraction
    - OCR support (placeholder for future implementation)
    - Comprehensive error handling and logging
    
    Supported Pattern Types:
    - Hashtags (#brand, #marketing)
    - URLs and email addresses
    - Phone numbers
    - Color specifications (HEX, RGB, CMYK, Pantone)
    - Font specifications
    - Dimensions and measurements
    - Quoted phrases and brand terms
    - Logo requirements and guidelines
    
    Example:
        >>> extractor = PDFRequirementExtractor()
        >>> result = extractor.extract_from_file("brand_guide.pdf")
        >>> print(f"Found {len(result.extracted_requirements)} requirement types")
    """
    
    def __init__(self, 
                 max_text_length: int = 1000,
                 enable_ocr: bool = False,
                 custom_patterns: Optional[Dict[str, str]] = None):
        """
        Initialize the PDF requirement extractor.
        
        Sets up the extractor with configuration options and regex patterns
        for identifying brand requirements in PDF documents.
        
        Args:
            max_text_length (int): Maximum length of raw text excerpt to include
                in results. Longer text will be truncated with "..." appended.
                Default is 1000 characters.
            enable_ocr (bool): Whether to enable OCR for scanned PDFs that
                contain no extractable text. Currently a placeholder for
                future OCR implementation. Default is False.
            custom_patterns (Optional[Dict[str, str]]): Custom regex patterns
                for extraction. Keys are pattern names, values are regex strings.
                These will be added to the default patterns.
                
        Example:
            >>> custom_patterns = {
            ...     "social_handles": r"@[A-Za-z0-9_]+",
            ...     "version_numbers": r"v\d+\.\d+"
            ... }
            >>> extractor = PDFRequirementExtractor(
            ...     max_text_length=2000,
            ...     custom_patterns=custom_patterns
            ... )
        """
        self.max_text_length = max_text_length
        self.enable_ocr = enable_ocr
        self.custom_patterns = custom_patterns or {}
        
        # Default regex patterns for brand requirements
        # Each pattern is designed to capture specific types of brand elements
        self.patterns = {
            # Social media hashtags: #BrandName, #Marketing
            "hashtags": r"#[\w\-_]+",
            
            # Web URLs: https://company.com, http://site.org
            "urls": r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
            
            # Email addresses: contact@company.com
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            
            # Quoted brand phrases: "Excellence in Everything"
            "quoted_phrases": r'"([^"]*)"',
            
            # Single quoted phrases: 'Brand Values'
            "single_quoted": r"'([^']*)'",
            
            # Phone numbers: (555) 123-4567, +1-800-555-0123
            "phone_numbers": r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
            
            # Color specifications: RGB, HEX, CMYK, Pantone
            "colors": r"\b(?:RGB|HEX|CMYK|Pantone)\s*:?\s*[#]?[\w\s,()%-]+\b",
            
            # Font specifications: font-family, typeface references
            "fonts": r"\b(?:font|typeface|typography)[\s:]*([\w\s,()-]+)",
            
            # Dimensions and measurements: 12px, 1in, 300dpi
            "dimensions": r"\b\d+\s*(?:px|pt|mm|cm|in|%)\b",
            
            # Brand-related terms: brand, logo, identity, etc.
            "brand_terms": r"\b(?:brand|logo|identity|guideline|standard|requirement|specification)\b",
        }
        
        # Merge custom patterns with defaults (custom patterns override defaults)
        self.patterns.update(self.custom_patterns)
        
        logger.info(f"Initialized PDFRequirementExtractor with {len(self.patterns)} patterns")
    
    def extract_from_file(self, file_path: Union[str, Path]) -> ExtractionResult:
        """
        Extract requirements from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ExtractionResult: Structured extraction results
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not validate_pdf(file_path):
            raise ValueError(f"Invalid PDF file: {file_path}")
        
        logger.info(f"Extracting requirements from: {file_path.name}")
        
        try:
            # Open PDF document
            doc = fitz.open(str(file_path))
            
            # Extract metadata
            metadata = self._extract_metadata(doc)
            
            # Extract text from all pages
            raw_text = self._extract_text(doc)
            
            # Clean and process text
            cleaned_text = clean_text(raw_text)
            
            # Extract structured requirements
            requirements = self._extract_requirements(cleaned_text)
            
            # Create text excerpt
            text_excerpt = cleaned_text[:self.max_text_length]
            if len(cleaned_text) > self.max_text_length:
                text_excerpt += "..."
            
            # Store page count before closing document
            page_count = len(doc)
            doc.close()
            
            result = ExtractionResult(
                file_name=file_path.name,
                total_pages=page_count,
                raw_text_excerpt=text_excerpt,
                extracted_requirements=requirements,
                metadata=metadata
            )
            
            logger.info(f"Successfully extracted requirements from {file_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from {file_path}: {str(e)}")
            raise
    
    def extract_from_bytes(self, pdf_bytes: bytes, file_name: str = "document.pdf") -> ExtractionResult:
        """
        Extract requirements from PDF bytes.
        
        Args:
            pdf_bytes: PDF file as bytes
            file_name: Name to use for the document
            
        Returns:
            ExtractionResult: Structured extraction results
        """
        logger.info(f"Extracting requirements from bytes: {file_name}")
        
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Extract metadata
            metadata = self._extract_metadata(doc)
            
            # Extract text from all pages
            raw_text = self._extract_text(doc)
            
            # Clean and process text
            cleaned_text = clean_text(raw_text)
            
            # Extract structured requirements
            requirements = self._extract_requirements(cleaned_text)
            
            # Create text excerpt
            text_excerpt = cleaned_text[:self.max_text_length]
            if len(cleaned_text) > self.max_text_length:
                text_excerpt += "..."
            
            # Store page count before closing document
            page_count = len(doc)
            doc.close()
            
            result = ExtractionResult(
                file_name=file_name,
                total_pages=page_count,
                raw_text_excerpt=text_excerpt,
                extracted_requirements=requirements,
                metadata=metadata
            )
            
            logger.info(f"Successfully extracted requirements from {file_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from bytes: {str(e)}")
            raise
    
    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """
        Extract PDF metadata information.
        
        Retrieves document properties like title, author, creation date, etc.
        This metadata is useful for document identification and context.
        
        Args:
            doc (fitz.Document): Opened PyMuPDF document object
            
        Returns:
            Dict[str, Any]: Dictionary containing metadata fields:
                - title: Document title
                - author: Document author
                - subject: Document subject
                - creator: Application that created the document
                - producer: PDF producer software
                - creation_date: When the document was created
                - modification_date: When the document was last modified
                - pages: Number of pages
                - encrypted: Whether the document is password protected
                
        Note:
            If metadata extraction fails, returns minimal info with page count.
        """
        try:
            metadata = doc.metadata
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "pages": len(doc),
                "encrypted": doc.needs_pass,
            }
        except Exception as e:
            logger.warning(f"Could not extract metadata: {str(e)}")
            return {"pages": len(doc)}
    
    def _extract_text(self, doc: fitz.Document) -> str:
        """
        Extract text from all pages of the PDF document.
        
        Iterates through each page and extracts readable text. For scanned PDFs
        or pages with no extractable text, OCR can be optionally applied
        (currently a placeholder for future implementation).
        
        Args:
            doc (fitz.Document): Opened PyMuPDF document object
            
        Returns:
            str: Combined text from all pages, with page separators.
                Format: "--- Page N ---\n[page text]\n\n--- Page N+1 ---\n..."
                
        Note:
            - Empty pages are skipped
            - OCR is not yet implemented but placeholder exists
            - Page extraction errors are logged but don't stop processing
        """
        text_parts = []
        
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                
                # Extract text using PyMuPDF's built-in text extraction
                page_text = page.get_text()
                
                # If OCR is enabled and no text found, attempt OCR
                # Note: This is a placeholder for future OCR implementation
                if self.enable_ocr and not page_text.strip():
                    try:
                        # Convert page to image for OCR processing
                        pix = page.get_pixmap()
                        img_data = pix.tobytes("png")
                        # TODO: Implement pytesseract OCR here
                        logger.warning(f"Page {page_num + 1} contains no text, OCR not implemented")
                    except Exception as ocr_error:
                        logger.warning(f"OCR failed for page {page_num + 1}: {str(ocr_error)}")
                
                # Only include pages with actual text content
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                
            except Exception as e:
                logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
        
        return "\n\n".join(text_parts)
    
    def _extract_requirements(self, text: str) -> Dict[str, Any]:
        """
        Extract structured requirements from text using regex patterns.
        
        Applies all configured regex patterns to the input text and organizes
        the results into a structured dictionary. Handles different pattern types
        appropriately (e.g., groups vs. full matches) and provides fallback
        for pattern matching errors.
        
        Args:
            text (str): Cleaned text from PDF document to analyze
            
        Returns:
            Dict[str, Any]: Dictionary of extracted requirements with pattern
                names as keys and lists of matches as values. Also includes
                enhanced brand-specific requirements like tone analysis.
                
        Note:
            - Patterns with regex groups extract the group content
            - Simple patterns extract the full match
            - Duplicate matches are automatically removed
            - Empty results are included as empty lists for consistency
        """
        requirements = {}
        
        for pattern_name, pattern in self.patterns.items():
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                
                # Handle patterns with groups (e.g., quoted text extraction)
                if pattern_name in ["quoted_phrases", "single_quoted", "fonts"]:
                    # For patterns with groups, extract the groups
                    if matches:
                        requirements[pattern_name] = list(set(match if isinstance(match, str) else match[0] for match in matches))
                    else:
                        requirements[pattern_name] = []
                else:
                    # For simple patterns, use the full match
                    requirements[pattern_name] = list(set(matches)) if matches else []
                
                logger.debug(f"Found {len(requirements[pattern_name])} {pattern_name}")
                
            except Exception as e:
                logger.warning(f"Error extracting {pattern_name}: {str(e)}")
                requirements[pattern_name] = []
        
        # Additional processing for brand-specific requirements
        requirements = self._process_brand_requirements(requirements, text)
        
        return requirements
    
    def _process_brand_requirements(self, requirements: Dict[str, Any], text: str) -> Dict[str, Any]:
        """
        Process and enhance brand-specific requirements.
        
        Performs additional analysis on the extracted text to identify brand-specific
        elements that require more sophisticated processing than simple regex matching.
        This includes tone analysis, logo requirement extraction, and brand phrase
        identification.
        
        Args:
            requirements (Dict[str, Any]): Initial requirements extracted by patterns
            text (str): Original text for additional analysis
            
        Returns:
            Dict[str, Any]: Enhanced requirements dictionary with additional fields:
                - tone: List of detected brand tones (formal, casual, modern, etc.)
                - logo_requirements: List of logo usage guidelines found
                - spoken_phrases: List of potential taglines/slogans from quotes
                
        Processing Steps:
        1. Tone Analysis: Searches for tone indicator keywords
        2. Logo Requirements: Extracts logo-related guidelines and rules
        3. Spoken Phrases: Filters quoted text for potential taglines
        4. Cleanup: Removes empty requirement categories
        """
        
        # Analyze tone and style indicators
        tone_indicators = {
            "formal": ["formal", "professional", "corporate", "official"],
            "casual": ["casual", "friendly", "approachable", "relaxed"],
            "modern": ["modern", "contemporary", "sleek", "minimalist"],
            "traditional": ["traditional", "classic", "timeless", "established"],
            "playful": ["playful", "fun", "energetic", "vibrant"],
            "sophisticated": ["sophisticated", "elegant", "refined", "premium"]
        }
        
        detected_tones = []
        text_lower = text.lower()
        
        for tone, indicators in tone_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                detected_tones.append(tone)
        
        requirements["tone"] = detected_tones
        
        # Extract logo requirements and usage guidelines
        logo_keywords = [
            "logo", "symbol", "icon", "mark", "emblem", "badge",
            "placement", "size", "spacing", "clear space", "minimum size"
        ]
        
        logo_requirements = []
        for keyword in logo_keywords:
            # Find sentences containing logo-related keywords
            pattern = rf"(?i)\b{keyword}\b.*?[.!?]"
            matches = re.findall(pattern, text)
            logo_requirements.extend(matches)
        
        # Limit and deduplicate logo requirements
        requirements["logo_requirements"] = list(set(logo_requirements[:10]))
        
        # Extract spoken phrases (potential taglines or slogans from quotes)
        spoken_phrases = []
        all_quoted = requirements.get("quoted_phrases", []) + requirements.get("single_quoted", [])
        
        for phrase in all_quoted:
            # Filter for phrases that look like taglines or slogans
            # - Not too long (max 10 words)
            # - Not too short (min 3 characters)
            # - Contains meaningful content
            if len(phrase.split()) <= 10 and len(phrase) > 3:
                spoken_phrases.append(phrase)
        
        requirements["spoken_phrases"] = spoken_phrases
        
        # Clean up empty lists (but keep tone even if empty for consistency)
        requirements = {k: v for k, v in requirements.items() if v or k in ["tone"]}
        
        return requirements
    
    def add_custom_pattern(self, name: str, pattern: str) -> None:
        """
        Add a custom regex pattern for extraction.
        
        Allows dynamic addition of new extraction patterns after initialization.
        The pattern will be applied during the next extraction operation.
        
        Args:
            name (str): Name for the pattern (will be used as key in results)
            pattern (str): Regular expression pattern to match
            
        Example:
            >>> extractor.add_custom_pattern("social_handles", r"@[A-Za-z0-9_]+")
            >>> extractor.add_custom_pattern("version_numbers", r"v\d+\.\d+")
            
        Note:
            If a pattern with the same name already exists, it will be overwritten.
        """
        self.patterns[name] = pattern
        logger.info(f"Added custom pattern '{name}': {pattern}")
    
    def get_supported_patterns(self) -> Dict[str, str]:
        """
        Get all supported extraction patterns.
        
        Returns a copy of the current pattern dictionary, including both
        default patterns and any custom patterns that have been added.
        
        Returns:
            Dict[str, str]: Dictionary mapping pattern names to regex strings
            
        Example:
            >>> extractor = PDFRequirementExtractor()
            >>> patterns = extractor.get_supported_patterns()
            >>> print(f"Supports {len(patterns)} pattern types:")
            >>> for name in patterns:
            ...     print(f"  - {name}")
        """
        return self.patterns.copy()
