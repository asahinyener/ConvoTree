# ConvoTree Terminal CLI 🌳

Interactive terminal chat interface with persistent knowledge graph and semantic testing capabilities.

## Quick Start

### Option 1: Using uv (Recommended)

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

4. **Start chatting:**
   ```bash
   ./run.sh
   # or:
   uv run python start_chat.py
   # or:
   uv run convotree-start
   ```

### Option 2: Using pip

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. **Start chatting:**
   ```bash
   python start_chat.py
   # or directly:
   python chat_cli.py
   ```

## Features

### 🗣️ Persistent Chat
- Continuous conversation with GPT-4o
- Persistent knowledge graph memory
- Context-aware responses
- Multiple conversation management

### 🔍 Analysis Commands
- `/knowledge` - View extracted knowledge facts
- `/context` - Show current context state
- `/history` - Display conversation history
- `/stats` - Detailed statistics
- `/analyze` - Pattern analysis

### 🧪 Semantic Testing
- `/test memory` - Memory retention tests
- `/test consistency` - Response consistency
- `/test knowledge` - Knowledge integration
- `/test context` - Context awareness
- `/test all` - Comprehensive test suite

### 📊 Visualization
- `/visualize` - Generate knowledge graph PNG
- `/search <query>` - Search knowledge base
- `/benchmark` - Performance testing

### 💾 Database Operations
- `/db <query>` - Execute SQL queries (read-only)
- `/export` - Export conversation data
- `/conversations` - List all conversations
- `/switch <id>` - Change active conversation

## Command Reference

### Basic Commands
| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show all commands | `/help` |
| `/status` | Conversation status | `/status` |
| `/clear` | Clear terminal | `/clear` |
| `/exit` | Quit chat | `/exit` |

### Conversation Management
| Command | Description | Example |
|---------|-------------|---------|
| `/conversations` | List all conversations | `/conversations` |
| `/switch <id>` | Switch conversation | `/switch project_chat` |
| `/new [id]` | Create conversation | `/new research_session` |
| `/delete <id>` | Delete conversation | `/delete old_chat` |

### Knowledge & Analysis
| Command | Description | Example |
|---------|-------------|---------|
| `/knowledge [N]` | Show N recent facts | `/knowledge 20` |
| `/history [N]` | Show N recent turns | `/history 10` |
| `/search <query>` | Search knowledge | `/search user preferences` |
| `/context` | Show context state | `/context` |
| `/analyze` | Analyze patterns | `/analyze` |

### Testing & Debugging
| Command | Description | Example |
|---------|-------------|---------|
| `/test <type>` | Run semantic test | `/test memory` |
| `/benchmark` | Performance test | `/benchmark` |
| `/debug` | Show debug info | `/debug` |
| `/db <sql>` | Execute SQL query | `/db SELECT COUNT(*) FROM turns` |

### Visualization
| Command | Description | Example |
|---------|-------------|---------|
| `/visualize` | Create graph PNG | `/viz` |
| `/export [format]` | Export data | `/export json` |
| `/stats` | Detailed statistics | `/stats` |

## Semantic Testing

The CLI includes built-in semantic testing to validate the knowledge graph system:

### Memory Tests
```bash
/test memory    # Test fact retention
/test consistency    # Response consistency  
/test knowledge     # Knowledge integration
/test context      # Context awareness
/test all         # Full test suite
```

### Performance Benchmarks
```bash
/benchmark    # Response time & retrieval speed
```

## Advanced Usage

### Custom Conversation ID
```bash
# With uv
uv run python chat_cli.py --conversation-id "my_project"

# With pip
python chat_cli.py --conversation-id "my_project"
```

### Custom Database
```bash
# With uv
uv run python chat_cli.py --database "custom.db"

# With pip
python chat_cli.py --database "custom.db"
```

### Development Mode
```bash
# Install with dev dependencies
uv sync --all-extras

# Run tests (if available)
uv run pytest

# Format code
uv run black .

# Lint code
uv run flake8 .
```

### Database Queries
```bash
# View all conversations
/db SELECT id, created_at FROM conversations

# Check knowledge growth
/db SELECT COUNT(*) FROM knowledge_triples WHERE conversation_id = 'current_id'

# Recent activity
/db SELECT DATE(timestamp), COUNT(*) FROM turns GROUP BY DATE(timestamp)
```

## Examples

### Basic Chat Flow
```
ConvoTree> Hello, I'm working on a Python web scraping project
Assistant> I'd be happy to help with your Python web scraping project! What specific aspects are you working on?

ConvoTree> /knowledge
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Knowledge Graph Facts (Last 3)           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ user → works_on → Python web scraping    │
│ user → has_project → web scraping        │
│ project → involves → Python programming  │
└───────────────────────────────────────────┘

ConvoTree> /test memory
✅ Memory Retention Test Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Test Fact             ┃ Retained ┃ Response Length ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Project type          │    ✓     │      156       │
│ Programming language  │    ✓     │      203       │
│ User expertise        │    ✓     │      178       │
└───────────────────────┴──────────┴─────────────────┘
```

### Knowledge Analysis
```bash
# Search for specific topics
ConvoTree> /search Python
ConvoTree> /search preferences

# Analyze conversation patterns  
ConvoTree> /analyze

# Visualize knowledge relationships
ConvoTree> /visualize
# Creates: knowledge_graph_session_20250813_143022.png
```

### Multi-Conversation Workflow
```bash
# List conversations
ConvoTree> /conversations

# Create focused conversation
ConvoTree> /new debugging_session

# Switch between contexts
ConvoTree> /switch project_planning
```

## Tips

1. **Use descriptive conversation IDs** for better organization
2. **Regular `/visualize`** to see knowledge growth
3. **Run `/test all`** periodically to validate system
4. **Use `/search`** to find specific information
5. **Export data** with `/export` for backup

## Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### OpenAI API Issues
- Check `.env` file exists with valid `OPENAI_API_KEY`
- Verify API key has sufficient credits
- Try `/debug` for diagnostic info

### Database Issues
- Database file permissions
- Disk space availability
- Use `/db` commands to inspect data

### Performance Issues
- Run `/benchmark` to identify bottlenecks
- Check `/stats` for usage patterns
- Consider conversation cleanup with `/delete`