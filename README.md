# ConvoTree 🌳

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **Enhanced Persistent AI Chat with Neural Memory Consolidation**

ConvoTree is an advanced conversational AI system that combines persistent memory, knowledge graph reasoning, and neural memory consolidation to create truly intelligent, context-aware conversations that remember and learn over time.

## 🚀 Key Features

### 🧠 Neural Memory Consolidation
- **LLM-Powered Reasoning**: Uses OpenAI GPT models for intelligent relationship discovery
- **Multi-Hop Inference**: Connects disparate facts to infer new knowledge (e.g., user + Alice properties → identity inference)
- **Gaussian Splatting Inspired**: Intelligently merges knowledge when confident, maintains granularity when uncertain
- **Dreaming States**: Offline memory consolidation that discovers implicit relationships

### 📊 Knowledge Graph Engine
- **Persistent Knowledge Storage**: SQLite-based knowledge graph with entity-relationship extraction
- **Multi-Dimensional Similarity**: Semantic, contextual, phonetic, structural, and conceptual analysis
- **Confidence Propagation**: Weighted relationship discovery with confidence scoring
- **Universal Semantic Clustering**: Conversation-agnostic knowledge consolidation

### 💬 Enhanced Chat Interface
- **Persistent Conversations**: Resume conversations across sessions with full context
- **Real-time Knowledge Extraction**: Automatic entity and relationship detection
- **Rich CLI Interface**: Beautiful terminal UI with progress indicators and panels
- **Debug Mode**: Comprehensive debugging and introspection capabilities

## 🏗️ Architecture

```
ConvoTree/
├── convotree/
│   ├── cli/                    # Command-line interface
│   │   ├── cli_v2.py          # Enhanced CLI with dreaming commands
│   │   └── chat_cli.py        # Core chat interface
│   ├── core/
│   │   ├── chat/              # Chat system components
│   │   │   ├── enhanced_chat_v2.py    # Main chat engine
│   │   │   └── enhanced_chat.py       # Legacy chat system
│   │   ├── config/            # Configuration management
│   │   ├── memory/            # Knowledge and memory systems
│   │   │   ├── graph_reasoning_engine.py  # 🧠 Neural consolidation engine
│   │   │   ├── cached_knowledge_graph.py  # Cached knowledge operations
│   │   │   └── persistent_kg.py           # Persistent knowledge graph
│   │   └── optimization/      # DSPy integration and optimization
│   ├── demos/                 # Example implementations
│   ├── tests/                 # Test suites
│   └── utils/                 # Utilities and error handling
└── docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- SQLite (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ConvoTree
   ```

2. **Set up environment**
   ```bash
   # Create .env file with your OpenAI API key
   echo 'OPENAI_API_KEY="your-api-key-here"' > .env
   ```

3. **Install dependencies**
   ```bash
   pip install openai rich sqlite3
   ```

### Basic Usage

```bash
# Start a new conversation
python -m convotree.cli.cli_v2

# Resume a specific conversation
python -m convotree.cli.cli_v2 -c my_conversation_id

# Enable debug mode
python -m convotree.cli.cli_v2 --debug
```

## 🎯 Core Commands

### Chat Commands
- **Regular chat**: Just type naturally - ConvoTree remembers everything
- **`/help`**: Show all available commands
- **`/knowledge`**: View your current knowledge graph
- **`/debug-mode`**: Toggle debug mode for detailed insights

### Memory & Reasoning Commands
- **`/dream`**: Trigger neural memory consolidation across all knowledge
- **`/reason`**: Perform knowledge graph reasoning and inference
- **`/compress`**: Compress and optimize knowledge representation
- **`/resume`**: Resume previous conversation context

### System Commands
- **`/test memory`**: Validate knowledge retention and reasoning
- **`/tutorial`**: Interactive system tutorial
- **`exit`**: End conversation session

## 🧠 Neural Memory Consolidation

The heart of ConvoTree is its neural memory consolidation system, inspired by how human memory works during sleep:

### How It Works

