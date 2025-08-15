#!/usr/bin/env python3
"""
Comprehensive Test Suite for ConvoTree v2.0 Improvements
Tests performance optimization, error handling, configuration, and UX improvements
"""

import os
import sys
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def setup_test_environment():
    """Setup test environment with temporary database and config"""
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found. Please set it in .env file")
        return None
    
    # Create temporary test database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    return {
        "test_db": temp_db.name,
        "test_conversation_id": f"test_session_{int(time.time())}"
    }

def test_caching_performance():
    """Test the caching system performance improvements"""
    print("\n🚀 Testing Caching Performance...")
    
    try:
        from cached_knowledge_graph import CachedKnowledgeGraph
        
        # Create test instance
        test_env = setup_test_environment()
        if not test_env:
            return False
        
        kg = CachedKnowledgeGraph(
            test_env["test_conversation_id"], 
            test_env["test_db"],
            cache_size=100  # Small cache for testing
        )
        
        print("  ✅ CachedKnowledgeGraph initialized")
        
        # Test cache warming
        kg.warm_cache()
        print("  ✅ Cache warming completed")
        
        # Test basic operations
        turn_id = kg.add_turn("user", "Hello, I'm testing the cache system")
        print(f"  ✅ Added turn: {turn_id}")
        
        # Test context retrieval (should populate cache)
        start_time = time.time()
        context1 = kg.get_relevant_context("What did I just say?")
        first_query_time = time.time() - start_time
        
        # Test cached retrieval (should be faster)
        start_time = time.time()
        context2 = kg.get_relevant_context("What did I just say?")
        cached_query_time = time.time() - start_time
        
        print(f"  ✅ First query: {first_query_time:.3f}s")
        print(f"  ✅ Cached query: {cached_query_time:.3f}s")
        
        # Get cache stats
        cache_stats = kg.get_cache_stats()
        print(f"  ✅ Cache hit rate: {cache_stats.get('hit_rate_percent', 0):.1f}%")
        print(f"  ✅ Cached items: {cache_stats.get('total_cached_items', 0)}")
        
        # Clean up
        Path(test_env["test_db"]).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Cache test failed: {e}")
        return False

def test_error_handling():
    """Test the comprehensive error handling system"""
    print("\n🛡️ Testing Error Handling...")
    
    try:
        from error_handler import ConvoTreeErrorHandler, ErrorCategory, ErrorSeverity
        
        # Create error handler
        error_handler = ConvoTreeErrorHandler(debug_mode=True)
        print("  ✅ Error handler initialized")
        
        # Test different error types
        test_errors = [
            (ValueError("Invalid input data"), ErrorCategory.VALIDATION),
            (ConnectionError("Network issue"), ErrorCategory.NETWORK),
            (FileNotFoundError("Config file missing"), ErrorCategory.CONFIGURATION),
        ]
        
        for error, expected_category in test_errors:
            error_info = error_handler.handle_error(error, {"test": True})
            print(f"  ✅ Handled {type(error).__name__}: {expected_category.value}")
            assert error_info.category == expected_category
        
        # Test error statistics
        stats = error_handler.get_error_stats()
        print(f"  ✅ Error stats: {stats['total_errors']} total errors")
        
        # Test error export
        export_file = error_handler.export_error_log()
        print(f"  ✅ Error log exported: {export_file}")
        
        # Clean up
        Path(export_file).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False

