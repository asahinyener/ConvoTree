#!/bin/bash
# ConvoTree Runner Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🌳 ConvoTree CLI Launcher"
echo "Working directory: $(pwd)"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found in $(pwd)"
    echo ""
    if [ -f ".env.example" ]; then
        echo "📋 Found .env.example file. You can copy it:"
        echo "   cp .env.example .env"
        echo "   # Then edit .env and add your OpenAI API key"
    else
        echo "Please create a .env file with your OpenAI API key:"
        echo "   echo 'OPENAI_API_KEY=your_api_key_here' > .env"
    fi
    echo ""
    exit 1
fi

# Check if .env has content
if [ ! -s ".env" ]; then
    echo "⚠️  .env file is empty!"
    echo "Please add your OpenAI API key to .env"
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed or not in PATH"
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Then run: source \$HOME/.local/bin/env"
    exit 1
fi

echo "✅ Environment check passed"
echo "🚀 Starting ConvoTree CLI with uv..."
echo ""

# Run with uv
uv run python start_chat.py "$@"