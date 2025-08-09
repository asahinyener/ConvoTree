#!/usr/bin/env python3
# ConvoTree Terminal Chat with KG Integration
# ─────────────────────────────────────────────────────────────────────────────
import os
import json
import datetime
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load environment variables from .env file
load_dotenv()

from openai import OpenAI

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OPENAI_API_KEY environment variable is not set.")
    print("Set it with: export OPENAI_API_KEY=your_api_key_here")
    print("or create a .env file with: OPENAI_API_KEY=your_api_key_here")

# Initialize OpenAI client
client = None
if api_key:
    client = OpenAI(api_key=api_key)

# Define the model to use
GPT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Load prompts
PROMPT_PATH = Path("prompts/compressor_prompt.txt")
if not os.path.exists(PROMPT_PATH):
    raise SystemExit("Missing compressor_prompt.txt – add your system prompt.")
SYSTEM_PROMPT = Path(PROMPT_PATH).read_text(encoding="utf-8")

TEMPLATE_PATH = Path("prompts/resume_prompt.txt")
if not TEMPLATE_PATH.exists():
    raise SystemExit(
        "Missing prompts/resume_prompt.txt – please create it before running the server."
    )

# Create output directory for chat recordings
RECORDINGS_DIR = Path("recordings")
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Graph Functions
# ─────────────────────────────────────────────────────────────────────────────
def draw_kg(triples: List[str], outfile: Path) -> None:
    """Render a simple force-layout PNG of the KG triples."""
    if not triples:
        return
    G = nx.DiGraph()
    for trip in triples:
        try:
            s, p, o = (x.strip() for x in trip.split("|", 2))
        except ValueError:
            continue
        G.add_edge(s, o, label=p)
    pos = nx.spring_layout(G, k=0.6, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightblue")
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="-|>")
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_size=6
    )
    plt.axis("off")
    plt.tight_layout()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outfile, dpi=150)
    plt.close()


