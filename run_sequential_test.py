#!/usr/bin/env python3
"""
Sequential Test Conversation Runner
Avoids database conflicts by using separate databases for each test
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

from enhanced_chat import EnhancedChatSystem

class SequentialTestRunner:
    """Runs test conversations sequentially with separate databases"""
    
    def run_memory_test(self):
        """Execute Memory & Knowledge Building Test"""
        print("🧪 Running Memory & Knowledge Building Test")
        
        # Use unique database for this test
        db_path = "test_memory.db"
        if Path(db_path).exists():
            Path(db_path).unlink()
        
        conv_id = "memory_test"
        chat = EnhancedChatSystem(conv_id, db_path)
        
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
        
        results = {"interactions": [], "test_name": "Memory Test"}
        
        for i, message in enumerate(test_messages, 1):
            print(f"  Turn {i}: {message[:60]}...")
            
            try:
                start_time = time.time()
                
                # Get knowledge before
                knowledge_before = chat.kg._get_recent_knowledge(100)
                context_before = chat.kg._get_context_state()
                
                # Process message
                result = chat.process_message(message)
                
                response_time = time.time() - start_time
                
                # Get knowledge after
                knowledge_after = chat.kg._get_recent_knowledge(100)
                context_after = chat.kg._get_context_state()
                new_knowledge = [k for k in knowledge_after if k not in knowledge_before]
                
                interaction = {
                    "turn": i,
                    "user_input": message,
                    "assistant_response": result['response'],
                    "response_time": response_time,
                    "knowledge_added": len(new_knowledge),
                    "new_facts": new_knowledge,
                    "total_knowledge": len(knowledge_after),
                    "context_facts_used": result.get('context_used', {}).get('relevant_facts_count', 0),
                    "success": True
                }
                
                results["interactions"].append(interaction)
                
                print(f"    ✅ {response_time:.2f}s, +{len(new_knowledge)} facts, Total: {len(knowledge_after)}")
                print(f"    📝 Response preview: {result['response'][:100]}...")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                import traceback
                print(f"    📍 Full traceback:")
                traceback.print_exc()
                results["interactions"].append({
                    "turn": i,
                    "user_input": message,
                    "error": str(e),
                    "success": False
                })
                # FAIL EARLY - stop on first error for faster iteration
                print(f"\n🚨 FAILING EARLY at turn {i} for faster debugging")
                break
        
        # Get final summary
        try:
            final_summary = chat.kg.get_conversation_summary()
            results["final_summary"] = final_summary
        except Exception as e:
            results["final_summary"] = {"error": str(e)}
        
        return results
    
    def run_reasoning_test(self):
        """Execute Complex Reasoning & Context Test"""
        print("\n🧪 Running Complex Reasoning & Context Test")
        
        # Use unique database for this test
        db_path = "test_reasoning.db"
        if Path(db_path).exists():
            Path(db_path).unlink()
        
        conv_id = "reasoning_test"
        chat = EnhancedChatSystem(conv_id, db_path)
        
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
        
        results = {"interactions": [], "test_name": "Reasoning Test"}
        
        for i, message in enumerate(test_messages, 1):
            print(f"  Turn {i}: {message[:60]}...")
            
            try:
                start_time = time.time()
                
                # Get knowledge before
                knowledge_before = chat.kg._get_recent_knowledge(100)
                context_before = chat.kg._get_context_state()
                
                # Process message
                result = chat.process_message(message)
                
                response_time = time.time() - start_time
                
                # Get knowledge after
                knowledge_after = chat.kg._get_recent_knowledge(100)
                context_after = chat.kg._get_context_state()
                new_knowledge = [k for k in knowledge_after if k not in knowledge_before]
                
                interaction = {
                    "turn": i,
                    "user_input": message,
                    "assistant_response": result['response'],
                    "response_time": response_time,
                    "knowledge_added": len(new_knowledge),
                    "new_facts": new_knowledge,
                    "total_knowledge": len(knowledge_after),
                    "context_facts_used": result.get('context_used', {}).get('relevant_facts_count', 0),
                    "success": True
                }
                
                results["interactions"].append(interaction)
                
                print(f"    ✅ {response_time:.2f}s, +{len(new_knowledge)} facts, Total: {len(knowledge_after)}")
                print(f"    📝 Response preview: {result['response'][:100]}...")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                import traceback
                print(f"    📍 Full traceback:")
                traceback.print_exc()
                results["interactions"].append({
                    "turn": i,
                    "user_input": message,
                    "error": str(e),
                    "success": False
                })
                # FAIL EARLY - stop on first error for faster iteration
                print(f"\n🚨 FAILING EARLY at turn {i} for faster debugging")
                break
        
        # Get final summary
        try:
            final_summary = chat.kg.get_conversation_summary()
            results["final_summary"] = final_summary
        except Exception as e:
            results["final_summary"] = {"error": str(e)}
        
        return results
    
    def analyze_results(self, memory_results, reasoning_results):
        """Analyze test results"""
        
        def analyze_test(test_results):
            interactions = test_results["interactions"]
            successful = [i for i in interactions if i.get("success", False)]
            
            if not successful:
                return {"error": "No successful interactions"}
            
            response_times = [i["response_time"] for i in successful]
            knowledge_added = [i["knowledge_added"] for i in successful]
            context_used = [i["context_facts_used"] for i in successful]
            
            return {
                "success_rate": len(successful) / len(interactions) * 100,
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "total_knowledge_added": sum(knowledge_added),
                "avg_knowledge_per_turn": sum(knowledge_added) / len(knowledge_added),
                "total_context_used": sum(context_used),
                "avg_context_per_turn": sum(context_used) / len(context_used),
                "final_knowledge_count": successful[-1]["total_knowledge"] if successful else 0
            }
        
        memory_analysis = analyze_test(memory_results)
        reasoning_analysis = analyze_test(reasoning_results)
        
        return {
            "memory_test": memory_analysis,
            "reasoning_test": reasoning_analysis,
            "comparison": {
                "knowledge_efficiency": {
                    "memory_test": memory_analysis.get("avg_knowledge_per_turn", 0),
                    "reasoning_test": reasoning_analysis.get("avg_knowledge_per_turn", 0)
                },
                "response_performance": {
                    "memory_test": memory_analysis.get("avg_response_time", 0),
                    "reasoning_test": reasoning_analysis.get("avg_response_time", 0)
                },
                "context_utilization": {
                    "memory_test": memory_analysis.get("avg_context_per_turn", 0),
                    "reasoning_test": reasoning_analysis.get("avg_context_per_turn", 0)
                }
            }
        }
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        print("🚀 Starting Sequential Test Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run tests
        memory_results = self.run_memory_test()
        reasoning_results = self.run_reasoning_test()
        
        # Analyze
        analysis = self.analyze_results(memory_results, reasoning_results)
        
        # Generate report
        report = {
            "metadata": {
                "test_type": "sequential",
                "execution_time": start_time.isoformat(),
                "duration": (datetime.now() - start_time).total_seconds()
            },
            "tests": {
                "memory_test": memory_results,
                "reasoning_test": reasoning_results
            },
            "analysis": analysis
        }
        
        # Save report
        report_file = f"sequential_test_report_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📊 Report saved: {report_file}")
        
        # Display results
        self.display_summary(analysis)
        
        return report
    
    def display_summary(self, analysis):
        """Display test summary"""
        print("\n📈 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        memory = analysis["memory_test"]
        reasoning = analysis["reasoning_test"]
        
        if "error" not in memory:
            print("🧠 Memory & Knowledge Building Test:")
            print(f"  ✅ Success Rate: {memory['success_rate']:.1f}%")
            print(f"  ⏱️  Avg Response Time: {memory['avg_response_time']:.2f}s")
            print(f"  📚 Total Knowledge Added: {memory['total_knowledge_added']} facts")
            print(f"  🎯 Knowledge Efficiency: {memory['avg_knowledge_per_turn']:.2f} facts/turn")
            print(f"  📖 Context Usage: {memory['avg_context_per_turn']:.1f} facts/turn")
            print(f"  📊 Final Knowledge Count: {memory['final_knowledge_count']}")
        else:
            print("🧠 Memory Test: ❌ Failed")
        
        print()
        
        if "error" not in reasoning:
            print("🔄 Complex Reasoning & Context Test:")
            print(f"  ✅ Success Rate: {reasoning['success_rate']:.1f}%")
            print(f"  ⏱️  Avg Response Time: {reasoning['avg_response_time']:.2f}s")
            print(f"  📚 Total Knowledge Added: {reasoning['total_knowledge_added']} facts")
            print(f"  🎯 Knowledge Efficiency: {reasoning['avg_knowledge_per_turn']:.2f} facts/turn")
            print(f"  📖 Context Usage: {reasoning['avg_context_per_turn']:.1f} facts/turn")
            print(f"  📊 Final Knowledge Count: {reasoning['final_knowledge_count']}")
        else:
            print("🔄 Reasoning Test: ❌ Failed")
        
        if "error" not in memory and "error" not in reasoning:
            print("\n🔍 Comparative Analysis:")
            comp = analysis["comparison"]
            print(f"  Knowledge Efficiency: Memory {comp['knowledge_efficiency']['memory_test']:.2f} vs Reasoning {comp['knowledge_efficiency']['reasoning_test']:.2f}")
            print(f"  Response Performance: Memory {comp['response_performance']['memory_test']:.2f}s vs Reasoning {comp['response_performance']['reasoning_test']:.2f}s")
            print(f"  Context Utilization: Memory {comp['context_utilization']['memory_test']:.1f} vs Reasoning {comp['context_utilization']['reasoning_test']:.1f}")

def main():
    """Main execution"""
    runner = SequentialTestRunner()
    return runner.run_full_test_suite()

if __name__ == "__main__":
    main()