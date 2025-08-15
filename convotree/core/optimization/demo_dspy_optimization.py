#!/usr/bin/env python3
"""
ConvoTree DSPy Optimization Demo
Demonstrates the prompt optimization and versioning capabilities
"""

import tempfile
from pathlib import Path
from universal_memory_interface import create_universal_memory, UniversalFact, FactType
from dspy_integration import create_dspy_convotree_engine


def demo_dspy_optimization_workflow():
    """Demonstrate the complete DSPy optimization workflow"""
    print("🧠 ConvoTree DSPy Optimization Demo")
    print("=" * 50)
    
    # Create temporary storage
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp2:
        version_file = tmp2.name
    
    try:
        print("\n📊 Step 1: Setting up Universal Memory with Knowledge")
        print("-" * 50)
        
        # Create Universal Memory Interface
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "demo_user")
        
        # Add diverse knowledge across multiple sessions
        knowledge_sessions = {
            "session_1": [
                UniversalFact.create(
                    content="User is a data scientist with 5 years experience",
                    fact_type=FactType.PERSONAL,
                    provider="initial_setup",
                    session_id="session_1",
                    confidence=0.9,
                    entities=["data scientist", "experience"],
                    tags=["profession", "expertise"]
                ),
                UniversalFact.create(
                    content="User prefers Python for data analysis over R",
                    fact_type=FactType.PREFERENCE,
                    provider="conversation",
                    session_id="session_1",
                    confidence=0.8,
                    entities=["Python", "R", "data analysis"],
                    tags=["programming", "tools"]
                )
            ],
            "session_2": [
                UniversalFact.create(
                    content="User is learning machine learning algorithms",
                    fact_type=FactType.GOAL,
                    provider="conversation",
                    session_id="session_2",
                    confidence=0.85,
                    entities=["machine learning", "algorithms"],
                    tags=["learning", "AI"]
                ),
                UniversalFact.create(
                    content="User has experience with neural networks and deep learning",
                    fact_type=FactType.KNOWLEDGE,
                    provider="conversation",
                    session_id="session_2",
                    confidence=0.9,
                    entities=["neural networks", "deep learning"],
                    tags=["AI", "expertise"]
                )
            ],
            "session_3": [
                UniversalFact.create(
                    content="User struggles with hyperparameter tuning",
                    fact_type=FactType.PERSONAL,
                    provider="conversation",
                    session_id="session_3",
                    confidence=0.7,
                    entities=["hyperparameter tuning"],
                    tags=["challenge", "learning"]
                )
            ]
        }
        
        # Store knowledge across sessions
        total_facts = 0
        for session_id, facts in knowledge_sessions.items():
            umi.store_knowledge(facts, session_id)
            total_facts += len(facts)
            print(f"  ✅ Stored {len(facts)} facts in {session_id}")
        
        print(f"  📈 Total knowledge base: {total_facts} facts across {len(knowledge_sessions)} sessions")
        
        print("\n🔧 Step 2: Initializing DSPy Optimization Engine")
        print("-" * 50)
        
        # Create DSPy ConvoTree Engine
        engine = create_dspy_convotree_engine(umi, version_file)
        print("  ✅ DSPy ConvoTree Engine initialized")
        print("  ✅ Prompt versioning system ready")
        print("  ✅ Knowledge graph insights analyzer ready")
        
        print("\n📊 Step 3: Analyzing Knowledge Graph for Optimization Insights")
        print("-" * 50)
        
        # Analyze knowledge patterns
        insights = engine.kg_insights.analyze_fact_extraction_patterns()
        print(f"  🎯 High confidence domains: {insights['high_confidence_domains']}")
        print(f"  📊 Domain distribution: {len(insights.get('domain_distribution', {}))}")
        
        interaction_patterns = engine.kg_insights.analyze_user_interaction_patterns()
        print(f"  👤 User interaction style: {interaction_patterns.get('preferred_response_styles', {})}")
        
        print("\n🔍 Step 4: Identifying Optimization Opportunities")
        print("-" * 50)
        
        # Identify optimization opportunities
        opportunities = engine.identify_optimization_opportunities()
        print(f"  🎯 Found {len(opportunities)} optimization opportunities:")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"    {i}. {opp.target_metric.value}")
            print(f"       Current: {opp.current_performance:.2f} → Target: {opp.current_performance + opp.target_improvement:.2f}")
            print(f"       Priority: {opp.priority_score:.1f}, Effort: {opp.estimated_effort}")
            print(f"       Suggestions: {', '.join(opp.suggested_changes[:2])}...")
        
        print("\n🚀 Step 5: Creating Optimized Prompt Versions")
        print("-" * 50)
        
        created_versions = []
        for opp in opportunities[:2]:  # Optimize top 2 opportunities
            print(f"  🔧 Optimizing for: {opp.target_metric.value}")
            
            # Create optimized version
            new_version = engine.optimize_for_opportunity(opp)
            created_versions.append(new_version)
            
            print(f"    ✅ Created version: {new_version.version_id[:8]}...")
            print(f"    📊 Prompt template length: {len(new_version.prompt_template)} characters")
            print(f"    🧠 Knowledge insights included: {len(new_version.knowledge_context)} keys")
            
            # Activate the new version
            engine.versioning.activate_version(new_version.version_id)
            print(f"    🎯 Activated version for {new_version.signature_name}")
        
        print("\n📈 Step 6: Testing Optimized Extraction Pipeline")
        print("-" * 50)
        
        # Test optimized fact extraction
        test_context = "I'm working on a new computer vision project using PyTorch. I need help with data augmentation techniques and model evaluation metrics."
        
        print(f"  📝 Test context: {test_context}")
        
        # Get user profile for context
        profile = umi.get_user_profile()
        user_profile_dict = profile.to_dict() if profile else {}
        
        # Test fact extraction
        extraction_result = engine.extract_facts_optimized(
            conversation_context=test_context,
            user_profile=user_profile_dict
        )
        
        print(f"  🧠 Fact extraction success: {extraction_result['success']}")
        print(f"  📊 Extracted facts: {len(extraction_result['extracted_facts'])}")
        
        # Test context synthesis
        context_result = engine.synthesize_context_optimized(
            user_query="Help me with computer vision project",
            relevant_facts=[{"content": "User prefers Python", "confidence": 0.8}],
            user_patterns=profile.interaction_style if profile else {}
        )
        
        print(f"  🔗 Context synthesis success: {context_result['success']}")
        
        # Test response generation
        response_result = engine.generate_response_optimized(
            user_input="What's the best approach for data augmentation?",
            synthesized_context=context_result['synthesized_context'],
            conversation_style={"tone": "helpful", "detail": "high"}
        )
        
        print(f"  💬 Response generation success: {response_result['success']}")
        print(f"  🎯 Response confidence: {response_result['confidence_score']}")
        
        print("\n📊 Step 7: Version Management and Analytics")
        print("-" * 50)
        
        # Show version history
        for signature in ["ExtractFacts", "SynthesizeContext"]:
            versions = engine.versioning.list_versions(signature)
            if versions:
                print(f"  📈 {signature}: {len(versions)} versions")
                active = engine.versioning.get_active_version(signature)
                if active:
                    print(f"    🎯 Active: {active.version_id[:8]}... (created: {active.created_at.strftime('%H:%M:%S')})")
        
        # Simulate version comparison
        if len(created_versions) >= 2:
            v1, v2 = created_versions[0], created_versions[1]
            
            # Add mock evaluation metrics
            engine.versioning.evaluate_version(v1.version_id, {
                "accuracy": 0.72, "relevance": 0.68, "efficiency": 0.85
            })
            engine.versioning.evaluate_version(v2.version_id, {
                "accuracy": 0.78, "relevance": 0.74, "efficiency": 0.82
            })
            
            comparison = engine.versioning.compare_versions(v1.version_id, v2.version_id)
            print(f"  📊 Version comparison:")
            print(f"    📈 Accuracy improvement: {comparison['metric_comparison']['accuracy']['improvement_percent']:.1f}%")
            print(f"    🎯 Recommendation: {comparison['recommendation']}")
        
        print("\n🎯 Step 8: Demonstration Summary")
        print("-" * 50)
        
        print("  ✅ Knowledge-informed prompt optimization workflow demonstrated")
        print(f"  📊 Analyzed {total_facts} facts across {len(knowledge_sessions)} sessions")
        print(f"  🎯 Identified {len(opportunities)} optimization opportunities")
        print(f"  🚀 Created {len(created_versions)} optimized prompt versions")
        print("  📈 Tested full pipeline: extraction → synthesis → generation")
        print("  🔧 Demonstrated version management and comparison")
        
        print(f"\n🧠 Architecture Benefits Demonstrated:")
        print("  • Knowledge graph insights inform prompt optimization")
        print("  • Versioned prompts enable A/B testing and rollback")
        print("  • Modular design allows integration with any LLM provider")
        print("  • Graceful degradation when DSPy is not available")
        print("  • Performance monitoring and continuous improvement")
        
        return True
        
    finally:
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
        Path(version_file).unlink(missing_ok=True)


