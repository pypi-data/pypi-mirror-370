import argparse
from datetime import datetime

from .processor import process_pdf
from .network_processor import process_pdf_network_diagrams
from .hybrid_processor import process_pdf_hybrid


def cli():
    parser = argparse.ArgumentParser(
        description="Convert PDF pages to images and transcribe them to Markdown using local ollama models. "
                    "Supports automatic network diagram detection to Mermaid.js conversion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # DEFAULT: Automatic network diagram detection (hybrid mode)
  netintel-ocr document.pdf
  
  # Text-only mode (skip detection for speed)
  netintel-ocr document.pdf --text-only
  
  # Network diagrams only (skip text pages)
  netintel-ocr network-architecture.pdf --network-only
  
  # Adjust detection sensitivity (icons are on by default)
  netintel-ocr document.pdf --confidence 0.8
  
  # Disable icons if needed
  netintel-ocr document.pdf --no-icons
  
  # Process specific pages
  netintel-ocr large.pdf --start 10 --end 20
  
  # Use a different model
  netintel-ocr doc.pdf --model llava:latest
        """
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the input PDF file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Output directory (default: output_YYYYMMDD_HHMMSS)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="nanonets-ocr-s:latest",
        help="Ollama model to use (default: nanonets-ocr-s:latest)",
    )
    parser.add_argument(
        "--keep-images",
        "-k",
        action="store_true",
        default=False,
        help="Keep the intermediate image files (default: False)",
    )
    parser.add_argument(
        "--width",
        "-w",
        type=int,
        default=0,
        help="Width of the resized images. Set to 0 to skip resizing (default: 0)",
    )
    parser.add_argument(
        "--start",
        "-s",
        type=int,
        default=0,
        help="Start page number (default: 0)",
    )
    parser.add_argument(
        "--end",
        "-e",
        type=int,
        default=0,
        help="End page number (default: 0)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=False,
        help="Enable debug output with detailed processing information",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Verbose output - show progress information (default is quiet)",
    )
    # Processing mode options
    mode_group = parser.add_argument_group('Processing Modes')
    mode_group.add_argument(
        "--text-only",
        "-t",
        action="store_true",
        default=False,
        help="Text-only mode: Skip network diagram detection for faster processing. "
             "Use this when you know the document contains only text.",
    )
    mode_group.add_argument(
        "--network-only",
        action="store_true",
        default=False,
        help="Process ONLY network diagrams, skip regular text pages (use when you know the document contains mainly diagrams).",
    )
    
    # Network diagram detection options (applies to default and network-only modes)
    network_group = parser.add_argument_group('Network Diagram Options')
    network_group.add_argument(
        "--confidence",
        "-c",
        type=float,
        default=0.7,
        help="Minimum confidence threshold for network diagram detection (0.0-1.0). "
             "Higher values = stricter detection. Default: 0.7",
    )
    network_group.add_argument(
        "--no-icons",
        action="store_true",
        default=False,
        help="Disable Font Awesome icons in Mermaid diagrams. "
             "By default, icons are added for better visual representation.",
    )
    network_group.add_argument(
        "--diagram-only",
        action="store_true",
        default=False,
        help="On pages with network diagrams, only extract the diagram without the text content. "
             "By default, both diagram and text are extracted.",
    )
    network_group.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for each LLM operation (default: 60). "
             "Increase for complex diagrams, decrease for faster fallback to text.",
    )
    network_group.add_argument(
        "--fast-extraction",
        action="store_true",
        default=False,
        help="Use optimized fast extraction for network diagrams. "
             "Reduces extraction time from 30-60s to 10-20s per diagram.",
    )
    network_group.add_argument(
        "--multi-diagram",
        action="store_true",
        default=False,
        help="Force multi-diagram extraction mode. "
             "Extracts each diagram on a page as a separate region for individual processing.",
    )
    network_group.add_argument(
        "--no-auto-detect",
        action="store_true",
        default=False,
        help="Disable automatic network diagram detection (deprecated, use --fast-mode instead).",
    )


    args = parser.parse_args()
    
    # Set global debug flag
    import os
    # Default to quiet mode (minimal output) unless debug is explicitly requested
    if args.debug:
        os.environ["NETINTEL_OCR_DEBUG"] = "1"
        os.environ["NETINTEL_OCR_QUIET"] = "0"  # Debug overrides quiet
    else:
        os.environ["NETINTEL_OCR_DEBUG"] = "0"
        # Default is quiet mode - minimal output (unless verbose is specified)
        os.environ["NETINTEL_OCR_QUIET"] = "0" if args.verbose else "1"

    # Determine processing mode
    if args.network_only:
        # Network-only mode: Process only network diagrams
        process_pdf_network_diagrams(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            keep_images=args.keep_images,
            width=args.width,
            start=args.start,
            end=args.end,
            confidence_threshold=args.confidence,
            use_icons=not args.no_icons,  # Icons enabled by default
        )
    elif args.text_only or args.no_auto_detect:
        # Text-only mode: Skip detection for speed
        process_pdf_hybrid(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            keep_images=args.keep_images,
            width=args.width,
            start=args.start,
            end=args.end,
            auto_detect=False,
            fast_mode=True,
        )
    else:
        # DEFAULT: Hybrid mode with automatic detection
        process_pdf_hybrid(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            keep_images=args.keep_images,
            width=args.width,
            start=args.start,
            end=args.end,
            auto_detect=True,
            confidence_threshold=args.confidence,
            use_icons=not args.no_icons,  # Icons enabled by default
            fast_mode=False,
            timeout_seconds=args.timeout,
            include_text_with_diagrams=not args.diagram_only,  # Include text by default
            fast_extraction=args.fast_extraction,  # Use fast extraction if requested
            force_multi_diagram=args.multi_diagram,  # Force multi-diagram extraction
            debug=args.debug,
            quiet=not args.verbose,  # Quiet by default unless verbose flag
        )


if __name__ == "__main__":
    cli()
