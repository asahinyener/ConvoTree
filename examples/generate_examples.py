#!/usr/bin/env python3
# Generate Example Chat Recordings
# ─────────────────────────────────────────────────────────────────────────────
import os
import sys
import json
import datetime
import time
from pathlib import Path
import argparse
import shutil

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from terminal_chat_kg import TerminalChat
from kg_utils import normalize_kg, draw_kg

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES_DIR = Path(__file__).parent
OUTPUTS_DIR = EXAMPLES_DIR / "outputs"
INPUTS_DIR = EXAMPLES_DIR / "sample_inputs"
ANALYSIS_DIR = EXAMPLES_DIR / "analysis"

# Create directories if they don't exist
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Example Scenarios
# ─────────────────────────────────────────────────────────────────────────────
ENTITY_NORMALIZATION_SCENARIO = [
    "Tell me about AI",
    "What's the difference between artificial intelligence and machine learning?",
    "How do neural nets relate to deep learning?",
    "When was artificial intelligence research started?",
    "What are some applications of AI systems today?",
    "kg",  # View knowledge graph
    "save"  # Save knowledge graph image
]

KNOWLEDGE_PRIORITIZATION_SCENARIO = [
    "What is climate change?",
    "What causes greenhouse gas emissions?",
    "Tell me about mitigation strategies",
    "How does adaptation differ from mitigation?",
    "What are the effects of climate change on ecosystems?",
    "kg",  # View knowledge graph
    "save"  # Save knowledge graph image
]

CONTEXT_TRACKING_SCENARIO = [
    "Can you tell me about renewable energy sources?",
    "Which one is most efficient?",
    "How does solar energy work?",
    "What about wind power?",
    "Are there any emerging technologies in this field?",
    "How do they compare in terms of cost?",
    "kg",  # View knowledge graph
    "save"  # Save knowledge graph image
]

RESPONSE_GENERATION_SCENARIO = [
    "What are the main programming paradigms?",
    "Tell me more about functional programming",
    "How does object-oriented programming differ?",
    "What languages support multiple paradigms?",
    "Which paradigm is best for web development?",
    "kg",  # View knowledge graph
    "save"  # Save knowledge graph image
]

