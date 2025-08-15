#!/usr/bin/env python3
"""
DSPy Integration Layer for ConvoTree
Provides prompt optimization capabilities using DSPy with knowledge graph insights
"""

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
import hashlib

# DSPy imports (conditional - graceful degradation if not available)
try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    print("⚠️ DSPy not available - using mock implementations")

from ..memory.universal_memory_interface import UniversalMemoryInterface, UniversalFact, FactType


class OptimizationTarget(Enum):
    """Optimization targets for prompt improvement"""
    FACT_EXTRACTION_ACCURACY = "fact_extraction_accuracy"
    CONTEXTUAL_RELEVANCE = "contextual_relevance" 
    USER_ENGAGEMENT = "user_engagement"
    KNOWLEDGE_CONSISTENCY = "knowledge_consistency"
    RESPONSE_TIME_EFFICIENCY = "response_time_efficiency"
    COMPOSITE_SCORE = "composite_score"


@dataclass
class PromptVersion:
    """Versioned prompt with performance metrics and knowledge context"""
    version_id: str
    prompt_template: str
    signature_name: str
    performance_metrics: Dict[str, float]
    knowledge_context: Dict[str, Any]
    optimization_history: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    evaluation_results: Dict[str, Any] = field(default_factory=dict)
    a_b_test_results: Optional[Dict] = None
    is_active: bool = False
    parent_version_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptVersion':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class OptimizationOpportunity:
    """Represents an opportunity for prompt optimization"""
    opportunity_id: str
    target_metric: OptimizationTarget
    current_performance: float
    target_improvement: float
    knowledge_insights: Dict[str, Any]
    priority_score: float
    estimated_effort: str  # 'low', 'medium', 'high'
    suggested_changes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationResult:
    """Results from evaluating a prompt version"""
    version_id: str
    test_cases_count: int
    metrics: Dict[str, float]
    detailed_results: List[Dict]
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['evaluation_timestamp'] = self.evaluation_timestamp.isoformat()
        return data


