#!/usr/bin/env python3
"""
Main entry point for the conversation parser application.
This script processes conversation text files and generates RAG-optimized JSON and Markdown outputs.
"""

import os
import sys
from conversation_parser import ConversationParser

def main():
    """Main function to run the conversation parser."""
    
    # Check if input file is provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <conversation_file_path>")
        print("Example: python main.py 'attached_assets/Meredith Lamb (+14169386001)_1751821634456.txt'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    try:
        # Initialize the parser
        parser = ConversationParser()
        
        # Parse the conversation file
        print(f"Parsing conversation file: {input_file}")
        parser.parse_file(input_file)
        
        # Generate the output files and zip
        print("Generating JSON and Markdown files...")
        zip_path = parser.generate_output()
        
        print(f"Successfully created conversation archive: {zip_path}")
        print("Files are organized by week and optimized for RAG consumption.")
        
    except Exception as e:
        print(f"Error processing conversation file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
