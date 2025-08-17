#!/usr/bin/env python3
"""Test the LLM-powered dreaming system."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from convotree.core.memory.graph_reasoning_engine import KnowledgeGraphReasoningEngine

def test_dreaming_system():
    """Test the dreaming system on current conversation."""
    
    print("🧪 Testing LLM-powered dreaming system...")
    
    # Initialize reasoning engine
    reasoning_engine = KnowledgeGraphReasoningEngine(db_path="convotree.db")
    
    # Get the current session conversation ID (should be the CLI session we just ran)
    print("💭 Starting memory dreaming process...")
    
    try:
        # Test with the test conversation we just created
        conv_id = "test_multihop"  # From the CLI output above
        results = reasoning_engine.perform_memory_dreaming(conv_id)
        
        print("\n✅ Dreaming completed successfully!")
        print(f"Results: {results}")
        
    except Exception as e:
        print(f"❌ Dreaming failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dreaming_system()