class KnowledgeGraphInsights:
    """Extract optimization insights from Universal Memory Interface"""
    
    def __init__(self, memory_interface: UniversalMemoryInterface):
        self.memory = memory_interface
    
    def analyze_fact_extraction_patterns(self) -> Dict[str, Any]:
        """Analyze which extraction patterns work best for different domains"""
        # Get user profile to understand domains
        profile = self.memory.get_user_profile()
        if not profile:
            return {'high_confidence_domains': [], 'patterns': {}}
        
        # Analyze successful extractions by domain
        insights = {
            'high_confidence_domains': profile.knowledge_domains[:5],
            'extraction_success_patterns': self._analyze_successful_extractions(),
            'common_failure_modes': self._identify_failure_patterns(),
            'optimal_context_sizes': self._analyze_context_effectiveness(),
            'domain_distribution': self._analyze_domain_distribution()
        }
        
        return insights
    
    def analyze_user_interaction_patterns(self) -> Dict[str, Any]:
        """Analyze user response patterns to optimize conversation flow"""
        profile = self.memory.get_user_profile()
        if not profile:
            return {'patterns': {}}
        
        return {
            'preferred_response_styles': profile.interaction_style,
            'engagement_factors': self._analyze_engagement_patterns(),
            'knowledge_utilization_effectiveness': self._analyze_knowledge_usage(),
            'conversation_flow_patterns': self._analyze_conversation_flows()
        }
    
    def detect_optimization_opportunities(self) -> List[OptimizationOpportunity]:
        """Identify specific opportunities for prompt optimization"""
        opportunities = []
        
        # Analyze fact extraction accuracy
        fact_accuracy = self._estimate_fact_extraction_accuracy()
        if fact_accuracy < 0.8:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=str(uuid.uuid4()),
                target_metric=OptimizationTarget.FACT_EXTRACTION_ACCURACY,
                current_performance=fact_accuracy,
                target_improvement=0.15,
                knowledge_insights=self.analyze_fact_extraction_patterns(),
                priority_score=0.9,
                estimated_effort='medium',
                suggested_changes=[
                    'Improve context selection for fact extraction',
                    'Add domain-specific extraction patterns',
                    'Enhance confidence scoring mechanisms'
                ]
            ))
        
        # Analyze contextual relevance
        context_relevance = self._estimate_contextual_relevance()
        if context_relevance < 0.75:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=str(uuid.uuid4()),
                target_metric=OptimizationTarget.CONTEXTUAL_RELEVANCE,
                current_performance=context_relevance,
                target_improvement=0.20,
                knowledge_insights=self.analyze_user_interaction_patterns(),
                priority_score=0.8,
                estimated_effort='low',
                suggested_changes=[
                    'Optimize context synthesis algorithms',
                    'Improve relevance scoring',
                    'Better user pattern recognition'
                ]
            ))
        
        return opportunities
    
    def _analyze_successful_extractions(self) -> Dict[str, Any]:
        """Analyze patterns in successful fact extractions"""
        # This would analyze stored facts with high confidence scores
        return {
            'high_confidence_fact_types': ['PREFERENCE', 'KNOWLEDGE'],
            'effective_entity_patterns': ['noun_phrases', 'domain_terms'],
            'optimal_extraction_contexts': ['recent_interactions', 'domain_focused']
        }
    
    def _identify_failure_patterns(self) -> Dict[str, Any]:
        """Identify common failure modes in fact extraction"""
        return {
            'low_confidence_indicators': ['ambiguous_language', 'insufficient_context'],
            'extraction_failures': ['complex_sentences', 'implicit_information'],
            'contradiction_sources': ['temporal_inconsistency', 'source_unreliability']
        }
    
    def _analyze_context_effectiveness(self) -> Dict[str, Any]:
        """Analyze effectiveness of different context window sizes"""
        return {
            'optimal_context_size': 50,
            'context_quality_factors': ['recency', 'relevance', 'confidence'],
            'context_synthesis_patterns': ['chronological', 'relevance_based', 'domain_clustered']
        }
    
    def _analyze_domain_distribution(self) -> Dict[str, Any]:
        """Analyze distribution of knowledge across domains"""
        profile = self.memory.get_user_profile()
        if not profile:
            return {}
        
        return {
            'primary_domains': profile.knowledge_domains[:3],
            'domain_expertise_levels': {domain: 0.7 for domain in profile.knowledge_domains},
            'cross_domain_connections': self._identify_domain_connections()
        }
    
    def _analyze_engagement_patterns(self) -> Dict[str, Any]:
        """Analyze patterns that lead to higher user engagement"""
        return {
            'high_engagement_factors': ['personalized_responses', 'knowledge_utilization'],
            'low_engagement_indicators': ['generic_responses', 'ignored_context'],
            'optimal_response_length': 'medium',
            'preferred_information_density': 'high'
        }
    
    def _analyze_knowledge_usage(self) -> Dict[str, Any]:
        """Analyze how effectively existing knowledge is being utilized"""
        return {
            'knowledge_utilization_rate': 0.65,
            'unused_knowledge_percentage': 0.35,
            'knowledge_freshness_impact': 0.8,
            'cross_session_knowledge_transfer': 0.7
        }
    
    def _analyze_conversation_flows(self) -> Dict[str, Any]:
        """Analyze conversation flow patterns"""
        return {
            'successful_flow_patterns': ['context_building', 'knowledge_accumulation'],
            'conversation_coherence_score': 0.75,
            'topic_transition_effectiveness': 0.8,
            'memory_continuity_score': 0.85
        }
    
    def _estimate_fact_extraction_accuracy(self) -> float:
        """Estimate current fact extraction accuracy"""
        # This would use actual performance data in a real implementation
        # For now, return a simulated estimate
        return 0.72
    
    def _estimate_contextual_relevance(self) -> float:
        """Estimate current contextual relevance of responses"""
        return 0.68
    
    def _identify_domain_connections(self) -> Dict[str, List[str]]:
        """Identify connections between different knowledge domains"""
        return {
            'technology': ['programming', 'AI', 'software'],
            'learning': ['education', 'skill', 'development'],
            'work': ['career', 'profession', 'expertise']
        }