def build_resume_prompt(kg: List[str], ds: Dict[str, Any]) -> str:
    """Build a prompt for resuming the conversation."""
    tmpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    # Include more KG facts (up to 15 instead of 7) for better context
    bullets = [f"• {t.replace('|', ' → ')}" for t in kg[:15]]
    facts = "\n".join(bullets) if bullets else "(none)"
    return (
        tmpl.replace("{{facts}}", facts)
            .replace("{{ds_json}}", json.dumps(ds, ensure_ascii=False))
    )


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI API Functions
# ─────────────────────────────────────────────────────────────────────────────
def compress_chat(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Compress a chat conversation into a knowledge graph."""
    if not client:
        return fallback_compress_chat(messages)
    
    try:
        resp = client.chat.completions.create(
            model=GPT_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps({"messages": messages})},
            ],
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"Error compressing chat: {e}")
        return fallback_compress_chat(messages)


def resume_chat(bundle: Dict[str, Any], next_user: str) -> Dict[str, str]:
    """Generate a response based on the knowledge graph and the next user message."""
    if not client:
        return {"assistant_reply": fallback_generate_response(bundle, next_user)}
    
    try:
        prompt = build_resume_prompt(bundle.get("kg", []), bundle.get("ds", {}))
        resp = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": next_user},
            ],
        )
        return {"assistant_reply": resp.choices[0].message.content}
    except Exception as e:
        print(f"Error resuming chat: {e}")
        return {"assistant_reply": fallback_generate_response(bundle, next_user)}


# ─────────────────────────────────────────────────────────────────────────────
# Fallback Functions (when API is unavailable)
# ─────────────────────────────────────────────────────────────────────────────
def fallback_compress_chat(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Fallback function for compressing chat when API is unavailable."""
    # Extract simple facts from messages
    kg = []
    for msg in messages:
        content = msg.get("content", "").lower()
        
        # Extract facts about jazz
        if "jazz" in content:
            kg.append("Jazz|is a|music genre")
        
        # Extract facts about Miles Davis
        if "miles davis" in content:
            kg.append("Miles Davis|is a|jazz musician")
            kg.append("Miles Davis|plays|trumpet")
        
        # Extract facts about albums
        if "kind of blue" in content:
            kg.append("Kind of Blue|is an album by|Miles Davis")
            kg.append("Kind of Blue|released in|1959")
        
        if "birth of the cool" in content:
            kg.append("Birth of the Cool|is an album by|Miles Davis")
        
        if "bitches brew" in content:
            kg.append("Bitches Brew|is an album by|Miles Davis")
            kg.append("Bitches Brew|is a|fusion album")
        
        # Extract facts about other musicians
        if "john coltrane" in content:
            kg.append("John Coltrane|plays|saxophone")
            kg.append("John Coltrane|collaborated with|Miles Davis")
        
        if "bill evans" in content:
            kg.append("Bill Evans|plays|piano")
            kg.append("Bill Evans|performed on|Kind of Blue")
    
    # Create trace of the conversation
    trace = []
    for i, msg in enumerate(messages):
        trace.append(f"{i}|{msg.get('role', 'user')}|{msg.get('content', '')[:25]}...")
    
    # Create a simple dialogue state
    ds = {
        "topic": "jazz music",
        "mentioned_artists": ["Miles Davis"] if any("miles davis" in msg.get("content", "").lower() for msg in messages) else [],
        "mentioned_albums": []
    }
    
    if any("kind of blue" in msg.get("content", "").lower() for msg in messages):
        ds["mentioned_albums"].append("Kind of Blue")
    
    # Create links between ds and kg
    links = [
        {"ds": "topic", "kg": ["Jazz"]}
    ]
    
    if "Miles Davis" in ds["mentioned_artists"]:
        links.append({"ds": "mentioned_artists", "kg": ["Miles Davis"]})
    
    if "Kind of Blue" in ds["mentioned_albums"]:
        links.append({"ds": "mentioned_albums", "kg": ["Kind of Blue"]})
    
    # Create a dialogue prompt
    dp = "You are discussing jazz music, focusing on Miles Davis and his albums."
    
    return {
        "kg": kg,
        "ds": ds,
        "links": links,
        "trace": trace,
        "dp": dp
    }


def fallback_generate_response(bundle: Dict[str, Any], next_user: str) -> str:
    """Fallback function for generating responses when API is unavailable."""
    # Simple rule-based response generation
    response = "I'm sorry, but I can't access the OpenAI API right now. "
    
    if "miles davis" in next_user.lower():
        response += "Miles Davis was a legendary jazz trumpeter known for albums like Kind of Blue and Bitches Brew."
    elif "coltrane" in next_user.lower():
        response += "John Coltrane was a revolutionary saxophonist who collaborated with Miles Davis before leading his own groups."
    elif "kind of blue" in next_user.lower():
        response += "Kind of Blue is considered one of the greatest jazz albums of all time, featuring Miles Davis, John Coltrane, and Bill Evans."
    elif "jazz" in next_user.lower():
        response += "Jazz is a music genre that originated in the African-American communities of New Orleans in the late 19th and early 20th centuries."
    else:
        response += "I can provide information about jazz musicians like Miles Davis and John Coltrane, or albums like Kind of Blue."
    
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Chat Recorder
# ─────────────────────────────────────────────────────────────────────────────
class ChatRecorder:
    def __init__(self):
        self.enabled = False
        self.transcript = []
        self.start_time = None
        self.filename = None
    
    def start(self):
        """Start recording the chat session."""
        self.enabled = True
        self.transcript = []
        self.start_time = datetime.datetime.now()
        self.filename = f"chat_recording_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt"
        self.transcript.append(f"=== Chat Recording Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        return self.filename
    
    def stop(self) -> Optional[str]:
        """Stop recording and save the transcript."""
        if not self.enabled:
            return None
        
        self.enabled = False
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        self.transcript.append(f"\n=== Chat Recording Ended at {end_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        self.transcript.append(f"=== Duration: {duration} ===")
        
        # Save transcript to file
        filepath = RECORDINGS_DIR / self.filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(self.transcript))
        
        return str(filepath)
    
    def add_message(self, role: str, content: str):
        """Add a message to the transcript."""
        if not self.enabled:
            return
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.transcript.append(f"[{timestamp}] {role.upper()}: {content}\n")
    
    def add_kg_snapshot(self, kg: List[str]):
        """Add a snapshot of the knowledge graph to the transcript."""
        if not self.enabled:
            return
        
        self.transcript.append("\n=== Knowledge Graph Snapshot ===")
        for i, fact in enumerate(kg, 1):
            self.transcript.append(f"{i}. {fact.replace('|', ' → ')}")
        self.transcript.append("=====================\n")
    
    def add_system_message(self, message: str):
        """Add a system message to the transcript."""
        if not self.enabled:
            return
        
        self.transcript.append(f"\n>>> {message} <<<\n")
    
    def add_new_facts(self, facts: List[str], source: str):
        """Add newly extracted facts to the transcript."""
        if not self.enabled or not facts:
            return
            
        self.transcript.append(f"\n>>> New facts from {source}: <<<")
        for fact in facts:
            self.transcript.append(f"  - {fact}")


# ─────────────────────────────────────────────────────────────────────────────
# File Loading Functions
# ─────────────────────────────────────────────────────────────────────────────
def load_content_from_file(filepath: str) -> str:
    """Load content from a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error loading file: {e}")
        return ""

def parse_content_to_messages(content: str) -> List[Dict[str, str]]:
    """Parse content into a list of messages.
    
    This function tries to detect conversation format. If it can't,
    it treats the entire content as a single user message.
    """
    messages = []
    
    # Try to detect conversation format
    lines = content.split('\n')
    current_role = None
    current_content = []
    
    # Common patterns for conversation markers
    user_patterns = ['user:', 'human:', 'you:', 'question:', 'q:']
    assistant_patterns = ['assistant:', 'ai:', 'bot:', 'answer:', 'a:']
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        line_lower = line.lower()
        
        # Check if this line starts a new message
        is_user = any(line_lower.startswith(pattern) for pattern in user_patterns)
        is_assistant = any(line_lower.startswith(pattern) for pattern in assistant_patterns)
        
        if is_user or is_assistant:
            # Save the previous message if there was one
            if current_role and current_content:
                messages.append({
                    "role": current_role,
                    "content": '\n'.join(current_content).strip()
                })
                current_content = []
            
            # Set the new role
            current_role = "user" if is_user else "assistant"
            
            # Extract content after the role marker
            content_start = line.find(':') + 1
            if content_start > 0:
                current_content.append(line[content_start:].strip())
        elif current_role:
            # Continue the current message
            current_content.append(line)
        else:
            # If no role detected yet, assume it's user content
            current_role = "user"
            current_content.append(line)
    
    # Add the last message
    if current_role and current_content:
        messages.append({
            "role": current_role,
            "content": '\n'.join(current_content).strip()
        })
    
    # If no messages were detected, treat the entire content as a single user message
    if not messages and content.strip():
        messages.append({
            "role": "user",
            "content": content.strip()
        })
    
    return messages

# ─────────────────────────────────────────────────────────────────────────────
# Terminal Chat Interface
# ─────────────────────────────────────────────────────────────────────────────
class TerminalChat:
    def __init__(self, initial_content: Optional[str] = None):
        self.messages = []
        self.bundle = None
        self.sequential_mode = True
        self.recorder = ChatRecorder()
        
        # Initialize with content if provided
        if initial_content:
            initial_messages = parse_content_to_messages(initial_content)
            for msg in initial_messages:
                self.add_message(msg["role"], msg["content"])
            
            # Build initial knowledge graph
            print("Building initial knowledge graph from provided content...")
            self.bundle = self.compress()
            print("Initial knowledge graph built successfully.")
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
        
        # Record the message if recording is enabled
        if self.recorder.enabled:
            self.recorder.add_message(role, content)
    
    def compress(self):
        """Compress the conversation into a knowledge graph."""
        self.bundle = compress_chat(self.messages)
        return self.bundle
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response based on the user input."""
        # Add user message to history
        self.add_message("user", user_input)
        
        # If this is the first message, compress the conversation
        if not self.bundle:
            self.bundle = self.compress()
        
        # Generate response
        if self.sequential_mode:
            # In sequential mode, we update the KG with each exchange
            response_data = resume_chat(self.bundle, user_input)
            response = response_data["assistant_reply"]
            
            # Add assistant message to history
            self.add_message("assistant", response)
            
            # Recompress the entire conversation to update the KG
            self.bundle = self.compress()
        else:
            # In non-sequential mode, we use the initial KG
            response_data = resume_chat(self.bundle, user_input)
            response = response_data["assistant_reply"]
            
            # Add assistant message to history
            self.add_message("assistant", response)
        
        return response
    
    def toggle_sequential_mode(self):
        """Toggle sequential compression mode."""
        self.sequential_mode = not self.sequential_mode
        return self.sequential_mode
    
    def display_kg(self):
        """Display the current knowledge graph."""
        if not self.bundle or not self.bundle.get("kg"):
            print("\n=== Knowledge Graph is empty ===\n")
            return
        
        kg = self.bundle.get("kg", [])
        print("\n=== Knowledge Graph ===")
        for i, fact in enumerate(kg, 1):
            print(f"{i}. {fact.replace('|', ' → ')}")
        print()
        
        # Record KG snapshot if recording is enabled
        if self.recorder.enabled:
            self.recorder.add_kg_snapshot(kg)
    
    def save_kg_image(self, filename: str = "kg_snapshot.png"):
        """Save the knowledge graph as an image."""
        if not self.bundle or not self.bundle.get("kg"):
            print("Knowledge Graph is empty, no image saved.")
            return None
        
        kg = self.bundle.get("kg", [])
        outfile = RECORDINGS_DIR / filename
        draw_kg(kg, outfile)
        print(f"Knowledge Graph image saved to {outfile}")
        return outfile


# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="ConvoTree Terminal Chat with KG Integration")
    parser.add_argument("--file", "-f", type=str, help="Path to a text file to initialize the conversation")
    parser.add_argument("--model", "-m", type=str, help="OpenAI model to use (default: from .env or gpt-3.5-turbo)")
    args = parser.parse_args()
    
    # Update model if specified
    global GPT_MODEL
    if args.model:
        GPT_MODEL = args.model
        print(f"Using specified model: {GPT_MODEL}")
    
    print("\n=== ConvoTree Terminal Chat ===")
    print("Type 'exit' to quit, 'kg' to view the knowledge graph, or 'toggle' to toggle sequential compression")
    print("Type 'record' to start recording, 'stop' to stop recording")
    print("Type 'save' to save the knowledge graph as an image")
    print("Sequential compression is ENABLED by default\n")
    
    # Check for API key
    if not api_key:
        print("WARNING: No OpenAI API key found in environment variables.")
        print("Please set your API key in a .env file or as an environment variable:")
        print("  echo 'OPENAI_API_KEY=\"your_api_key_here\"' > .env\n")
        print("Continuing with fallback mode (rule-based responses)...\n")
    else:
        print(f"OpenAI API key found. Using API with model: {GPT_MODEL}\n")
    
    # Initialize chat with file content if provided
    initial_content = None
    if args.file:
        print(f"Loading content from file: {args.file}")
        initial_content = load_content_from_file(args.file)
        if not initial_content:
            print("Failed to load content from file. Starting with empty conversation.")
    
    # Initialize chat
    chat = TerminalChat(initial_content)
    
    # Display initial knowledge graph if it exists
    if chat.bundle and chat.bundle.get("kg"):
        print("\nInitial Knowledge Graph:")
        chat.display_kg()
    
    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Handle special commands
        if user_input.lower() == "exit":
            if chat.recorder.enabled:
                filepath = chat.recorder.stop()
                print(f"Chat recording saved to {filepath}")
            print("Goodbye!")
            break
        
        elif user_input.lower() == "kg":
            chat.display_kg()
            continue
        
        elif user_input.lower() == "toggle":
            mode = chat.toggle_sequential_mode()
            print(f"Sequential compression {'ENABLED' if mode else 'DISABLED'}")
            if chat.recorder.enabled:
                chat.recorder.add_system_message(f"Sequential compression {'ENABLED' if mode else 'DISABLED'}")
            continue
        
        elif user_input.lower() == "record":
            if chat.recorder.enabled:
                print("Recording is already active.")
            else:
                filename = chat.recorder.start()
                print(f"Recording started. Output will be saved to {filename}")
                # Add KG snapshot to recording
                if chat.bundle and chat.bundle.get("kg"):
                    chat.recorder.add_kg_snapshot(chat.bundle.get("kg", []))
            continue
        
        elif user_input.lower() == "stop":
            if not chat.recorder.enabled:
                print("No recording is active.")
            else:
                filepath = chat.recorder.stop()
                print(f"Recording stopped. Transcript saved to {filepath}")
            continue
        
        elif user_input.lower() == "save":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kg_snapshot_{timestamp}.png"
            filepath = chat.save_kg_image(filename)
            if filepath and chat.recorder.enabled:
                chat.recorder.add_system_message(f"Knowledge Graph image saved to {filepath}")
            continue
        
        # Generate response
        print("Assistant: ", end="", flush=True)
        
        # Show typing animation
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.3)
        print("\b\b\b", end="", flush=True)  # Erase the dots
        
        response = chat.generate_response(user_input)
        print(response)
        
        # Display updated KG if in sequential mode
        if chat.sequential_mode:
            print("\n(Knowledge Graph updated)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")