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

# Assistant response generation
def generate_response(user_input: str, kg: KnowledgeGraph) -> str:
    """Generate a response based on the user input and knowledge graph."""
    user_input = user_input.lower()
    
    # Simple rule-based responses
    if "hello" in user_input or "hi" in user_input or "hey" in user_input:
        return "Hello! I'm your jazz conversation assistant. How can I help you today?"
    
    if "bye" in user_input or "goodbye" in user_input:
        return "Goodbye! It was nice chatting with you about jazz."
    
    if "thank" in user_input:
        return "You're welcome! Is there anything else you'd like to know about jazz?"
    
    # Miles Davis related queries
    if "miles davis" in user_input:
        if "who" in user_input:
            return "Miles Davis was a legendary jazz trumpeter and composer born on May 26, 1926. He was one of the most influential figures in the history of jazz and 20th-century music."
        
        if "album" in user_input or "record" in user_input:
            return "Miles Davis recorded many influential albums throughout his career. Some of his most notable albums include 'Kind of Blue', 'Birth of the Cool', 'Milestones', 'Sketches of Spain', 'E.S.P.', 'In a Silent Way', and 'Bitches Brew' which pioneered jazz fusion."
        
        if "play" in user_input or "musician" in user_input or "band" in user_input:
            return "Miles Davis collaborated with many talented musicians throughout his career. On 'Kind of Blue', he worked with Bill Evans, John Coltrane, Cannonball Adderley, Paul Chambers, and Jimmy Cobb. His 'Second Great Quintet' included Wayne Shorter, Herbie Hancock, Ron Carter, and Tony Williams."
        
        return "Miles Davis was a pioneering jazz musician who constantly evolved his style throughout his career, from bebop to cool jazz to modal jazz to fusion."
    
    # Kind of Blue related queries
    if "kind of blue" in user_input:
        if "pianist" in user_input or "piano" in user_input:
            return "Bill Evans played piano on most tracks of 'Kind of Blue', with Wynton Kelly playing on 'Freddie Freeloader'."
        
        if "record" in user_input or "when" in user_input:
            return "'Kind of Blue' was recorded in 1959 and is considered one of the greatest jazz albums of all time."
        
        if "musician" in user_input or "play" in user_input:
            return "The musicians on 'Kind of Blue' were Miles Davis (trumpet), John Coltrane (tenor saxophone), Cannonball Adderley (alto saxophone), Bill Evans (piano), Wynton Kelly (piano on 'Freddie Freeloader'), Paul Chambers (bass), and Jimmy Cobb (drums)."
        
        return "'Kind of Blue' is considered one of the most influential jazz albums of all time and is known for its use of modal jazz."
    
    # Jazz related queries
    if "jazz" in user_input:
        if "what" in user_input and "is" in user_input:
            return "Jazz is a music genre that originated in the African-American communities of New Orleans in the late 19th and early 20th centuries. It's characterized by swing and blue notes, complex chords, call and response vocals, polyrhythms, and improvisation."
        
        if "history" in user_input:
            return "Jazz has a rich history that evolved from ragtime and blues in the early 20th century. It developed through various styles including Dixieland, swing, bebop, cool jazz, hard bop, modal jazz, free jazz, and fusion."
        
        return "Jazz is a diverse and rich musical tradition with many subgenres and influential artists throughout its history."
    
    # Default response
    return "I'm not sure about that. Would you like to know more about Miles Davis, his albums like 'Kind of Blue', or jazz in general?"

def main():
    print("\n=== ConvoTree Terminal Chat ===")
    print("Type 'exit' to quit, 'kg' to view the knowledge graph, or 'toggle' to toggle sequential compression")
    print("Type 'record' to start recording, 'stop' to stop recording")
    print("Sequential compression is ENABLED by default\n")
    
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