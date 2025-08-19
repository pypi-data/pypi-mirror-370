"""
Unit tests for PDF requirement extractor.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pdf_requirements_extractor.extractor import PDFRequirementExtractor, ExtractionResult
from pdf_requirements_extractor.utils import validate_pdf, clean_text, extract_patterns
from pdf_requirements_extractor.gpt_parser import GPTParser, GPTConfig, GPTRequirementParser


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
        
        Logo Usage:
        Minimum size: 1 inch
        Clear space: 2x logo height
        
        Contact: brand@company.com
        Website: https://company.com
        
        Hashtags: #BrandName #CompanyStyle
        
        Tagline: "Excellence in Everything"
        
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
        assert "#BrandName" in requirements["hashtags"]
        assert "#CompanyStyle" in requirements["hashtags"]
        
        # Test URLs
        assert "urls" in requirements
        assert "https://company.com" in requirements["urls"]
        
        # Test emails
        assert "emails" in requirements
        assert "brand@company.com" in requirements["emails"]
        
        # Test quoted phrases
        assert "quoted_phrases" in requirements
        assert "Excellence in Everything" in requirements["quoted_phrases"]
        
        # Test colors
        assert "colors" in requirements
        color_found = any("#FF5733" in color or "RGB(255, 87, 51)" in color 
                         for color in requirements["colors"])
        assert color_found
    
    def test_process_brand_requirements(self):
        """Test brand-specific requirement processing."""
        basic_requirements = {
            "quoted_phrases": ["Excellence in Everything", "Quality First"],
            "colors": ["#FF5733"],
        }
        
        enhanced = self.extractor._process_brand_requirements(
            basic_requirements, self.sample_text
        )
        
        assert "tone" in enhanced
        assert "logo_requirements" in enhanced
        assert "spoken_phrases" in enhanced
    
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
    
    def test_extraction_result(self):
        """Test ExtractionResult data class."""
        requirements = {"hashtags": ["#test"], "urls": ["http://example.com"]}
        
        result = ExtractionResult(
            file_name="test.pdf",
            total_pages=1,
            raw_text_excerpt="Test text",
            extracted_requirements=requirements
        )
        
        # Test to_dict
        result_dict = result.to_dict()
        assert result_dict["file_name"] == "test.pdf"
        assert result_dict["extracted_requirements"] == requirements
        
        # Test to_json
        json_str = result.to_json()
        parsed = json.loads(json_str)
        assert parsed["file_name"] == "test.pdf"


class TestUtils:
    """Test cases for utility functions."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  Test   text\n\n\nwith   extra\t\tspaces  \n"
        cleaned = clean_text(dirty_text)
        
        assert cleaned == "Test text with extra spaces"
    
    def test_extract_patterns(self):
        """Test pattern extraction."""
        text = "Contact us at test@example.com or visit https://example.com"
        patterns = {
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "urls": r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*)?",
        }
        
        results = extract_patterns(text, patterns)
        
        assert "test@example.com" in results["emails"]
        assert "https://example.com" in results["urls"]
    
    def test_validate_pdf_invalid_file(self):
        """Test PDF validation with invalid file."""
        assert not validate_pdf("nonexistent.pdf")
    
    def test_validate_pdf_with_temp_file(self):
        """Test PDF validation with temporary file."""
        # Create a temporary file with PDF header
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"%PDF-1.4\ntest content")
            tmp_path = tmp_file.name
        
        try:
            assert validate_pdf(tmp_path)
        finally:
            Path(tmp_path).unlink()
        
        # Test non-PDF file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"not a pdf")
            tmp_path = tmp_file.name
        
        try:
            assert not validate_pdf(tmp_path)
        finally:
            Path(tmp_path).unlink()


