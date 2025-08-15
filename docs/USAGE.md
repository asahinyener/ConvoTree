# ConvoTree Usage Guide

## ✅ Ready to Run!

Your ConvoTree is now properly set up with `uv` and ready to use.

## 🚀 How to Start

### Method 1: Using the run script (Recommended)
```bash
./run.sh
```

### Method 2: Direct uv commands
```bash
uv run python start_chat.py
uv run convotree-start
```

### Method 3: From anywhere (if you add to PATH)
```bash
./convotree    # From ConvoTree directory
```

## 🎯 Common Usage Patterns

### Start a new conversation
```bash
./run.sh --conversation-id "my_project"
```

### Use a different database
```bash
./run.sh --database "project.db"
```

### Get help
```bash
./run.sh --help
```

## 🔧 Inside the CLI

Once running, you'll see a prompt like:
```
conversation_id> 
```

### Essential Commands:
- `/help` - Show all available commands
- `/status` - Show conversation status
- `/knowledge` - View knowledge graph
- `/test all` - Run semantic tests
- `/visualize` - Create knowledge graph image
- `/exit` - Quit

### Example Session:
```
my_project> Hello, I'm working on a Python web app
Assistant> I'd be happy to help with your Python web application! What specific aspects are you working on?

my_project> /knowledge
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Knowledge Graph Facts (Last 3)           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ user → works_on → Python web app        │
│ user → has_project → web application    │
│ project → type → Python web app         │
└───────────────────────────────────────────┘

my_project> /test memory
[Running memory retention tests...]

my_project> /visualize  
[Creates knowledge_graph_my_project_20250813_210000.png]

my_project> /exit
```

## 🛠️ Troubleshooting

### Environment Issues

**Run the diagnostics script first:**
```bash
uv run python debug_env.py
```
This will check your environment setup and identify issues.

### If the script says .env not found:
1. Make sure you're in the ConvoTree directory
2. Check the .env file exists: `ls -la .env`
3. If not, copy from example: `cp .env.example .env`

### If dependencies are missing:
```bash
uv sync --upgrade
```

### If uv is not found:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### If OpenAI API issues:
- Run `uv run python debug_env.py` to diagnose
- Check your `.env` file has a valid `OPENAI_API_KEY`
- Verify your API key has credits
- Ensure the API key is properly formatted (no extra quotes/spaces)
- Use `/debug` inside the CLI for diagnostic info

### If "OpenAI API key is required" error:
This usually means the `.env` file isn't being loaded. The fix:
1. **Use the provided start script**: `./run.sh` or `uv run python start_chat.py`
2. **Don't run `chat_cli.py` directly** - it may not load `.env`
3. **Run diagnostics**: `uv run python debug_env.py`

## 🎉 You're Ready!

Run `./run.sh` to start your interactive conversation with persistent knowledge graph capabilities!