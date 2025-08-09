#!/usr/bin/env python3
"""
Test script for sequential KG compression in ConvoTree.
"""

from terminal_chat_kg import TerminalChat

def main():
    # Create a new chat instance
    chat = TerminalChat()
    
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