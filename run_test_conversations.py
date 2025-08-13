#!/usr/bin/env python3
"""
Automated Test Conversation Runner
Executes the predefined test conversations and records the results
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import dotenv

# Load environment variables
dotenv.load_dotenv()

from enhanced_chat import EnhancedChatSystem, ConversationManager

class AutomatedTestRunner:
    """Runs automated test conversations and records detailed metrics"""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.test_results = []
    
    def run_test_conversation_1(self):
        """Execute Test Conversation 1: Memory & Knowledge Building"""
        print("🧪 Starting Test Conversation 1: Memory & Knowledge Building")
        
        # Create conversation
        conv_id = f"memory_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chat = self.conversation_manager.get_conversation(conv_id)
        
        # Test conversation flow
        test_messages = [
            "Hi, I'm Sarah. I'm a software engineer working at TechCorp in San Francisco.",
            "I'm working on a Python web scraping project for analyzing e-commerce data.",
            "My favorite programming languages are Python and JavaScript. I prefer React for frontend work.",
            "I have a meeting with my manager John tomorrow at 2 PM to discuss the project timeline.",
            "What do you know about me so far?",
            "I'm also learning machine learning in my spare time. I'm particularly interested in NLP and computer vision.",
            "My project deadline is next Friday. I'm a bit stressed about finishing the data pipeline in time.",
            "Can you remind me what I told you about my meeting tomorrow?",
            "I live in the Mission District and usually take the BART to work.",
            "What would you suggest for my Python web scraping project based on what I've told you?"
        ]
        
        # Execute conversation with detailed recording
        conversation_record = {
            "test_name": "Memory & Knowledge Building",
            "conversation_id": conv_id,
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "performance_metrics": {}
        }
        
        knowledge_before = len(chat.kg._get_recent_knowledge(1000))
        
        for i, message in enumerate(test_messages, 1):
            print(f"  {i}/10: {message[:50]}...")
            
            start_time = time.time()
            
            # Capture pre-message state
            pre_knowledge = chat.kg._get_recent_knowledge(1000)
            pre_context = chat.kg._get_context_state()
            
            try:
                # Send message
                result = chat.process_message(message)
                response_time = time.time() - start_time
                
                # Capture post-message state
                post_knowledge = chat.kg._get_recent_knowledge(1000)
                post_context = chat.kg._get_context_state()
                new_knowledge = [k for k in post_knowledge if k not in pre_knowledge]
                
                # Record interaction
                interaction_data = {
                    "turn": i,
                    "user_input": message,
                    "assistant_response": result['response'],
                    "response_time": response_time,
                    "knowledge_before_count": len(pre_knowledge),
                    "knowledge_after_count": len(post_knowledge),
                    "new_knowledge": new_knowledge,
                    "context_before": pre_context,
                    "context_after": post_context,
                    "context_used": result.get('context_used', {}),
                    "timestamp": datetime.now().isoformat()
                }
                
                conversation_record["interactions"].append(interaction_data)
                
                print(f"    ✅ Response: {response_time:.2f}s, Knowledge: +{len(new_knowledge)}")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                interaction_data = {
                    "turn": i,
                    "user_input": message,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                conversation_record["interactions"].append(interaction_data)
        
        # Calculate final metrics
        knowledge_after = len(chat.kg._get_recent_knowledge(1000))
        conversation_record["performance_metrics"] = {
            "total_interactions": len(test_messages),
            "successful_interactions": len([i for i in conversation_record["interactions"] if "error" not in i]),
            "knowledge_growth": knowledge_after - knowledge_before,
            "avg_response_time": sum(i.get("response_time", 0) for i in conversation_record["interactions"]) / len(conversation_record["interactions"]),
            "total_new_facts": sum(len(i.get("new_knowledge", [])) for i in conversation_record["interactions"])
        }
        
        conversation_record["end_time"] = datetime.now().isoformat()
        
        # Save conversation summary
        conversation_record["final_summary"] = chat.kg.get_conversation_summary()
        
        return conversation_record
    
    def run_test_conversation_2(self):
        """Execute Test Conversation 2: Complex Reasoning & Context"""
        print("🧪 Starting Test Conversation 2: Complex Reasoning & Context")
        
        # Create conversation
        conv_id = f"reasoning_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chat = self.conversation_manager.get_conversation(conv_id)
        
        # Test conversation flow
        test_messages = [
            "I'm debugging a performance issue in my React application. The initial page load takes 8 seconds.",
            "The app has a large dashboard with 20+ data visualization components. Each component makes its own API call.",
            "My bundle size is currently 2.5MB. I'm using Chart.js, Moment.js, and several other heavy libraries.",
            "What do you think is causing the performance issue?",
            "I tried code splitting but it didn't help much. The dashboard still loads slowly.",
            "Let me switch topics - do you know any good techniques for React optimization?",
            "Going back to my specific issue - I just realized all 20 API calls happen simultaneously on page load.",
            "The API calls are fetching different types of data: user analytics, sales metrics, inventory levels, and performance KPIs.",
            "Each API call takes about 200-500ms. Since they're all parallel, what's causing the 8-second delay?",
            "Wait, I think the issue might be that the components are re-rendering constantly. How can I check this?",
            "You were right about re-rendering. I see thousands of unnecessary renders. What's the best way to fix this?",
            "After implementing React.memo and optimizing renders, my load time dropped to 1.2 seconds! What should I tackle next?"
        ]
        
        # Execute conversation with detailed recording
        conversation_record = {
            "test_name": "Complex Reasoning & Context",
            "conversation_id": conv_id,
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "performance_metrics": {}
        }
        
        knowledge_before = len(chat.kg._get_recent_knowledge(1000))
        
        for i, message in enumerate(test_messages, 1):
            print(f"  {i}/12: {message[:50]}...")
            
            start_time = time.time()
            
            # Capture pre-message state
            pre_knowledge = chat.kg._get_recent_knowledge(1000)
            pre_context = chat.kg._get_context_state()
            
            try:
                # Send message
                result = chat.process_message(message)
                response_time = time.time() - start_time
                
                # Capture post-message state
                post_knowledge = chat.kg._get_recent_knowledge(1000)
                post_context = chat.kg._get_context_state()
                new_knowledge = [k for k in post_knowledge if k not in pre_knowledge]
                
                # Record interaction
                interaction_data = {
                    "turn": i,
                    "user_input": message,
                    "assistant_response": result['response'],
                    "response_time": response_time,
                    "knowledge_before_count": len(pre_knowledge),
                    "knowledge_after_count": len(post_knowledge),
                    "new_knowledge": new_knowledge,
                    "context_before": pre_context,
                    "context_after": post_context,
                    "context_used": result.get('context_used', {}),
                    "timestamp": datetime.now().isoformat()
                }
                
                conversation_record["interactions"].append(interaction_data)
                
                print(f"    ✅ Response: {response_time:.2f}s, Knowledge: +{len(new_knowledge)}")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                interaction_data = {
                    "turn": i,
                    "user_input": message,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                conversation_record["interactions"].append(interaction_data)
        
        # Calculate final metrics
        knowledge_after = len(chat.kg._get_recent_knowledge(1000))
        conversation_record["performance_metrics"] = {
            "total_interactions": len(test_messages),
            "successful_interactions": len([i for i in conversation_record["interactions"] if "error" not in i]),
            "knowledge_growth": knowledge_after - knowledge_before,
            "avg_response_time": sum(i.get("response_time", 0) for i in conversation_record["interactions"]) / len(conversation_record["interactions"]),
            "total_new_facts": sum(len(i.get("new_knowledge", [])) for i in conversation_record["interactions"])
        }
        
        conversation_record["end_time"] = datetime.now().isoformat()
        
        # Save conversation summary
        conversation_record["final_summary"] = chat.kg.get_conversation_summary()
        
        return conversation_record
    
    def analyze_results(self, test1_results, test2_results):
        """Analyze and compare test results"""
        
        analysis = {
            "test_execution_time": datetime.now().isoformat(),
            "test1_analysis": self._analyze_single_test(test1_results),
            "test2_analysis": self._analyze_single_test(test2_results),
            "comparative_analysis": self._compare_tests(test1_results, test2_results)
        }
        
        return analysis
    
    def _analyze_single_test(self, test_results):
        """Analyze a single test conversation"""
        interactions = test_results["interactions"]
        metrics = test_results["performance_metrics"]
        
        # Response time analysis
        response_times = [i.get("response_time", 0) for i in interactions if "response_time" in i]
        
        # Knowledge analysis
        knowledge_per_turn = [len(i.get("new_knowledge", [])) for i in interactions]
        
        # Context usage analysis
        context_usage = [i.get("context_used", {}) for i in interactions]
        facts_used = [ctx.get("relevant_facts_count", 0) for ctx in context_usage]
        
        return {
            "performance": {
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "response_time_trend": response_times
            },
            "knowledge": {
                "total_facts_added": sum(knowledge_per_turn),
                "avg_facts_per_turn": sum(knowledge_per_turn) / len(knowledge_per_turn) if knowledge_per_turn else 0,
                "knowledge_growth_trend": knowledge_per_turn
            },
            "context": {
                "avg_facts_used": sum(facts_used) / len(facts_used) if facts_used else 0,
                "total_facts_used": sum(facts_used),
                "context_usage_trend": facts_used
            },
            "quality_metrics": {
                "successful_interactions": metrics["successful_interactions"],
                "success_rate": metrics["successful_interactions"] / metrics["total_interactions"] * 100,
                "knowledge_efficiency": metrics["total_new_facts"] / metrics["total_interactions"]
            }
        }
    
    def _compare_tests(self, test1, test2):
        """Compare the two test conversations"""
        t1_metrics = test1["performance_metrics"]
        t2_metrics = test2["performance_metrics"]
        
        return {
            "response_time_comparison": {
                "test1_avg": t1_metrics.get("avg_response_time", 0),
                "test2_avg": t2_metrics.get("avg_response_time", 0),
                "difference": t2_metrics.get("avg_response_time", 0) - t1_metrics.get("avg_response_time", 0)
            },
            "knowledge_growth_comparison": {
                "test1_growth": t1_metrics.get("knowledge_growth", 0),
                "test2_growth": t2_metrics.get("knowledge_growth", 0),
                "difference": t2_metrics.get("knowledge_growth", 0) - t1_metrics.get("knowledge_growth", 0)
            },
            "efficiency_comparison": {
                "test1_facts_per_interaction": t1_metrics.get("total_new_facts", 0) / t1_metrics.get("total_interactions", 1),
                "test2_facts_per_interaction": t2_metrics.get("total_new_facts", 0) / t2_metrics.get("total_interactions", 1)
            }
        }
    
    def run_all_tests(self):
        """Run all test conversations and generate comprehensive report"""
        print("🚀 Starting Automated Test Conversation Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run Test 1
        test1_results = self.run_test_conversation_1()
        
        print()
        
        # Run Test 2 
        test2_results = self.run_test_conversation_2()
        
        print()
        print("🔍 Analyzing results...")
        
        # Analyze results
        analysis = self.analyze_results(test1_results, test2_results)
        
        # Generate comprehensive report
        report = {
            "metadata": {
                "test_suite_version": "1.0",
                "execution_time": start_time.isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            },
            "test_conversations": {
                "test1": test1_results,
                "test2": test2_results
            },
            "analysis": analysis
        }
        
        # Save report
        report_filename = f"test_conversation_report_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📊 Report saved: {report_filename}")
        
        # Display summary
        self._display_summary(analysis)
        
        return report
    
    def _display_summary(self, analysis):
        """Display test summary to console"""
        print()
        print("📈 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        t1_analysis = analysis["test1_analysis"]
        t2_analysis = analysis["test2_analysis"]
        comparison = analysis["comparative_analysis"]
        
        print(f"Test 1 (Memory & Knowledge Building):")
        print(f"  ✅ Success Rate: {t1_analysis['quality_metrics']['success_rate']:.1f}%")
        print(f"  ⏱️  Avg Response Time: {t1_analysis['performance']['avg_response_time']:.2f}s")
        print(f"  🧠 Knowledge Growth: {t1_analysis['knowledge']['total_facts_added']} facts")
        print(f"  📚 Avg Facts Used: {t1_analysis['context']['avg_facts_used']:.1f}")
        
        print()
        print(f"Test 2 (Complex Reasoning & Context):")
        print(f"  ✅ Success Rate: {t2_analysis['quality_metrics']['success_rate']:.1f}%")
        print(f"  ⏱️  Avg Response Time: {t2_analysis['performance']['avg_response_time']:.2f}s")
        print(f"  🧠 Knowledge Growth: {t2_analysis['knowledge']['total_facts_added']} facts")
        print(f"  📚 Avg Facts Used: {t2_analysis['context']['avg_facts_used']:.1f}")
        
        print()
        print("🔄 Comparative Analysis:")
        print(f"  Response Time Difference: {comparison['response_time_comparison']['difference']:+.2f}s")
        print(f"  Knowledge Growth Difference: {comparison['knowledge_growth_comparison']['difference']:+d} facts")
        print(f"  Efficiency (Test1): {comparison['efficiency_comparison']['test1_facts_per_interaction']:.2f} facts/interaction")
        print(f"  Efficiency (Test2): {comparison['efficiency_comparison']['test2_facts_per_interaction']:.2f} facts/interaction")

def main():
    """Main execution function"""
    try:
        runner = AutomatedTestRunner()
        report = runner.run_all_tests()
        
        print()
        print("🎉 Test execution completed successfully!")
        return report
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()