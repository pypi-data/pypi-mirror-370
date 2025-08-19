from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf-requirements-extractor",
    version="1.0.0",
    author="S M Asiful Islam Saky",
    author_email="saky.aiu22@gmail.com",
    description="Extract structured brand requirements from PDF documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sushivid7/pdf-requirements-extractor",
    project_urls={
        "Bug Tracker": "https://github.com/sushivid7/pdf-requirements-extractor/issues",
        "Documentation": "https://github.com/sushivid7/pdf-requirements-extractor#readme",
        "Source Code": "https://github.com/sushivid7/pdf-requirements-extractor",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "gpt": [
            "openai>=1.3.0",
        ],
        "ocr": [
            "pytesseract>=0.3.10",
            "Pillow>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-extract-requirements=pdf_requirements_extractor.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pdf_requirements_extractor": ["*.txt", "*.md"],
    },
    keywords=[
        "pdf", "extraction", "brand", "requirements", "guidelines", 
        "parsing", "text-processing", "document-analysis", "openai", "gpt"
    ],
    zip_safe=False,
)
