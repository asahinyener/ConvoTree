#!/usr/bin/env python3
"""
Main entry point for ConvoTree - A persistent conversational AI with knowledge graph integration.
"""

import sys
import argparse
from pathlib import Path

# Add the convotree package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from convotree.cli.start_chat import main as start_chat_main
from convotree.cli.cli_v2 import main as cli_v2_main


def main():
    """Main entry point with command selection"""
    parser = argparse.ArgumentParser(
        description="ConvoTree - Persistent Conversational AI with Knowledge Graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --cli-v2          # Launch advanced CLI with v2.0 features
  python main.py --simple          # Launch simple chat interface
  
Environment Setup:
  Make sure you have a .env file with:
    OPENAI_API_KEY=your_api_key_here
        """
    )
    
    parser.add_argument(
        "--cli-v2", 
        action="store_true", 
        help="Launch the advanced CLI v2.0 with all features"
    )
    parser.add_argument(
        "--simple", 
        action="store_true", 
        help="Launch the simple chat interface"
    )
    parser.add_argument(
        "--version", 
        action="store_true", 
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.version:
        from convotree import __version__
        print(f"ConvoTree v{__version__}")
        return
    
    if args.cli_v2:
        print("🚀 Launching ConvoTree CLI v2.0...")
        cli_v2_main()
    elif args.simple:
        print("💬 Launching Simple Chat Interface...")
        start_chat_main()
    else:
        # Default to CLI v2.0
        print("🚀 Launching ConvoTree CLI v2.0 (default)...")
        print("Use --help to see all options")
        cli_v2_main()


if __name__ == "__main__":
    main()