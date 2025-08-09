#!/usr/bin/env python3
"""
Test script for sequential compression feature in ConvoTree.
This script demonstrates how the KG is updated with each new exchange when sequential compression is enabled.
"""

import json
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
PORT = os.getenv("PORT", "12001")
BASE_URL = f"http://localhost:{PORT}"

def main():
    print(f"Testing sequential compression with server at {BASE_URL}")
    
    # Sample chat for initial compression
    sample_chat = [
        {"role": "user", "content": "Hi, I'm Julia and I love jazz."},
        {"role": "assistant", "content": "Hello Julia! What can I do for you today?"},
        {"role": "user", "content": "Who is the pianist in Miles Davis' Kind of Blue?"},
        {"role": "assistant", "content": "That would be Bill Evans on most tracks."},
        {"role": "user", "content": "Cool, add that to my notes please."},
        {"role": "assistant", "content": "Noted!"},
        {"role": "user", "content": "Thanks, bye!"},
        {"role": "assistant", "content": "Good-bye!"}
    ]
    
    # Initial compression
    print("\n1. Compressing initial chat...")
    try:
        response = requests.post(f"{BASE_URL}/compress", json=sample_chat)
        response.raise_for_status()
        data = response.json()
        bundle_path = data.get("bundle_path")
        kg_path = data.get("kg_path")
        
        print(f"Initial bundle created at: {bundle_path}")
        print(f"Initial KG path: {kg_path}")
        
        # Print initial KG
        kg_response = requests.get(f"{BASE_URL}/{kg_path}")
        kg_response.raise_for_status()
        print("\nInitial Knowledge Graph:")
        print(kg_response.text)
    except Exception as e:
        print(f"Error in initial compression: {e}")
        return
    
    # Test sequential compression with new exchanges
    new_exchanges = [
        "Tell me more about Miles Davis.",
        "What other albums did Miles Davis record?",
        "Who played with Miles Davis on those albums?"
    ]
    
    for i, user_message in enumerate(new_exchanges):
        print(f"\n{i+2}. Testing exchange: '{user_message}'")
        
        try:
            # Resume with sequential compression
            response = requests.post(
                f"{BASE_URL}/resume", 
                json={
                    "bundle_path": bundle_path,
                    "next_user": user_message,
                    "sequential_compression": True
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Update bundle path for next iteration
            if "bundle_path" in data:
                bundle_path = data.get("bundle_path")
            
            print(f"Assistant reply: {data.get('assistant_reply')}")
            
            # Print updated KG if available
            if "kg_path" in data:
                kg_path = data.get("kg_path")
                kg_response = requests.get(f"{BASE_URL}/{kg_path}")
                kg_response.raise_for_status()
                print("\nUpdated Knowledge Graph:")
                print(kg_response.text)
            
            # Small delay to avoid overwhelming the server
            time.sleep(1)
        except Exception as e:
            print(f"Error in exchange {i+1}: {e}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()