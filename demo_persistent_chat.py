#!/usr/bin/env python3
"""
Demo script for Persistent Knowledge Graph Chat System
Demonstrates context preservation across conversation turns
"""

import json
from enhanced_chat import create_conversation, continue_conversation

def demo_conversation():
    """Demonstrate the persistent KG chat system"""
    
    conversation_id = "demo_session_001"
    print(f"🚀 Starting conversation: {conversation_id}")
    print("=" * 60)
    
    # Create conversation instance
    chat = create_conversation(conversation_id)
    
    # Simulate a multi-turn conversation
    messages = [
        "Hi, I'm Alex and I'm working on a machine learning project about sentiment analysis.",
        "I'm using Python with scikit-learn and I need help with feature extraction.",
        "The dataset has about 10,000 movie reviews. I want to use TF-IDF.",
        "Actually, let me step away for now. I'll be back later.",
        # Simulating a gap/new session
        "Hi again! Can you remind me what we were discussing about my ML project?",
        "Right, the TF-IDF approach. What parameters should I tune for movie reviews?",
        "Also, I mentioned I'm using scikit-learn. Any other libraries I should consider?",
    ]
    
    for i, user_msg in enumerate(messages, 1):
        print(f"\n🧑 User (Turn {i}): {user_msg}")
        
        # Process the message through our persistent KG system
        result = chat.process_message(user_msg)
        
        print(f"🤖 Assistant: {result['response']}")
        
        # Show context information
        context_info = result['context_used']
        print(f"📊 Context used: {context_info['relevant_facts_count']} facts, {context_info['recent_turns_count']} recent turns")
        
        if i == 4:  # After "step away" message
            print("\n" + "="*60)
            print("🔄 SIMULATING SESSION GAP - User returns later")
            print("="*60)
    
    # Show conversation statistics
    print("\n" + "="*60)
    print("📈 CONVERSATION STATISTICS")
    print("="*60)
    
    stats = result['conversation_stats']
    print(f"Total turns: {stats['turn_count']}")
    print(f"Knowledge triples: {stats['knowledge_triples']}")
    print(f"Duration: {stats['first_turn']} → {stats['last_turn']}")
    
    # Export conversation data
    export_data = chat.export_conversation_data()
    print(f"\n🧠 KNOWLEDGE EXTRACTED:")
    for fact in export_data['knowledge_facts'][:5]:
        print(f"  • {fact}")
    
    print(f"\n💾 Context State: {json.dumps(export_data['context_state'], indent=2)}")

def simple_demo():
    """Simple demonstration using the continue_conversation utility"""
    
    print("\n" + "="*60) 
    print("🔄 SIMPLE UTILITY DEMO")
    print("="*60)
    
    conv_id = "simple_demo"
    
    # Use the simple utility function
    response1 = continue_conversation(conv_id, "My name is Sarah and I love cooking Italian food.")
    print(f"🧑 User: My name is Sarah and I love cooking Italian food.")
    print(f"🤖 Assistant: {response1}")
    
    response2 = continue_conversation(conv_id, "What's my name and what do I love?")
    print(f"\n🧑 User: What's my name and what do I love?") 
    print(f"🤖 Assistant: {response2}")

if __name__ == "__main__":
    print("🧠 PERSISTENT KNOWLEDGE GRAPH CHAT DEMO")
    print("Demonstrating context preservation without context rot")
    
    try:
        demo_conversation()
        simple_demo()
        print(f"\n✅ Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()