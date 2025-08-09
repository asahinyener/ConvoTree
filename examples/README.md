# ConvoTree Example Chat Recordings

This directory contains example chat recordings that demonstrate the various features of ConvoTree's conversation-aware Knowledge Graph.

## Examples Overview

### 1. Entity Normalization
- **File**: `entity_normalization_example.txt`
- **Description**: Demonstrates how the system normalizes different references to the same entity, ensuring consistent knowledge representation.
- **Key Features**: Entity resolution, triple standardization, deduplication

### 2. Knowledge Prioritization
- **File**: `knowledge_prioritization_example.txt`
- **Description**: Shows how the system prioritizes knowledge based on relevance to the current conversation topic.
- **Key Features**: Recency scoring, relevance scoring, confidence scoring

### 3. Conversation Context Tracking
- **File**: `context_tracking_example.txt`
- **Description**: Illustrates how the system maintains conversation context across multiple exchanges.
- **Key Features**: Topic detection, context preservation, sequential compression

### 4. Response Generation
- **File**: `response_generation_example.txt`
- **Description**: Demonstrates how the system generates responses that incorporate knowledge from the KG.
- **Key Features**: KG-aware responses, fact references, context-sensitive answers

## Analysis Methodology

Each example includes:
1. The raw chat recording
2. Knowledge graph snapshots at different points in the conversation
3. An analysis document explaining what's happening "under the hood"

## Running the Examples

To run these examples yourself:

```bash
cd /path/to/ConvoTree
python terminal_chat_kg.py --file examples/sample_inputs/[example_input].txt
```

You can then interact with the system and observe how it builds and maintains the knowledge graph.