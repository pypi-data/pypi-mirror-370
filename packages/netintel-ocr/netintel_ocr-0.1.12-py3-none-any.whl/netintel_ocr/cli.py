import argparse
import sys
import os
import json
from pathlib import Path

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
  
  # NEW v0.1.11: Initialize project with Docker/Kubernetes support
  netintel-ocr --init
  
  # Use configuration file
  netintel-ocr document.pdf --config config.yml
  
  # Query vector database (foundation mode)
  netintel-ocr --query "network topology"
        """
    )
    
    # Special commands (v0.1.11-v0.1.12)
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new NetIntel-OCR project with Docker, Helm charts, and configuration files (v0.1.11)",
    )
    parser.add_argument(
        "--query",
        type=str,
        metavar="QUERY",
        help="Query the vector database with full search capabilities (v0.1.12)",
    )
    parser.add_argument(
        "--merge-to-centralized",
        action="store_true",
        help="Merge per-document databases to centralized LanceDB with embeddings (v0.1.12)",
    )
    parser.add_argument(
        "--batch-ingest",
        action="store_true",
        help="Process multiple PDFs in parallel and merge to centralized DB (v0.1.12)",
    )
    parser.add_argument(
        "--db-stats",
        action="store_true",
        help="Show centralized database statistics (v0.1.12)",
    )
    parser.add_argument(
        "--db-optimize",
        action="store_true",
        help="Optimize centralized database with compaction and index rebuilding (v0.1.12)",
    )
    parser.add_argument(
        "--db-export",
        type=str,
        metavar="OUTPUT_FILE",
        help="Export centralized database to file (v0.1.12)",
    )
    
    parser.add_argument(
        "pdf_path",
        nargs="?",
        help="Path to the input PDF file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output",
        help="Base output directory (default: output). Each document will be stored in output/<md5_checksum>/",
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
    
    # Table extraction options
    table_group = parser.add_argument_group('Table Extraction Options')
    table_group.add_argument(
        "--extract-tables",
        action="store_true",
        default=True,
        help="Extract tables from PDF (default: enabled). "
             "Tables are detected and converted to structured JSON format.",
    )
    table_group.add_argument(
        "--no-tables",
        action="store_true",
        default=False,
        help="Disable table extraction for faster processing.",
    )
    table_group.add_argument(
        "--table-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence for table detection (0.0-1.0, default: 0.7).",
    )
    table_group.add_argument(
        "--table-method",
        choices=['hybrid', 'pdfplumber', 'llm'],
        default='hybrid',
        help="Table extraction method. 'hybrid' uses pdfplumber first then LLM if needed, "
             "'pdfplumber' uses only library extraction, 'llm' uses only vision models. Default: hybrid",
    )
    table_group.add_argument(
        "--save-table-json",
        action="store_true",
        default=False,
        help="Save extracted tables as separate JSON files in addition to markdown.",
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
    network_group.add_argument(
        "--network-model",
        type=str,
        default=None,
        help="Ollama model to use specifically for network diagram processing. "
             "If not specified, uses the --model parameter for all tasks. "
             "Recommended: qwen2.5vl for diagrams, nanonets-ocr-s for text. "
             "Example: --model nanonets-ocr-s --network-model qwen2.5vl",
    )
    
    # Checkpoint/resume options
    checkpoint_group = parser.add_argument_group('Checkpoint Options')
    checkpoint_group.add_argument(
        "--resume",
        action="store_true",
        default=False,
        help="Resume processing from a checkpoint if one exists. "
             "Checkpoints are automatically saved during processing and "
             "allow you to continue from where a previous run was interrupted. "
             "The checkpoint is stored in output/<md5>/.checkpoint/",
    )
    
    # Vector generation options (v0.1.7 - enabled by default)
    vector_group = parser.add_argument_group('Vector Database Options (v0.1.7)')
    vector_group.add_argument(
        "--no-vector",
        action="store_true",
        default=False,
        help="DISABLE vector generation (v0.1.6 behavior). "
             "By default (v0.1.7+), NetIntel-OCR automatically generates: "
             "1) Vector-optimized markdown (document-vector.md), "
             "2) LanceDB-ready chunks (chunks.jsonl), "
             "3) Complete metadata and schema files. "
             "Use this flag to only generate human-friendly markdown.",
    )
    vector_group.add_argument(
        "--vector-only",
        action="store_true",
        default=False,
        help="Generate ONLY vector files (skip human-friendly markdown). "
             "Faster when you only need vector database output.",
    )
    vector_group.add_argument(
        "--vector-format",
        choices=['lancedb', 'pinecone', 'weaviate', 'qdrant', 'chroma'],
        default='lancedb',
        help="Target vector database format (default: lancedb). "
             "LanceDB format is optimized and includes pre-chunked JSONL.",
    )
    vector_group.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in tokens for vector database (default: 1000). "
             "Optimal for most embedding models.",
    )
    vector_group.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Overlap between chunks in tokens (default: 100). "
             "Helps preserve context across chunk boundaries.",
    )
    vector_group.add_argument(
        "--chunk-strategy",
        choices=['semantic', 'fixed', 'sentence'],
        default='semantic',
        help="Chunking strategy (default: semantic). "
             "'semantic' respects document structure, "
             "'fixed' uses fixed-size chunks, "
             "'sentence' chunks at sentence boundaries.",
    )
    vector_group.add_argument(
        "--array-strategy",
        choices=['separate_rows', 'concatenate', 'serialize'],
        default='separate_rows',
        help="How to handle arrays in JSON flattening (default: separate_rows). "
             "'separate_rows' creates individual rows, "
             "'concatenate' joins with delimiter, "
             "'serialize' converts to JSON string.",
    )
    vector_group.add_argument(
        "--embedding-metadata",
        action="store_true",
        default=False,
        help="Include additional metadata for embedding generation. "
             "Adds entity extraction, technical term detection, and quality scores.",
    )
    vector_group.add_argument(
        "--legacy",
        action="store_true",
        default=False,
        help="Use v0.1.6 behavior (equivalent to --no-vector). "
             "Disables all vector generation features.",
    )
    vector_group.add_argument(
        "--vector-regenerate",
        action="store_true",
        default=False,
        help="Regenerate vector files from existing markdown output. "
             "Use this when you have already processed a PDF and want to "
             "regenerate vector files with different settings. "
             "Skips PDF processing and uses existing markdown files.",
    )
    vector_group.add_argument(
        "--embedding-model",
        type=str,
        default="qwen3-embedding:4b",
        help="Embedding model to use for vector generation. "
             "For Ollama: qwen3-embedding:4b (default), qwen3-embedding:8b, "
             "qwen3-embedding:0.6b, nomic-embed-text, mxbai-embed-large. "
             "For OpenAI: text-embedding-ada-002, text-embedding-3-small, etc.",
    )
    vector_group.add_argument(
        "--embedding-provider",
        choices=['ollama', 'openai'],
        default='ollama',
        help="Provider for embedding generation (default: ollama). "
             "Use 'ollama' for local embeddings with Ollama models, "
             "or 'openai' for OpenAI embeddings (requires API key).",
    )
    
    # Configuration and infrastructure options (v0.1.11)
    config_group = parser.add_argument_group('Configuration Options (v0.1.11)')
    config_group.add_argument(
        "--config",
        type=str,
        metavar="CONFIG_FILE",
        help="Path to YAML configuration file. Overrides default settings and environment variables.",
    )
    config_group.add_argument(
        "--lancedb-path",
        type=str,
        help="Local path to LanceDB for query operations",
    )
    config_group.add_argument(
        "--lancedb-uri",
        type=str,
        help="Remote URI for LanceDB (S3/MinIO) for distributed deployments",
    )
    config_group.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing files during --init",
    )
    config_group.add_argument(
        "--base-dir",
        type=str,
        default="./netintel-ocr",
        help="Base directory for --init command (default: ./netintel-ocr)",
    )
    
    # v0.1.12 Query options
    query_group = parser.add_argument_group('Query Options (v0.1.12)')
    query_group.add_argument(
        "--query-limit",
        type=int,
        default=10,
        help="Maximum number of query results (default: 10)",
    )
    query_group.add_argument(
        "--rerank",
        action="store_true",
        help="Apply reranking to query results for better relevance",
    )
    query_group.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.7,
        help="Minimum similarity score for query results (default: 0.7)",
    )
    query_group.add_argument(
        "--output-format",
        choices=['json', 'markdown', 'csv'],
        default='json',
        help="Output format for query results (default: json)",
    )
    
    # v0.1.12 Batch processing options
    batch_group = parser.add_argument_group('Batch Processing Options (v0.1.12)')
    batch_group.add_argument(
        "--input-pattern",
        type=str,
        help="Input pattern for batch processing (e.g., '*.pdf', 'docs/*.pdf')",
    )
    batch_group.add_argument(
        "--parallel",
        type=int,
        default=4,
        help="Number of parallel workers for batch processing (default: 4)",
    )
    batch_group.add_argument(
        "--auto-merge",
        action="store_true",
        default=True,
        help="Automatically merge to centralized DB after batch processing",
    )
    batch_group.add_argument(
        "--compute-embeddings",
        action="store_true",
        help="Generate embeddings during merge operation",
    )
    batch_group.add_argument(
        "--dedupe",
        action="store_true",
        default=True,
        help="Skip duplicate documents during merge",
    )

    args = parser.parse_args()
    
    # Handle v0.1.11 special commands first
    if args.init:
        from .project_initializer import ProjectInitializer
        initializer = ProjectInitializer(base_dir=args.base_dir)
        success = initializer.initialize_project(force=args.force)
        sys.exit(0 if success else 1)
    
    # Handle v0.1.12 query command
    if args.query:
        from .query_engine import QueryEngine, OutputFormat
        engine = QueryEngine(
            lancedb_path=args.lancedb_path,
            lancedb_uri=args.lancedb_uri,
            embedding_model=args.embedding_model if hasattr(args, 'embedding_model') else "nomic-embed-text"
        )
        result = engine.query(
            args.query,
            limit=args.query_limit,
            rerank=args.rerank,
            similarity_threshold=args.similarity_threshold
        )
        
        # Format output
        output_format = OutputFormat(args.output_format)
        formatted = engine.format_results(result, output_format)
        print(formatted)
        sys.exit(0)
    
    # Handle v0.1.12 merge command
    if args.merge_to_centralized:
        from .centralized_db import CentralizedDatabaseManager, MergeMode
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb"),
            compute_embeddings=args.compute_embeddings
        )
        result = manager.merge_to_centralized(
            source_dir=args.output,
            mode=MergeMode.APPEND,
            dedupe=args.dedupe
        )
        print(f"✅ Merged {result.documents_merged} documents")
        print(f"   Added {result.chunks_added} chunks")
        print(f"   Skipped {result.documents_skipped} duplicates")
        if result.errors:
            print(f"⚠️  {len(result.errors)} errors occurred")
        sys.exit(0)
    
    # Handle v0.1.12 batch ingestion
    if args.batch_ingest:
        from .batch_processor import BatchProcessor
        
        # Get input patterns
        patterns = []
        if args.input_pattern:
            patterns.append(args.input_pattern)
        elif args.pdf_path:
            patterns.append(args.pdf_path)
        else:
            parser.error("--batch-ingest requires --input-pattern or pdf_path")
        
        processor = BatchProcessor(
            output_dir=args.output,
            parallel_workers=args.parallel,
            auto_merge=args.auto_merge
        )
        
        result = processor.process_batch(
            input_patterns=patterns,
            dedupe=args.dedupe
        )
        
        print(f"✅ Batch processing complete")
        print(f"   Processed: {result.processed}/{result.total_files}")
        print(f"   Failed: {result.failed}")
        print(f"   Skipped: {result.skipped}")
        print(f"   Total chunks: {result.total_chunks}")
        print(f"   Time: {result.total_time:.2f}s")
        sys.exit(0)
    
    # Handle v0.1.12 database statistics
    if args.db_stats:
        from .centralized_db import CentralizedDatabaseManager
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb")
        )
        stats = manager.get_statistics()
        documents = manager.list_documents()
        
        print("📊 Database Statistics")
        print(f"   Documents: {stats.get('total_documents', 0)}")
        print(f"   Chunks: {stats.get('total_chunks', 0)}")
        print(f"   Size: {stats.get('database_size_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"   Last update: {stats.get('last_update', 'Never')}")
        
        if documents:
            print("\n📄 Recent Documents:")
            for doc in documents[:5]:
                print(f"   - {doc.source_file} ({doc.chunk_count} chunks)")
        sys.exit(0)
    
    # Handle v0.1.12 database optimization
    if args.db_optimize:
        from .centralized_db import CentralizedDatabaseManager
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb")
        )
        result = manager.optimize_database(compact=True, rebuild_indices=True)
        print("✅ Database optimization complete")
        for action in result.get('actions_performed', []):
            print(f"   - {action}")
        sys.exit(0)
    
    # Handle v0.1.12 database export
    if args.db_export:
        from .centralized_db import CentralizedDatabaseManager
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb")
        )
        
        # Export chunks to file
        import json
        chunks_file = Path(args.output) / "lancedb" / "chunks.jsonl"
        if chunks_file.exists():
            with open(args.db_export, 'w') as out:
                with open(chunks_file, 'r') as inp:
                    if args.db_export.endswith('.json'):
                        # Convert JSONL to JSON array
                        chunks = [json.loads(line) for line in inp if line.strip()]
                        json.dump(chunks, out, indent=2)
                    else:
                        # Copy as JSONL
                        out.write(inp.read())
            print(f"✅ Exported database to {args.db_export}")
        else:
            print("❌ No database to export")
        sys.exit(0)
    
    # Check if pdf_path is required but missing
    if not args.pdf_path:
        parser.error("pdf_path is required unless using --init, --query, or --merge-to-centralized")
    
    # Load configuration if provided
    config = None
    if args.config:
        from .config_manager import ConfigManager
        config = ConfigManager(args.config)
        config.merge_cli_args(args)
        # Validate configuration
        is_valid, errors = config.validate_config()
        if not is_valid:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)
    
    # Set global debug flag
    # Default to quiet mode (minimal output) unless debug is explicitly requested
    if args.debug:
        os.environ["NETINTEL_OCR_DEBUG"] = "1"
        os.environ["NETINTEL_OCR_QUIET"] = "0"  # Debug overrides quiet
    else:
        os.environ["NETINTEL_OCR_DEBUG"] = "0"
        # Default is quiet mode - minimal output (unless verbose is specified)
        os.environ["NETINTEL_OCR_QUIET"] = "0" if args.verbose else "1"

    # Handle vector regeneration mode
    if args.vector_regenerate:
        # Import the vector regeneration function
        from .vector_regenerator import regenerate_vectors
        
        # Regenerate vectors from existing markdown
        regenerate_vectors(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            vector_format=args.vector_format,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            chunk_strategy=args.chunk_strategy,
            array_strategy=args.array_strategy,
            include_extended_metadata=args.embedding_metadata,
            embedding_model=args.embedding_model,
            embedding_provider=args.embedding_provider,
            debug=args.debug,
            quiet=not args.verbose
        )
        return
    
    # Determine processing mode
    if args.network_only:
        # Network-only mode: Process only network diagrams
        process_pdf_network_diagrams(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.network_model or args.model,  # Use network_model if specified
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
            resume=args.resume,
            extract_tables=not args.no_tables,
            table_confidence=args.table_confidence,
            table_method=args.table_method,
            save_table_json=args.save_table_json,
        )
    else:
        # DEFAULT: Hybrid mode with automatic detection
        # Determine if vector generation should be enabled
        generate_vector = not (args.no_vector or args.legacy)
        
        process_pdf_hybrid(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            network_model=args.network_model,  # Pass network model if specified
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
            resume=args.resume,  # Pass resume flag for checkpoint support
            extract_tables=not args.no_tables,  # Table extraction enabled by default
            table_confidence=args.table_confidence,
            table_method=args.table_method,
            save_table_json=args.save_table_json,
            # Vector generation options (v0.1.7)
            generate_vector=generate_vector,
            vector_format=args.vector_format,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            chunk_strategy=args.chunk_strategy,
            array_strategy=args.array_strategy,
            embedding_metadata=args.embedding_metadata,
            embedding_model=args.embedding_model,
            embedding_provider=args.embedding_provider,
        )


if __name__ == "__main__":
    cli()
