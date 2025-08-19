from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf-requirement-extractor",
    version="2.0.0",
    author="S M Asiful Islam Saky",
    author_email="saky.aiu22@gmail.com",
    description="Extract structured brand requirements from PDF documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/pdf-requirement-extractor/",
    project_urls={
        "Documentation": "https://pypi.org/project/pdf-requirement-extractor/",
        "Source Code": "https://pypi.org/project/pdf-requirement-extractor/",
        "Download": "https://pypi.org/project/pdf-requirement-extractor/#files",
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
    install_requires=[
        "pymupdf>=1.23.0",
        "regex>=2023.10.3",
        "typing-extensions>=4.5.0",
    ],
    extras_require={
        "gpt": [
            "openai>=1.3.0",
        ],
        "ocr": [
            "pytesseract>=0.3.10",
            "Pillow>=10.0.0",
        ],
        "all": [
            "openai>=1.3.0",
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