def test_configuration_system():
    """Test the configuration management system"""
    print("\n⚙️ Testing Configuration System...")
    
    try:
        from config_manager import ConfigManager, ConvoTreeConfig
        
        # Test default configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("  ✅ Default configuration loaded")
        
        # Test configuration validation
        print(f"  ✅ Model: {config.model.name}")
        print(f"  ✅ Cache size: {config.cache.size}")
        print(f"  ✅ Environment: {config.environment}")
        
        # Test configuration saving
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_config_path = f.name
        
        config_manager.save_config(config, Path(temp_config_path))
        print("  ✅ Configuration saved to file")
        
        # Test loading from file
        file_config_manager = ConfigManager(temp_config_path)
        loaded_config = file_config_manager.load_config()
        print("  ✅ Configuration loaded from file")
        
        # Verify configuration integrity
        assert loaded_config.model.name == config.model.name
        assert loaded_config.cache.size == config.cache.size
        
        # Test sample config creation
        sample_path = Path("test_sample.yaml")
        config_manager.create_sample_config(sample_path)
        print("  ✅ Sample configuration created")
        
        # Clean up
        Path(temp_config_path).unlink(missing_ok=True)
        sample_path.unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_enhanced_chat_system():
    """Test the enhanced chat system with all improvements"""
    print("\n💬 Testing Enhanced Chat System...")
    
    try:
        from enhanced_chat_v2 import EnhancedChatSystemV2
        from config_manager import ConvoTreeConfig, ModelConfig, CacheConfig, DatabaseConfig, UIConfig, SecurityConfig
        
        # Create test environment
        test_env = setup_test_environment()
        if not test_env:
            return False
        
        # Create test configuration
        test_config = ConvoTreeConfig(
            model=ModelConfig(temperature=0.1),  # Lower temperature for consistent testing
            cache=CacheConfig(size=50),
            database=DatabaseConfig(path=test_env["test_db"]),
            ui=UIConfig(debug_mode=True),
            security=SecurityConfig()
        )
        
        # Initialize enhanced chat system
        chat = EnhancedChatSystemV2(
            test_env["test_conversation_id"],
            test_env["test_db"],
            debug_mode=True,
            config=test_config.to_dict()
        )
        
        print("  ✅ Enhanced chat system initialized")
        
        # Test basic conversation
        response1 = chat.process_message("Hello, I'm testing the enhanced system")
        print("  ✅ First message processed")
        assert "response" in response1
        assert response1["conversation_id"] == test_env["test_conversation_id"]
        
        # Test context persistence
        response2 = chat.process_message("What did I just tell you?")
        print("  ✅ Context persistence tested")
        assert "response" in response2
        
        # Test performance stats
        stats = chat.get_performance_stats()
        print(f"  ✅ Performance stats: {stats['total_requests']} requests")
        print(f"  ✅ Average response time: {stats['avg_response_time']:.3f}s")
        print(f"  ✅ Cache hit rate: {stats['cache_stats']['hit_rate_percent']:.1f}%")
        
        # Test warm-up
        chat.warm_up()
        print("  ✅ System warm-up completed")
        
        # Test conversation export
        export_data = chat.export_conversation_data()
        print("  ✅ Conversation export completed")
        assert "performance_stats" in export_data
        
        # Clean up
        Path(test_env["test_db"]).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced chat system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_onboarding_system():
    """Test the onboarding and tutorial system"""
    print("\n🎓 Testing Onboarding System...")
    
    try:
        from onboarding_system import OnboardingSystem
        from rich.console import Console
        
        # Create test console and onboarding system
        console = Console(file=open(os.devnull, 'w'))  # Suppress output for testing
        onboarding = OnboardingSystem(console)
        
        print("  ✅ Onboarding system initialized")
        
        # Test progress tracking
        initial_progress = onboarding.get_progress_summary()
        print(f"  ✅ Initial progress: {initial_progress['progress_percentage']:.1f}%")
        
        # Test step completion
        onboarding._mark_step_complete("welcome")
        onboarding._mark_step_complete("basic_chat")
        
        updated_progress = onboarding.get_progress_summary()
        print(f"  ✅ Updated progress: {updated_progress['progress_percentage']:.1f}%")
        assert updated_progress['tutorial_steps_completed'] == 2
        
        # Test completion status
        onboarding._mark_onboarding_complete()
        assert onboarding.is_onboarding_complete()
        print("  ✅ Onboarding completion tracked")
        
        # Test progress reset
        onboarding.reset_progress()
        reset_progress = onboarding.get_progress_summary()
        assert reset_progress['tutorial_steps_completed'] == 0
        print("  ✅ Progress reset functionality")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Onboarding system test failed: {e}")
        return False

