"""
Basic tests for PDF requirement extractor.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pdf_requirements_extractor import PDFRequirementExtractor, ExtractionResult
from pdf_requirements_extractor.utils import clean_text, validate_pdf
from pdf_requirements_extractor.gpt_parser import GPTConfig


class TestPDFRequirementExtractor:
    """Test cases for PDFRequirementExtractor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFRequirementExtractor()
        
        # Sample text for testing
        self.sample_text = """
        Brand Guidelines Document
        
        Colors:
        Primary: #FF5733 (Hex), RGB(255, 87, 51)
        Secondary: Pantone 286 C
        
        Typography:
        Primary font: Helvetica Neue Bold
        Body font: Arial Regular
        
        Contact: brand@company.com
        Website: https://company.com
        
        Hashtags: #BrandName #CompanyStyle
        
        Phone: (555) 123-4567
        """
    
    def test_initialization(self):
        """Test extractor initialization."""
        assert self.extractor.max_text_length == 1000
        assert not self.extractor.enable_ocr
        assert len(self.extractor.patterns) > 0
    
    def test_custom_patterns(self):
        """Test adding custom patterns."""
        custom_patterns = {"test_pattern": r"\btest\b"}
        extractor = PDFRequirementExtractor(custom_patterns=custom_patterns)
        
        assert "test_pattern" in extractor.patterns
        assert extractor.patterns["test_pattern"] == r"\btest\b"
    
    def test_add_custom_pattern(self):
        """Test adding pattern after initialization."""
        self.extractor.add_custom_pattern("new_pattern", r"\bnew\b")
        assert "new_pattern" in self.extractor.patterns
    
    def test_extract_requirements(self):
        """Test requirement extraction from text."""
        requirements = self.extractor._extract_requirements(self.sample_text)
        
        # Test hashtags
        assert "hashtags" in requirements
        hashtags = requirements["hashtags"]
        assert any("#BrandName" in str(hashtags))
        
        # Test URLs
        assert "urls" in requirements
        urls = requirements["urls"]
        assert any("https://company.com" in str(urls))
        
        # Test emails
        assert "emails" in requirements
        emails = requirements["emails"]
        assert any("brand@company.com" in str(emails))
    
    @patch('pdf_requirements_extractor.extractor.fitz')
    def test_extract_from_bytes(self, mock_fitz):
        """Test extraction from PDF bytes."""
        # Mock PyMuPDF document
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2
        mock_doc.metadata = {
            "title": "Test Doc",
            "author": "Test Author"
        }
        mock_doc.needs_pass = False
        
        # Mock page
        mock_page = MagicMock()
        mock_page.get_text.return_value = self.sample_text
        mock_doc.__getitem__.return_value = mock_page
        
        mock_fitz.open.return_value = mock_doc
        
        # Test extraction
        pdf_bytes = b"%PDF-1.4 test content"
        result = self.extractor.extract_from_bytes(pdf_bytes, "test.pdf")
        
        assert isinstance(result, ExtractionResult)
        assert result.file_name == "test.pdf"
        assert result.total_pages == 2
        assert "extracted_requirements" in result.to_dict()


class TestUtils:
    """Test cases for utility functions."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  Test   text\n\n\nwith   extra\t\tspaces  \n"
        cleaned = clean_text(dirty_text)
        
        assert cleaned == "Test text with extra spaces"
    
    def test_validate_pdf_invalid_file(self):
        """Test PDF validation with invalid file."""
        assert not validate_pdf("nonexistent.pdf")


class TestGPTConfig:
    """Test cases for GPT configuration."""
    
    def test_gpt_config_creation(self):
        """Test GPT configuration creation."""
        config = GPTConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=2000
        )
        
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
    
    def test_factory_methods(self):
        """Test GPT config factory methods."""
        cost_config = GPTConfig.for_cost_effective()
        quality_config = GPTConfig.for_high_quality()
        mini_config = GPTConfig.for_mini_model()
        
        assert cost_config.model == "gpt-3.5-turbo"
        assert quality_config.model == "gpt-4"
        assert mini_config.model == "gpt-4o-mini"


# Basic integration test
def test_package_import():
    """Test that the package can be imported."""
    import pdf_requirements_extractor
    assert pdf_requirements_extractor.__version__ == "1.0.0"


# Parametrized tests
@pytest.mark.parametrize("text,expected_count", [
    ("Visit https://example.com", 1),
    ("Check https://site1.com and https://site2.com", 2),
    ("No URLs here", 0),
])
def test_url_extraction(text, expected_count):
    """Test URL extraction with different inputs."""
    extractor = PDFRequirementExtractor()
    requirements = extractor._extract_requirements(text)
    urls = requirements.get("urls", [])
    assert len(urls) == expected_count


@pytest.mark.parametrize("text,expected_hashtags", [
    ("#Brand #Style", 2),
    ("Use #MyBrand for posts", 1),
    ("No hashtags here", 0),
])
def test_hashtag_extraction(text, expected_hashtags):
    """Test hashtag extraction with different inputs."""
    extractor = PDFRequirementExtractor()
    requirements = extractor._extract_requirements(text)
    hashtags = requirements.get("hashtags", [])
    assert len(hashtags) == expected_hashtags