class TestGPTParser:
    """Test cases for GPT parser (mocked)."""
    
    def test_gpt_config(self):
        """Test GPT configuration."""
        config = GPTConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=2000
        )
        
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
    
    @patch('pdf_requirements_extractor.gpt_parser.OPENAI_AVAILABLE', True)
    @patch('pdf_requirements_extractor.gpt_parser.OpenAI')
    def test_gpt_parser_initialization(self, mock_openai):
        """Test GPT parser initialization."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        config = GPTConfig(api_key="test-key")
        parser = GPTParser(config)
        
        assert parser.config.api_key == "test-key"
        mock_openai.assert_called_once_with(api_key="test-key")
    
    @patch('pdf_requirements_extractor.gpt_parser.OPENAI_AVAILABLE', True)
    @patch('pdf_requirements_extractor.gpt_parser.OpenAI')
    def test_parse_requirements(self, mock_openai):
        """Test requirement parsing with GPT."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "brand_name": "Test Brand",
            "primary_colors": ["#FF5733"],
            "fonts": {"primary": "Helvetica"}
        })
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        config = GPTConfig(api_key="test-key")
        parser = GPTParser(config)
        
        result = parser.parse_requirements("Test brand guidelines text")
        
        assert result["brand_name"] == "Test Brand"
        assert "#FF5733" in result["primary_colors"]
        assert result["fonts"]["primary"] == "Helvetica"
    
    @patch('pdf_requirements_extractor.gpt_parser.OPENAI_AVAILABLE', False)
    def test_gpt_requirement_parser_no_openai(self):
        """Test GPT requirement parser when OpenAI not available."""
        parser = GPTRequirementParser()
        
        assert not parser.is_available()
        
        result = parser.parse_with_gpt("test text", {"hashtags": ["#test"]})
        assert result == {"hashtags": ["#test"]}


class TestIntegration:
    """Integration tests."""
    
    @patch('pdf_requirements_extractor.extractor.fitz')
    def test_full_extraction_pipeline(self, mock_fitz):
        """Test complete extraction pipeline."""
        # Mock PyMuPDF
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.metadata = {"title": "Brand Guidelines"}
        mock_doc.needs_pass = False
        
        mock_page = MagicMock()
        mock_page.get_text.return_value = """
        Brand Guidelines
        
        Primary Color: #FF5733
        Font: Helvetica Bold
        Email: contact@brand.com
        Website: https://brand.com
        Hashtag: #BrandName
        Logo: "Minimum 1 inch clear space required"
        """
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz.open.return_value = mock_doc
        
        # Test extraction
        extractor = PDFRequirementExtractor()
        
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            tmp_file.write(b"%PDF-1.4\ntest")
            tmp_file.flush()
            
            result = extractor.extract_from_file(tmp_file.name)
            
            assert isinstance(result, ExtractionResult)
            assert result.total_pages == 1
            assert "extracted_requirements" in result.to_dict()
            
            requirements = result.extracted_requirements
            assert "colors" in requirements
            assert "emails" in requirements
            assert "hashtags" in requirements


# Fixtures for pytest
@pytest.fixture
def sample_extractor():
    """Create a sample extractor for testing."""
    return PDFRequirementExtractor()


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    Brand Guidelines
    
    Colors: #FF5733, RGB(255,87,51), Pantone 286 C
    Fonts: Helvetica Neue, Arial Bold
    Email: brand@company.com
    Website: https://company.com
    Hashtags: #Brand #Style
    Quote: "Quality First"
    Phone: (555) 123-4567
    """


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
    assert len(requirements.get("urls", [])) == expected_count


@pytest.mark.parametrize("text,expected_hashtags", [
    ("#Brand #Style", ["#Brand", "#Style"]),
    ("Use #MyBrand for posts", ["#MyBrand"]),
    ("No hashtags here", []),
])
def test_hashtag_extraction(text, expected_hashtags):
    """Test hashtag extraction with different inputs."""
    extractor = PDFRequirementExtractor()
    requirements = extractor._extract_requirements(text)
    hashtags = requirements.get("hashtags", [])
    
    for expected in expected_hashtags:
        assert expected in hashtags
