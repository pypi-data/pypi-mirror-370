#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command line interface for qa-gen-cn
"""

import argparse
import sys
import json
from pathlib import Path
from . import generate_qa_pairs


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Generate QA pairs from Chinese documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qagen document.txt
  qagen document.txt --provider openai --model gpt-3.5-turbo
  qagen document.txt --output result.json --show-chunks
        """
    )
    
    parser.add_argument(
        "document",
        help="Path to the input document file"
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["ollama", "openai"],
        default="ollama",
        help="LLM provider (default: ollama)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="llama3.1:8b",
        help="Model name (default: llama3.1:8b)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: qa_pairs.json)"
    )
    
    parser.add_argument(
        "--show-chunks", "-s",
        action="store_true",
        help="Show document chunks during processing"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=4000,
        help="Document chunk size (default: 4000)"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Document chunk overlap (default: 200)"
    )
    
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.3,
        help="Similarity threshold for validation (default: 0.3)"
    )
    
    parser.add_argument(
        "--keyword-top-n",
        type=int,
        default=15,
        help="Number of keywords to extract (default: 15)"
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for OpenAI (if using OpenAI provider)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="qa-gen-cn 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Check if document exists
    doc_path = Path(args.document)
    if not doc_path.exists():
        print(f"Error: Document '{args.document}' not found")
        sys.exit(1)
    
    # Prepare validation config
    validation_config = {
        "similarity_threshold": args.similarity_threshold,
        "similarity_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "keyword_top_n": args.keyword_top_n,
    }
    
    # Prepare kwargs for LLM
    llm_kwargs = {}
    if args.provider == "openai" and args.api_key:
        llm_kwargs["api_key"] = args.api_key
    
    try:
        print(f"Processing document: {args.document}")
        print(f"Using {args.provider} model: {args.model}")
        
        # Generate QA pairs
        qa_pairs = generate_qa_pairs(
            doc_path=str(doc_path),
            llm_provider=args.provider,
            llm_model=args.model,
            show_chunks=args.show_chunks,
            validation_config=validation_config,
            **llm_kwargs
        )
        
        if not qa_pairs:
            print("No QA pairs were generated.")
            sys.exit(1)
        
        # Determine output file
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = Path("qa_pairs.json")
        
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully generated {len(qa_pairs)} QA pairs")
        print(f"Results saved to: {output_file}")
        
        # Show sample
        if qa_pairs:
            print("\nSample QA pairs:")
            for i, pair in enumerate(qa_pairs[:3]):
                print(f"\n{i+1}. Q: {pair['question']}")
                print(f"   A: {pair['answer'][:100]}{'...' if len(pair['answer']) > 100 else ''}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
