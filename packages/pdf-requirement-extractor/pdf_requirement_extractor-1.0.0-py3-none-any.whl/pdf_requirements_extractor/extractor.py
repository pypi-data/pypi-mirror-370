"""
Core PDF extraction logic using PyMuPDF for extracting structured brand requirements.
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
    """Data class for PDF extraction results."""
    
    file_name: str
    total_pages: int
    raw_text_excerpt: str
    extracted_requirements: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class PDFRequirementExtractor:
    """
    Extract structured brand requirements from PDF documents.
    
    This class uses PyMuPDF to extract text and applies regex patterns to identify
    hashtags, URLs, quoted phrases, and other brand requirement elements.
    """
    
    def __init__(self, 
                 max_text_length: int = 1000,
                 enable_ocr: bool = False,
                 custom_patterns: Optional[Dict[str, str]] = None):
        """
        Initialize the PDF requirement extractor.
        
        Args:
            max_text_length: Maximum length of raw text excerpt to include
            enable_ocr: Whether to enable OCR for scanned PDFs
            custom_patterns: Custom regex patterns for extraction
        """
        self.max_text_length = max_text_length
        self.enable_ocr = enable_ocr
        self.custom_patterns = custom_patterns or {}
        
        # Default regex patterns for brand requirements
        self.patterns = {
            "hashtags": r"#[\w\-_]+",
            "urls": r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "quoted_phrases": r'"([^"]*)"',
            "single_quoted": r"'([^']*)'",
            "phone_numbers": r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
            "colors": r"\b(?:RGB|HEX|CMYK|Pantone)\s*:?\s*[#]?[\w\s,()%-]+\b",
            "fonts": r"\b(?:font|typeface|typography)[\s:]*([\w\s,()-]+)",
            "dimensions": r"\b\d+\s*(?:px|pt|mm|cm|in|%)\b",
            "brand_terms": r"\b(?:brand|logo|identity|guideline|standard|requirement|specification)\b",
        }
        
        # Update with custom patterns
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
        """Extract PDF metadata."""
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
        """Extract text from all pages of the PDF."""
        text_parts = []
        
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                
                # Extract text
                page_text = page.get_text()
                
                # If OCR is enabled and no text found, try OCR
                if self.enable_ocr and not page_text.strip():
                    try:
                        # Convert page to image and OCR
                        pix = page.get_pixmap()
                        img_data = pix.tobytes("png")
                        # Note: Would need pytesseract for OCR
                        # This is a placeholder for OCR functionality
                        logger.warning(f"Page {page_num + 1} contains no text, OCR not implemented")
                    except Exception as ocr_error:
                        logger.warning(f"OCR failed for page {page_num + 1}: {str(ocr_error)}")
                
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                
            except Exception as e:
                logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
        
        return "\n\n".join(text_parts)
    
    def _extract_requirements(self, text: str) -> Dict[str, Any]:
        """Extract structured requirements from text using regex patterns."""
        requirements = {}
        
        for pattern_name, pattern in self.patterns.items():
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                
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
        """Process and enhance brand-specific requirements."""
        
        # Analyze tone and style
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
        
        # Extract logo requirements
        logo_keywords = [
            "logo", "symbol", "icon", "mark", "emblem", "badge",
            "placement", "size", "spacing", "clear space", "minimum size"
        ]
        
        logo_requirements = []
        for keyword in logo_keywords:
            pattern = rf"(?i)\b{keyword}\b.*?[.!?]"
            matches = re.findall(pattern, text)
            logo_requirements.extend(matches)
        
        requirements["logo_requirements"] = list(set(logo_requirements[:10]))  # Limit to 10
        
        # Extract spoken phrases (things in quotes that sound like taglines or slogans)
        spoken_phrases = []
        all_quoted = requirements.get("quoted_phrases", []) + requirements.get("single_quoted", [])
        
        for phrase in all_quoted:
            # Filter for phrases that look like taglines or slogans
            if len(phrase.split()) <= 10 and len(phrase) > 3:
                spoken_phrases.append(phrase)
        
        requirements["spoken_phrases"] = spoken_phrases
        
        # Clean up empty lists
        requirements = {k: v for k, v in requirements.items() if v or k in ["tone"]}
        
        return requirements
    
    def add_custom_pattern(self, name: str, pattern: str) -> None:
        """Add a custom regex pattern for extraction."""
        self.patterns[name] = pattern
        logger.info(f"Added custom pattern '{name}': {pattern}")
    
    def get_supported_patterns(self) -> Dict[str, str]:
        """Get all supported extraction patterns."""
        return self.patterns.copy()
