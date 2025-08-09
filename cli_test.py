#!/usr/bin/env python3
"""
Simple CLI test for sequential compression in ConvoTree.
This script simulates a conversation with sequential compression.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Sample conversation
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

# New user messages for sequential compression
new_messages = [
    "Tell me more about Miles Davis.",
    "What other albums did Miles Davis record?",
    "Who played with Miles Davis on those albums?"
]

# Mock responses (to avoid using OpenAI API)
mock_responses = [
    "Miles Davis was a legendary jazz trumpeter and composer born on May 26, 1926. He was one of the most influential figures in the history of jazz and 20th-century music. Davis led many important jazz groups and helped develop several major jazz styles including cool jazz, hard bop, modal jazz, and jazz fusion.",
    "Miles Davis recorded many influential albums throughout his career. Some of his most notable albums besides 'Kind of Blue' include: 'Birth of the Cool', 'Milestones', 'Sketches of Spain', 'E.S.P.', 'In a Silent Way', and 'Bitches Brew' which pioneered jazz fusion.",
    "Miles Davis collaborated with many talented musicians throughout his career. On 'Bitches Brew', he worked with Wayne Shorter, Chick Corea, and John McLaughlin. On 'Birth of the Cool', he worked with Gil Evans and Gerry Mulligan. His 'Second Great Quintet' included Wayne Shorter, Herbie Hancock, Ron Carter, and Tony Williams."
]

def simulate_kg_extraction(messages: List[Dict[str, str]]) -> List[str]:
    """Simulate knowledge graph extraction from messages."""
    # Extract potential facts from the conversation
    facts = []
    for msg in messages:
        if "jazz" in msg["content"].lower():
            facts.append("Julia likes jazz music")
        if "miles davis" in msg["content"].lower():
            facts.append("The conversation discusses Miles Davis")
        if "kind of blue" in msg["content"].lower():
            facts.append("Kind of Blue is an album by Miles Davis")
        if "bill evans" in msg["content"].lower():
            facts.append("Bill Evans played piano on Kind of Blue")
        if "birth of the cool" in msg["content"].lower():
            facts.append("Birth of the Cool is an album by Miles Davis")
        if "bitches brew" in msg["content"].lower():
            facts.append("Bitches Brew is an album by Miles Davis that pioneered jazz fusion")
        if "wayne shorter" in msg["content"].lower():
            facts.append("Wayne Shorter collaborated with Miles Davis")
        if "herbie hancock" in msg["content"].lower():
            facts.append("Herbie Hancock was part of Miles Davis' Second Great Quintet")
    
    # Remove duplicates while preserving order
    unique_facts = []
    for fact in facts:
        if fact not in unique_facts:
            unique_facts.append(fact)
    
    return unique_facts

def main():
    print("ConvoTree Sequential Compression CLI Test")
    print("=" * 50)
    
    # Initialize conversation and KG
    conversation = sample_chat.copy()
    kg_facts = simulate_kg_extraction(conversation)
    
    # Display initial conversation
    print("\nInitial Conversation:")
    for msg in conversation:
        prefix = "User: " if msg["role"] == "user" else "Assistant: "
        print(f"{prefix}{msg['content']}")
    
    # Display initial KG
    print("\nInitial Knowledge Graph:")
    for i, fact in enumerate(kg_facts, 1):
        print(f"{i}. {fact}")
    
    # Simulate sequential compression
    for i, (user_msg, assistant_response) in enumerate(zip(new_messages, mock_responses)):
        print("\n" + "=" * 50)
        print(f"Exchange {i+1}:")
        
        # Add new messages to conversation
        conversation.append({"role": "user", "content": user_msg})
        conversation.append({"role": "assistant", "content": assistant_response})
        
        # Display new exchange
        print(f"User: {user_msg}")
        print(f"Assistant: {assistant_response}")
        
        # Update KG with sequential compression
        kg_facts = simulate_kg_extraction(conversation)
        
        # Display updated KG
        print("\nUpdated Knowledge Graph:")
        for i, fact in enumerate(kg_facts, 1):
            print(f"{i}. {fact}")
        
        # Ask to continue
        if i < len(new_messages) - 1:
            input("\nPress Enter to continue to the next exchange...")

if __name__ == "__main__":
    main()