# ─────────────────────────────────────────────────────────────────────────────
# Example Generation Functions
# ─────────────────────────────────────────────────────────────────────────────
def generate_example(name, input_file, scenario, analysis_template):
    """Generate an example chat recording."""
    print(f"Generating {name} example...")
    
    # Load input content
    input_path = INPUTS_DIR / input_file
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return
    
    input_content = input_path.read_text(encoding="utf-8")
    
    # Create chat instance
    chat = TerminalChat(input_content)
    
    # Create output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{name.lower().replace(' ', '_')}_{timestamp}.txt"
    output_path = OUTPUTS_DIR / output_file
    
    # Start recording
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"=== {name} Example ===\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write initial knowledge graph
        f.write("=== Initial Knowledge Graph ===\n")
        if chat.bundle and chat.bundle.get("kg"):
            for i, fact in enumerate(chat.bundle.get("kg", []), 1):
                f.write(f"{i}. {fact.replace('|', ' → ')}\n")
        else:
            f.write("(empty)\n")
        f.write("\n")
        
        # Process scenario
        kg_snapshots = []
        for i, query in enumerate(scenario):
            if query == "kg":
                # Skip KG command in the output
                continue
            elif query == "save":
                # Skip save command in the output
                continue
            else:
                f.write(f"User: {query}\n")
                response = chat.generate_response(query)
                f.write(f"Assistant: {response}\n\n")
                
                # Take KG snapshot after each exchange
                if chat.bundle and chat.bundle.get("kg"):
                    kg_snapshot = {
                        "query": query,
                        "kg": chat.bundle.get("kg", []),
                        "current_topic": chat.current_topic
                    }
                    kg_snapshots.append(kg_snapshot)
    
    # Save KG snapshots
    kg_snapshots_file = f"{name.lower().replace(' ', '_')}_kg_snapshots_{timestamp}.json"
    kg_snapshots_path = OUTPUTS_DIR / kg_snapshots_file
    with open(kg_snapshots_path, "w", encoding="utf-8") as f:
        json.dump(kg_snapshots, f, indent=2)
    
    # Save final KG image
    if chat.bundle and chat.bundle.get("kg"):
        kg_image_file = f"{name.lower().replace(' ', '_')}_kg_{timestamp}.png"
        kg_image_path = OUTPUTS_DIR / kg_image_file
        draw_kg(chat.bundle.get("kg", []), kg_image_path)
    
    # Generate analysis
    analysis_file = f"{name.lower().replace(' ', '_')}_analysis_{timestamp}.md"
    analysis_path = ANALYSIS_DIR / analysis_file
    
    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(f"# {name} Example Analysis\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Add analysis template
        f.write(analysis_template)
        
        # Add KG snapshots analysis
        f.write("\n## Knowledge Graph Evolution\n\n")
        for i, snapshot in enumerate(kg_snapshots):
            f.write(f"### After Query {i+1}: \"{snapshot['query']}\"\n\n")
            f.write(f"Current Topic: {snapshot['current_topic']}\n\n")
            f.write("Knowledge Graph:\n")
            for j, fact in enumerate(snapshot['kg'], 1):
                f.write(f"{j}. {fact.replace('|', ' → ')}\n")
            f.write("\n")
    
    print(f"Example generated successfully:")
    print(f"- Chat recording: {output_path}")
    print(f"- KG snapshots: {kg_snapshots_path}")
    print(f"- Analysis: {analysis_path}")
    if chat.bundle and chat.bundle.get("kg"):
        print(f"- KG image: {kg_image_path}")
    
    return {
        "recording": output_path,
        "snapshots": kg_snapshots_path,
        "analysis": analysis_path,
        "image": kg_image_path if chat.bundle and chat.bundle.get("kg") else None
    }

# ─────────────────────────────────────────────────────────────────────────────
# Analysis Templates
# ─────────────────────────────────────────────────────────────────────────────
ENTITY_NORMALIZATION_ANALYSIS = """
## Entity Normalization Features

This example demonstrates how ConvoTree normalizes different references to the same entity, ensuring consistent knowledge representation.

### Key Features Demonstrated:

1. **Entity Resolution**: The system recognizes when different terms refer to the same entity.
   - Example: "AI", "Artificial Intelligence", and "Artificial intelligence" are normalized to the same entity.
   - Example: "Neural networks", "neural nets", and "neural network" are recognized as the same entity.

2. **Triple Standardization**: The system standardizes the format of knowledge graph triples.
   - Subjects and objects are properly normalized
   - Predicates are converted to lowercase and standardized
   - Consistent formatting makes the KG more readable and usable

3. **Deduplication**: The system removes duplicate triples that might arise from different phrasings.
   - When the same fact is mentioned multiple times in different ways, it's stored only once
   - This keeps the KG concise and prevents redundancy

### Implementation Details:

The EntityNormalizer class handles entity normalization through:
- String similarity detection
- Canonical entity mapping
- Entity frequency tracking

The normalize_triple function ensures consistent triple formatting by:
- Normalizing subject and object entities
- Standardizing predicates
- Maintaining the subject|predicate|object format

The normalize_kg function deduplicates triples by:
- Tracking seen triples in a set
- Only adding new, unique triples to the KG
"""

KNOWLEDGE_PRIORITIZATION_ANALYSIS = """
## Knowledge Prioritization Features

This example demonstrates how ConvoTree prioritizes knowledge based on relevance to the current conversation topic.

### Key Features Demonstrated:

1. **Recency Scoring**: More recent information is prioritized in the KG.
   - Newer triples are given higher priority scores
   - This ensures the conversation stays current with the latest information

2. **Relevance Scoring**: Information relevant to the current topic is prioritized.
   - Triples related to the current conversation topic receive higher scores
   - This makes responses more focused and contextually appropriate

3. **Confidence Scoring**: Facts with higher confidence are prioritized.
   - Triples with stronger evidence or more mentions get higher confidence scores
   - This ensures more reliable information is presented first

### Implementation Details:

The KnowledgePrioritizer class handles prioritization through:
- A scoring system that combines recency, relevance, and confidence
- Weighting factors that can be adjusted based on importance
- A prioritize_kg method that returns the most important triples first

The current_topic tracking ensures:
- The system knows what the user is currently interested in
- Relevant knowledge is surfaced in responses
- The conversation maintains coherence across multiple exchanges
"""

CONTEXT_TRACKING_ANALYSIS = """
## Conversation Context Tracking Features

This example demonstrates how ConvoTree maintains conversation context across multiple exchanges.

### Key Features Demonstrated:

1. **Topic Detection**: The system automatically detects the current conversation topic.
   - It analyzes user queries to identify the main topic
   - It extracts key entities from the KG that appear in user messages
   - This allows for more coherent and contextually appropriate responses

2. **Context Preservation**: The system maintains context across multiple exchanges.
   - Previous topics and information are remembered
   - Follow-up questions are understood in context
   - This creates a more natural conversation flow

3. **Sequential Compression**: The KG is updated with each exchange while maintaining context.
   - New information is integrated with existing knowledge
   - Important context is preserved even as the conversation evolves
   - This ensures the KG stays relevant to the current conversation

### Implementation Details:

The _update_current_topic method:
- Analyzes recent user messages to identify the current topic
- Extracts key entities from the KG that appear in the current topic
- Updates the current_topic attribute to guide knowledge prioritization

The generate_response method:
- Updates the current topic based on user input
- Passes the current topic to resume_chat for context-aware responses
- Recompresses the conversation after each exchange to update the KG
"""

RESPONSE_GENERATION_ANALYSIS = """
## Response Generation Features

This example demonstrates how ConvoTree generates responses that incorporate knowledge from the KG.

### Key Features Demonstrated:

1. **KG-Aware Responses**: Responses are generated based on the knowledge graph.
   - The system uses the KG to provide accurate, fact-based responses
   - Information is drawn from multiple related triples
   - This creates more comprehensive and informative answers

2. **Fact References**: Responses explicitly reference facts from the KG.
   - The system includes specific facts from the KG in responses
   - This grounds the responses in the established knowledge
   - Users can see how the system is using the information it has

3. **Context-Sensitive Answers**: Responses are tailored to the current conversation context.
   - The system prioritizes facts relevant to the current topic
   - Follow-up questions are answered in context
   - This creates a more coherent and natural conversation

### Implementation Details:

The build_resume_prompt function:
- Normalizes and prioritizes KG triples based on the current topic
- Formats facts as bullets for easy reference
- Includes the current topic explicitly in the prompt

The resume_chat function:
- Uses the current topic to guide response generation
- Passes prioritized KG facts to the language model
- Ensures responses are relevant to the current conversation context
"""

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────
def main():
    """Generate all examples."""
    examples = []
    
    # Generate entity normalization example
    examples.append(generate_example(
        "Entity Normalization",
        "entity_normalization_input.txt",
        ENTITY_NORMALIZATION_SCENARIO,
        ENTITY_NORMALIZATION_ANALYSIS
    ))
    
    # Generate knowledge prioritization example
    examples.append(generate_example(
        "Knowledge Prioritization",
        "knowledge_prioritization_input.txt",
        KNOWLEDGE_PRIORITIZATION_SCENARIO,
        KNOWLEDGE_PRIORITIZATION_ANALYSIS
    ))
    
    # Generate context tracking example
    examples.append(generate_example(
        "Context Tracking",
        "context_tracking_input.txt",
        CONTEXT_TRACKING_SCENARIO,
        CONTEXT_TRACKING_ANALYSIS
    ))
    
    # Generate response generation example
    examples.append(generate_example(
        "Response Generation",
        "response_generation_input.txt",
        RESPONSE_GENERATION_SCENARIO,
        RESPONSE_GENERATION_ANALYSIS
    ))
    
    # Generate index file
    index_path = EXAMPLES_DIR / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# ConvoTree Examples Index\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, example in enumerate(examples, 1):
            if example:
                name = example["recording"].stem.split("_")[0].replace("_", " ").title()
                f.write(f"## {i}. {name}\n\n")
                f.write(f"- [Chat Recording]({example['recording'].relative_to(EXAMPLES_DIR)})\n")
                f.write(f"- [KG Snapshots]({example['snapshots'].relative_to(EXAMPLES_DIR)})\n")
                f.write(f"- [Analysis]({example['analysis'].relative_to(EXAMPLES_DIR)})\n")
                if example["image"]:
                    f.write(f"- [KG Image]({example['image'].relative_to(EXAMPLES_DIR)})\n")
                f.write("\n")
    
    print(f"\nAll examples generated successfully. Index file created at {index_path}")

if __name__ == "__main__":
    main()