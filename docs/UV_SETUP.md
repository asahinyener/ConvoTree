# ConvoTree with uv Setup Guide

## ✅ Setup Complete!

Your ConvoTree project is now configured to work with `uv`, Python's fast package manager.

## Quick Commands

### 🚀 Start ConvoTree
```bash
# Easy way (recommended)
./run.sh

# Direct uv commands
uv run python start_chat.py
uv run convotree-start
```

### 🔧 Development Commands
```bash
# Sync dependencies
uv sync

# Install with dev dependencies  
uv sync --all-extras

# Add new dependencies
uv add package-name

# Remove dependencies
uv remove package-name

# Update dependencies
uv sync --upgrade
```

### 🧪 Code Quality
```bash
# Format code
uv run black .

# Lint code  
uv run flake8 .

# Run tests (when available)
uv run pytest
```

## Environment Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your OpenAI API key:**
   ```bash
   # Edit the file and add your key
   vim .env  # or nano .env
   ```

## Available Run Options

| Command | Description |
|---------|-------------|
| `./run.sh` | Convenient script with error checking |
| `uv run python start_chat.py` | Direct start with dependency checks |
| `uv run python chat_cli.py` | Direct CLI access |
| `uv run convotree-start` | Using project script (from pyproject.toml) |

## Project Structure

```
ConvoTree/
├── pyproject.toml          # uv/Python project config
├── requirements.txt        # Fallback for pip users
├── .env.example           # Environment template
├── run.sh                 # Easy run script
├── start_chat.py         # Entry point with checks
├── chat_cli.py          # Main CLI application
└── .venv/              # Virtual environment (created by uv)
```

## Benefits of uv

- ⚡ **Faster**: 10-100x faster than pip
- 🔒 **Better dependency resolution**: More reliable lock files
- 🐍 **Python version management**: Automatic Python installation
- 📦 **Modern tooling**: Built-in project management
- 🎯 **Single tool**: Replaces pip, venv, and more

## Next Steps

1. Set up your `.env` file with OpenAI API key
2. Run `./run.sh` to start chatting
3. Use `/help` inside the CLI to see all available commands
4. Try `/test all` to run the semantic test suite

## Troubleshooting

### If `uv` command not found:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### If dependencies fail:
```bash
# Clean and reinstall
rm -rf .venv
uv sync
```

### If .env issues:
```bash
# Check the file exists and has your API key
cat .env
```

Happy chatting! 🌳