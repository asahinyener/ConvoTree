# ConvoTree

A conversation compression and knowledge graph tool that extracts structured knowledge from conversations using GPT-5.

## Features

- Compress conversations into knowledge graphs (KG) using GPT-5
- Extract structured facts from conversations
- Visualize knowledge graphs
- Resume conversations with context from the KG
- Sequential compression for continuous KG updates
- Interactive web interface for testing

## Sequential Compression

The sequential compression feature allows the knowledge graph to be continuously updated with each new exchange in the conversation. This ensures that the KG remains up-to-date and relevant to the ongoing conversation.

### How it works

1. When a user enables sequential compression, each new exchange (user message + assistant reply) is used to update the KG
2. The system recompresses the entire conversation history, including the new exchange
3. The updated KG is used for generating the next response
4. This creates a feedback loop where the KG grows and evolves with the conversation

### Usage

To use sequential compression, set the `sequential_compression` parameter to `true` when calling the `/resume` endpoint:

```json
{
  "bundle_path": "runs/20250809_123456/bundle.json",
  "next_user": "Tell me more about this topic",
  "sequential_compression": true
}
```

## API Endpoints

- `/compress` - Compress a JSON list of messages
- `/compress_txt` - Compress a plain text transcript
- `/resume` - Resume a conversation with context from the KG

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key in a .env file:
   ```
   echo 'OPENAI_API_KEY="your_api_key_here"' > .env
   ```

3. Run the server:
   ```
   python app.py
   ```

4. Open the web interface:
   ```
   http://localhost:12000
   ```

5. Test the sequential compression feature:
   ```
   python test_sequential_compression.py
   ```

Note: The application uses the GPT-5 model for both compression and conversation resumption.

## Example

Initial KG after compression:
```
User|likes|Jazz
User|name|Julia
Miles Davis|recorded|Kind of Blue
Bill Evans|pianist on|Kind of Blue
```

After sequential compression with new exchanges:
```
User|likes|Jazz
User|name|Julia
Miles Davis|recorded|Kind of Blue
Bill Evans|pianist on|Kind of Blue
Miles Davis|recorded|Bitches Brew
Miles Davis|recorded|Birth of the Cool
John Coltrane|collaborated with|Miles Davis
```