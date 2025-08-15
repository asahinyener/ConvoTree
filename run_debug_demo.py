#!/usr/bin/env python3
"""
Quick demo of ConvoTree debug features
Shows CLI debug commands and capabilities
"""

from dotenv import load_dotenv
load_dotenv()

from enhanced_chat import EnhancedChatSystem, ConversationManager
from chat_cli import ConvoTreeCLI
import os

def demo_debug_features():
    """Demonstrate the debug features available in ConvoTree"""
    
    print("🔍 ConvoTree Debug Features Demo")
    print("=" * 50)
    
    print("\n🎯 Available Debug Commands:")
    print("- --debug flag: Start CLI with debug mode enabled")
    print("- /debug-mode: Toggle debug mode on/off in CLI")
    print("- /debug-llm: Show last LLM input/output details")
    print("- /debug: Show system debug information")
    
    print("\n📋 What Debug Mode Shows:")
    print("✅ Exact system prompt sent to OpenAI")
    print("✅ Context breakdown (facts, recent turns, user state)")
    print("✅ Knowledge extraction process")
    print("✅ LLM response details (model, tokens, timing)")
    print("✅ Proof that raw history isn't sent")
    
    print("\n🚀 How to Use:")
    print("1. Start CLI with debug:")
    print("   ./run.sh --debug")
    print("   # or")
    print("   uv run python chat_cli.py --debug")
    
    print("\n2. Enable debug in existing session:")
    print("   your_session> /debug-mode")
    
    print("\n3. Send messages and observe debug output")
    
    print("\n4. Check last LLM interaction:")
    print("   your_session> /debug-llm")
    
    print("\n📊 Key Verification Points:")
    print("- Recent Context: Shows limited recent turns (not full history)")
    print("- Relevant Facts: Shows extracted semantic facts")
    print("- System Prompt: Shows processed context, not raw messages")
    print("- Token Usage: Shows actual API usage")
    
    print("\n🧪 Test Commands to Try:")
    test_commands = [
        "Hello, I'm a Python developer",
        "I work at TechCorp as a data scientist",
        "I have 5 years of ML experience", 
        "What do you know about my background?",
        "/debug-llm"
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        if cmd.startswith('/'):
            print(f"{i}. {cmd}")
        else:
            print(f"{i}. \"{cmd}\"")
    
    print(f"\n💡 Expected Result:")
    print("- Debug output shows knowledge extraction")
    print("- System prompt contains facts, not raw messages")
    print("- Context stays manageable regardless of conversation length")
    print("- LLM receives processed context, not entire chat history")

def show_cli_integration():
    """Show how debug mode integrates with the CLI"""
    
    print("\n" + "=" * 60)
    print("🔧 CLI Integration Example")
    print("=" * 60)
    
    print("\n📱 Normal CLI Output:")
    print("conversation_id> Hello, I'm a developer")
    print("┌─────────────────────────────────────┐")
    print("│ Hi! It's great to meet you! What    │")
    print("│ kind of development work do you do? │")
    print("└─────────────────────────────────────┘")
    print("💡 Used 0 knowledge facts, 1 recent turns")
    
    print("\n🔍 Debug CLI Output:")
    print("conversation_id> Hello, I'm a developer")
    print("\n🔍 [DEBUG] Processing message: 'Hello, I'm a developer'")
    print("📝 [DEBUG] Added user turn ID: abc123")
    print("🧠 [DEBUG] Context retrieved - Facts: 0, Recent turns: 1")
    print("🔗 [DEBUG] Has synthesized context: True")
    print("\n🎯 [DEBUG] === LLM INPUT DETAILS ===")
    print("📊 Context Summary: User has introduced themselves as a developer")
    print("💡 Relevant Facts (0 facts): (no relevant facts)")
    print("📝 Recent Context (1 turns): user: Hello, I'm a developer")
    print("👤 User Context: {'profession': 'developer'}")
    print("\n📤 [DEBUG] === FULL SYSTEM PROMPT SENT TO LLM ===")
    print("=" * 40)
    print("You are an AI assistant continuing a conversation...")
    print("CONVERSATION CONTEXT: User has introduced themselves...")
    print("RELEVANT FACTS: (no relevant facts found)")
    print("RECENT CONVERSATION: user: Hello, I'm a developer...")
    print("=" * 40)
    print("📤 [DEBUG] User message: Hello, I'm a developer")
    print("=" * 40)
    print("\n📥 [DEBUG] === LLM RESPONSE ===")
    print("Response length: 156 characters")
    print("Model used: gpt-4o-mini")
    print("Usage: CompletionUsage(completion_tokens=31, prompt_tokens=158)")
    print("=" * 25)
    
    print("\n┌─────────────────────────────────────┐")
    print("│ Hi! It's great to meet you! What    │")
    print("│ kind of development work do you do? │")
    print("└─────────────────────────────────────┘")
    print("💡 Used 0 knowledge facts, 1 recent turns")
    print("🔍 Debug mode active - Use /debug-llm to see LLM input details")

if __name__ == "__main__":
    print("🌳 ConvoTree Debug System Overview")
    demo_debug_features()
    show_cli_integration()
    
    print("\n" + "🎉" * 25)
    print("Ready to test context ephemerality!")
    print("Run: ./run.sh --debug")
    print("🎉" * 25)