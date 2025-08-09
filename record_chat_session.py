#!/usr/bin/env python3
"""
Script to record a chat session with the terminal chat interface.
This will simulate a conversation and save the transcript to a file.
"""

import json
import os
import time
import datetime
from typing import List, Dict, Any

# Simulated conversation
conversation = [
    {"role": "user", "content": "Hello, I'm interested in learning about jazz music."},
    {"role": "assistant", "content": "Hello! I'm your jazz conversation assistant. How can I help you today?"},
    {"role": "user", "content": "Tell me about Miles Davis."},
    {"role": "assistant", "content": "Miles Davis was a pioneering jazz musician who constantly evolved his style throughout his career, from bebop to cool jazz to modal jazz to fusion."},
    {"role": "user", "content": "kg"},  # Special command to view knowledge graph
    {"role": "user", "content": "What albums did he record?"},
    {"role": "assistant", "content": "Miles Davis recorded many influential albums throughout his career. Some of his most notable albums include 'Kind of Blue', 'Birth of the Cool', 'Milestones', 'Sketches of Spain', 'E.S.P.', 'In a Silent Way', and 'Bitches Brew' which pioneered jazz fusion."},
    {"role": "user", "content": "kg"},  # Check knowledge graph again
    {"role": "user", "content": "toggle"},  # Turn off sequential compression
    {"role": "user", "content": "Who played on Bitches Brew?"},
    {"role": "assistant", "content": "I'm not sure about that. Would you like to know more about Miles Davis, his albums like 'Kind of Blue', or jazz in general?"},
    {"role": "user", "content": "kg"},  # Check knowledge graph (should be unchanged)
    {"role": "user", "content": "toggle"},  # Turn sequential compression back on
    {"role": "user", "content": "Who played on Bitches Brew?"},
    {"role": "assistant", "content": "Miles Davis collaborated with many talented musicians throughout his career. On 'Bitches Brew', he worked with Wayne Shorter, Chick Corea, and John McLaughlin. On 'Birth of the Cool', he worked with Gil Evans and Gerry Mulligan. His 'Second Great Quintet' included Wayne Shorter, Herbie Hancock, Ron Carter, and Tony Williams."},
    {"role": "user", "content": "kg"},  # Check final knowledge graph
    {"role": "user", "content": "exit"}  # End the session
]

# Knowledge Graph simulation
class KnowledgeGraph:
    def __init__(self):
        self.facts = [
            "Julia likes jazz music",
            "The conversation discusses Miles Davis",
            "Kind of Blue is an album by Miles Davis",
            "Bill Evans played piano on Kind of Blue"
        ]
        self.sequential_mode = True
    
    def extract_facts(self, message: str) -> List[str]:
        """Extract potential facts from a message."""
        new_facts = []
        
        # Simple rule-based fact extraction
        message = message.lower()
        
        # Jazz-related facts
        if "jazz" in message:
            new_facts.append("The conversation involves jazz music")
        
        # Miles Davis facts
        if "miles davis" in message:
            new_facts.append("Miles Davis is being discussed")
        if "trumpet" in message and "davis" in message:
            new_facts.append("Miles Davis was a trumpet player")
        if "1926" in message and "davis" in message:
            new_facts.append("Miles Davis was born in 1926")
        
        # Album facts
        if "kind of blue" in message:
            new_facts.append("Kind of Blue is an album by Miles Davis")
        if "birth of the cool" in message:
            new_facts.append("Birth of the Cool is an album by Miles Davis")
        if "bitches brew" in message:
            new_facts.append("Bitches Brew is an album by Miles Davis")
        if "sketches of spain" in message:
            new_facts.append("Sketches of Spain is an album by Miles Davis")
        if "in a silent way" in message:
            new_facts.append("In a Silent Way is an album by Miles Davis")
        
        # Musician facts
        if "bill evans" in message:
            new_facts.append("Bill Evans was a pianist")
        if "john coltrane" in message:
            new_facts.append("John Coltrane played saxophone")
        if "cannonball adderley" in message:
            new_facts.append("Cannonball Adderley played saxophone")
        if "wayne shorter" in message:
            new_facts.append("Wayne Shorter collaborated with Miles Davis")
        if "herbie hancock" in message:
            new_facts.append("Herbie Hancock played piano with Miles Davis")
        if "tony williams" in message:
            new_facts.append("Tony Williams was a drummer who played with Miles Davis")
        if "chick corea" in message:
            new_facts.append("Chick Corea played with Miles Davis on Bitches Brew")
        if "john mclaughlin" in message:
            new_facts.append("John McLaughlin played guitar on Bitches Brew")
        
        return new_facts
    
    def update(self, message: str):
        """Update the knowledge graph with new facts from a message."""
        if not self.sequential_mode:
            return
        
        new_facts = self.extract_facts(message)
        for fact in new_facts:
            if fact not in self.facts:
                self.facts.append(fact)
    
    def get_facts(self):
        """Return the current knowledge graph facts."""
        return self.facts
    
    def toggle_mode(self):
        """Toggle sequential compression mode."""
        self.sequential_mode = not self.sequential_mode
        return self.sequential_mode

def main():
    # Initialize transcript
    transcript = []
    transcript.append("=== ConvoTree Chat Session Recording ===")
    transcript.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    transcript.append("Sequential compression is ENABLED by default\n")
    
    # Initialize knowledge graph
    kg = KnowledgeGraph()
    
    # Display initial knowledge graph
    transcript.append("=== Initial Knowledge Graph ===")
    for i, fact in enumerate(kg.get_facts(), 1):
        transcript.append(f"{i}. {fact}")
    transcript.append("=====================\n")
    
    # Process the conversation
    for msg in conversation:
        role = msg["role"]
        content = msg["content"]
        
        # Handle special commands
        if role == "user" and content == "kg":
            transcript.append("User requested knowledge graph:")
            transcript.append("=== Knowledge Graph ===")
            for i, fact in enumerate(kg.get_facts(), 1):
                transcript.append(f"{i}. {fact}")
            transcript.append("=====================\n")
            continue
        
        if role == "user" and content == "toggle":
            mode = kg.toggle_mode()
            status = "ENABLED" if mode else "DISABLED"
            transcript.append(f"User toggled sequential compression: {status}\n")
            continue
        
        if role == "user" and content == "exit":
            transcript.append("User exited the chat.")
            break
        
        # Add message to transcript
        prefix = "User: " if role == "user" else "Assistant: "
        transcript.append(f"{prefix}{content}")
        
        # Update knowledge graph if sequential compression is enabled
        if role == "user" or role == "assistant":
            kg.update(content)
        
        # Add a small delay to simulate real-time conversation
        time.sleep(0.5)
    
    # Save transcript to file
    with open("chat_session_recording.txt", "w") as f:
        f.write("\n".join(transcript))
    
    print(f"Chat session recorded and saved to chat_session_recording.txt")

if __name__ == "__main__":
    main()