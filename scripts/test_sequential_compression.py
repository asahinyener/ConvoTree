#!/usr/bin/env python3
"""
Test script for sequential compression feature in ConvoTree.
This script demonstrates how the KG is updated with each new exchange when sequential compression is enabled.
"""

import json
import requests
import time
import os
import sys
from pathlib import Path

# Configuration
PORT = os.getenv("PORT", "12000")  # Use environment variable or default to 12000
BASE_URL = f"http://localhost:{PORT}"
SAMPLE_CHAT_PATH = Path(__file__).parent.parent / "sample_chat.json"

print(f"Using server URL: {BASE_URL}")
print(f"Sample chat path: {SAMPLE_CHAT_PATH}")

def main():
    # Check if the server is running
    try:
        response = requests.get(f"{BASE_URL}")
        if response.status_code != 200:
            print(f"Server returned status code {response.status_code}. Make sure the server is running.")
            return
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {BASE_URL}. Make sure the server is running.")
        return

    # Load sample chat
    if not SAMPLE_CHAT_PATH.exists():
        print(f"Sample chat file not found at {SAMPLE_CHAT_PATH}")
        return
    
    with open(SAMPLE_CHAT_PATH, "r") as f:
        sample_chat = json.load(f)
    
    # Initial compression
    print("Compressing initial chat...")
    response = requests.post(f"{BASE_URL}/compress", json=sample_chat)
    if response.status_code != 200:
        print(f"Error compressing chat: {response.text}")
        return
    
    bundle_path = response.json().get("bundle_path")
    print(f"Initial bundle created at: {bundle_path}")
    print(f"Initial KG image: {response.json().get('kg_image')}")
    
    # Add new exchanges with sequential compression
    new_exchanges = [
        "Tell me more about Miles Davis.",
        "What other albums did Miles Davis record?",
        "Who played with Miles Davis on those albums?"
    ]
    
    for i, user_message in enumerate(new_exchanges):
        print(f"\nExchange {i+1}: {user_message}")
        
        # Resume with sequential compression
        response = requests.post(
            f"{BASE_URL}/resume", 
            json={
                "bundle_path": bundle_path,
                "next_user": user_message,
                "sequential_compression": True
            }
        )
        
        if response.status_code != 200:
            print(f"Error in resume: {response.text}")
            continue
        
        # Update bundle path for next iteration
        bundle_path = response.json().get("bundle_path")
        
        print(f"Assistant reply: {response.json().get('assistant_reply')}")
        print(f"Updated KG image: {response.json().get('kg_image')}")
        print(f"Updated bundle: {bundle_path}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(1)
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()