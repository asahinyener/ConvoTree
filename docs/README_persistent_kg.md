# Persistent Knowledge Graph Chat System

A conversation system that maintains context across ephemeral LLM interactions using a persistent knowledge graph approach.

## Overview

This system solves the context rot problem in long conversations by:

1. **Extracting knowledge** from each conversation turn into structured triples
2. **Storing persistently** in a SQLite database 
3. **Retrieving relevant context** for each new message
4. **Synthesizing context** into prompts for the LLM
5. **Maintaining conversation continuity** without token limits

## Architecture

```
User Message → KG Update → Context Retrieval → LLM + Context → Response → KG Update
     ↓              ↓             ↓                ↓              ↓           ↓
   SQLite      Extract Facts   Query Relevant   Generate      Store New   Update State
  Database    (entities,rels)   Knowledge      Response      Knowledge   (preferences)
```

## Key Components

### 1. PersistentKG (`persistent_kg.py`)
- Knowledge extraction from conversations
- SQLite storage for triples and context
- Relevance-based context retrieval
- Conversation state management

### 2. EnhancedChatSystem (`enhanced_chat.py`) 
- Chat pipeline with KG integration
- Context synthesis for LLM prompts
- Response generation with full memory
- Conversation management utilities

### 3. Flask API Integration (`app.py`)
- REST endpoints for chat interactions
- Conversation history and export
- Integration with existing compression system

## Usage

### Simple API Usage

```python
from enhanced_chat import continue_conversation

# Each call maintains full conversation context
response1 = continue_conversation("user_123", "I'm working on a ML project")
response2 = continue_conversation("user_123", "What was my project about?") 
# Response2 will remember the ML project context
```

### Full System Usage

```python
from enhanced_chat import EnhancedChatSystem

chat = EnhancedChatSystem("conversation_id")
result = chat.process_message("Hi, I'm Alex and I love jazz music")

print(result["response"])  # AI response with context
print(result["context_used"])  # Debug info about context usage
```

### REST API Usage

```bash
# Start a conversation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "user_123", "message": "I love jazz music"}'

# Continue conversation (AI remembers jazz preference)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "user_123", "message": "Recommend some artists"}'

# Get conversation history
curl http://localhost:8000/conversation/user_123/history

# Export conversation data
curl http://localhost:8000/conversation/user_123/export
```

## Database Schema

### Tables
- **conversations**: Conversation metadata
- **turns**: Individual chat turns with extracted entities
- **knowledge_triples**: Subject-Relation-Object facts
- **context_state**: Persistent user/conversation state

### Knowledge Representation
- **Entities**: Named entities, concepts, preferences
- **Relations**: Relationships between entities (`John|likes|jazz`)
- **Context State**: Key-value pairs for conversation state
- **Turn History**: Chronological conversation record

## Features

### Context Preservation
- Extracts facts from each conversation turn
- Maintains user preferences and state
- Retrieves relevant context for each new message
- No token limit constraints

### Conversation Continuity  
- AI responds as if it has complete conversation memory
- References previous topics naturally
- Maintains consistent personality across sessions
- Handles conversation gaps gracefully

### Scalability
- SQLite storage for persistence
- Efficient relevance-based retrieval
- Context synthesis to manage prompt size
- Multiple concurrent conversations

## Running the System

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# Requires: flask, openai, networkx, matplotlib
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run Tests
```bash
python test_system.py  # Basic functionality tests
```

### 4. Start the Server
```bash
python app.py
# Server runs on http://localhost:8000
```

### 5. Demo the System
```bash
python demo_persistent_chat.py  # Interactive demonstration
```

## API Endpoints

### Chat Endpoints
- `POST /chat` - Send message to conversation
- `GET /conversation/{id}/history` - Get conversation history  
- `GET /conversation/{id}/export` - Export conversation data
- `GET /conversation/{id}/summary` - Get conversation statistics
- `GET /conversations` - List active conversations

### Legacy Endpoints (ConvoCompressor)
- `POST /compress` - Compress conversation to KG
- `POST /resume` - Resume from compressed bundle

## Benefits vs Traditional Approaches

### vs Long Context Windows
- No token limits or costs scaling with conversation length
- Maintains relevant facts across very long conversations
- Faster processing (small prompts vs massive context)

### vs RAG Systems
- Purpose-built for conversation context
- Maintains conversation state and user preferences
- Structured knowledge representation
- Temporal awareness of conversation flow

### vs Session Storage
- Persistent across application restarts
- Structured knowledge vs raw text storage
- Intelligent context retrieval vs dump everything
- Scalable to many concurrent users

## File Structure

```
ConvoTree/
├── persistent_kg.py           # Core KG system
├── enhanced_chat.py           # Chat system integration  
├── app.py                     # Flask API (enhanced)
├── demo_persistent_chat.py    # Demo script
├── test_system.py            # Basic tests
├── README_persistent_kg.md    # This documentation
├── conversations.db          # SQLite database (created on run)
├── requirements.txt          # Dependencies
└── prompts/                  # System prompts
    ├── compressor_prompt.txt
    └── resume_prompt.txt
```

## Configuration

The system uses these models by default:
- **Knowledge Extraction**: GPT-4o-mini (fast, cost-effective)
- **Context Synthesis**: GPT-4o-mini (structured output)  
- **Chat Generation**: GPT-4o (high-quality responses)

Models can be configured in the respective classes.

## Future Enhancements

- **Multi-modal knowledge**: Support images, documents in KG
- **Knowledge validation**: Fact-checking and consistency
- **Advanced retrieval**: Vector embeddings for semantic search
- **Conversation clustering**: Group related conversation threads
- **Privacy controls**: User data management and deletion
- **Analytics dashboard**: Conversation insights and statistics