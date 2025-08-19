"""
Command-line interface for PDF Requirement Extractor.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Optional

from .extractor import PDFRequirementExtractor
from .gpt_parser import GPTRequirementParser, GPTConfig, OPENAI_AVAILABLE


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract structured brand requirements from PDF documents",
        prog="pdf-extract-requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf-extract-requirements document.pdf
  pdf-extract-requirements document.pdf --output results.json
  pdf-extract-requirements document.pdf --gpt --api-key your-openai-key
  pdf-extract-requirements *.pdf --batch --output-dir results/
        """
    )
    
    # Input files
    parser.add_argument(
        "files",
        nargs="+",
        help="PDF file(s) to process"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file (default: print to stdout)"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for batch processing"
    )
    
    # Processing options
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Enable batch processing mode"
    )
    
    parser.add_argument(
        "--max-text-length",
        type=int,
        default=1000,
        help="Maximum text excerpt length (default: 1000)"
    )
    
    parser.add_argument(
        "--enable-ocr",
        action="store_true",
        help="Enable OCR for scanned PDFs"
    )
    
    # GPT enhancement
    parser.add_argument(
        "--gpt",
        action="store_true",
        help="Enable GPT enhancement (requires OpenAI API key)"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY environment variable)"
    )
    
    parser.add_argument(
        "--gpt-model",
        default="gpt-4.1-mini",
        help="GPT model to use (options: gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4.1-mini)"
    )
    
    parser.add_argument(
        "--gpt-temperature",
        type=float,
        default=0.3,
        help="GPT temperature (0.0-1.0, default: 0.3)"
    )
    
    # Custom patterns
    parser.add_argument(
        "--patterns",
        help="JSON file with custom regex patterns"
    )
    
    # Verbosity
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="pdf-requirement-extractor 1.0.0"
    )
    
    return parser


def load_custom_patterns(patterns_file: str) -> dict:
    """Load custom patterns from JSON file."""
    try:
        with open(patterns_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading patterns file: {e}", file=sys.stderr)
        return {}


def process_single_file(
    file_path: Path,
    extractor: PDFRequirementExtractor,
    gpt_parser: Optional[GPTRequirementParser] = None,
    verbose: bool = False
) -> dict:
    """Process a single PDF file."""
    if verbose:
        print(f"Processing: {file_path}")
    
    try:
        # Basic extraction
        result = extractor.extract_from_file(file_path)
        
        # GPT enhancement if enabled
        if gpt_parser and gpt_parser.is_available():
            if verbose:
                print(f"  Enhancing with GPT...")
            enhanced_requirements = gpt_parser.parse_with_gpt(
                result.raw_text_excerpt,
                result.extracted_requirements
            )
            result.extracted_requirements = enhanced_requirements
        
        if verbose:
            req_count = len([v for v in result.extracted_requirements.values() if v])
            print(f"  Found {req_count} requirement categories")
        
        return result.to_dict()
        
    except Exception as e:
        error_msg = f"Error processing {file_path}: {str(e)}"
        if verbose:
            print(f"  {error_msg}")
        return {"error": error_msg, "file": str(file_path)}


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize extractor
    custom_patterns = {}
    if args.patterns:
        custom_patterns = load_custom_patterns(args.patterns)
    
    extractor = PDFRequirementExtractor(
        max_text_length=args.max_text_length,
        enable_ocr=args.enable_ocr,
        custom_patterns=custom_patterns
    )
    
    # Initialize GPT parser if requested
    gpt_parser = None
    if args.gpt:
        if not OPENAI_AVAILABLE:
            print("Error: OpenAI package not available. Install with: pip install openai", 
                  file=sys.stderr)
            sys.exit(1)
        
        api_key = args.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OpenAI API key required. Use --api-key or set OPENAI_API_KEY", 
                  file=sys.stderr)
            sys.exit(1)
        
        gpt_config = GPTConfig(
            model=args.gpt_model,
            temperature=args.gpt_temperature,
            api_key=api_key
        )
        
        try:
            gpt_parser = GPTRequirementParser(gpt_config=gpt_config)
            if args.verbose:
                print(f"GPT enhancement enabled with model: {args.gpt_model}")
        except Exception as e:
            print(f"Error initializing GPT parser: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Process files
    file_paths = []
    for file_pattern in args.files:
        paths = list(Path(".").glob(file_pattern))
        if not paths:
            # Try as literal path
            path = Path(file_pattern)
            if path.exists():
                paths = [path]
        file_paths.extend(paths)
    
    if not file_paths:
        print("Error: No PDF files found", file=sys.stderr)
        sys.exit(1)
    
    # Filter for PDF files
    pdf_files = [f for f in file_paths if f.suffix.lower() == '.pdf']
    if not pdf_files:
        print("Error: No PDF files found in input", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process files
    results = []
    errors = []
    
    for pdf_file in pdf_files:
        result = process_single_file(pdf_file, extractor, gpt_parser, args.verbose)
        
        if "error" in result:
            errors.append(result)
        else:
            results.append(result)
    
    # Handle output
    if args.batch:
        # Batch mode - save individual files or to directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for result in results:
                output_file = output_dir / f"{Path(result['file_name']).stem}_results.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                if args.verbose:
                    print(f"Saved: {output_file}")
            
            # Save summary
            summary = {
                "processed": len(results),
                "errors": len(errors),
                "files": [r["file_name"] for r in results],
                "error_details": errors
            }
            summary_file = output_dir / "processing_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
        else:
            # Save all results to single file or stdout
            batch_output = {
                "results": results,
                "summary": {
                    "processed": len(results),
                    "errors": len(errors),
                    "total_files": len(pdf_files)
                },
                "errors": errors
            }
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(batch_output, f, indent=2, ensure_ascii=False)
                if args.verbose:
                    print(f"Batch results saved to: {args.output}")
            else:
                print(json.dumps(batch_output, indent=2, ensure_ascii=False))
    
    else:
        # Single file mode
        if len(results) == 1:
            output_data = results[0]
        else:
            output_data = {
                "results": results,
                "errors": errors
            }
    
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            if args.verbose:
                print(f"Results saved to: {args.output}")
        else:
            print(json.dumps(output_data, indent=2, ensure_ascii=False))
    
    # Print summary if verbose
    if args.verbose:
        print(f"\nProcessing completed:")
        print(f"  Successful: {len(results)}")
        print(f"  Errors: {len(errors)}")
        
        if errors:
            print(f"\nErrors:")
            for error in errors:
                print(f"  {error['file']}: {error['error']}")
    
    # Exit with error code if there were failures
    if errors and not results:
        sys.exit(1)


if __name__ == "__main__":
    main()