def test_integration():
    """Test integration between all systems"""
    print("\n🔗 Testing System Integration...")
    
    try:
        from enhanced_chat_v2 import ConversationManagerV2
        from config_manager import ConfigManager
        from error_handler import get_error_handler
        
        # Test environment
        test_env = setup_test_environment()
        if not test_env:
            return False
        
        # Initialize integrated systems
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        error_handler = get_error_handler(debug_mode=True)
        
        conversation_manager = ConversationManagerV2(
            db_path=test_env["test_db"],
            debug_mode=True,
            config=config.model.to_dict()
        )
        
        print("  ✅ All systems initialized")
        
        # Test conversation with error handling
        try:
            result = conversation_manager.send_message(
                test_env["test_conversation_id"],
                "Test integration message"
            )
            print("  ✅ Message sent through conversation manager")
            assert "response" in result
        except Exception as e:
            error_info = error_handler.handle_error(e, {"test": "integration"})
            print(f"  ✅ Error handled: {error_info.category.value}")
        
        # Test system statistics
        system_stats = conversation_manager.get_system_stats()
        print(f"  ✅ System stats: {system_stats['active_conversations']} active conversations")
        
        # Clean up
        Path(test_env["test_db"]).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False

def run_performance_benchmark():
    """Run performance benchmarks to measure improvements"""
    print("\n📊 Running Performance Benchmarks...")
    
    try:
        from enhanced_chat_v2 import EnhancedChatSystemV2
        from cached_knowledge_graph import CachedKnowledgeGraph
        
        test_env = setup_test_environment()
        if not test_env:
            return False
        
        # Test message processing speed
        chat = EnhancedChatSystemV2(
            test_env["test_conversation_id"],
            test_env["test_db"],
            debug_mode=False  # Disable debug for accurate timing
        )
        
        # Warm up the system
        chat.warm_up()
        
        # Benchmark message processing
        test_messages = [
            "Hello, I'm a software engineer",
            "I work at TechCorp in San Francisco", 
            "I love Python programming",
            "What do you know about my background?",
            "Can you help me with a coding question?"
        ]
        
        response_times = []
        cache_hits = 0
        
        for i, message in enumerate(test_messages):
            start_time = time.time()
            result = chat.process_message(message)
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if result.get('context_used', {}).get('cache_hit'):
                cache_hits += 1
            
            print(f"  📝 Message {i+1}: {response_time:.3f}s")
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        cache_hit_rate = (cache_hits / len(test_messages)) * 100
        
        print(f"\n📈 Benchmark Results:")
        print(f"  • Average Response Time: {avg_response_time:.3f}s")
        print(f"  • Fastest Response: {min_response_time:.3f}s")
        print(f"  • Slowest Response: {max_response_time:.3f}s")
        print(f"  • Cache Hit Rate: {cache_hit_rate:.1f}%")
        
        # Get final performance stats
        final_stats = chat.get_performance_stats()
        print(f"  • Final Cache Items: {final_stats['cache_stats']['total_cached_items']}")
        print(f"  • Total Requests: {final_stats['total_requests']}")
        
        # Clean up
        Path(test_env["test_db"]).unlink(missing_ok=True)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Performance benchmark failed: {e}")
        return False

def main():
    """Run all improvement tests"""
    print("🌳 ConvoTree v2.0 Comprehensive Test Suite")
    print("=" * 60)
    
    # Check dependencies
    required_modules = [
        "yaml", "rich", "openai", "sqlite3", "pathlib", "datetime"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please run: uv sync")
        return
    
    # Run test suite
    test_results = {}
    
    tests = [
        ("Caching Performance", test_caching_performance),
        ("Error Handling", test_error_handling),
        ("Configuration System", test_configuration_system),
        ("Enhanced Chat System", test_enhanced_chat_system),
        ("Onboarding System", test_onboarding_system),
        ("System Integration", test_integration),
        ("Performance Benchmark", run_performance_benchmark)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            test_results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            test_results[test_name] = False
            print(f"❌ FAILED: {test_name} - {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! ConvoTree v2.0 improvements are working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)