#!/usr/bin/env python3
"""Create a test conversation for multi-hop reasoning testing."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from convotree.core.chat.enhanced_chat_v2 import ConversationManagerV2
from convotree.core.config.config_manager import ConfigManager
import uuid

def create_test_conversation():
    """Create a test conversation with multi-hop reasoning scenario."""
    
    # Initialize configuration and conversation manager
    config = ConfigManager().load_config()
    conv_manager = ConversationManagerV2(
        db_path=config.database.path,
        debug_mode=True,
        config=config.model.to_dict()
    )
    
    # Create a fixed test conversation ID for consistency
    test_conv_id = "test_multihop_reasoning_conv"
    conv_manager.conversation_id = test_conv_id
    
    # Messages that create the multi-hop scenario
    test_messages = [
        "I have a cat named Whiskers",
        "I work at TechCorp as a software engineer", 
        "My favorite color is blue",
        "I drive a red Tesla",
        "Alice owns a cat called Whiskers",
        "Alice is employed at TechCorp in engineering",
        "Alice loves the color blue", 
        "Alice drives a red Tesla Model 3"
    ]
    
    print(f"Creating test conversation: {test_conv_id}")
    
    # Add each message and extract knowledge
    for i, message in enumerate(test_messages):
        print(f"Adding message {i+1}: {message}")
        
        try:
            # Add message to conversation
            conv_manager.add_message(message, role="user")
            print(f"  → Message added successfully")
        except Exception as e:
            print(f"  → Failed to add message: {e}")
    
    print(f"\n✅ Test conversation created: {test_conv_id}")
    print("This conversation contains the multi-hop scenario:")
    print("- User has properties: cat=Whiskers, work=TechCorp, color=blue, car=Tesla")  
    print("- Alice has properties: cat=Whiskers, work=TechCorp, color=blue, car=Tesla")
    print("- The system should infer: user = Alice through shared properties")
    
    return test_conv_id

if __name__ == "__main__":
    test_conv_id = create_test_conversation()