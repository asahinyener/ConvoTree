# ConvoTree Debug Guide 🔍

## Context Ephemerality Testing & LLM Input Debugging

This guide shows how to verify that ConvoTree is properly using knowledge graph extraction instead of passing raw chat history directly to the LLM.

## 🎯 Quick Test: Context Ephemerality

### Run the Automated Test
```bash
uv run python test_context_ephemerality.py
```

This will demonstrate:
- ✅ Raw chat history is NOT sent to the LLM
- ✅ Context is processed through knowledge graph
- ✅ Only relevant facts and recent turns are included
- ✅ Memory usage stays constant regardless of conversation length

## 🔧 Interactive Debug Mode

### Enable Debug Mode
```bash
# Start CLI with debug mode
./run.sh --debug

# Or enable in existing session
your_session> /debug-mode
```

### Debug Commands

| Command | Purpose | Usage |
|---------|---------|--------|
| `/debug-mode` | Toggle debug mode on/off | `/debug-mode` |
| `/debug-llm` | Show last LLM input/output | `/debug-llm` |
| `/debug` | Show system debug info | `/debug` |

### What Debug Mode Shows

When debug mode is active, you'll see detailed information for each message:

```
🔍 [DEBUG] Processing message: 'Hello, how are you today?'
📝 [DEBUG] Added user turn ID: 123
🧠 [DEBUG] Context retrieved - Facts: 5, Recent turns: 3
🔗 [DEBUG] Has synthesized context: True

🎯 [DEBUG] === LLM INPUT DETAILS ===
📊 Context Summary: Ongoing conversation
💡 Relevant Facts (5 facts):
   1. user → prefers → Python programming
   2. user → works_as → data scientist
   3. user → location → San Francisco
   ...

📝 Recent Context (3 turns):
   user: I work as a data scientist in San Francisco
   assistant: That's great! What kind of data science projects do you work on?
   user: Mostly machine learning and NLP projects

👤 User Context: {"preferences": {"language": "Python"}, "location": "San Francisco"}

📤 [DEBUG] === FULL SYSTEM PROMPT SENT TO LLM ===
================================================================================
You are an AI assistant continuing a conversation. You have access to persistent context from previous interactions.

CONVERSATION CONTEXT:
Ongoing conversation

RELEVANT FACTS:
• user → prefers → Python programming
• user → works_as → data scientist
• user → location → San Francisco
...

RECENT CONVERSATION:
user: I work as a data scientist in San Francisco...
assistant: That's great! What kind of data science projects...

USER STATE/PREFERENCES:
{
  "preferences": {
    "language": "Python"
  },
  "location": "San Francisco"
}

IMPORTANT:
- Respond naturally as if you remember the entire conversation history
...
================================================================================
📤 [DEBUG] User message: Hello, how are you today?
================================================================================

📥 [DEBUG] === LLM RESPONSE ===
Response length: 156 characters
Model used: gpt-4o-mini
Usage: CompletionUsage(completion_tokens=31, prompt_tokens=234, total_tokens=265)
==================================================
```

## 🧪 Manual Testing Steps

### 1. Start a Debug Session
```bash
./run.sh --debug --conversation-id "context_test"
```

### 2. Build Context Over Multiple Messages
```
context_test> My name is Alice and I'm a Python developer
context_test> I work at TechCorp as a senior engineer  
context_test> I have 5 years of experience with machine learning
context_test> I'm currently working on a recommendation system
```

### 3. Test Context Retrieval
```
context_test> What do you know about my background?
```

### 4. Examine LLM Input
```
context_test> /debug-llm
```

## 🔍 What You Should See

### ✅ Correct Behavior (ConvoTree)
- **Context Summary**: Brief overview of conversation
- **Relevant Facts**: Extracted semantic triples (user → works_at → TechCorp)
- **Recent Context**: Only last few turns, truncated
- **System Prompt**: ~500-2000 characters regardless of conversation length

### ❌ What Traditional Chat Would Send
- **Raw History**: Every single message from the beginning
- **Growing Size**: Exponentially increasing prompt size
- **No Processing**: Direct message history without knowledge extraction

## 📊 Key Metrics to Verify

### Context Processing Verification
```
context_test> /stats
```

Look for:
- **Knowledge Triples**: Growing number as conversation progresses
- **Turn Count**: Total turns vs what's sent to LLM
- **Context Efficiency**: Relevant facts << Total conversation content

### Memory Usage Verification  
```
context_test> /debug
```

Check:
- **Database Size**: Growing with knowledge
- **Memory Usage**: Should stay relatively constant
- **Active Conversations**: Multiple conversations possible

## 🎮 Interactive Demo Scenarios

### Scenario 1: Long Conversation Test
1. Have a 50+ turn conversation
2. Enable debug mode: `/debug-mode`
3. Ask: "What do you remember about our conversation?"
4. Check `/debug-llm` - should show extracted facts, not all 50 turns

### Scenario 2: Context Switch Test  
1. Talk about work projects
2. Switch to talking about hobbies
3. Ask about work again
4. Verify relevant work facts are retrieved (not hobby context)

### Scenario 3: Knowledge Persistence Test
1. Start session, mention preferences
2. `/exit`
3. Restart with same conversation ID
4. Verify knowledge is retained and used

## 📈 Performance Comparison

### Traditional Chat (Growing Context)
```
Turn 1:   ~100 tokens
Turn 10:  ~1,000 tokens  
Turn 100: ~10,000 tokens
Turn 1000: ~100,000+ tokens (hits limits!)
```

### ConvoTree (Ephemeral Context)
```
Turn 1:   ~300 tokens (system prompt + context)
Turn 10:  ~500 tokens (more facts, same structure)
Turn 100: ~600 tokens (relevant facts only)
Turn 1000: ~600 tokens (still only relevant facts!)
```

## 🚀 Testing Commands Summary

```bash
# Quick ephemerality test
uv run python test_context_ephemerality.py

# Interactive debugging
./run.sh --debug

# In CLI commands
/debug-mode          # Toggle debug mode
/debug-llm           # Show last LLM input  
/knowledge           # Show extracted facts
/context             # Show context state
/stats               # Show conversation metrics
/debug               # Show system info
```

## 🎯 Expected Results

After testing, you should be able to confirm:

1. **✅ Context Ephemerality**: Old messages don't appear in LLM prompts
2. **✅ Knowledge Extraction**: Information is stored as semantic facts
3. **✅ Relevance Filtering**: Only pertinent facts are included
4. **✅ Constant Memory**: Prompt size doesn't grow with conversation length
5. **✅ Persistence**: Knowledge survives session restarts
6. **✅ Efficiency**: Better performance than traditional chat systems

## 🔬 Deep Dive: LLM Input Analysis

The debug output reveals the actual message structure sent to OpenAI:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "[Processed context with facts, not raw history]"
    },
    {
      "role": "user", 
      "content": "[Current user message only]"
    }
  ]
}
```

**Key Point**: The messages array contains only 2 items - the system prompt (with processed context) and the current user message. No raw message history is included!

---

This demonstrates ConvoTree's core innovation: **Ephemeral Context with Persistent Knowledge** 🌳