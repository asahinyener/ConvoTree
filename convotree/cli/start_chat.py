#!/usr/bin/env python3
"""
Quick start script for ConvoTree CLI
"""

import os
import sys
from pathlib import Path

def main():
    # Check if .env exists
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("Please create a .env file with your OpenAI API key:")
        print("echo 'OPENAI_API_KEY=your_api_key_here' > .env")
        return
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded environment variables from .env")
    except ImportError:
        print("❌ python-dotenv not installed")
        print("Install with: pip install python-dotenv")
        return
    
    # Verify OpenAI API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.strip() == "":
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please check your .env file contains: OPENAI_API_KEY=your_api_key_here")
        return
    
    print(f"✅ OpenAI API key loaded (ending in ...{api_key[-4:]})")
    
    # Check if required packages are installed
    try:
        import rich
        import openai
        import psutil
    except ImportError as e:
        print(f"❌ Missing required package: {e.name}")
        print("Install requirements with: pip install -r requirements.txt")
        return
    
    # Start the CLI
    print("🌳 Starting ConvoTree CLI...")
    from .chat_cli import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()