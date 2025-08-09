#!/usr/bin/env python3
"""
Terminal-based chat interface for ConvoTree with sequential compression.
This script provides a simple CLI for interacting with the sequential compression feature.
Includes recording functionality to save chat sessions.
"""

import json
import os
import sys
import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Sample initial conversation
initial_conversation = [
    {"role": "user", "content": "Hi, I'm Julia and I love jazz."},
    {"role": "assistant", "content": "Hello Julia! What can I do for you today?"},
    {"role": "user", "content": "Who is the pianist in Miles Davis' Kind of Blue?"},
    {"role": "assistant", "content": "That would be Bill Evans on most tracks."},
]

# Recording functionality
class ChatRecorder:
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.transcript = []
        self.filename = f"chat_recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    def start(self):
        """Start recording the chat session."""
        self.enabled = True
        self.transcript = []
        self.transcript.append(f"=== ConvoTree Chat Session Recording ===")
        self.transcript.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.transcript.append(f"Recording started\n")
        print(f"\n>>> Recording started. Output will be saved to {self.filename} <<<\n")
    
    def stop(self):
        """Stop recording and save the transcript."""
        if not self.enabled:
            return
        
        self.enabled = False
        self.transcript.append(f"\nRecording ended: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with open(self.filename, "w") as f:
            f.write("\n".join(self.transcript))
        
        print(f"\n>>> Recording stopped. Saved to {self.filename} <<<\n")
    
    def add_message(self, role, content):
        """Add a message to the transcript."""
        if not self.enabled:
            return
        
        prefix = "User: " if role == "user" else "Assistant: "
        self.transcript.append(f"{prefix}{content}")
    
    def add_kg_snapshot(self, facts):
        """Add a knowledge graph snapshot to the transcript."""
        if not self.enabled:
            return
        
        self.transcript.append("\n=== Knowledge Graph ===")
        for i, fact in enumerate(facts, 1):
            self.transcript.append(f"{i}. {fact}")
        self.transcript.append("=====================\n")
    
    def add_system_message(self, message):
        """Add a system message to the transcript."""
        if not self.enabled:
            return
        
        self.transcript.append(f"\n>>> {message} <<<\n")

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
        self.client = None
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
    
    def extract_facts(self, message: str) -> List[str]:
        """Extract potential facts from a message using OpenAI API."""
        # If no API key or client, use fallback extraction
        if not self.client:
            return self._fallback_extract_facts(message)
        
        try:
            # Create prompt for fact extraction
            prompt = f"""Extract 3-5 factual statements from the following text. 
Focus on jazz-related facts, musicians, albums, and musical concepts.
Return ONLY a numbered list of facts, one per line, with no additional text.

Text: {message}

Facts:"""
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You extract factual statements from text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            # Process the response
            facts_text = response.choices[0].message.content.strip()
            
            # Parse the numbered list
            new_facts = []
            for line in facts_text.split('\n'):
                # Remove numbering and any extra spaces
                line = line.strip()
                if line:
                    # Remove numbering (e.g., "1. ", "1) ", etc.)
                    if '. ' in line[:4] or ') ' in line[:4]:
                        line = line[line.find(' ')+1:]
                    new_facts.append(line)
            
            return new_facts
            
        except Exception as e:
            print(f"\nError extracting facts with API: {e}")
            # Fall back to rule-based extraction if API fails
            return self._fallback_extract_facts(message)
    
    def _fallback_extract_facts(self, message: str) -> List[str]:
        """Fallback method for fact extraction when API is unavailable."""
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
        
        return new_facts
    
    def update(self, message: str):
        """Update the knowledge graph with new facts from a message."""
        if not self.sequential_mode:
            return
        
        new_facts = self.extract_facts(message)
        for fact in new_facts:
            if fact not in self.facts:
                self.facts.append(fact)
    
    def display(self):
        """Display the current knowledge graph."""
        print("\n=== Knowledge Graph ===")
        for i, fact in enumerate(self.facts, 1):
            print(f"{i}. {fact}")
        print("=====================\n")
    
    def toggle_mode(self):
        """Toggle sequential compression mode."""
        self.sequential_mode = not self.sequential_mode
        mode = "ENABLED" if self.sequential_mode else "DISABLED"
        print(f"\n>>> Sequential compression {mode} <<<\n")

# Assistant response generation using OpenAI API
def generate_response(user_input: str, kg: KnowledgeGraph) -> str:
    """Generate a response based on the user input and knowledge graph using OpenAI API."""
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Prepare knowledge graph facts as context
        kg_facts = kg.facts
        kg_context = "\n".join([f"- {fact}" for fact in kg_facts])
        
        # Create the system message with knowledge graph context
        system_message = f"""You are a helpful assistant with knowledge about jazz music. 
The following facts have been extracted from the conversation so far:

{kg_context}

Please use this knowledge to answer the user's question. If you don't know the answer based on the provided facts, 
acknowledge that you're not sure but try to be helpful by suggesting related topics you can discuss.
Keep your responses concise (1-3 sentences)."""
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a more widely available model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Extract and return the response text
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"\nError calling OpenAI API: {e}")
        # Fallback response if API call fails
        return "I apologize, but I encountered an error when trying to generate a response. Please check your API key and internet connection."

def main():
    print("\n=== ConvoTree Terminal Chat ===")
    print("Type 'exit' to quit, 'kg' to view the knowledge graph, or 'toggle' to toggle sequential compression")
    print("Type 'record' to start recording, 'stop' to stop recording")
    print("Sequential compression is ENABLED by default\n")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: No OpenAI API key found in environment variables.")
        print("Please set your API key in a .env file or as an environment variable:")
        print("  echo 'OPENAI_API_KEY=\"your_api_key_here\"' > .env\n")
        print("Continuing with fallback mode (rule-based responses)...\n")
    else:
        print("OpenAI API key found. Using API for responses and fact extraction.\n")
    
    # Initialize knowledge graph and recorder
    kg = KnowledgeGraph()
    recorder = ChatRecorder()
    
    # Display initial knowledge graph
    kg.display()
    
    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for special commands
        if user_input.lower() == 'exit':
            if recorder.enabled:
                recorder.stop()
            print("Goodbye!")
            break
        
        if user_input.lower() == 'kg':
            kg.display()
            if recorder.enabled:
                recorder.add_kg_snapshot(kg.facts)
            continue
        
        if user_input.lower() == 'toggle':
            mode = kg.toggle_mode()
            status = "ENABLED" if mode else "DISABLED"
            print(f"\n>>> Sequential compression {status} <<<\n")
            if recorder.enabled:
                recorder.add_system_message(f"Sequential compression {status}")
            continue
        
        if user_input.lower() == 'record':
            recorder.start()
            # Add initial KG snapshot to recording
            recorder.add_kg_snapshot(kg.facts)
            continue
        
        if user_input.lower() == 'stop':
            recorder.stop()
            continue
        
        # Add user message to recording
        if recorder.enabled:
            recorder.add_message("user", user_input)
        
        # Generate response
        response = generate_response(user_input, kg)
        print(f"Assistant: {response}")
        
        # Add assistant response to recording
        if recorder.enabled:
            recorder.add_message("assistant", response)
        
        # Update knowledge graph if sequential compression is enabled
        kg.update(user_input)
        kg.update(response)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)