#!/usr/bin/env python3
"""
Comprehensive Stress Test Suite for the Persistent KG System
Tests performance, concurrency, edge cases, and system limits
"""

import json
import sqlite3
import time
import threading
import concurrent.futures
import random
import string
import psutil
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from ..core.memory.persistent_kg import PersistentKG, ConversationTurn, KnowledgeTriple
from ..core.chat.enhanced_chat import EnhancedChatSystem, ConversationManager
from unittest.mock import Mock, patch

def test_database_creation():
    """Test database initialization"""
    print("🔧 Testing database creation...")
    
    # Use a test database
    test_db = "test_conversations.db"
    if Path(test_db).exists():
        Path(test_db).unlink()
    
    # Set a dummy API key for testing
    import os
    import dotenv
    dotenv.load_dotenv()
    # os.environ["OPENAI_API_KEY"] = "test-key-for-db-init"
    
    kg = PersistentKG("test_conv", test_db)
    
    # Check if tables were created
    with sqlite3.connect(test_db) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['conversations', 'turns', 'knowledge_triples', 'context_state']
        for table in expected_tables:
            assert table in tables, f"Missing table: {table}"
    
    print("✅ Database creation successful")
    return test_db

def test_knowledge_storage(test_db):
    """Test knowledge triple storage and retrieval"""
    print("🔧 Testing knowledge storage...")
    
    kg = PersistentKG("test_conv", test_db)
    
    # Manually add some test data (without OpenAI API)
    with sqlite3.connect(test_db) as conn:
        # Add a test turn
        conn.execute('''
            INSERT INTO turns (turn_id, conversation_id, role, content, timestamp, entities, relations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("turn_001", "test_conv", "user", "My name is John", "2025-01-01T10:00:00", 
              '["John"]', '["John|is_named|John"]'))
        
        # Add test knowledge triples
        conn.execute('''
            INSERT INTO knowledge_triples 
            (conversation_id, subject, relation, object, source_turn, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("test_conv", "John", "is_named", "John", "turn_001", 1.0, "2025-01-01T10:00:00"))
        
        conn.commit()
    
    # Test retrieval
    recent_knowledge = kg._get_recent_knowledge(10)
    assert len(recent_knowledge) > 0, "No knowledge retrieved"
    print(f"   Retrieved knowledge: {recent_knowledge}")
    
    # Test context state
    kg._update_context_state({"user_name": "John", "topic": "introduction"})
    context = kg._get_context_state()
    assert context.get("user_name") == "John", "Context state not stored properly"
    
    print("✅ Knowledge storage successful")

def test_conversation_summary(test_db):
    """Test conversation summary generation"""
    print("🔧 Testing conversation summary...")
    
    kg = PersistentKG("test_conv", test_db)
    summary = kg.get_conversation_summary()
    
    assert summary["conversation_id"] == "test_conv", "Wrong conversation ID"
    assert summary["turn_count"] > 0, "No turns counted"
    assert summary["knowledge_triples"] > 0, "No knowledge triples counted"
    
    print(f"   Summary: {json.dumps(summary, indent=2)}")
    print("✅ Conversation summary successful")

@dataclass
class TestMetrics:
    """Test execution metrics"""
    test_name: str
    duration: float
    memory_usage: float
    success: bool
    error_message: str = ""
    additional_data: Dict[str, Any] = None

class StressTestSuite:
    """Comprehensive stress testing suite"""
    
    def __init__(self):
        self.test_results: List[TestMetrics] = []
        self.mock_openai = True  # Use mocked OpenAI by default
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete stress test suite"""
        print("🚀 RUNNING COMPREHENSIVE STRESS TEST SUITE")
        print("=" * 60)
        
        test_categories = [
            ("Basic Functionality", self._run_basic_tests),
            ("Performance Tests", self._run_performance_tests),
            ("Concurrency Tests", self._run_concurrency_tests),
            ("Edge Case Tests", self._run_edge_case_tests),
            ("Memory/Resource Tests", self._run_resource_tests),
            ("Database Stress Tests", self._run_database_stress_tests),
            ("API Integration Tests", self._run_api_integration_tests),
            ("Load Tests", self._run_load_tests)
        ]
        
        overall_start = time.time()
        
        for category_name, test_function in test_categories:
            print(f"\n📊 {category_name}")
            print("-" * 40)
            try:
                test_function()
            except Exception as e:
                print(f"❌ Category {category_name} failed: {e}")
                import traceback
                traceback.print_exc()
        
        overall_duration = time.time() - overall_start
        
        # Generate comprehensive report
        report = self._generate_test_report(overall_duration)
        
        # Save report to file
        report_file = f"stress_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📝 Detailed report saved to: {report_file}")
        
        return report
    
    def _measure_test(self, test_name: str, test_func, *args, **kwargs) -> TestMetrics:
        """Measure test execution metrics"""
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            success = True
            error_message = ""
            additional_data = result if isinstance(result, dict) else {}
        except Exception as e:
            success = False
            error_message = str(e)
            additional_data = {}
        
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        metrics = TestMetrics(
            test_name=test_name,
            duration=end_time - start_time,
            memory_usage=end_memory - start_memory,
            success=success,
            error_message=error_message,
            additional_data=additional_data
        )
        
        self.test_results.append(metrics)
        
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}: {metrics.duration:.3f}s, {metrics.memory_usage:+.2f}MB")
        
        return metrics

    def _run_basic_tests(self):
        """Run basic functionality tests"""
        self._measure_test("Database Creation", test_database_creation)
        
        test_db = "test_conversations.db"
        self._measure_test("Knowledge Storage", test_knowledge_storage, test_db)
        self._measure_test("Conversation Summary", test_conversation_summary, test_db)
        
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
    
    def _run_performance_tests(self):
        """Run performance-focused tests"""
        
        # Test large knowledge base performance
        self._measure_test("Large Knowledge Base", self._test_large_knowledge_base)
        
        # Test query performance with many triples
        self._measure_test("Query Performance", self._test_query_performance)
        
        # Test context retrieval speed
        self._measure_test("Context Retrieval Speed", self._test_context_retrieval_speed)
        
        # Test database operations speed
        self._measure_test("Database Operations Speed", self._test_db_operations_speed)
    
    def _run_concurrency_tests(self):
        """Run concurrency and threading tests"""
        
        # Test concurrent conversations
        self._measure_test("Concurrent Conversations", self._test_concurrent_conversations)
        
        # Test concurrent database writes
        self._measure_test("Concurrent DB Writes", self._test_concurrent_db_writes)
        
        # Test thread safety
        self._measure_test("Thread Safety", self._test_thread_safety)
        
        # Test conversation manager under load
        self._measure_test("Conversation Manager Load", self._test_conversation_manager_load)
    
    def _run_edge_case_tests(self):
        """Run edge case and error handling tests"""
        
        # Test with malformed data
        self._measure_test("Malformed Data Handling", self._test_malformed_data)
        
        # Test with very long messages
        self._measure_test("Long Message Handling", self._test_long_messages)
        
        # Test with special characters
        self._measure_test("Special Characters", self._test_special_characters)
        
        # Test database corruption recovery
        self._measure_test("Database Recovery", self._test_database_recovery)
        
        # Test API failures
        self._measure_test("API Failure Handling", self._test_api_failures)
    
    def _run_resource_tests(self):
        """Run memory and resource usage tests"""
        
        # Test memory usage growth
        self._measure_test("Memory Usage Growth", self._test_memory_usage_growth)
        
        # Test database file size growth
        self._measure_test("Database Size Growth", self._test_database_size_growth)
        
        # Test cleanup and garbage collection
        self._measure_test("Resource Cleanup", self._test_resource_cleanup)
    
    def _run_database_stress_tests(self):
        """Run database-specific stress tests"""
        
        # Test high-volume inserts
        self._measure_test("High Volume Inserts", self._test_high_volume_inserts)
        
        # Test complex queries
        self._measure_test("Complex Queries", self._test_complex_queries)
        
        # Test database locking
        self._measure_test("Database Locking", self._test_database_locking)
    
    def _run_api_integration_tests(self):
        """Run OpenAI API integration tests"""
        
        # Test with mocked API responses
        self._measure_test("Mocked API Responses", self._test_mocked_api_responses)
        
        # Test API error handling
        self._measure_test("API Error Handling", self._test_api_error_handling)
        
        # Test rate limiting
        self._measure_test("Rate Limiting", self._test_rate_limiting)
    
    def _run_load_tests(self):
        """Run high-load scenario tests"""
        
        # Test sustained load
        self._measure_test("Sustained Load Test", self._test_sustained_load)
        
        # Test burst load
        self._measure_test("Burst Load Test", self._test_burst_load)
        
        # Test system limits
        self._measure_test("System Limits Test", self._test_system_limits)
    
    # Individual test implementations
    
    def _test_large_knowledge_base(self) -> Dict[str, Any]:
        """Test performance with large knowledge base"""
        test_db = "large_kb_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("large_test", test_db)
        
        # Insert 10,000 knowledge triples
        start_time = time.time()
        with sqlite3.connect(test_db) as conn:
            for i in range(10000):
                entity = f"entity_{i}"
                relation = random.choice(["is_related_to", "has_property", "connects_to"])
                target = f"target_{i % 1000}"  # Create some overlap
                
                conn.execute('''
                    INSERT INTO knowledge_triples 
                    (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ("large_test", entity, relation, target, f"turn_{i}", 1.0, datetime.now().isoformat()))
            conn.commit()
        
        insert_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        recent_knowledge = kg._get_recent_knowledge(100)
        retrieval_time = time.time() - start_time
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "triples_inserted": 10000,
            "insert_time": insert_time,
            "retrieval_time": retrieval_time,
            "retrieved_count": len(recent_knowledge)
        }
    
    def _test_query_performance(self) -> Dict[str, Any]:
        """Test query performance with various scenarios"""
        test_db = "query_perf_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("query_test", test_db)
        
        # Insert test data
        with sqlite3.connect(test_db) as conn:
            for i in range(5000):
                conn.execute('''
                    INSERT INTO knowledge_triples 
                    (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ("query_test", f"subject_{i}", f"relation_{i % 10}", f"object_{i}", 
                      f"turn_{i}", random.uniform(0.5, 1.0), datetime.now().isoformat()))
            conn.commit()
        
        # Test different query patterns
        queries = [
            "SELECT COUNT(*) FROM knowledge_triples WHERE conversation_id = ?",
            "SELECT * FROM knowledge_triples WHERE subject LIKE 'subject_1%' LIMIT 100",
            "SELECT subject, COUNT(*) FROM knowledge_triples GROUP BY subject LIMIT 50",
            "SELECT * FROM knowledge_triples ORDER BY created_at DESC LIMIT 100"
        ]
        
        query_times = []
        for query in queries:
            start_time = time.time()
            with sqlite3.connect(test_db) as conn:
                if "?" in query:
                    conn.execute(query, ("query_test",)).fetchall()
                else:
                    conn.execute(query).fetchall()
            query_times.append(time.time() - start_time)
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "query_count": len(queries),
            "avg_query_time": sum(query_times) / len(query_times),
            "max_query_time": max(query_times),
            "min_query_time": min(query_times)
        }
    
    def _test_context_retrieval_speed(self) -> Dict[str, Any]:
        """Test context retrieval speed with mocked API"""
        test_db = "context_speed_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Mock OpenAI responses
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "entities": ["test_entity"],
            "relations": ["test|relation|target"],
            "key_concepts": ["concept"],
            "context_updates": {"test_key": "test_value"}
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            kg = PersistentKG("speed_test", test_db)
            
            # Add some turns to build context
            for i in range(100):
                kg.add_turn("user", f"Test message {i}")
            
            # Test context retrieval speed
            retrieval_times = []
            for i in range(20):
                start_time = time.time()
                context = kg.get_relevant_context(f"Query {i}")
                retrieval_times.append(time.time() - start_time)
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "retrieval_count": len(retrieval_times),
            "avg_retrieval_time": sum(retrieval_times) / len(retrieval_times),
            "max_retrieval_time": max(retrieval_times)
        }
    
    def _test_db_operations_speed(self) -> Dict[str, Any]:
        """Test raw database operations speed"""
        test_db = "db_speed_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Test insert speed
        start_time = time.time()
        with sqlite3.connect(test_db) as conn:
            conn.execute('''
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    data TEXT,
                    timestamp TEXT
                )
            ''')
            
            for i in range(10000):
                conn.execute("INSERT INTO test_table (data, timestamp) VALUES (?, ?)",
                           (f"test_data_{i}", datetime.now().isoformat()))
            conn.commit()
        
        insert_time = time.time() - start_time
        
        # Test query speed
        start_time = time.time()
        with sqlite3.connect(test_db) as conn:
            results = conn.execute("SELECT * FROM test_table WHERE data LIKE 'test_data_1%'").fetchall()
        query_time = time.time() - start_time
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "insert_time": insert_time,
            "query_time": query_time,
            "records_inserted": 10000,
            "records_found": len(results)
        }
    
    def _test_concurrent_conversations(self) -> Dict[str, Any]:
        """Test concurrent conversation handling"""
        manager = ConversationManager()
        num_conversations = 50
        messages_per_conversation = 20
        
        # Mock OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        extraction_response = Mock()
        extraction_response.choices = [Mock()]
        extraction_response.choices[0].message.content = json.dumps({
            "entities": ["entity"],
            "relations": ["subject|relation|object"],
            "key_concepts": ["concept"],
            "context_updates": {}
        })
        
        def mock_create(*args, **kwargs):
            if kwargs.get('response_format', {}).get('type') == 'json_object':
                return extraction_response
            return mock_response
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.side_effect = mock_create
            
            def send_messages(conv_id):
                results = []
                for i in range(messages_per_conversation):
                    try:
                        result = manager.send_message(f"conv_{conv_id}", f"Message {i} from conversation {conv_id}")
                        results.append(result)
                    except Exception as e:
                        results.append({"error": str(e)})
                return results
            
            start_time = time.time()
            
            # Run conversations concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(send_messages, i) for i in range(num_conversations)]
                all_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            total_time = time.time() - start_time
        
        # Cleanup test databases
        for i in range(num_conversations):
            db_path = Path(f"conversations.db")
            if db_path.exists():
                try:
                    db_path.unlink()
                except:
                    pass  # May be in use by other threads
        
        successful_messages = sum(1 for results in all_results for result in results if "error" not in result)
        total_messages = num_conversations * messages_per_conversation
        
        return {
            "conversations": num_conversations,
            "messages_per_conv": messages_per_conversation,
            "total_messages": total_messages,
            "successful_messages": successful_messages,
            "total_time": total_time,
            "messages_per_second": successful_messages / total_time if total_time > 0 else 0
        }
    
    def _test_concurrent_db_writes(self) -> Dict[str, Any]:
        """Test concurrent database write operations"""
        test_db = "concurrent_writes_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Initialize database
        kg = PersistentKG("concurrent_test", test_db)
        
        num_writers = 20
        writes_per_writer = 100
        
        def write_data(writer_id):
            successful_writes = 0
            for i in range(writes_per_writer):
                try:
                    with sqlite3.connect(test_db) as conn:
                        conn.execute('''
                            INSERT INTO knowledge_triples 
                            (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', ("concurrent_test", f"writer_{writer_id}_entity_{i}", "writes", 
                              f"data_{i}", f"turn_{writer_id}_{i}", 1.0, datetime.now().isoformat()))
                        conn.commit()
                    successful_writes += 1
                except Exception as e:
                    print(f"Write error in writer {writer_id}: {e}")
            return successful_writes
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_writers) as executor:
            futures = [executor.submit(write_data, i) for i in range(num_writers)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Verify data integrity
        with sqlite3.connect(test_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM knowledge_triples")
            actual_count = cursor.fetchone()[0]
        
        expected_count = sum(results)
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "writers": num_writers,
            "writes_per_writer": writes_per_writer,
            "expected_writes": num_writers * writes_per_writer,
            "successful_writes": expected_count,
            "actual_db_count": actual_count,
            "data_integrity": actual_count == expected_count,
            "total_time": total_time,
            "writes_per_second": expected_count / total_time if total_time > 0 else 0
        }
    
    def _test_thread_safety(self) -> Dict[str, Any]:
        """Test thread safety of the system"""
        test_db = "thread_safety_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("thread_test", test_db)
        
        # Shared counter for race condition detection
        shared_counter = {"value": 0}
        lock = threading.Lock()
        
        def thread_worker(thread_id):
            operations = []
            for i in range(50):
                try:
                    # Test various operations
                    kg._update_context_state({f"thread_{thread_id}_key_{i}": f"value_{i}"})
                    context = kg._get_context_state()
                    recent = kg._get_recent_knowledge(10)
                    
                    # Safely increment counter
                    with lock:
                        shared_counter["value"] += 1
                    
                    operations.append("success")
                except Exception as e:
                    operations.append(f"error: {e}")
            
            return operations
        
        num_threads = 10
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(thread_worker, i) for i in range(num_threads)]
            all_operations = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Cleanup
        Path(test_db).unlink()
        
        successful_ops = sum(1 for ops in all_operations for op in ops if op == "success")
        total_ops = sum(len(ops) for ops in all_operations)
        
        return {
            "threads": num_threads,
            "operations_per_thread": 50,
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "shared_counter_final": shared_counter["value"],
            "expected_counter": num_threads * 50,
            "counter_integrity": shared_counter["value"] == num_threads * 50,
            "total_time": total_time
        }
    
    def _test_conversation_manager_load(self) -> Dict[str, Any]:
        """Test conversation manager under high load"""
        manager = ConversationManager()
        
        # Create many conversations simultaneously
        num_conversations = 100
        
        def create_and_use_conversation(conv_id):
            try:
                conv = manager.get_conversation(f"load_test_{conv_id}")
                # Simulate some usage without OpenAI calls
                summary = conv.kg.get_conversation_summary()
                return {"success": True, "conv_id": f"load_test_{conv_id}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_and_use_conversation, i) for i in range(num_conversations)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if r["success"])
        active_conversations = manager.list_conversations()
        
        return {
            "requested_conversations": num_conversations,
            "successful_creations": successful,
            "active_conversations": len(active_conversations),
            "total_time": total_time
        }
    
    def _test_malformed_data(self) -> Dict[str, Any]:
        """Test handling of malformed data"""
        test_db = "malformed_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("malformed_test", test_db)
        
        malformed_inputs = [
            "",  # Empty string
            None,  # None value
            "\x00\x01\x02",  # Binary data
            "\n\r\t",  # Just whitespace
            "a" * 100000,  # Very long string
            "SELECT * FROM users; DROP TABLE users;",  # SQL injection attempt
            "{'malformed': json}",  # Invalid JSON
            "🔥💯🎉" * 1000,  # Many emojis
        ]
        
        results = []
        for i, malformed_input in enumerate(malformed_inputs):
            try:
                if malformed_input is not None:
                    turn_id = kg.add_turn("user", malformed_input)
                    results.append({"input_index": i, "success": True, "turn_id": turn_id})
                else:
                    # Handle None case separately
                    results.append({"input_index": i, "success": False, "error": "None input skipped"})
            except Exception as e:
                results.append({"input_index": i, "success": False, "error": str(e)})
        
        # Test database integrity after malformed inputs
        try:
            summary = kg.get_conversation_summary()
            integrity_check = True
        except Exception as e:
            integrity_check = False
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "malformed_inputs_tested": len(malformed_inputs),
            "successful_handles": sum(1 for r in results if r["success"]),
            "failed_handles": sum(1 for r in results if not r["success"]),
            "database_integrity": integrity_check,
            "results": results
        }
    
    def _test_long_messages(self) -> Dict[str, Any]:
        """Test handling of very long messages"""
        test_db = "long_messages_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Mock OpenAI to avoid actual API calls
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "entities": ["long_entity"],
            "relations": ["subject|relation|object"],
            "key_concepts": ["long_concept"],
            "context_updates": {"status": "processed_long_message"}
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            kg = PersistentKG("long_test", test_db)
            
            # Test messages of increasing length
            message_lengths = [1000, 10000, 50000, 100000]  # characters
            results = []
            
            for length in message_lengths:
                long_message = "This is a very long message. " * (length // 30)
                long_message = long_message[:length]  # Trim to exact length
                
                start_time = time.time()
                try:
                    turn_id = kg.add_turn("user", long_message)
                    process_time = time.time() - start_time
                    results.append({
                        "length": length,
                        "success": True,
                        "process_time": process_time,
                        "turn_id": turn_id
                    })
                except Exception as e:
                    results.append({
                        "length": length,
                        "success": False,
                        "error": str(e)
                    })
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "message_lengths_tested": message_lengths,
            "results": results,
            "all_successful": all(r["success"] for r in results)
        }
    
    def _test_special_characters(self) -> Dict[str, Any]:
        """Test handling of special characters and encodings"""
        test_db = "special_chars_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Mock OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "entities": ["special_entity"],
            "relations": ["subject|relation|object"],
            "key_concepts": ["special_concept"],
            "context_updates": {}
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            kg = PersistentKG("special_test", test_db)
            
            special_messages = [
                "Hello 世界! 🌍",  # Unicode and emojis
                "Ñoño piñata jalapeño",  # Accented characters
                "Здравствуй мир",  # Cyrillic
                "مرحبا بالعالم",  # Arabic
                "こんにちは世界",  # Japanese
                "<script>alert('xss')</script>",  # HTML/JS
                "\\n\\t\\r",  # Escaped characters
                "''; DROP TABLE users; --",  # SQL injection patterns
                "\u0000\u0001\u001f",  # Control characters
            ]
            
            results = []
            for i, message in enumerate(special_messages):
                try:
                    turn_id = kg.add_turn("user", message)
                    # Verify retrieval
                    context = kg.get_relevant_context("test query")
                    results.append({"message_index": i, "success": True, "turn_id": turn_id})
                except Exception as e:
                    results.append({"message_index": i, "success": False, "error": str(e)})
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "special_messages_tested": len(special_messages),
            "successful_handles": sum(1 for r in results if r["success"]),
            "results": results
        }
    
    def _test_database_recovery(self) -> Dict[str, Any]:
        """Test database corruption recovery"""
        test_db = "recovery_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Create a normal database first
        kg = PersistentKG("recovery_test", test_db)
        
        # Add some data
        kg._update_context_state({"test_key": "test_value"})
        
        # Close connection and corrupt the database file
        del kg
        
        # Corrupt the database file
        with open(test_db, 'ab') as f:
            f.write(b'CORRUPTED_DATA' * 100)
        
        # Try to use the corrupted database
        recovery_successful = False
        try:
            kg_new = PersistentKG("recovery_test", test_db)
            summary = kg_new.get_conversation_summary()
            recovery_successful = True
        except Exception as e:
            recovery_error = str(e)
        
        # Test with completely missing database
        Path(test_db).unlink()
        try:
            kg_missing = PersistentKG("missing_test", test_db)
            missing_db_recovery = True
        except Exception as e:
            missing_db_recovery = False
        
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        return {
            "corruption_recovery": recovery_successful,
            "missing_db_recovery": missing_db_recovery
        }
    
    def _test_api_failures(self) -> Dict[str, Any]:
        """Test handling of OpenAI API failures"""
        test_db = "api_failure_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Test different types of API failures
        failure_scenarios = [
            {"exception": Exception("Connection timeout"), "name": "timeout"},
            {"exception": Exception("Rate limit exceeded"), "name": "rate_limit"},
            {"exception": Exception("Invalid API key"), "name": "auth_error"},
            {"exception": ValueError("Invalid JSON response"), "name": "invalid_json"}
        ]
        
        results = []
        
        for scenario in failure_scenarios:
            try:
                with patch('openai.OpenAI') as mock_openai:
                    mock_openai.return_value.chat.completions.create.side_effect = scenario["exception"]
                    
                    kg = PersistentKG(f"api_fail_{scenario['name']}", test_db)
                    
                    # This should handle the API failure gracefully
                    turn_id = kg.add_turn("user", "Test message during API failure")
                    
                    results.append({
                        "scenario": scenario["name"],
                        "handled_gracefully": True,
                        "turn_id": turn_id
                    })
            except Exception as e:
                results.append({
                    "scenario": scenario["name"],
                    "handled_gracefully": False,
                    "error": str(e)
                })
        
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        return {
            "scenarios_tested": len(failure_scenarios),
            "gracefully_handled": sum(1 for r in results if r["handled_gracefully"]),
            "results": results
        }
    
    def _test_memory_usage_growth(self) -> Dict[str, Any]:
        """Test memory usage growth over time"""
        process = psutil.Process()
        
        # Mock OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "entities": ["memory_entity"],
            "relations": ["subject|relation|object"],
            "key_concepts": ["memory_concept"],
            "context_updates": {}
        })
        
        memory_measurements = []
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            manager = ConversationManager()
            
            # Measure memory at different points
            memory_measurements.append(("start", process.memory_info().rss / 1024 / 1024))
            
            # Create many conversations
            for i in range(50):
                conv = manager.get_conversation(f"memory_test_{i}")
                
                # Add messages to each conversation
                for j in range(10):
                    conv.process_message(f"Message {j} for conversation {i}")
                
                if i % 10 == 0:
                    memory_measurements.append((f"after_{i}_conversations", process.memory_info().rss / 1024 / 1024))
        
        # Final measurement
        memory_measurements.append(("end", process.memory_info().rss / 1024 / 1024))
        
        # Calculate growth
        start_memory = memory_measurements[0][1]
        end_memory = memory_measurements[-1][1]
        memory_growth = end_memory - start_memory
        
        return {
            "start_memory_mb": start_memory,
            "end_memory_mb": end_memory,
            "memory_growth_mb": memory_growth,
            "memory_measurements": memory_measurements,
            "conversations_created": 50,
            "messages_per_conversation": 10
        }
    
    def _test_database_size_growth(self) -> Dict[str, Any]:
        """Test database file size growth"""
        test_db = "size_growth_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("size_test", test_db)
        
        size_measurements = []
        size_measurements.append(("start", 0))  # File doesn't exist yet
        
        # Add data in batches and measure size
        for batch in range(10):
            # Add 1000 knowledge triples per batch
            with sqlite3.connect(test_db) as conn:
                for i in range(1000):
                    conn.execute('''
                        INSERT INTO knowledge_triples 
                        (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', ("size_test", f"batch_{batch}_entity_{i}", "has_data", f"value_{i}", 
                          f"turn_{batch}_{i}", 1.0, datetime.now().isoformat()))
                conn.commit()
            
            file_size_mb = Path(test_db).stat().st_size / 1024 / 1024
            size_measurements.append((f"batch_{batch}", file_size_mb))
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "batches": 10,
            "records_per_batch": 1000,
            "total_records": 10000,
            "final_size_mb": size_measurements[-1][1],
            "size_measurements": size_measurements
        }
    
    def _test_resource_cleanup(self) -> Dict[str, Any]:
        """Test resource cleanup and garbage collection"""
        import gc
        
        # Force garbage collection and measure
        gc.collect()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Create many objects that should be cleaned up
        test_objects = []
        for i in range(1000):
            # Create temporary conversation objects
            manager = ConversationManager()
            conv = manager.get_conversation(f"cleanup_test_{i}")
            test_objects.append((manager, conv))
        
        memory_after_creation = process.memory_info().rss / 1024 / 1024
        
        # Clear references
        test_objects.clear()
        
        # Force cleanup
        gc.collect()
        memory_after_cleanup = process.memory_info().rss / 1024 / 1024
        
        return {
            "initial_memory_mb": initial_memory,
            "memory_after_creation_mb": memory_after_creation,
            "memory_after_cleanup_mb": memory_after_cleanup,
            "memory_freed_mb": memory_after_creation - memory_after_cleanup,
            "objects_created": 1000
        }
    
    def _test_high_volume_inserts(self) -> Dict[str, Any]:
        """Test high-volume database inserts"""
        test_db = "high_volume_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("volume_test", test_db)
        
        # Test batch inserts
        batch_sizes = [100, 1000, 5000, 10000]
        results = []
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            with sqlite3.connect(test_db) as conn:
                # Prepare batch data
                batch_data = []
                for i in range(batch_size):
                    batch_data.append((
                        "volume_test", f"entity_{i}", "batch_relation", f"value_{i}",
                        f"turn_{i}", 1.0, datetime.now().isoformat()
                    ))
                
                # Execute batch insert
                conn.executemany('''
                    INSERT INTO knowledge_triples 
                    (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', batch_data)
                conn.commit()
            
            insert_time = time.time() - start_time
            
            # Verify count
            with sqlite3.connect(test_db) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM knowledge_triples")
                count = cursor.fetchone()[0]
            
            results.append({
                "batch_size": batch_size,
                "insert_time": insert_time,
                "inserts_per_second": batch_size / insert_time if insert_time > 0 else 0,
                "total_count": count
            })
            
            # Clear for next test
            with sqlite3.connect(test_db) as conn:
                conn.execute("DELETE FROM knowledge_triples")
                conn.commit()
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "batch_sizes_tested": batch_sizes,
            "results": results
        }
    
    def _test_complex_queries(self) -> Dict[str, Any]:
        """Test complex database queries"""
        test_db = "complex_queries_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("query_test", test_db)
        
        # Insert test data with patterns
        with sqlite3.connect(test_db) as conn:
            # Create hierarchical data
            for i in range(1000):
                category = f"category_{i % 10}"
                subcategory = f"subcategory_{i % 100}"
                entity = f"entity_{i}"
                
                conn.execute('''
                    INSERT INTO knowledge_triples 
                    (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ("query_test", entity, "belongs_to", subcategory, f"turn_{i}", 
                      random.uniform(0.5, 1.0), datetime.now().isoformat()))
                
                conn.execute('''
                    INSERT INTO knowledge_triples 
                    (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ("query_test", subcategory, "part_of", category, f"turn_{i}", 
                      1.0, datetime.now().isoformat()))
            
            conn.commit()
        
        # Test complex queries
        complex_queries = [
            {
                "name": "hierarchical_join",
                "query": '''
                    SELECT e.subject, s.object, c.object 
                    FROM knowledge_triples e
                    JOIN knowledge_triples s ON e.object = s.subject
                    JOIN knowledge_triples c ON s.object = c.subject
                    WHERE e.relation = 'belongs_to' AND s.relation = 'part_of'
                    LIMIT 100
                '''
            },
            {
                "name": "confidence_aggregation",
                "query": '''
                    SELECT object, AVG(confidence), COUNT(*)
                    FROM knowledge_triples
                    WHERE relation = 'belongs_to'
                    GROUP BY object
                    HAVING COUNT(*) > 5
                    ORDER BY AVG(confidence) DESC
                    LIMIT 50
                '''
            },
            {
                "name": "temporal_analysis",
                "query": '''
                    SELECT DATE(created_at) as day, COUNT(*) as daily_count
                    FROM knowledge_triples
                    GROUP BY DATE(created_at)
                    ORDER BY day DESC
                '''
            },
            {
                "name": "relationship_paths",
                "query": '''
                    WITH RECURSIVE relationship_paths AS (
                        SELECT subject, object, relation, 1 as depth
                        FROM knowledge_triples
                        WHERE subject = 'entity_0'
                        
                        UNION ALL
                        
                        SELECT rp.subject, kt.object, kt.relation, rp.depth + 1
                        FROM relationship_paths rp
                        JOIN knowledge_triples kt ON rp.object = kt.subject
                        WHERE rp.depth < 3
                    )
                    SELECT * FROM relationship_paths ORDER BY depth, subject
                '''
            }
        ]
        
        query_results = []
        
        for query_info in complex_queries:
            start_time = time.time()
            try:
                with sqlite3.connect(test_db) as conn:
                    cursor = conn.execute(query_info["query"])
                    results = cursor.fetchall()
                
                query_time = time.time() - start_time
                query_results.append({
                    "query_name": query_info["name"],
                    "execution_time": query_time,
                    "result_count": len(results),
                    "success": True
                })
            except Exception as e:
                query_results.append({
                    "query_name": query_info["name"],
                    "execution_time": 0,
                    "result_count": 0,
                    "success": False,
                    "error": str(e)
                })
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "queries_tested": len(complex_queries),
            "successful_queries": sum(1 for r in query_results if r["success"]),
            "query_results": query_results
        }
    
    def _test_database_locking(self) -> Dict[str, Any]:
        """Test database locking under concurrent access"""
        test_db = "locking_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        kg = PersistentKG("lock_test", test_db)
        
        # Test concurrent read/write operations
        def reader_worker(worker_id):
            successful_reads = 0
            for i in range(50):
                try:
                    with sqlite3.connect(test_db) as conn:
                        cursor = conn.execute("SELECT COUNT(*) FROM knowledge_triples")
                        count = cursor.fetchone()[0]
                    successful_reads += 1
                    time.sleep(0.001)  # Small delay
                except Exception as e:
                    print(f"Reader {worker_id} error: {e}")
            return successful_reads
        
        def writer_worker(worker_id):
            successful_writes = 0
            for i in range(20):
                try:
                    with sqlite3.connect(test_db) as conn:
                        conn.execute('''
                            INSERT INTO knowledge_triples 
                            (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', ("lock_test", f"writer_{worker_id}_entity_{i}", "writes", 
                              f"data_{i}", f"turn_{worker_id}_{i}", 1.0, datetime.now().isoformat()))
                        conn.commit()
                    successful_writes += 1
                    time.sleep(0.005)  # Longer delay for writes
                except Exception as e:
                    print(f"Writer {worker_id} error: {e}")
            return successful_writes
        
        start_time = time.time()
        
        # Run concurrent readers and writers
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            # Start readers
            reader_futures = [executor.submit(reader_worker, i) for i in range(10)]
            # Start writers
            writer_futures = [executor.submit(writer_worker, i) for i in range(5)]
            
            # Collect results
            reader_results = [future.result() for future in reader_futures]
            writer_results = [future.result() for future in writer_futures]
        
        total_time = time.time() - start_time
        
        # Verify final state
        with sqlite3.connect(test_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM knowledge_triples")
            final_count = cursor.fetchone()[0]
        
        # Cleanup
        Path(test_db).unlink()
        
        return {
            "readers": 10,
            "writers": 5,
            "successful_reads": sum(reader_results),
            "successful_writes": sum(writer_results),
            "expected_writes": 5 * 20,
            "actual_final_count": final_count,
            "total_time": total_time
        }
    
    def _test_mocked_api_responses(self) -> Dict[str, Any]:
        """Test system with various mocked API responses"""
        test_db = "mocked_api_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        # Test different response scenarios
        response_scenarios = [
            {
                "name": "normal_response",
                "response": json.dumps({
                    "entities": ["test_entity"],
                    "relations": ["subject|relation|object"],
                    "key_concepts": ["concept"],
                    "context_updates": {"key": "value"}
                })
            },
            {
                "name": "empty_response",
                "response": json.dumps({
                    "entities": [],
                    "relations": [],
                    "key_concepts": [],
                    "context_updates": {}
                })
            },
            {
                "name": "large_response",
                "response": json.dumps({
                    "entities": [f"entity_{i}" for i in range(100)],
                    "relations": [f"subj_{i}|rel_{i}|obj_{i}" for i in range(50)],
                    "key_concepts": [f"concept_{i}" for i in range(25)],
                    "context_updates": {f"key_{i}": f"value_{i}" for i in range(20)}
                })
            }
        ]
        
        results = []
        
        for scenario in response_scenarios:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = scenario["response"]
            
            try:
                with patch('openai.OpenAI') as mock_openai:
                    mock_openai.return_value.chat.completions.create.return_value = mock_response
                    
                    kg = PersistentKG(f"mock_test_{scenario['name']}", test_db)
                    
                    # Test adding turns
                    turn_id = kg.add_turn("user", f"Test message for {scenario['name']}")
                    context = kg.get_relevant_context("test query")
                    summary = kg.get_conversation_summary()
                    
                    results.append({
                        "scenario": scenario["name"],
                        "success": True,
                        "turn_id": turn_id,
                        "context_has_data": len(context.get("raw_facts", [])) > 0
                    })
            except Exception as e:
                results.append({
                    "scenario": scenario["name"],
                    "success": False,
                    "error": str(e)
                })
        
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        return {
            "scenarios_tested": len(response_scenarios),
            "successful_scenarios": sum(1 for r in results if r["success"]),
            "results": results
        }
    
    def _test_api_error_handling(self) -> Dict[str, Any]:
        """Test API error handling scenarios"""
        test_db = "api_error_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        error_scenarios = [
            {"name": "network_timeout", "exception": Exception("Network timeout")},
            {"name": "rate_limit", "exception": Exception("Rate limit exceeded")},
            {"name": "invalid_response", "exception": json.JSONDecodeError("Invalid JSON", "", 0)},
            {"name": "auth_error", "exception": Exception("Authentication failed")}
        ]
        
        results = []
        
        for scenario in error_scenarios:
            try:
                with patch('openai.OpenAI') as mock_openai:
                    mock_openai.return_value.chat.completions.create.side_effect = scenario["exception"]
                    
                    kg = PersistentKG(f"error_test_{scenario['name']}", test_db)
                    
                    # System should handle the error gracefully
                    turn_id = kg.add_turn("user", f"Test message for {scenario['name']}")
                    
                    # Basic operations should still work
                    summary = kg.get_conversation_summary()
                    
                    results.append({
                        "scenario": scenario["name"],
                        "handled_gracefully": True,
                        "turn_created": turn_id is not None
                    })
            except Exception as e:
                results.append({
                    "scenario": scenario["name"],
                    "handled_gracefully": False,
                    "error": str(e)
                })
        
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        return {
            "error_scenarios_tested": len(error_scenarios),
            "gracefully_handled": sum(1 for r in results if r["handled_gracefully"]),
            "results": results
        }
    
    def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting behavior"""
        # This test simulates rate limiting scenarios
        call_count = {"value": 0}
        
        def rate_limited_call(*args, **kwargs):
            call_count["value"] += 1
            if call_count["value"] % 5 == 0:  # Every 5th call fails
                raise Exception("Rate limit exceeded")
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "entities": [f"entity_{call_count['value']}"],
                "relations": [f"subj_{call_count['value']}|rel|obj"],
                "key_concepts": ["concept"],
                "context_updates": {}
            })
            return mock_response
        
        test_db = "rate_limit_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        successful_calls = 0
        failed_calls = 0
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.side_effect = rate_limited_call
            
            kg = PersistentKG("rate_test", test_db)
            
            # Make many API calls
            for i in range(20):
                try:
                    turn_id = kg.add_turn("user", f"Message {i}")
                    successful_calls += 1
                except Exception as e:
                    failed_calls += 1
        
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        return {
            "total_attempts": 20,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "actual_api_calls": call_count["value"]
        }
    
    def _test_sustained_load(self) -> Dict[str, Any]:
        """Test sustained load over time"""
        # Mock OpenAI to avoid real API costs
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "entities": ["sustained_entity"],
            "relations": ["subject|relation|object"],
            "key_concepts": ["sustained_concept"],
            "context_updates": {}
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            manager = ConversationManager()
            
            # Run sustained load for 30 seconds
            start_time = time.time()
            end_time = start_time + 30  # 30 seconds
            
            operations_completed = 0
            errors = 0
            
            while time.time() < end_time:
                try:
                    conv_id = f"sustained_test_{operations_completed % 10}"  # Rotate conversations
                    result = manager.send_message(conv_id, f"Sustained message {operations_completed}")
                    operations_completed += 1
                except Exception as e:
                    errors += 1
                
                # Small delay to prevent overwhelming
                time.sleep(0.01)
            
            actual_duration = time.time() - start_time
        
        return {
            "target_duration_seconds": 30,
            "actual_duration_seconds": actual_duration,
            "operations_completed": operations_completed,
            "errors": errors,
            "operations_per_second": operations_completed / actual_duration if actual_duration > 0 else 0
        }
    
    def _test_burst_load(self) -> Dict[str, Any]:
        """Test burst load handling"""
        # Mock OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "entities": ["burst_entity"],
            "relations": ["subject|relation|object"],
            "key_concepts": ["burst_concept"],
            "context_updates": {}
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            manager = ConversationManager()
            
            # Create burst of concurrent operations
            num_operations = 200
            
            def burst_operation(op_id):
                try:
                    conv_id = f"burst_test_{op_id % 20}"  # 20 different conversations
                    result = manager.send_message(conv_id, f"Burst message {op_id}")
                    return {"success": True, "op_id": op_id}
                except Exception as e:
                    return {"success": False, "op_id": op_id, "error": str(e)}
            
            start_time = time.time()
            
            # Execute burst operations
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(burst_operation, i) for i in range(num_operations)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            burst_duration = time.time() - start_time
        
        successful_ops = sum(1 for r in results if r["success"])
        failed_ops = sum(1 for r in results if not r["success"])
        
        return {
            "total_operations": num_operations,
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "burst_duration_seconds": burst_duration,
            "operations_per_second": successful_ops / burst_duration if burst_duration > 0 else 0
        }
    
    def _test_system_limits(self) -> Dict[str, Any]:
        """Test system limits and boundaries"""
        limits_tested = []
        
        # Test maximum conversation ID length
        try:
            very_long_id = "a" * 10000
            manager = ConversationManager()
            conv = manager.get_conversation(very_long_id)
            limits_tested.append({"test": "long_conversation_id", "success": True})
        except Exception as e:
            limits_tested.append({"test": "long_conversation_id", "success": False, "error": str(e)})
        
        # Test maximum number of active conversations
        try:
            manager = ConversationManager()
            for i in range(1000):  # Try to create 1000 conversations
                conv = manager.get_conversation(f"limit_test_{i}")
            
            active_count = len(manager.list_conversations())
            limits_tested.append({
                "test": "max_active_conversations", 
                "success": True, 
                "active_count": active_count
            })
        except Exception as e:
            limits_tested.append({"test": "max_active_conversations", "success": False, "error": str(e)})
        
        # Test database with many tables (simulating many conversations)
        test_db = "limits_test.db"
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        try:
            # Create databases for many conversations
            for i in range(100):
                kg = PersistentKG(f"limits_test_{i}", test_db)
                kg._update_context_state({f"test_key_{i}": f"test_value_{i}"})
            
            limits_tested.append({"test": "many_conversation_contexts", "success": True})
        except Exception as e:
            limits_tested.append({"test": "many_conversation_contexts", "success": False, "error": str(e)})
        
        # Cleanup
        if Path(test_db).exists():
            Path(test_db).unlink()
        
        return {
            "limits_tested": len(limits_tested),
            "successful_tests": sum(1 for t in limits_tested if t["success"]),
            "test_results": limits_tested
        }
    
    def _generate_test_report(self, overall_duration: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        successful_tests = sum(1 for result in self.test_results if result.success)
        total_tests = len(self.test_results)
        
        # Calculate statistics
        durations = [result.duration for result in self.test_results]
        memory_changes = [result.memory_usage for result in self.test_results]
        
        # Group by test category (inferred from test name)
        categories = {}
        for result in self.test_results:
            category = result.test_name.split(" ")[0] if " " in result.test_name else "Other"
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        category_stats = {}
        for category, results in categories.items():
            category_stats[category] = {
                "total_tests": len(results),
                "successful": sum(1 for r in results if r.success),
                "avg_duration": sum(r.duration for r in results) / len(results),
                "total_memory_change": sum(r.memory_usage for r in results)
            }
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "overall_duration": overall_duration
            },
            "performance_stats": {
                "total_execution_time": sum(durations),
                "average_test_duration": sum(durations) / len(durations) if durations else 0,
                "longest_test_duration": max(durations) if durations else 0,
                "shortest_test_duration": min(durations) if durations else 0,
                "total_memory_change": sum(memory_changes),
                "average_memory_change": sum(memory_changes) / len(memory_changes) if memory_changes else 0
            },
            "category_breakdown": category_stats,
            "failed_tests": [
                {
                    "test_name": result.test_name,
                    "error_message": result.error_message,
                    "duration": result.duration,
                    "memory_usage": result.memory_usage
                }
                for result in self.test_results if not result.success
            ],
            "detailed_results": [
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "duration": result.duration,
                    "memory_usage": result.memory_usage,
                    "error_message": result.error_message,
                    "additional_data": result.additional_data
                }
                for result in self.test_results
            ],
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cpu_count": os.cpu_count(),
                "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024
            },
            "timestamp": datetime.now().isoformat()
        }

