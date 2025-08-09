## Description
This PR adds a conversation-aware sequential compression feature to ConvoTree, where the repulled knowledge graph (KG) information is refed at every step if the user selects the sequential compression option.

## Changes
- Updated app.py to use GPT-5 model instead of gpt-4o-mini
- Added python-dotenv to load the API key from .env file
- Enhanced the web interface with better styling and status messages
- Updated the resume_route to handle sequential compression parameter
- Enhanced build_resume_prompt to include more KG facts (15 instead of 7)
- Updated resume_prompt.txt to better handle conversation-aware KG
- Updated compressor_prompt.txt to support sequential compression
- Created a test script (test_sequential_compression.py) to demonstrate the feature
- Added a CLI test script (cli_test.py) for testing without API calls
- Added a terminal-based chat interface (terminal_chat.py) for interactive testing
- Added chat session recording functionality to save conversations and KG snapshots
- Implemented actual OpenAI API integration for terminal chat responses and fact extraction
- Enhanced KG to extract facts from both user queries and assistant responses
- Added specialized fact extraction for user queries to capture implied knowledge
- Added terminal_chat_kg.py that uses the same KG structure as app.py for consistency
- Added support for general content beyond the jazz demo in terminal_chat_kg.py
- Added KG visualization with NetworkX and Matplotlib in terminal_chat_kg.py
- Added CORS headers to allow iframe embedding
- Updated .gitignore to exclude the .env file
- Added .env.example file to help users set up their API keys

## How to Test
1. Install dependencies: `pip install -r requirements.txt`
2. Set your OpenAI API key in a .env file: `echo "OPENAI_API_KEY=your_api_key_here" > .env`
3. Run the server: `python app.py`
4. Open the web interface: `http://localhost:12000`
5. Test the sequential compression feature by checking the "Enable Sequential Compression" checkbox
6. For CLI testing without API calls: `python cli_test.py`
7. For interactive terminal testing with jazz demo: `python terminal_chat.py`
8. For interactive terminal testing with app.py KG integration: `python terminal_chat_kg.py`

## Terminal Chat Commands
- `kg` - View the current knowledge graph
- `toggle` - Toggle sequential compression on/off
- `record` - Start recording the chat session
- `stop` - Stop recording and save the transcript
- `save` - Save the knowledge graph as an image (only in terminal_chat_kg.py)
- `exit` - Exit the chat

## Screenshots
N/A

## Additional Notes
- The application now uses the GPT-5 model for both compression and conversation resumption
- Sequential compression ensures the KG stays up-to-date with the latest conversation context
- The terminal chat interface uses the OpenAI API for both responses and fact extraction
- Specialized fact extraction for user queries captures implied knowledge and context
- Facts are extracted from both user queries and assistant responses
- Fallback mechanisms are in place for when the API is unavailable
- The knowledge graph is continuously updated with each exchange, making the conversation more coherent
- terminal_chat_kg.py uses the same KG structure as app.py (triples with subject|predicate|object format)
- terminal_chat_kg.py can handle any user-pasted content, not just jazz-related topics
- KG visualization is available in terminal_chat_kg.py using NetworkX and Matplotlib