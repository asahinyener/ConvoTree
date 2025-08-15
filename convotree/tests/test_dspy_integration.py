#!/usr/bin/env python3
"""
Test Suite for DSPy Integration with ConvoTree
Tests the prompt optimization and versioning capabilities
"""

import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

from universal_memory_interface import create_universal_memory, UniversalFact, FactType
from dspy_integration import (
    DSPyConvoTreeEngine,
    PromptVersioningSystem,
    KnowledgeGraphInsights,
    OptimizationTarget,
    OptimizationOpportunity,
    PromptVersion,
    create_dspy_convotree_engine
)


def test_knowledge_graph_insights():
    """Test knowledge graph insights extraction"""
    print("🧪 Testing Knowledge Graph Insights...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create UMI with some test data
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        
        # Add some facts to analyze
        facts = [
            UniversalFact.create(
                content="User enjoys data analysis and visualization",
                fact_type=FactType.PREFERENCE,
                provider="test",
                session_id="session1",
                confidence=0.9,
                entities=["data analysis", "visualization"],
                tags=["analytics", "skills"]
            ),
            UniversalFact.create(
                content="User has experience with Python programming",
                fact_type=FactType.KNOWLEDGE,
                provider="test",
                session_id="session1",
                confidence=0.8,
                entities=["Python", "programming"],
                tags=["programming", "expertise"]
            )
        ]
        
        umi.store_knowledge(facts, "session1")
        
        # Test insights extraction
        insights = KnowledgeGraphInsights(umi)
        
        # Test fact extraction pattern analysis
        extraction_patterns = insights.analyze_fact_extraction_patterns()
        assert isinstance(extraction_patterns, dict), "Extraction patterns should be a dictionary"
        assert 'high_confidence_domains' in extraction_patterns, "Should identify high confidence domains"
        
        # Test user interaction pattern analysis
        interaction_patterns = insights.analyze_user_interaction_patterns()
        assert isinstance(interaction_patterns, dict), "Interaction patterns should be a dictionary"
        
        # Test optimization opportunity detection
        opportunities = insights.detect_optimization_opportunities()
        assert isinstance(opportunities, list), "Should return list of opportunities"
        
        print(f"  ✅ Found {len(extraction_patterns['high_confidence_domains'])} domains")
        print(f"  ✅ Detected {len(opportunities)} optimization opportunities")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_prompt_versioning_system():
    """Test prompt version management"""
    print("🧪 Testing Prompt Versioning System...")
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        version_file = tmp.name
    
    try:
        versioning = PromptVersioningSystem(version_file)
        
        # Test creating versions
        version1 = versioning.create_version(
            prompt_template="Extract facts from: {context}",
            signature_name="ExtractFacts",
            knowledge_insights={"domain": "test"}
        )
        
        assert version1.version_id is not None, "Version should have ID"
        assert version1.signature_name == "ExtractFacts", "Signature name should match"
        
        # Test activating version
        success = versioning.activate_version(version1.version_id)
        assert success, "Should successfully activate version"
        
        # Test getting active version
        active = versioning.get_active_version("ExtractFacts")
        assert active is not None, "Should return active version"
        assert active.version_id == version1.version_id, "Should return correct active version"
        
        # Test creating child version
        version2 = versioning.create_version(
            prompt_template="Extract detailed facts from: {context} with reasoning",
            signature_name="ExtractFacts",
            knowledge_insights={"domain": "test", "improvement": "added_reasoning"},
            parent_version_id=version1.version_id
        )
        
        assert version2.parent_version_id == version1.version_id, "Should track parent version"
        
        # Test evaluation
        eval_result = versioning.evaluate_version(
            version2.version_id,
            {"accuracy": 0.85, "relevance": 0.78}
        )
        
        assert eval_result.version_id == version2.version_id, "Evaluation should match version"
        assert eval_result.metrics["accuracy"] == 0.85, "Should store metrics correctly"
        
        # Test comparison
        versioning.activate_version(version2.version_id)
        versioning.evaluate_version(version1.version_id, {"accuracy": 0.75, "relevance": 0.70})
        
        comparison = versioning.compare_versions(version1.version_id, version2.version_id)
        assert "metric_comparison" in comparison, "Should provide metric comparison"
        assert comparison["metric_comparison"]["accuracy"]["improvement_percent"] > 0, "Should show improvement"
        
        # Test rollback
        rollback_success = versioning.rollback_version("ExtractFacts")
        assert rollback_success, "Should successfully rollback"
        
        active_after_rollback = versioning.get_active_version("ExtractFacts")
        assert active_after_rollback.version_id == version1.version_id, "Should rollback to parent"
        
        # Test version history
        history = versioning.get_version_history("ExtractFacts")
        assert len(history) == 2, "Should have 2 versions in history"
        
        print(f"  ✅ Created and managed {len(history)} prompt versions")
        print(f"  ✅ Version comparison showed {comparison['metric_comparison']['accuracy']['improvement_percent']:.1f}% improvement")
        
        return True
        
    finally:
        Path(version_file).unlink(missing_ok=True)


def test_dspy_engine_initialization():
    """Test DSPy engine initialization and setup"""
    print("🧪 Testing DSPy Engine Initialization...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create UMI
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        
        # Create engine
        engine = create_dspy_convotree_engine(umi)
        
        assert engine.memory is not None, "Engine should have memory interface"
        assert engine.versioning is not None, "Engine should have versioning system"
        assert engine.kg_insights is not None, "Engine should have KG insights"
        
        # Test that engine can identify optimization opportunities
        opportunities = engine.identify_optimization_opportunities()
        assert isinstance(opportunities, list), "Should return list of opportunities"
        
        print(f"  ✅ Engine initialized with {len(opportunities)} optimization opportunities")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_fact_extraction_optimization():
    """Test optimized fact extraction"""
    print("🧪 Testing Optimized Fact Extraction...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create UMI with test data
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        
        # Add some context
        facts = [
            UniversalFact.create(
                content="User is a software engineer",
                fact_type=FactType.PERSONAL,
                provider="test",
                session_id="session1",
                entities=["software engineer"],
                tags=["profession"]
            )
        ]
        umi.store_knowledge(facts, "session1")
        
        # Create engine
        engine = create_dspy_convotree_engine(umi)
        
        # Test fact extraction
        result = engine.extract_facts_optimized(
            conversation_context="I've been working on a new Python project for data visualization",
            user_profile={"domains": ["programming", "data"]}
        )
        
        assert isinstance(result, dict), "Should return dictionary result"
        assert "success" in result, "Should include success status"
        
        # Should work even without DSPy (fallback mode)
        if not result["success"]:
            assert "fallback_facts" in result, "Should provide fallback facts"
        
        print(f"  ✅ Fact extraction completed successfully: {result['success']}")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_context_synthesis_optimization():
    """Test optimized context synthesis"""
    print("🧪 Testing Optimized Context Synthesis...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create UMI with test data
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        engine = create_dspy_convotree_engine(umi)
        
        # Test context synthesis
        result = engine.synthesize_context_optimized(
            user_query="What should I learn next in programming?",
            relevant_facts=[
                {"content": "User knows Python", "confidence": 0.9},
                {"content": "User interested in web development", "confidence": 0.7}
            ],
            user_patterns={"learning_style": "hands_on", "preferred_depth": "detailed"}
        )
        
        assert isinstance(result, dict), "Should return dictionary result"
        assert "success" in result, "Should include success status"
        
        print(f"  ✅ Context synthesis completed: {result['success']}")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_response_generation_optimization():
    """Test optimized response generation"""
    print("🧪 Testing Optimized Response Generation...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        engine = create_dspy_convotree_engine(umi)
        
        # Test response generation
        result = engine.generate_response_optimized(
            user_input="I want to improve my Python skills",
            synthesized_context="User has basic Python knowledge and prefers practical learning",
            conversation_style={"tone": "helpful", "detail_level": "medium"}
        )
        
        assert isinstance(result, dict), "Should return dictionary result"
        assert "success" in result, "Should include success status"
        
        print(f"  ✅ Response generation completed: {result['success']}")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_optimization_opportunity_creation():
    """Test creation of optimized prompts for opportunities"""
    print("🧪 Testing Optimization Opportunity Creation...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp2:
        version_file = tmp2.name
    
    try:
        # Create UMI with some data
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        
        facts = [
            UniversalFact.create(
                content="User prefers detailed explanations",
                fact_type=FactType.PREFERENCE,
                provider="test",
                session_id="session1",
                entities=["explanations"],
                tags=["communication"]
            )
        ]
        umi.store_knowledge(facts, "session1")
        
        # Create engine with specific versioning file
        versioning = PromptVersioningSystem(version_file)
        engine = DSPyConvoTreeEngine(umi, versioning)
        
        # Get optimization opportunities
        opportunities = engine.identify_optimization_opportunities()
        assert len(opportunities) > 0, "Should find optimization opportunities"
        
        # Test optimizing for an opportunity
        opp = opportunities[0]
        new_version = engine.optimize_for_opportunity(opp)
        
        assert new_version is not None, "Should create new optimized version"
        assert new_version.signature_name is not None, "Should have signature name"
        assert len(new_version.prompt_template) > 0, "Should have prompt template"
        assert opp.knowledge_insights == new_version.knowledge_context, "Should include insights"
        
        print(f"  ✅ Created optimized version for {opp.target_metric.value}")
        print(f"  ✅ Prompt template length: {len(new_version.prompt_template)} characters")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(version_file).unlink(missing_ok=True)


def test_system_integration():
    """Test integration between all components"""
    print("🧪 Testing System Integration...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp2:
        version_file = tmp2.name
    
    try:
        # Create full system
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        versioning = PromptVersioningSystem(version_file)
        engine = DSPyConvoTreeEngine(umi, versioning)
        
        # Add knowledge to UMI
        facts = [
            UniversalFact.create(
                content="User is learning machine learning",
                fact_type=FactType.PERSONAL,
                provider="test",
                session_id="session1",
                entities=["machine learning"],
                tags=["learning", "AI"]
            ),
            UniversalFact.create(
                content="User prefers step-by-step tutorials",
                fact_type=FactType.PREFERENCE,
                provider="test", 
                session_id="session1",
                entities=["tutorials"],
                tags=["learning_style"]
            )
        ]
        umi.store_knowledge(facts, "session1")
        
        # Test full pipeline
        # 1. Identify opportunities
        opportunities = engine.identify_optimization_opportunities()
        assert len(opportunities) > 0, "Should identify opportunities"
        
        # 2. Create optimized version
        if opportunities:
            new_version = engine.optimize_for_opportunity(opportunities[0])
            assert new_version is not None, "Should create optimized version"
            
            # 3. Activate version
            activated = versioning.activate_version(new_version.version_id)
            assert activated, "Should activate new version"
            
            # 4. Test optimized extraction
            profile = umi.get_user_profile()
            user_profile_dict = profile.to_dict() if profile else {}
            
            extraction_result = engine.extract_facts_optimized(
                conversation_context="I'm struggling with understanding neural networks",
                user_profile=user_profile_dict
            )
            assert extraction_result["success"] or "fallback_facts" in extraction_result, "Should provide extraction result"
        
        print(f"  ✅ Full system integration test completed")
        print(f"  ✅ Processed {len(opportunities)} optimization opportunities")
        print(f"  ✅ System working end-to-end")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(version_file).unlink(missing_ok=True)


def test_performance_with_large_knowledge_base():
    """Test performance with larger knowledge base"""
    print("🧪 Testing Performance with Large Knowledge Base...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create UMI with larger dataset
        umi = create_universal_memory("sqlite", {"db_path": db_path}, "test_user")
        
        # Generate diverse facts
        domains = ["technology", "science", "art", "sports", "cooking"]
        fact_types = [FactType.PERSONAL, FactType.PREFERENCE, FactType.KNOWLEDGE, FactType.GOAL]
        
        all_facts = []
        for i in range(50):  # Create 50 facts
            domain = domains[i % len(domains)]
            fact_type = fact_types[i % len(fact_types)]
            
            fact = UniversalFact.create(
                content=f"User has experience with {domain} topic {i}",
                fact_type=fact_type,
                provider="test",
                session_id=f"session_{i//10}",
                entities=[domain, f"topic_{i}"],
                tags=[domain, "experience"]
            )
            all_facts.append(fact)
        
        # Store facts in batches
        for i in range(0, len(all_facts), 10):
            batch = all_facts[i:i+10]
            session_id = f"session_{i//10}"
            umi.store_knowledge(batch, session_id)
        
        # Test engine performance with large KB
        engine = create_dspy_convotree_engine(umi)
        
        import time
        start_time = time.time()
        
        # Test insights extraction
        insights = engine.kg_insights.analyze_fact_extraction_patterns()
        insights_time = time.time() - start_time
        
        # Test optimization opportunities
        start_time = time.time()
        opportunities = engine.identify_optimization_opportunities()
        opp_time = time.time() - start_time
        
        # Test fact extraction
        start_time = time.time()
        extraction_result = engine.extract_facts_optimized(
            conversation_context="Tell me about technology and science",
            user_profile={"domains": ["technology", "science"]}
        )
        extraction_time = time.time() - start_time
        
        # Performance assertions
        assert insights_time < 5.0, f"Insights extraction too slow: {insights_time:.2f}s"
        assert opp_time < 3.0, f"Opportunity detection too slow: {opp_time:.2f}s"
        assert extraction_time < 2.0, f"Fact extraction too slow: {extraction_time:.2f}s"
        
        print(f"  ✅ Performance with 50 facts:")
        print(f"    - Insights extraction: {insights_time:.3f}s")
        print(f"    - Opportunity detection: {opp_time:.3f}s")
        print(f"    - Fact extraction: {extraction_time:.3f}s")
        print(f"  ✅ All operations completed within performance thresholds")
        
        return True
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def run_dspy_integration_tests():
    """Run complete DSPy integration test suite"""
    print("🧠 DSPy Integration Test Suite for ConvoTree")
    print("=" * 60)
    
    tests = [
        test_knowledge_graph_insights,
        test_prompt_versioning_system,
        test_dspy_engine_initialization,
        test_fact_extraction_optimization,
        test_context_synthesis_optimization,
        test_response_generation_optimization,
        test_optimization_opportunity_creation,
        test_system_integration,
        test_performance_with_large_knowledge_base
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test failed with error: {e}")
            failed += 1
        except AssertionError as e:
            print(f"  ❌ Assertion failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 DSPy Integration Test Results: {passed}/{len(tests)} passed")
    
    if failed == 0:
        print("🎉 All DSPy integration tests passed!")
        print("✅ System ready for prompt optimization")
        return True
    else:
        print(f"⚠️ {failed} tests failed")
        return False


if __name__ == "__main__":
    success = run_dspy_integration_tests()
    exit(0 if success else 1)