def run_basic_tests():
    """Run original basic tests for backward compatibility"""
    print("🧪 RUNNING BASIC SYSTEM TESTS")
    print("=" * 50)
    
    try:
        test_db = test_database_creation()
        test_knowledge_storage(test_db)
        test_conversation_summary(test_db)
        
        print("\n✅ ALL BASIC TESTS PASSED!")
        print("System is ready for use with OpenAI API")
        
        # Cleanup
        Path(test_db).unlink()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ConvoTree Test Suite")
    parser.add_argument("--mode", choices=["basic", "stress", "all"], default="basic",
                       help="Test mode to run (default: basic)")
    parser.add_argument("--mock-api", action="store_true", default=True,
                       help="Use mocked OpenAI API (default: True)")
    
    args = parser.parse_args()
    
    if args.mode == "basic":
        run_basic_tests()
    elif args.mode == "stress":
        suite = StressTestSuite()
        suite.mock_openai = args.mock_api
        report = suite.run_all_tests()
        
        print("\n" + "=" * 60)
        print("📊 STRESS TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Successful: {report['test_summary']['successful_tests']}")
        print(f"Failed: {report['test_summary']['failed_tests']}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print(f"Total Duration: {report['test_summary']['overall_duration']:.2f}s")
        
        if report['test_summary']['failed_tests'] > 0:
            print("\n❌ FAILED TESTS:")
            for failed in report['failed_tests']:
                print(f"  • {failed['test_name']}: {failed['error_message']}")
    else:  # all
        # Run basic tests first
        run_basic_tests()
        
        # Then run stress tests
        print("\n" + "=" * 60)
        print("🚀 PROCEEDING TO STRESS TESTS")
        print("=" * 60)
        
        suite = StressTestSuite()
        suite.mock_openai = args.mock_api
        report = suite.run_all_tests()