# DSPy Signatures (if DSPy is available)
if DSPY_AVAILABLE:
    class ExtractFacts(dspy.Signature):
        """Extract structured facts from conversation context using knowledge patterns"""
        
        conversation_context = dspy.InputField(desc="Recent conversation history")
        user_profile = dspy.InputField(desc="User's accumulated knowledge profile")
        domain_patterns = dspy.InputField(desc="Domain-specific extraction patterns from KG")
        
        extracted_facts = dspy.OutputField(desc="List of structured facts with confidence scores")
        extraction_reasoning = dspy.OutputField(desc="Reasoning behind extraction decisions")
    
    class SynthesizeContext(dspy.Signature):
        """Synthesize relevant context from knowledge graph for response generation"""
        
        user_query = dspy.InputField(desc="Current user input")
        relevant_facts = dspy.InputField(desc="Retrieved facts from Universal Memory")
        user_patterns = dspy.InputField(desc="User behavioral patterns from profile")
        
        synthesized_context = dspy.OutputField(desc="Optimally synthesized context")
        context_reasoning = dspy.OutputField(desc="Context selection strategy explanation")
    
    class GenerateResponse(dspy.Signature):
        """Generate contextually aware responses using optimized prompts"""
        
        user_input = dspy.InputField(desc="User's current message")
        synthesized_context = dspy.InputField(desc="Relevant knowledge context")
        conversation_style = dspy.InputField(desc="User's preferred interaction style")
        
        response = dspy.OutputField(desc="Contextually appropriate response")
        confidence_score = dspy.OutputField(desc="Confidence in response quality")
        knowledge_utilization = dspy.OutputField(desc="How knowledge was utilized")
    
    class ValidateFact(dspy.Signature):
        """Validate extracted facts against existing knowledge and evidence"""
        
        candidate_fact = dspy.InputField(desc="Newly extracted fact")
        existing_knowledge = dspy.InputField(desc="Related facts from knowledge graph")
        source_reliability = dspy.InputField(desc="Reliability metrics of extraction source")
        
        validation_result = dspy.OutputField(desc="Validation outcome with confidence")
        contradiction_flags = dspy.OutputField(desc="Any contradictions with existing knowledge")
        improvement_suggestions = dspy.OutputField(desc="Suggestions for fact refinement")

else:
    # Mock signatures if DSPy is not available
    class ExtractFacts:
        def __init__(self): pass
    
    class SynthesizeContext:
        def __init__(self): pass
    
    class GenerateResponse:
        def __init__(self): pass
    
    class ValidateFact:
        def __init__(self): pass


