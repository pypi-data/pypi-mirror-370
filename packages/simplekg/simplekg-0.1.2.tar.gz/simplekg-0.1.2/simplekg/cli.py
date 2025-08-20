#!/usr/bin/env python3
"""
Command Line Interface for SimpleKG package.
"""

import argparse
import os
import sys
from pathlib import Path

from . import KnowledgeGraphGenerator, get_version


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SimpleKG: Generate Knowledge Graphs from Hebrew text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  simplekg --version
  simplekg --help
  
For detailed usage, see the documentation at:
https://gitlab.com/millerhadar/simplekg
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"SimpleKG {get_version()}"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="openai/gpt-4o",
        help="Language model to use (default: openai/gpt-4o)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for the language model (can also use OPENAI_API_KEY env var)"
    )
    
    parser.add_argument(
        "--input-file",
        "-i",
        type=str,
        help="Input text file to process"
    )
    
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="./output",
        help="Output directory for generated files (default: ./output)"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=0,
        help="Text chunk size (0 = process as whole, >0 = split into chunks)"
    )
    
    parser.add_argument(
        "--ontologies",
        nargs="+",
        default=["SKOS"],
        help="Ontologies to use (default: SKOS)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Print version and basic info
    if len(sys.argv) == 1:
        print(f"SimpleKG {get_version()}")
        print("For help, use: simplekg --help")
        return 0

    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key and args.input_file:
        print("Error: API key required. Use --api-key or set OPENAI_API_KEY environment variable")
        return 1

    # Process file if provided
    if args.input_file:
        if not os.path.exists(args.input_file):
            print(f"Error: Input file not found: {args.input_file}")
            return 1
            
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        print(f"Processing {args.input_file}...")
        print(f"Model: {args.model}")
        print(f"Chunk size: {args.chunk_size}")
        print(f"Ontologies: {args.ontologies}")
        
        try:
            # Initialize KG generator
            kggen = KnowledgeGraphGenerator(
                model=args.model,
                api_key=api_key
            )
            
            # Process the file
            with open(args.input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract entities and relations
            kggen.extractConcepts(text=text, chunk_size=args.chunk_size, verbose=args.verbose)
            kggen.extractRelations(verbose=args.verbose)
            kggen.groupConcepts(verbose=args.verbose)
            
            # Process ontologies
            for ontology in args.ontologies:
                kggen.relations2ontology([ontology])
            
            # Generate outputs
            input_name = Path(args.input_file).stem
            
            # Save JSON
            json_file = os.path.join(args.output_dir, f"{input_name}_kg.json")
            kggen.dump_graph(json_file)
            print(f"Saved graph to: {json_file}")
            
            # Generate visualization for each ontology
            for ontology in args.ontologies:
                kggen.graph2Ontology(ontology)
                viz_file = os.path.join(args.output_dir, f"{input_name}_{ontology}.html")
                kggen.visualize(viz_file)
                print(f"Saved visualization to: {viz_file}")
                
            print("Processing complete!")
            
        except Exception as e:
            print(f"Error processing file: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
