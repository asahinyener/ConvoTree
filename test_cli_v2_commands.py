#!/usr/bin/env python3
"""
Test script to verify CLI v2 slash commands work
"""

import sys
import os
from pathlib import Path

# Add convotree to path
sys.path.insert(0, str(Path(__file__).parent))

from convotree.cli.cli_v2 import ConvoTreeCLIV2
from convotree.core.config.config_manager import ConfigManager
from unittest.mock import Mock, patch
import io

def test_cli_v2_slash_commands():
    """Test that slash commands are properly implemented in CLI v2"""
    
    # Mock environment and dependencies
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'mock-key'}):
        with patch('convotree.cli.cli_v2.ConversationManagerV2') as mock_manager:
            with patch('convotree.cli.cli_v2.ConfigManager') as mock_config_mgr:
                # Setup mocks
                mock_config = Mock()
                mock_config.ui.debug_mode = False
                mock_config.ui.verbose_logging = False
                mock_config.database.path = "test.db"
                mock_config.model.to_dict.return_value = {}
                mock_config_mgr.return_value.load_config.return_value = mock_config
                
                mock_chat = Mock()
                mock_chat.kg.get_conversation_summary.return_value = {
                    'turn_count': 5,
                    'knowledge_triples': 10,
                    'first_turn': '2025-01-01 10:00:00',
                    'last_turn': '2025-01-01 11:00:00'
                }
                mock_chat.kg._get_recent_knowledge.return_value = ['Test fact 1', 'Test fact 2']
                mock_manager.return_value.get_conversation.return_value = mock_chat
                
                # Create CLI instance
                cli = ConvoTreeCLIV2(conversation_id="test_session")
                
                # Test implemented commands
                commands_to_test = [
                    ('/status', '_cmd_status'),
                    ('/knowledge', '_cmd_knowledge'),
                    ('/history', '_cmd_history'),
                    ('/debug-mode', '_cmd_toggle_debug_mode'),
                    ('/help', '_cmd_help'),
                    ('/version', '_cmd_version'),
                ]
                
                results = {}
                
                for command, method_name in commands_to_test:
                    try:
                        # Capture output
                        old_stdout = sys.stdout
                        sys.stdout = captured_output = io.StringIO()
                        
                        # Test if command exists in commands dict
                        if command in cli.commands:
                            # Test if method exists and is not just pass
                            method = getattr(cli, method_name)
                            if method.__code__.co_code != (lambda: None).__code__.co_code:
                                # Try executing the command
                                cli.commands[command]([])
                                results[command] = "✅ IMPLEMENTED"
                            else:
                                results[command] = "❌ STUB (pass statement)"
                        else:
                            results[command] = "❌ NOT IN COMMANDS DICT"
                            
                    except Exception as e:
                        results[command] = f"⚠️  ERROR: {str(e)[:50]}..."
                    finally:
                        sys.stdout = old_stdout
                
                # Print results
                print("ConvoTree CLI v2.0 Slash Commands Test Results:")
                print("=" * 50)
                
                for command, result in results.items():
                    print(f"{command:<15} {result}")
                
                # Count implemented vs stub commands
                implemented = sum(1 for r in results.values() if r == "✅ IMPLEMENTED")
                total = len(results)
                
                print("\n" + "=" * 50)
                print(f"Summary: {implemented}/{total} commands properly implemented")
                
                if implemented >= 4:  # At least basic commands work
                    print("🎉 CLI v2 slash commands are working!")
                    return True
                else:
                    print("❌ More commands need to be implemented")
                    return False

if __name__ == "__main__":
    test_cli_v2_slash_commands()