class PromptVersioningSystem:
    """Version control system for DSPy-optimized prompts"""
    
    def __init__(self, storage_path: str = "prompt_versions.json"):
        self.storage_path = Path(storage_path)
        self.versions: Dict[str, PromptVersion] = {}
        self.active_versions: Dict[str, str] = {}  # signature_name -> version_id
        self._load_versions()
    
    def create_version(self, 
                      prompt_template: str,
                      signature_name: str,
                      knowledge_insights: Dict[str, Any],
                      parent_version_id: Optional[str] = None) -> PromptVersion:
        """Create new prompt version with knowledge insights"""
        
        version = PromptVersion(
            version_id=str(uuid.uuid4()),
            prompt_template=prompt_template,
            signature_name=signature_name,
            performance_metrics={},
            knowledge_context=knowledge_insights,
            parent_version_id=parent_version_id
        )
        
        self.versions[version.version_id] = version
        self._save_versions()
        
        return version
    
    def activate_version(self, version_id: str) -> bool:
        """Activate a specific version for production use"""
        if version_id not in self.versions:
            return False
        
        version = self.versions[version_id]
        
        # Deactivate current version for this signature
        current_active = self.active_versions.get(version.signature_name)
        if current_active and current_active in self.versions:
            self.versions[current_active].is_active = False
        
        # Activate new version
        version.is_active = True
        self.active_versions[version.signature_name] = version_id
        
        self._save_versions()
        return True
    
    def get_active_version(self, signature_name: str) -> Optional[PromptVersion]:
        """Get currently active version for a signature"""
        version_id = self.active_versions.get(signature_name)
        if version_id and version_id in self.versions:
            return self.versions[version_id]
        return None
    
    def evaluate_version(self, 
                        version_id: str,
                        evaluation_metrics: Dict[str, float]) -> EvaluationResult:
        """Evaluate prompt version performance"""
        if version_id not in self.versions:
            raise ValueError(f"Version {version_id} not found")
        
        version = self.versions[version_id]
        
        result = EvaluationResult(
            version_id=version_id,
            test_cases_count=len(evaluation_metrics),
            metrics=evaluation_metrics,
            detailed_results=[]
        )
        
        # Update version with evaluation results
        version.evaluation_results = result.to_dict()
        version.performance_metrics.update(evaluation_metrics)
        
        self._save_versions()
        return result
    
    def compare_versions(self, version_a_id: str, version_b_id: str) -> Dict[str, Any]:
        """Compare performance between two versions"""
        if version_a_id not in self.versions or version_b_id not in self.versions:
            raise ValueError("One or both versions not found")
        
        version_a = self.versions[version_a_id]
        version_b = self.versions[version_b_id]
        
        comparison = {
            'version_a': version_a_id,
            'version_b': version_b_id,
            'metric_comparison': {},
            'improvement_summary': {},
            'recommendation': 'no_clear_winner'
        }
        
        # Compare metrics
        for metric in version_a.performance_metrics:
            if metric in version_b.performance_metrics:
                a_score = version_a.performance_metrics[metric]
                b_score = version_b.performance_metrics[metric]
                improvement = ((b_score - a_score) / a_score) * 100 if a_score > 0 else 0
                
                comparison['metric_comparison'][metric] = {
                    'version_a_score': a_score,
                    'version_b_score': b_score,
                    'improvement_percent': improvement
                }
        
        # Determine recommendation
        total_improvement = sum(
            comp['improvement_percent'] 
            for comp in comparison['metric_comparison'].values()
        )
        
        if total_improvement > 5:  # 5% overall improvement threshold
            comparison['recommendation'] = 'version_b'
        elif total_improvement < -5:
            comparison['recommendation'] = 'version_a'
        
        return comparison
    
    def rollback_version(self, signature_name: str) -> bool:
        """Rollback to previous version for a signature"""
        current_version_id = self.active_versions.get(signature_name)
        if not current_version_id or current_version_id not in self.versions:
            return False
        
        current_version = self.versions[current_version_id]
        parent_id = current_version.parent_version_id
        
        if parent_id and parent_id in self.versions:
            return self.activate_version(parent_id)
        
        return False
    
    def list_versions(self, signature_name: Optional[str] = None) -> List[PromptVersion]:
        """List all versions, optionally filtered by signature"""
        versions = list(self.versions.values())
        
        if signature_name:
            versions = [v for v in versions if v.signature_name == signature_name]
        
        # Sort by creation date (newest first)
        versions.sort(key=lambda v: v.created_at, reverse=True)
        return versions
    
    def get_version_history(self, signature_name: str) -> List[PromptVersion]:
        """Get optimization history for a signature"""
        versions = [v for v in self.versions.values() if v.signature_name == signature_name]
        versions.sort(key=lambda v: v.created_at)
        return versions
    
    def _load_versions(self):
        """Load versions from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                for version_id, version_data in data.get('versions', {}).items():
                    self.versions[version_id] = PromptVersion.from_dict(version_data)
                
                self.active_versions = data.get('active_versions', {})
            except Exception as e:
                print(f"Error loading prompt versions: {e}")
    
    def _save_versions(self):
        """Save versions to storage"""
        try:
            data = {
                'versions': {vid: version.to_dict() for vid, version in self.versions.items()},
                'active_versions': self.active_versions
            }
            
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving prompt versions: {e}")


class DSPyConvoTreeEngine:
    """Main DSPy integration engine for ConvoTree"""
    
    def __init__(self, 
                 memory_interface: UniversalMemoryInterface,
                 versioning_system: PromptVersioningSystem = None):
        self.memory = memory_interface
        self.versioning = versioning_system or PromptVersioningSystem()
        self.kg_insights = KnowledgeGraphInsights(memory_interface)
        
        # Initialize DSPy programs if available
        if DSPY_AVAILABLE:
            self._setup_dspy_programs()
        else:
            print("⚠️ DSPy not available - optimization features disabled")
    
    def _setup_dspy_programs(self):
        """Setup DSPy programs with current best versions"""
        if not DSPY_AVAILABLE:
            return
        
        # Initialize base programs
        self.fact_extractor = dspy.ChainOfThought(ExtractFacts)
        self.context_synthesizer = dspy.ChainOfThought(SynthesizeContext)
        self.response_generator = dspy.ChainOfThought(GenerateResponse)
        self.fact_validator = dspy.ChainOfThought(ValidateFact)
        
        # Load optimized versions if available
        self._load_optimized_programs()
    
    def _load_optimized_programs(self):
        """Load optimized DSPy programs from version control"""
        program_mappings = {
            'ExtractFacts': 'fact_extractor',
            'SynthesizeContext': 'context_synthesizer', 
            'GenerateResponse': 'response_generator',
            'ValidateFact': 'fact_validator'
        }
        
        for signature_name, program_attr in program_mappings.items():
            active_version = self.versioning.get_active_version(signature_name)
            if active_version:
                # In a real implementation, this would load the optimized program
                print(f"📈 Loaded optimized version {active_version.version_id} for {signature_name}")
    
    def extract_facts_optimized(self, 
                               conversation_context: str,
                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract facts using optimized DSPy program"""
        if not DSPY_AVAILABLE:
            return {
                'extracted_facts': self._mock_fact_extraction(conversation_context),
                'extraction_reasoning': 'Mock extraction - DSPy not available',
                'success': True
            }
        
        # Get domain patterns from knowledge insights
        insights = self.kg_insights.analyze_fact_extraction_patterns()
        domain_patterns = insights.get('extraction_success_patterns', {})
        
        try:
            result = self.fact_extractor(
                conversation_context=conversation_context,
                user_profile=str(user_profile),
                domain_patterns=str(domain_patterns)
            )
            
            return {
                'extracted_facts': result.extracted_facts,
                'extraction_reasoning': result.extraction_reasoning,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False,
                'fallback_facts': self._mock_fact_extraction(conversation_context)
            }
    
    def synthesize_context_optimized(self,
                                   user_query: str,
                                   relevant_facts: List[Dict],
                                   user_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize context using optimized DSPy program"""
        if not DSPY_AVAILABLE:
            return {
                'synthesized_context': self._mock_context_synthesis(user_query, relevant_facts),
                'context_reasoning': 'Mock synthesis - DSPy not available',
                'success': True
            }
        
        try:
            result = self.context_synthesizer(
                user_query=user_query,
                relevant_facts=str(relevant_facts),
                user_patterns=str(user_patterns)
            )
            
            return {
                'synthesized_context': result.synthesized_context,
                'context_reasoning': result.context_reasoning,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False,
                'fallback_context': self._mock_context_synthesis(user_query, relevant_facts)
            }
    
    def generate_response_optimized(self,
                                  user_input: str,
                                  synthesized_context: str,
                                  conversation_style: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using optimized DSPy program"""
        if not DSPY_AVAILABLE:
            return {
                'response': self._mock_response_generation(user_input, synthesized_context),
                'confidence_score': '0.75',
                'knowledge_utilization': 'Mock utilization - DSPy not available',
                'success': True
            }
        
        try:
            result = self.response_generator(
                user_input=user_input,
                synthesized_context=synthesized_context,
                conversation_style=str(conversation_style)
            )
            
            return {
                'response': result.response,
                'confidence_score': result.confidence_score,
                'knowledge_utilization': result.knowledge_utilization,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False,
                'fallback_response': self._mock_response_generation(user_input, synthesized_context)
            }
    
    def identify_optimization_opportunities(self) -> List[OptimizationOpportunity]:
        """Identify opportunities for prompt optimization"""
        return self.kg_insights.detect_optimization_opportunities()
    
    def optimize_for_opportunity(self, opportunity: OptimizationOpportunity) -> PromptVersion:
        """Create optimized prompt version for specific opportunity"""
        # Generate improved prompt based on insights
        insights = opportunity.knowledge_insights
        suggested_changes = opportunity.suggested_changes
        
        # Create new prompt template with improvements
        improved_template = self._generate_improved_prompt(
            opportunity.target_metric,
            insights,
            suggested_changes
        )
        
        # Create new version
        signature_name = self._get_signature_for_metric(opportunity.target_metric)
        new_version = self.versioning.create_version(
            prompt_template=improved_template,
            signature_name=signature_name,
            knowledge_insights=insights,
            parent_version_id=self.versioning.get_active_version(signature_name)
        )
        
        return new_version
    
    def _mock_fact_extraction(self, context: str) -> List[Dict]:
        """Mock fact extraction for when DSPy is not available"""
        return [
            {
                'content': f'Extracted from: {context[:50]}...',
                'confidence': 0.7,
                'type': 'GENERAL'
            }
        ]
    
    def _mock_context_synthesis(self, query: str, facts: List[Dict]) -> str:
        """Mock context synthesis for when DSPy is not available"""
        return f"Context for '{query}' based on {len(facts)} facts"
    
    def _mock_response_generation(self, user_input: str, context: str) -> str:
        """Mock response generation for when DSPy is not available"""
        return f"Response to '{user_input}' using context: {context[:50]}..."
    
    def _generate_improved_prompt(self, 
                                 target_metric: OptimizationTarget,
                                 insights: Dict[str, Any],
                                 suggestions: List[str]) -> str:
        """Generate improved prompt template based on optimization insights"""
        base_templates = {
            OptimizationTarget.FACT_EXTRACTION_ACCURACY: """
Extract structured facts from the conversation with high accuracy.
Focus on: {focus_areas}
Use patterns: {successful_patterns}
Avoid: {failure_modes}
""",
            OptimizationTarget.CONTEXTUAL_RELEVANCE: """
Synthesize the most relevant context for the user query.
Prioritize: {relevance_factors}
Consider user patterns: {user_patterns}
Optimize for: {engagement_factors}
""",
        }
        
        template = base_templates.get(target_metric, "Optimize for {target_metric}")
        
        # Fill in template with insights
        return template.format(
            target_metric=target_metric.value,
            focus_areas=insights.get('high_confidence_domains', []),
            successful_patterns=insights.get('extraction_success_patterns', {}),
            failure_modes=insights.get('common_failure_modes', {}),
            relevance_factors=insights.get('effective_context_utilization', {}),
            user_patterns=insights.get('preferred_response_styles', {}),
            engagement_factors=insights.get('engagement_optimization_factors', {})
        )
    
    def _get_signature_for_metric(self, metric: OptimizationTarget) -> str:
        """Get DSPy signature name for optimization target"""
        mappings = {
            OptimizationTarget.FACT_EXTRACTION_ACCURACY: 'ExtractFacts',
            OptimizationTarget.CONTEXTUAL_RELEVANCE: 'SynthesizeContext',
            OptimizationTarget.USER_ENGAGEMENT: 'GenerateResponse',
            OptimizationTarget.KNOWLEDGE_CONSISTENCY: 'ValidateFact'
        }
        return mappings.get(metric, 'GenerateResponse')


# Factory function for easy setup
def create_dspy_convotree_engine(memory_interface: UniversalMemoryInterface,
                                version_storage_path: str = "prompt_versions.json") -> DSPyConvoTreeEngine:
    """Create DSPy ConvoTree engine with versioning system"""
    versioning_system = PromptVersioningSystem(version_storage_path)
    return DSPyConvoTreeEngine(memory_interface, versioning_system)


if __name__ == "__main__":
    # Example usage
    from universal_memory_interface import create_universal_memory
    
    # Create Universal Memory Interface
    umi = create_universal_memory()
    
    # Create DSPy ConvoTree Engine
    engine = create_dspy_convotree_engine(umi)
    
    print("🧠 DSPy ConvoTree Engine initialized")
    print(f"DSPy available: {DSPY_AVAILABLE}")
    
    # Identify optimization opportunities
    opportunities = engine.identify_optimization_opportunities()
    print(f"Found {len(opportunities)} optimization opportunities")
    
    for opp in opportunities:
        print(f"- {opp.target_metric.value}: {opp.current_performance:.2f} -> {opp.current_performance + opp.target_improvement:.2f}")
    
    # Test fact extraction
    result = engine.extract_facts_optimized(
        conversation_context="User mentioned they enjoy hiking and photography",
        user_profile={"domains": ["outdoor", "creative"]}
    )
    print(f"Fact extraction result: {result['success']}")
    
    # Test context synthesis
    context_result = engine.synthesize_context_optimized(
        user_query="Tell me about outdoor photography",
        relevant_facts=[{"content": "User enjoys hiking", "confidence": 0.9}],
        user_patterns={"style": "detailed"}
    )
    print(f"Context synthesis result: {context_result['success']}")