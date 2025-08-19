# PDF Requirement Extractor

[![Python Version](https://img.shields.io/pypi/pyversions/pdf-requirement-extractor)](https://pypi.org/project/pdf-requirement-extractor/)
[![PyPI Version](https://img.shields.io/pypi/v/pdf-requirement-extractor)](https://pypi.org/project/pdf-requirement-extractor/)
[![License](https://img.shields.io/github/license/yourusername/pdf-requirement-extractor)](https://github.com/yourusername/pdf-requirement-extractor/blob/main/LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/yourusername/pdf-requirement-extractor/tests.yml)](https://github.com/yourusername/pdf-requirement-extractor/actions)

A powerful Python package for extracting structured brand requirements from PDF documents using PyMuPDF and optional GPT enhancement.

## 🚀 Features

- **📄 PDF Text Extraction**: Extract text from PDF documents using PyMuPDF (fitz)
- **🔍 Pattern Recognition**: Detect hashtags, URLs, emails, colors, fonts, and more using regex
- **🤖 GPT Enhancement**: Optional GPT-powered analysis for deeper insights (requires OpenAI API)
- **📊 Structured Output**: Get results in JSON format with organized categories
- **🎨 Brand-Specific**: Tailored for brand guidelines, style guides, and requirement documents  
- **⚡ Fast & Efficient**: Optimized for batch processing of multiple documents
- **🔧 Customizable**: Add custom regex patterns for specific extraction needs
- **💪 Type Hints**: Full type annotation support for better development experience

## 📦 Installation

### Basic Installation
```bash
pip install pdf-requirement-extractor
```

### With GPT Enhancement
```bash
pip install pdf-requirement-extractor[gpt]
```

### With OCR Support  
```bash
pip install pdf-requirement-extractor[ocr]
```

### Development Installation
```bash
pip install pdf-requirement-extractor[dev]
```

### All Features
```bash
pip install pdf-requirement-extractor[all]
```

## 🔧 Quick Start

### Basic Usage

```python
from pdf_requirement_extractor import PDFRequirementExtractor

# Initialize the extractor
extractor = PDFRequirementExtractor()

# Extract requirements from a PDF file
result = extractor.extract_from_file("brand_guidelines.pdf")

# Access the results
print(f"Document: {result.file_name}")
print(f"Pages: {result.total_pages}")
print(f"Requirements found: {len(result.extracted_requirements)}")

# Get specific requirement categories
requirements = result.extracted_requirements
hashtags = requirements.get("hashtags", [])
colors = requirements.get("colors", [])
fonts = requirements.get("fonts", [])

print(f"Hashtags: {hashtags}")
print(f"Colors: {colors}")
print(f"Fonts: {fonts}")
```

### Enhanced Extraction with GPT

```python
import os
from pdf_requirement_extractor import PDFRequirementExtractor
from pdf_requirement_extractor.gpt_parser import GPTRequirementParser, GPTConfig

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Configure GPT (model must be explicitly specified)
gpt_config = GPTConfig(
    model="gpt-3.5-turbo",  # Model is required - specify your preferred model
    temperature=0.3,
    max_tokens=1500
)

# Or use factory methods for common configurations:
# gpt_config = GPTConfig.for_cost_effective()      # gpt-3.5-turbo optimized
# gpt_config = GPTConfig.for_high_quality()        # gpt-4 optimized  
# gpt_config = GPTConfig.for_fast_processing()     # gpt-3.5-turbo fast
# gpt_config = GPTConfig.for_mini_model()          # gpt-4o-mini cost-effective

# Initialize enhanced parser
parser = GPTRequirementParser(gpt_config=gpt_config)

# Basic extraction first
extractor = PDFRequirementExtractor()
basic_result = extractor.extract_from_file("brand_guidelines.pdf")

# Enhance with GPT
enhanced_requirements = parser.parse_with_gpt(
    basic_result.raw_text_excerpt,
    basic_result.extracted_requirements
)

# Access enhanced results
print("Enhanced requirements:")
for category, data in enhanced_requirements.items():
    print(f"{category}: {data}")
```

### Custom Pattern Extraction

```python
from pdf_requirement_extractor import PDFRequirementExtractor

# Define custom patterns
custom_patterns = {
    "social_handles": r"@[A-Za-z0-9_]+",
    "price_mentions": r"\$\d+(?:\.\d{2})?",
    "version_numbers": r"v?\d+\.\d+(?:\.\d+)?",
}

# Initialize with custom patterns
extractor = PDFRequirementExtractor(custom_patterns=custom_patterns)

# Extract with custom patterns
result = extractor.extract_from_file("document.pdf")
social_handles = result.extracted_requirements.get("social_handles", [])
```

### Batch Processing

```python
from pdf_requirement_extractor import PDFRequirementExtractor
import json
from pathlib import Path

# Initialize extractor
extractor = PDFRequirementExtractor()

# Process multiple files
pdf_files = Path("pdf_directory").glob("*.pdf")
results = []

for pdf_file in pdf_files:
    try:
        result = extractor.extract_from_file(pdf_file)
        results.append(result.to_dict())
        print(f"✅ Processed: {pdf_file.name}")
    except Exception as e:
        print(f"❌ Error processing {pdf_file.name}: {e}")

# Save all results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## 📊 Output Format

The extractor returns structured JSON with the following format:

```json
{
  "file_name": "brand_guidelines.pdf",
  "total_pages": 24,
  "raw_text_excerpt": "Brand Guidelines Document...",
  "extracted_requirements": {
    "hashtags": ["#BrandName", "#QualityFirst"],
    "urls": ["https://company.com", "https://support.company.com"],
    "emails": ["contact@company.com", "support@company.com"],
    "colors": ["#FF5733", "RGB(255, 87, 51)", "Pantone 286 C"],
    "fonts": ["Helvetica Neue Bold", "Arial Regular"],
    "quoted_phrases": ["Excellence in Everything", "Your Trusted Partner"],
    "phone_numbers": ["(555) 123-4567", "1-800-COMPANY"],
    "dimensions": ["1 inch", "12pt", "300 DPI"],
    "tone": ["professional", "modern"],
    "logo_requirements": ["Minimum size: 1 inch", "Clear space required"],
    "spoken_phrases": ["Excellence in Everything"]
  },
  "metadata": {
    "title": "Brand Guidelines",
    "author": "Design Team", 
    "pages": 24,
    "creation_date": "2024-01-15"
  }
}
```

## 🎯 Supported Extraction Patterns

### Default Patterns

The package comes with built-in patterns for:

- **Hashtags**: `#BrandName`, `#Marketing`
- **URLs**: `https://company.com`, `www.example.org`
- **Emails**: `contact@company.com`
- **Phone Numbers**: `(555) 123-4567`, `+1-800-555-0123`
- **Colors**: `#FF5733`, `RGB(255,87,51)`, `Pantone 286 C`
- **Fonts**: Font family names and specifications
- **Dimensions**: `12pt`, `1 inch`, `300 DPI`, `50px`
- **Quoted Text**: `"Brand taglines"`, `'Voice guidelines'`
- **Brand Terms**: Keywords related to brand guidelines

### Custom Patterns

Add your own regex patterns:

```python
extractor.add_custom_pattern("social_handles", r"@[A-Za-z0-9_]+")
extractor.add_custom_pattern("price_ranges", r"\$\d+-\$\d+")
extractor.add_custom_pattern("dates", r"\b\d{1,2}/\d{1,2}/\d{4}\b")
```

## 🤖 GPT Enhancement Features

When using GPT enhancement, you get:

### Advanced Analysis
- **Brand Name Detection**: Automatic brand name identification
- **Tone Analysis**: Professional, casual, modern, traditional classifications
- **Logo Guidelines**: Structured logo usage rules and restrictions
- **Color Categorization**: Primary, secondary, accent color groupings
- **Typography Hierarchy**: Primary, secondary, body font classifications

### Strategic Insights
- **Priority Levels**: Importance ranking for each requirement
- **Implementation Notes**: Practical guidance for applying guidelines
- **Compliance Analysis**: Risk assessment for brand consistency
- **Missing Elements**: Identification of gaps in brand guidelines

### Enhanced Structure
```json
{
  "brand_name": "Company Name",
  "document_type": "Brand Guidelines",
  "primary_colors": ["#FF5733", "#0066CC"],
  "fonts": {
    "primary": "Helvetica Neue Bold",
    "secondary": "Arial Regular",
    "body": "Open Sans"
  },
  "logo_requirements": {
    "minimum_size": "1 inch",
    "clear_space": "2x logo height",
    "usage_rules": ["Always use on white background"],
    "prohibited_uses": ["Never stretch or distort"]
  },
  "tone_of_voice": {
    "personality": ["professional", "approachable"],
    "style": "Clear and confident communication",
    "do_say": ["We deliver excellence"],
    "dont_say": ["Maybe", "Possibly"]
  }
}
```

## 🛠 Configuration Options

### Extractor Configuration

```python
extractor = PDFRequirementExtractor(
    max_text_length=2000,     # Maximum excerpt length
    enable_ocr=True,          # Enable OCR for scanned PDFs
    custom_patterns={         # Custom regex patterns
        "pattern_name": r"regex_pattern"
    }
)
```

### GPT Configuration

```python
from pdf_requirement_extractor.gpt_parser import GPTConfig

# Method 1: Explicit configuration (recommended)
gpt_config = GPTConfig(
    model="gpt-4",           # Model is required - choose your preferred model
    temperature=0.3,         # Creativity level (0.0-1.0)
    max_tokens=2000,        # Maximum response tokens
    timeout=30              # Request timeout in seconds
)

# Method 2: Use factory methods for common use cases
cost_config = GPTConfig.for_cost_effective()    # gpt-3.5-turbo, optimized for cost
quality_config = GPTConfig.for_high_quality()   # gpt-4, optimized for quality
fast_config = GPTConfig.for_fast_processing()   # gpt-3.5-turbo, optimized for speed
mini_config = GPTConfig.for_mini_model()        # gpt-4o-mini, cost-effective high quality

# Method 3: Create default with custom model
custom_config = GPTConfig.create_default(model="gpt-4-turbo", temperature=0.2)
```

## 📝 Command Line Usage

The package includes a command-line interface:

```bash
# Basic extraction
pdf-extract-requirements input.pdf

# Save to specific output file
pdf-extract-requirements input.pdf --output results.json

# Enable GPT enhancement
pdf-extract-requirements input.pdf --gpt --api-key your-key

# Process multiple files
pdf-extract-requirements *.pdf --batch --output-dir results/

# Use custom patterns
pdf-extract-requirements input.pdf --patterns patterns.json
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install pdf-requirement-extractor[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=pdf_requirement_extractor

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-requirement-extractor.git
cd pdf-requirement-extractor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks

```bash
# Format code
black pdf_requirement_extractor/

# Check linting
flake8 pdf_requirement_extractor/

# Type checking
mypy pdf_requirement_extractor/
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyMuPDF](https://pymupdf.readthedocs.io/) for excellent PDF processing capabilities
- [OpenAI](https://openai.com/) for GPT API integration
- All contributors and users of this package

## 📞 Support

- 📧 **Email**: your.email@example.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/pdf-requirement-extractor/issues)
- 📖 **Documentation**: [GitHub README](https://github.com/yourusername/pdf-requirement-extractor#readme)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/pdf-requirement-extractor/discussions)

---

Made with ❤️ for the developer community