def demo_optimization_scenarios():
    """Demonstrate different optimization scenarios"""
    print("\n🎭 Advanced Optimization Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Domain Expert User",
            "description": "User with deep expertise in specific domain",
            "facts": [
                ("User is a PhD in computational biology", FactType.PERSONAL),
                ("User prefers detailed technical explanations", FactType.PREFERENCE),
                ("User has 10+ years research experience", FactType.KNOWLEDGE)
            ],
            "optimization_focus": "Technical depth and precision"
        },
        {
            "name": "Learning Beginner",
            "description": "New user learning basics",
            "facts": [
                ("User is new to programming", FactType.PERSONAL),
                ("User prefers step-by-step explanations", FactType.PREFERENCE),
                ("User wants to learn web development", FactType.GOAL)
            ],
            "optimization_focus": "Clarity and gradual complexity"
        },
        {
            "name": "Cross-Domain Professional",
            "description": "User working across multiple domains",
            "facts": [
                ("User is both engineer and designer", FactType.PERSONAL),
                ("User values both technical and creative approaches", FactType.PREFERENCE),
                ("User leads cross-functional teams", FactType.KNOWLEDGE)
            ],
            "optimization_focus": "Balanced technical and creative insights"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n  Scenario {i}: {scenario['name']}")
        print(f"  🎯 Focus: {scenario['optimization_focus']}")
        print(f"  📊 Fact types: {len(scenario['facts'])} facts")
        print(f"  💡 Optimization strategy: Adapt prompts for {scenario['description'].lower()}")
    
    print("\n  🚀 Each scenario would generate different optimized prompts:")
    print("    • Expert: Technical terminology, assume background knowledge")
    print("    • Beginner: Simple language, more examples and explanations")
    print("    • Cross-domain: Bridge technical and creative perspectives")


if __name__ == "__main__":
    print("🌳 ConvoTree DSPy Integration Demonstration")
    print("Showcasing knowledge-informed prompt optimization")
    print("")
    
    success = demo_dspy_optimization_workflow()
    
    if success:
        demo_optimization_scenarios()
        
        print("\n" + "=" * 60)
        print("🎉 DSPy Integration Demo Completed Successfully!")
        print("✅ Architecture ready for real-world deployment")
        print("🚀 Next steps: Install DSPy and integrate with live LLM providers")
    else:
        print("❌ Demo failed")
        exit(1)