1. **Knowledge Extraction**: Automatic entity and relationship detection from conversations
2. **Similarity Analysis**: Multi-dimensional comparison of knowledge nodes
3. **LLM Reasoning**: GPT-4 powered inference discovery and relationship validation
4. **Consolidation**: Intelligent merging of related concepts with confidence scoring

### Example Workflow

```python
# Initial facts from conversation:
# "I have a cat named Whiskers"
# "I work at TechCorp" 
# "Alice owns a cat called Whiskers"
# "Alice works at TechCorp"

# After /dream command:
# System discovers: user is_same_person_as Alice (confidence: 0.90)
# Reasoning: "Both user and Alice work at TechCorp and have pet Whiskers"

# Result: When asked "What is my name?" → "Your name is Alice!"
```

## 🔧 Development

### Running Tests

```bash
# Test neural memory consolidation
python test_dreaming.py

# Create test conversations
python create_test_conversation.py

# Run comprehensive tests
python -m convotree.tests.test_system
```

### Key Development Areas

#### Memory Engine (`convotree/core/memory/graph_reasoning_engine.py`)
- **`perform_memory_dreaming()`**: Main consolidation pipeline
- **`_reason_with_llm()`**: LLM-powered relationship discovery
- **`_find_universal_similarities()`**: Multi-dimensional similarity analysis
- **`_apply_llm_inferences()`**: Knowledge graph updates with new discoveries

#### Chat System (`convotree/core/chat/enhanced_chat_v2.py`)
- **`ConversationManagerV2`**: Persistent conversation management
- **Knowledge extraction pipeline**: Real-time entity/relationship detection
- **Context management**: Intelligent context window optimization

#### CLI Interface (`convotree/cli/cli_v2.py`)
- **Command processing**: `/dream`, `/reason`, `/compress` implementations
- **Rich UI components**: Progress bars, panels, and debugging displays
- **Error handling**: Comprehensive error management and recovery

### Configuration

ConvoTree uses a flexible configuration system:

```python
# convotree/core/config/config_manager.py
class ConvoTreeConfig:
    database: DatabaseConfig
    model: ModelConfig  
    ui: UIConfig
    memory: MemoryConfig
```

## 🎨 Example Use Cases

### 1. Personal Assistant
- Remembers your preferences, relationships, and context across sessions
- Infers connections between people, places, and events
- Provides contextually aware responses based on accumulated knowledge

### 2. Research Companion
- Tracks research topics, papers, and connections over time
- Discovers implicit relationships between concepts
- Maintains persistent research context across multiple sessions

### 3. Learning System
- Builds knowledge graphs of learning topics
- Connects new information to existing knowledge
- Identifies knowledge gaps and learning opportunities

## 🔬 Advanced Features

### DSPy Integration
- Optimized prompts for knowledge extraction and reasoning
- Automated prompt engineering and optimization
- Performance monitoring and improvement

### Caching System
- Intelligent knowledge graph caching for performance
- Context-aware cache warming and optimization
- Memory-efficient knowledge representation

### Error Handling
- Comprehensive error recovery and logging
- Graceful degradation for API failures
- Debug mode for system introspection

## 📊 Performance

- **Knowledge Extraction**: ~100ms per message
- **Memory Consolidation**: ~2-5s for full conversation dreaming
- **Cache Hit Rate**: 85%+ for repeated knowledge queries
- **Storage**: ~1KB per conversation turn in SQLite

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit with descriptive messages: `git commit -m "Add amazing feature"`
5. Push to your branch: `git push origin feature/amazing-feature`
6. Submit a pull request

### Development Guidelines

- Follow existing code style and patterns
- Add tests for new features
- Update documentation for API changes
- Use meaningful commit messages
- Test with real OpenAI API (not mocks) for memory features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API enabling intelligent reasoning
- **Rich** library for beautiful terminal interfaces
- **SQLite** for reliable persistent storage
- Inspired by research in **gaussian splatting** and **neural memory consolidation**

---

<div align="center">
  <strong>🌳 ConvoTree - Where conversations grow into knowledge 🌳</strong>
</div>