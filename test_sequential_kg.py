#!/usr/bin/env python3
"""
Test script for sequential KG compression in ConvoTree.
"""

import sys
import os
import json

# Create a simple implementation for testing
class MockTerminalChat:
    """Mock implementation of TerminalChat for testing sequential compression."""
    
    def __init__(self):
        """Initialize the chat."""
        self.messages = []
        self.bundle = None
        self.sequential_mode = False
        self.current_topic = ""
        self._last_compressed_index = 0
        
    def toggle_sequential_mode(self):
        """Toggle sequential compression mode."""
        self.sequential_mode = not self.sequential_mode
        return self.sequential_mode
    
    def add_message(self, role, content):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
    
    def generate_response(self, user_input):
        """Generate a response based on the user input."""
        # Add user message to history
        self.add_message("user", user_input)
        
        # Update current topic based on user input
        self.current_topic = user_input
        
        # Generate response based on user input
        response = self._mock_generate_response(user_input)
        
        # Add assistant message to history
        self.add_message("assistant", response)
        
        # Update KG
        self._update_kg()
        
        return response
    
    def _mock_generate_response(self, user_input):
        """Generate a mock response based on user input."""
        user_input_lower = user_input.lower()
        
        if "miles davis" in user_input_lower:
            if "influence" in user_input_lower:
                return "Miles Davis had an enormous influence on jazz and popular music. He pioneered several jazz movements, including cool jazz, modal jazz, and jazz fusion."
            elif "instrument" in user_input_lower:
                return "Miles Davis primarily played the trumpet. He was known for his distinctive playing style, characterized by his use of space and lyrical phrasing."
            elif "album" in user_input_lower:
                return "Miles Davis released many influential albums. His most famous album is 'Kind of Blue' (1959), which is often regarded as the greatest jazz album of all time."
            else:
                return "Miles Davis was one of the most influential jazz musicians of the 20th century. He was a trumpeter, bandleader, and composer."
        
        elif "coltrane" in user_input_lower:
            return "John Coltrane was a legendary jazz saxophonist who collaborated with Miles Davis in the 1950s. His album 'A Love Supreme' is considered one of the greatest jazz albums ever recorded."
        
        else:
            return "I'm not sure what specific information you're looking for. Could you please clarify your question?"
    
    def _update_kg(self):
        """Update the knowledge graph based on conversation history."""
        # In sequential mode, we accumulate knowledge
        if self.sequential_mode:
            # Initialize KG if it doesn't exist
            if not self.bundle:
                self.bundle = {"kg": []}
            
            # Add new facts based on the latest exchange
            latest_user_msg = self.messages[-2]["content"].lower()
            latest_assistant_msg = self.messages[-1]["content"]
            
            new_facts = []
            
            # Add facts based on user input
            if "miles davis" in latest_user_msg:
                new_facts.append("Miles Davis|is a|legendary jazz musician")
                new_facts.append("Miles Davis|played|trumpet")
                
                if "instrument" in latest_user_msg:
                    new_facts.append("Miles Davis|was known for|distinctive playing style")
                    new_facts.append("Trumpet|is a|brass instrument")
                
                if "album" in latest_user_msg:
                    new_facts.append("Kind of Blue|is an album by|Miles Davis")
                    new_facts.append("Kind of Blue|was released in|1959")
                    new_facts.append("Bitches Brew|is an album by|Miles Davis")
                
                if "influence" in latest_user_msg:
                    new_facts.append("Miles Davis|pioneered|cool jazz")
                    new_facts.append("Miles Davis|pioneered|modal jazz")
                    new_facts.append("Miles Davis|pioneered|jazz fusion")
            
            if "coltrane" in latest_user_msg:
                new_facts.append("John Coltrane|is a|legendary jazz saxophonist")
                new_facts.append("John Coltrane|played with|Miles Davis")
                new_facts.append("John Coltrane|released|A Love Supreme")
            
            # Add conversation meta-facts
            new_facts.append(f"User|asked about|{latest_user_msg[:20]}...")
            
            # Add to existing KG, avoiding duplicates
            existing_kg = set(self.bundle["kg"])
            for fact in new_facts:
                existing_kg.add(fact)
            
            self.bundle["kg"] = list(existing_kg)
    
    def display_kg(self):
        """Display the knowledge graph."""
        if not self.bundle or not self.bundle.get("kg"):
            print("No knowledge graph available yet.")
            return
        
        print("\n=== Knowledge Graph ===")
        for i, fact in enumerate(self.bundle["kg"], 1):
            print(f"{i}. {fact.replace('|', ' → ')}")
        
        if self.current_topic:
            print(f"\nCurrent topic: {self.current_topic}")
        print()

def main():
    # Create a new chat instance
    chat = MockTerminalChat()
    
    # Enable sequential mode
    chat.toggle_sequential_mode()
    print("Sequential mode enabled")
    
    # First exchange
    print("\n--- First Exchange ---")
    response = chat.generate_response("Tell me about Miles Davis")
    print(f"User: Tell me about Miles Davis")
    print(f"Assistant: {response}")
    
    # Display KG after first exchange
    print("\nKnowledge Graph after first exchange:")
    chat.display_kg()
    
    # Second exchange
    print("\n--- Second Exchange ---")
    response = chat.generate_response("What instruments did he play?")
    print(f"User: What instruments did he play?")
    print(f"Assistant: {response}")
    
    # Display KG after second exchange
    print("\nKnowledge Graph after second exchange:")
    chat.display_kg()
    
    # Third exchange
    print("\n--- Third Exchange ---")
    response = chat.generate_response("Tell me about his most famous albums")
    print(f"User: Tell me about his most famous albums")
    print(f"Assistant: {response}")
    
    # Display KG after third exchange
    print("\nKnowledge Graph after third exchange:")
    chat.display_kg()
    
    # Fourth exchange - change topic
    print("\n--- Fourth Exchange (Topic Change) ---")
    response = chat.generate_response("Let's talk about John Coltrane instead")
    print(f"User: Let's talk about John Coltrane instead")
    print(f"Assistant: {response}")
    
    # Display KG after fourth exchange
    print("\nKnowledge Graph after fourth exchange:")
    chat.display_kg()
    
    # Fifth exchange - back to Miles Davis
    print("\n--- Fifth Exchange (Back to Original Topic) ---")
    response = chat.generate_response("Actually, let's go back to Miles Davis. What was his influence on jazz?")
    print(f"User: Actually, let's go back to Miles Davis. What was his influence on jazz?")
    print(f"Assistant: {response}")
    
    # Display KG after fifth exchange
    print("\nKnowledge Graph after fifth exchange:")
    chat.display_kg()

if __name__ == "__main__":
    main()