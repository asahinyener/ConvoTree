#!/usr/bin/env python3
"""
Universal Memory Interface (UMI) for ConvoTree v3.0
Provides a single abstraction layer for all memory operations across sessions and providers
"""

import hashlib
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from pathlib import Path
import sqlite3
import threading
from collections import defaultdict


class FactType(Enum):
    """Types of facts that can be stored"""
    PERSONAL = "personal"          # Personal information about user
    PREFERENCE = "preference"      # User preferences and choices
    KNOWLEDGE = "knowledge"        # General knowledge or expertise
    RELATIONSHIP = "relationship"  # Relationships between entities
    EVENT = "event"               # Events or activities
    GOAL = "goal"                 # User goals or objectives
    CONTEXT = "context"           # Contextual information
    METADATA = "metadata"         # System metadata


class ConfidenceSource(Enum):
    """Sources of confidence scoring"""
    LLM_EXTRACTION = "llm_extraction"
    USER_CONFIRMATION = "user_confirmation"
    CROSS_REFERENCE = "cross_reference"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    PROVIDER_CONSENSUS = "provider_consensus"


@dataclass
class Evidence:
    """Evidence supporting or contradicting a fact"""
    source: str
    confidence: float
    timestamp: datetime
    provider: str
    content: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'provider': self.provider,
            'content': self.content
        }


@dataclass
class Contradiction:
    """Represents a contradiction between facts"""
    fact_id_1: str
    fact_id_2: str
    contradiction_type: str
    confidence: float
    detected_at: datetime
    resolution_strategy: Optional[str] = None
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UniversalFact:
    """Enhanced fact model with cross-session persistence and confidence scoring"""
    id: str
    content: str
    fact_type: FactType
    confidence_score: float
    extraction_provider: str
    extraction_method: str
    source_sessions: List[str]
    created_at: datetime
    last_verified: datetime
    verification_count: int
    contradictions: List[str] = field(default_factory=list)
    semantic_tags: List[str] = field(default_factory=list)
    user_context: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Evidence] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    
    @classmethod
    def create(cls, content: str, fact_type: FactType, provider: str, 
               session_id: str, confidence: float = 0.5, **kwargs) -> 'UniversalFact':
        """Create a new universal fact"""
        return cls(
            id=str(uuid.uuid4()),
            content=content,
            fact_type=fact_type,
            confidence_score=confidence,
            extraction_provider=provider,
            extraction_method=kwargs.get('method', 'auto'),
            source_sessions=[session_id],
            created_at=datetime.now(),
            last_verified=datetime.now(),
            verification_count=1,
            semantic_tags=kwargs.get('tags', []),
            user_context=kwargs.get('context', {}),
            entities=kwargs.get('entities', []),
            relationships=kwargs.get('relationships', [])
        )
    
    def merge_with(self, other_fact: 'UniversalFact') -> 'UniversalFact':
        """Merge this fact with another similar fact"""
        # Combine evidence and increase confidence
        combined_evidence = self.evidence + other_fact.evidence
        new_confidence = min(1.0, (self.confidence_score + other_fact.confidence_score) / 2 + 0.1)
        
        # Merge sessions and tags
        combined_sessions = list(set(self.source_sessions + other_fact.source_sessions))
        combined_tags = list(set(self.semantic_tags + other_fact.semantic_tags))
        combined_entities = list(set(self.entities + other_fact.entities))
        
        # Use the more recent content if different
        content = other_fact.content if other_fact.created_at > self.created_at else self.content
        
        return UniversalFact(
            id=self.id,  # Keep original ID
            content=content,
            fact_type=self.fact_type,
            confidence_score=new_confidence,
            extraction_provider=f"{self.extraction_provider}+{other_fact.extraction_provider}",
            extraction_method="merged",
            source_sessions=combined_sessions,
            created_at=self.created_at,
            last_verified=datetime.now(),
            verification_count=self.verification_count + other_fact.verification_count,
            contradictions=self.contradictions,
            semantic_tags=combined_tags,
            user_context={**self.user_context, **other_fact.user_context},
            evidence=combined_evidence,
            entities=combined_entities,
            relationships=self.relationships + other_fact.relationships
        )
    
    def update_confidence(self, new_evidence: Evidence) -> float:
        """Update confidence score based on new evidence"""
        self.evidence.append(new_evidence)
        self.last_verified = datetime.now()
        self.verification_count += 1
        
        # Calculate new confidence based on evidence
        evidence_scores = [e.confidence for e in self.evidence]
        provider_diversity = len(set(e.provider for e in self.evidence))
        
        # Boost confidence with provider diversity and evidence count
        base_confidence = sum(evidence_scores) / len(evidence_scores)
        diversity_boost = min(0.2, provider_diversity * 0.05)
        evidence_boost = min(0.1, len(evidence_scores) * 0.01)
        
        self.confidence_score = min(1.0, base_confidence + diversity_boost + evidence_boost)
        return self.confidence_score
    
    def mark_contradiction(self, contradicting_fact: 'UniversalFact'):
        """Mark this fact as contradicting another"""
        if contradicting_fact.id not in self.contradictions:
            self.contradictions.append(contradicting_fact.id)
    
    def get_semantic_hash(self) -> str:
        """Get semantic hash for deduplication"""
        # Normalize content for semantic comparison
        normalized = self.content.lower().strip()
        # Include type and key entities for better matching
        hash_content = f"{normalized}|{self.fact_type.value}|{'|'.join(sorted(self.entities))}"
        return hashlib.md5(hash_content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['fact_type'] = self.fact_type.value
        data['created_at'] = self.created_at.isoformat()
        data['last_verified'] = self.last_verified.isoformat()
        data['evidence'] = [e.to_dict() for e in self.evidence]
        return data


@dataclass 
class UserPattern:
    """Detected user behavior or preference pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    confidence: float
    evidence_sessions: List[str]
    detected_at: datetime
    last_seen: datetime
    frequency: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type, 
            'description': self.description,
            'confidence': self.confidence,
            'evidence_sessions': self.evidence_sessions,
            'detected_at': self.detected_at.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'frequency': self.frequency
        }


@dataclass
class UniversalUserProfile:
    """Cross-session user profile with consolidated knowledge"""
    user_id: str
    sessions: List[str]
    preferences: Dict[str, Any]
    behavior_patterns: List[UserPattern]
    knowledge_domains: List[str]
    interaction_style: Dict[str, Any]
    provider_preferences: Dict[str, float]
    privacy_settings: Dict[str, Any]
    created_at: datetime
    last_updated: datetime
    total_interactions: int
    
    @classmethod
    def create_empty(cls, user_id: str) -> 'UniversalUserProfile':
        """Create an empty user profile"""
        return cls(
            user_id=user_id,
            sessions=[],
            preferences={},
            behavior_patterns=[],
            knowledge_domains=[],
            interaction_style={},
            provider_preferences={},
            privacy_settings={'data_retention_days': 365, 'share_analytics': False},
            created_at=datetime.now(),
            last_updated=datetime.now(),
            total_interactions=0
        )
    
    def consolidate_from_sessions(self, facts: List[UniversalFact]):
        """Consolidate profile from session facts"""
        # Extract preferences from facts (including PERSONAL facts that indicate preferences)
        preference_facts = [f for f in facts if f.fact_type in [FactType.PREFERENCE, FactType.PERSONAL, FactType.GOAL]]
        for fact in preference_facts:
            # Parse preference facts into structured preferences
            key = fact.entities[0] if fact.entities else 'general'
            # For non-preference facts, derive preference context
            if fact.fact_type == FactType.PERSONAL and 'learning' in fact.content.lower():
                key = f"learning_{key}"
            elif fact.fact_type == FactType.GOAL:
                key = f"goal_{key}"
            self.preferences[key] = fact.content
        
        # Extract knowledge domains from all fact types and their tags
        domains = set()
        for fact in facts:
            domains.update(fact.semantic_tags)
            # Also add entities as potential domains
            domains.update(fact.entities)
        
        # Accept all domains without hardcoded filtering - let the data speak for itself
        # Only filter out very short or obviously meaningless terms
        meaningful_domains = [d for d in domains if len(d) > 2 and d.replace(' ', '').isalnum()]
        
        # Merge with existing domains
        existing_domains = set(self.knowledge_domains)
        existing_domains.update(meaningful_domains)
        self.knowledge_domains = list(existing_domains)
        
        # Update interaction style based on fact patterns
        self.interaction_style = self._analyze_interaction_style(facts)
        self.last_updated = datetime.now()
    
    def _analyze_interaction_style(self, facts: List[UniversalFact]) -> Dict[str, Any]:
        """Analyze interaction style from facts"""
        total_facts = len(facts)
        if total_facts == 0:
            return {}
        
        # Analyze fact types distribution
        type_counts = defaultdict(int)
        for fact in facts:
            type_counts[fact.fact_type.value] += 1
        
        # Calculate interaction characteristics
        style = {
            'detail_level': 'high' if type_counts.get('personal', 0) > total_facts * 0.3 else 'medium',
            'question_frequency': 'high' if type_counts.get('knowledge', 0) > total_facts * 0.4 else 'medium',
            'preference_clarity': 'high' if type_counts.get('preference', 0) > total_facts * 0.2 else 'medium',
            'session_length': 'long' if total_facts > 50 else 'medium' if total_facts > 20 else 'short'
        }
        
        return style
    
    def predict_preferences(self, context: str) -> Dict[str, float]:
        """Predict user preferences for given context"""
        predictions = {}
        
        # Use existing preferences and patterns
        for pattern in self.behavior_patterns:
            if context.lower() in pattern.description.lower():
                predictions[pattern.pattern_type] = pattern.confidence
        
        # Use knowledge domains for prediction
        for domain in self.knowledge_domains:
            if domain.lower() in context.lower():
                predictions[f"interested_in_{domain}"] = 0.7
        
        return predictions
    
    def suggest_conversation_topics(self) -> List[str]:
        """Suggest conversation topics based on profile - completely generalizable"""
        topics = []
        
        # Topics from knowledge domains (no hardcoded assumptions)
        for domain in self.knowledge_domains[:3]:
            topics.append(f"More about {domain}")
            topics.append(f"Recent developments in {domain}")
        
        # Topics from behavior patterns
        for pattern in self.behavior_patterns[:2]:
            topics.append(f"Further discussion about {pattern.description}")
        
        # Topics from preferences (generic suggestions)
        for pref_key, pref_value in list(self.preferences.items())[:2]:
            # Extract the main subject from the key
            clean_key = pref_key.replace('learning_', '').replace('goal_', '')
            topics.append(f"More information about {clean_key}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_topics = []
        for topic in topics:
            if topic not in seen:
                seen.add(topic)
                unique_topics.append(topic)
        
        return unique_topics[:5]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['behavior_patterns'] = [p.to_dict() for p in self.behavior_patterns]
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data


class MemoryBackend(ABC):
    """Abstract base class for memory storage backends"""
    
    @abstractmethod
    def store_fact(self, fact: UniversalFact) -> bool:
        pass
    
    @abstractmethod
    def retrieve_facts(self, query: str, limit: int = 100) -> List[UniversalFact]:
        pass
    
    @abstractmethod
    def get_facts_by_session(self, session_id: str) -> List[UniversalFact]:
        pass
    
    @abstractmethod
    def update_fact(self, fact: UniversalFact) -> bool:
        pass
    
    @abstractmethod
    def delete_fact(self, fact_id: str) -> bool:
        pass
    
    @abstractmethod
    def store_user_profile(self, profile: UniversalUserProfile) -> bool:
        pass
    
    @abstractmethod
    def get_user_profile(self, user_id: str) -> Optional[UniversalUserProfile]:
        pass


class SQLiteMemoryBackend(MemoryBackend):
    """SQLite implementation of memory backend with enhanced indexing"""
    
    def __init__(self, db_path: str = "universal_memory.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database with enhanced schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Enhanced facts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS universal_facts (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    fact_type TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    extraction_provider TEXT NOT NULL,
                    extraction_method TEXT NOT NULL,
                    source_sessions TEXT NOT NULL,  -- JSON array
                    created_at TEXT NOT NULL,
                    last_verified TEXT NOT NULL,
                    verification_count INTEGER DEFAULT 1,
                    contradictions TEXT DEFAULT '[]',  -- JSON array
                    semantic_tags TEXT DEFAULT '[]',  -- JSON array
                    user_context TEXT DEFAULT '{}',  -- JSON object
                    evidence TEXT DEFAULT '[]',  -- JSON array
                    entities TEXT DEFAULT '[]',  -- JSON array
                    relationships TEXT DEFAULT '[]',  -- JSON array
                    semantic_hash TEXT,
                    embedding BLOB  -- For vector storage if needed
                )
            """)
            
            # User profiles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    sessions TEXT NOT NULL,  -- JSON array
                    preferences TEXT DEFAULT '{}',  -- JSON object
                    behavior_patterns TEXT DEFAULT '[]',  -- JSON array
                    knowledge_domains TEXT DEFAULT '[]',  -- JSON array
                    interaction_style TEXT DEFAULT '{}',  -- JSON object
                    provider_preferences TEXT DEFAULT '{}',  -- JSON object
                    privacy_settings TEXT DEFAULT '{}',  -- JSON object
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    total_interactions INTEGER DEFAULT 0
                )
            """)
            
            # Contradictions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contradictions (
                    id TEXT PRIMARY KEY,
                    fact_id_1 TEXT NOT NULL,
                    fact_id_2 TEXT NOT NULL,
                    contradiction_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    detected_at TEXT NOT NULL,
                    resolution_strategy TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (fact_id_1) REFERENCES universal_facts (id),
                    FOREIGN KEY (fact_id_2) REFERENCES universal_facts (id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_type ON universal_facts (fact_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_confidence ON universal_facts (confidence_score)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_provider ON universal_facts (extraction_provider)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_hash ON universal_facts (semantic_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_created ON universal_facts (created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_contradictions_facts ON contradictions (fact_id_1, fact_id_2)")
            
            # Full-text search for content
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
                    fact_id, content, entities, semantic_tags
                )
            """)
    
    def store_fact(self, fact: UniversalFact) -> bool:
        """Store a universal fact"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Store in main table
                    conn.execute("""
                        INSERT OR REPLACE INTO universal_facts 
                        (id, content, fact_type, confidence_score, extraction_provider, 
                         extraction_method, source_sessions, created_at, last_verified, 
                         verification_count, contradictions, semantic_tags, user_context,
                         evidence, entities, relationships, semantic_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        fact.id, fact.content, fact.fact_type.value, fact.confidence_score,
                        fact.extraction_provider, fact.extraction_method,
                        json.dumps(fact.source_sessions), fact.created_at.isoformat(),
                        fact.last_verified.isoformat(), fact.verification_count,
                        json.dumps(fact.contradictions), json.dumps(fact.semantic_tags),
                        json.dumps(fact.user_context), json.dumps([e.to_dict() for e in fact.evidence]),
                        json.dumps(fact.entities), json.dumps(fact.relationships),
                        fact.get_semantic_hash()
                    ))
                    
                    # Store in FTS table for full-text search
                    conn.execute("""
                        INSERT OR REPLACE INTO facts_fts (fact_id, content, entities, semantic_tags)
                        VALUES (?, ?, ?, ?)
                    """, (
                        fact.id, fact.content, 
                        ' '.join(fact.entities), ' '.join(fact.semantic_tags)
                    ))
                    
                return True
            except Exception as e:
                print(f"Error storing fact: {e}")
                return False
    
    def retrieve_facts(self, query: str, limit: int = 100) -> List[UniversalFact]:
        """Retrieve facts using full-text search with fallback to LIKE search"""
        with self.lock:
            facts = []
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    
                    # Try FTS search first
                    try:
                        cursor = conn.execute("""
                            SELECT f.* FROM universal_facts f
                            JOIN facts_fts fts ON f.id = fts.fact_id
                            WHERE facts_fts MATCH ?
                            ORDER BY f.confidence_score DESC, f.last_verified DESC
                            LIMIT ?
                        """, (query, limit))
                        
                        for row in cursor.fetchall():
                            facts.append(self._row_to_fact(row))
                    except:
                        # Fallback to LIKE search if FTS fails
                        cursor = conn.execute("""
                            SELECT * FROM universal_facts 
                            WHERE content LIKE ? OR semantic_tags LIKE ? OR entities LIKE ?
                            ORDER BY confidence_score DESC, last_verified DESC
                            LIMIT ?
                        """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
                        
                        for row in cursor.fetchall():
                            facts.append(self._row_to_fact(row))
                        
            except Exception as e:
                print(f"Error retrieving facts: {e}")
                
            return facts
    
    def get_facts_by_session(self, session_id: str) -> List[UniversalFact]:
        """Get all facts from a specific session"""
        with self.lock:
            facts = []
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    
                    cursor = conn.execute("""
                        SELECT * FROM universal_facts 
                        WHERE source_sessions LIKE ?
                        ORDER BY created_at DESC
                    """, (f'%{session_id}%',))
                    
                    for row in cursor.fetchall():
                        fact = self._row_to_fact(row)
                        if session_id in fact.source_sessions:
                            facts.append(fact)
                            
            except Exception as e:
                print(f"Error getting session facts: {e}")
                
            return facts
    
    def update_fact(self, fact: UniversalFact) -> bool:
        """Update an existing fact"""
        return self.store_fact(fact)  # INSERT OR REPLACE handles updates
    
    def delete_fact(self, fact_id: str) -> bool:
        """Delete a fact"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM universal_facts WHERE id = ?", (fact_id,))
                    conn.execute("DELETE FROM facts_fts WHERE fact_id = ?", (fact_id,))
                return True
            except Exception as e:
                print(f"Error deleting fact: {e}")
                return False
    
    def store_user_profile(self, profile: UniversalUserProfile) -> bool:
        """Store user profile"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO user_profiles
                        (user_id, sessions, preferences, behavior_patterns, knowledge_domains,
                         interaction_style, provider_preferences, privacy_settings,
                         created_at, last_updated, total_interactions)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        profile.user_id, json.dumps(profile.sessions),
                        json.dumps(profile.preferences), 
                        json.dumps([p.to_dict() for p in profile.behavior_patterns]),
                        json.dumps(profile.knowledge_domains),
                        json.dumps(profile.interaction_style),
                        json.dumps(profile.provider_preferences),
                        json.dumps(profile.privacy_settings),
                        profile.created_at.isoformat(),
                        profile.last_updated.isoformat(),
                        profile.total_interactions
                    ))
                return True
            except Exception as e:
                print(f"Error storing user profile: {e}")
                return False
    
    def get_user_profile(self, user_id: str) -> Optional[UniversalUserProfile]:
        """Get user profile"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    
                    cursor = conn.execute("""
                        SELECT * FROM user_profiles WHERE user_id = ?
                    """, (user_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_profile(row)
                        
            except Exception as e:
                print(f"Error getting user profile: {e}")
                
            return None
    
    def _row_to_fact(self, row) -> UniversalFact:
        """Convert database row to UniversalFact"""
        evidence_data = json.loads(row['evidence'])
        evidence = [
            Evidence(
                source=e['source'],
                confidence=e['confidence'],
                timestamp=datetime.fromisoformat(e['timestamp']),
                provider=e['provider'],
                content=e['content']
            ) for e in evidence_data
        ]
        
        return UniversalFact(
            id=row['id'],
            content=row['content'],
            fact_type=FactType(row['fact_type']),
            confidence_score=row['confidence_score'],
            extraction_provider=row['extraction_provider'],
            extraction_method=row['extraction_method'],
            source_sessions=json.loads(row['source_sessions']),
            created_at=datetime.fromisoformat(row['created_at']),
            last_verified=datetime.fromisoformat(row['last_verified']),
            verification_count=row['verification_count'],
            contradictions=json.loads(row['contradictions']),
            semantic_tags=json.loads(row['semantic_tags']),
            user_context=json.loads(row['user_context']),
            evidence=evidence,
            entities=json.loads(row['entities']),
            relationships=json.loads(row['relationships'])
        )
    
    def _row_to_profile(self, row) -> UniversalUserProfile:
        """Convert database row to UniversalUserProfile"""
        patterns_data = json.loads(row['behavior_patterns'])
        patterns = [
            UserPattern(
                pattern_id=p['pattern_id'],
                pattern_type=p['pattern_type'],
                description=p['description'],
                confidence=p['confidence'],
                evidence_sessions=p['evidence_sessions'],
                detected_at=datetime.fromisoformat(p['detected_at']),
                last_seen=datetime.fromisoformat(p['last_seen']),
                frequency=p['frequency']
            ) for p in patterns_data
        ]
        
        return UniversalUserProfile(
            user_id=row['user_id'],
            sessions=json.loads(row['sessions']),
            preferences=json.loads(row['preferences']),
            behavior_patterns=patterns,
            knowledge_domains=json.loads(row['knowledge_domains']),
            interaction_style=json.loads(row['interaction_style']),
            provider_preferences=json.loads(row['provider_preferences']),
            privacy_settings=json.loads(row['privacy_settings']),
            created_at=datetime.fromisoformat(row['created_at']),
            last_updated=datetime.fromisoformat(row['last_updated']),
            total_interactions=row['total_interactions']
        )


@dataclass
class ConsolidationResult:
    """Result of cross-session knowledge consolidation"""
    merged_facts: int
    deduplicated_facts: int
    contradictions_found: int
    new_patterns: int
    processing_time: float
    confidence_improvements: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RelevantKnowledge:
    """Relevant knowledge retrieved for a query"""
    facts: List[UniversalFact]
    user_context: Dict[str, Any]
    patterns: List[UserPattern]
    confidence_threshold: float
    retrieval_method: str
    total_processing_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'facts': [f.to_dict() for f in self.facts],
            'user_context': self.user_context,
            'patterns': [p.to_dict() for p in self.patterns],
            'confidence_threshold': self.confidence_threshold,
            'retrieval_method': self.retrieval_method,
            'total_processing_time': self.total_processing_time
        }


class UniversalMemoryInterface:
    """
    Universal Memory Interface - Single abstraction for all memory operations
    """
    
    def __init__(self, backend: MemoryBackend, default_user_id: str = "default"):
        self.backend = backend
        self.default_user_id = default_user_id
        self._semantic_similarity_cache = {}
        
        # Initialize default user profile if doesn't exist
        if not self.backend.get_user_profile(default_user_id):
            profile = UniversalUserProfile.create_empty(default_user_id)
            self.backend.store_user_profile(profile)
    
    def store_knowledge(self, facts: List[UniversalFact], session_id: str, 
                       user_id: str = None) -> bool:
        """Store knowledge facts with automatic deduplication"""
        user_id = user_id or self.default_user_id
        
        # Check for duplicates and merge similar facts
        stored_count = 0
        for fact in facts:
            # Check for semantic duplicates
            duplicate = self._find_semantic_duplicate(fact)
            if duplicate:
                # Merge with existing fact
                merged_fact = duplicate.merge_with(fact)
                self.backend.update_fact(merged_fact)
            else:
                # Store new fact
                if self.backend.store_fact(fact):
                    stored_count += 1
        
        # Update user profile with new session
        self._update_user_profile_with_session(user_id, session_id, facts)
        
        return stored_count > 0
    
    def retrieve_relevant(self, query: str, context_window: int = 50, 
                         user_id: str = None, confidence_threshold: float = 0.3) -> RelevantKnowledge:
        """Retrieve relevant knowledge for a query with intelligent context selection"""
        import time
        start_time = time.time()
        
        user_id = user_id or self.default_user_id
        
        # Get user profile for personalization
        user_profile = self.backend.get_user_profile(user_id)
        user_context = user_profile.preferences if user_profile else {}
        patterns = user_profile.behavior_patterns if user_profile else []
        
        # Retrieve facts using multiple strategies
        facts = []
        
        # 1. Direct content search
        content_facts = self.backend.retrieve_facts(query, limit=context_window // 2)
        facts.extend([f for f in content_facts if f.confidence_score >= confidence_threshold])
        
        # 2. Try individual words from the query
        query_words = query.lower().split()
        for word in query_words:
            if len(word) > 3:  # Skip short words
                word_facts = self.backend.retrieve_facts(word, limit=5)
                facts.extend([f for f in word_facts if f.confidence_score >= confidence_threshold])
        
        # 3. Entity-based search if user profile has relevant entities
        if user_profile:
            for domain in user_profile.knowledge_domains:
                if domain.lower() in query.lower():
                    domain_facts = self.backend.retrieve_facts(domain, limit=10)
                    facts.extend([f for f in domain_facts if f.confidence_score >= confidence_threshold])
        
        # 3. Remove duplicates and sort by relevance
        seen_ids = set()
        unique_facts = []
        for fact in facts:
            if fact.id not in seen_ids:
                unique_facts.append(fact)
                seen_ids.add(fact.id)
        
        # Sort by confidence and recency
        unique_facts.sort(key=lambda f: (f.confidence_score, f.last_verified), reverse=True)
        
        # Limit to context window
        final_facts = unique_facts[:context_window]
        
        processing_time = time.time() - start_time
        
        return RelevantKnowledge(
            facts=final_facts,
            user_context=user_context,
            patterns=patterns,
            confidence_threshold=confidence_threshold,
            retrieval_method="multi_strategy",
            total_processing_time=processing_time
        )
    
    def consolidate_sessions(self, session_ids: List[str], user_id: str = None) -> ConsolidationResult:
        """Consolidate knowledge across multiple sessions"""
        import time
        start_time = time.time()
        
        user_id = user_id or self.default_user_id
        
        # Get all facts from specified sessions
        all_facts = []
        for session_id in session_ids:
            session_facts = self.backend.get_facts_by_session(session_id)
            all_facts.extend(session_facts)
        
        # Group facts by semantic similarity
        fact_groups = self._group_facts_by_similarity(all_facts)
        
        merged_count = 0
        deduplicated_count = 0
        contradictions_found = 0
        confidence_improvements = 0
        
        # Process each group
        for group in fact_groups:
            if len(group) > 1:
                # Merge similar facts
                primary_fact = group[0]
                for other_fact in group[1:]:
                    old_confidence = primary_fact.confidence_score
                    merged_fact = primary_fact.merge_with(other_fact)
                    
                    if merged_fact.confidence_score > old_confidence:
                        confidence_improvements += 1
                    
                    # Update primary fact
                    self.backend.update_fact(merged_fact)
                    
                    # Remove duplicate
                    self.backend.delete_fact(other_fact.id)
                    deduplicated_count += 1
                    
                merged_count += 1
        
        # Detect contradictions
        contradictions_found = self._detect_contradictions(all_facts)
        
        # Update user profile
        user_profile = self.backend.get_user_profile(user_id)
        if user_profile:
            user_profile.consolidate_from_sessions(all_facts)
            user_profile.sessions.extend([s for s in session_ids if s not in user_profile.sessions])
            self.backend.store_user_profile(user_profile)
        
        # Detect new patterns
        new_patterns = self._detect_new_patterns(all_facts, user_profile)
        
        processing_time = time.time() - start_time
        
        return ConsolidationResult(
            merged_facts=merged_count,
            deduplicated_facts=deduplicated_count,
            contradictions_found=contradictions_found,
            new_patterns=len(new_patterns),
            processing_time=processing_time,
            confidence_improvements=confidence_improvements
        )
    
    def prune_redundant(self, threshold: float = 0.2, max_age_days: int = 365) -> Dict[str, int]:
        """Prune redundant and low-confidence facts"""
        # This would implement intelligent pruning logic
        # For now, return a placeholder
        return {
            'facts_pruned': 0,
            'facts_archived': 0,
            'storage_saved_mb': 0
        }
    
    def get_user_profile(self, user_id: str = None) -> Optional[UniversalUserProfile]:
        """Get user profile"""
        user_id = user_id or self.default_user_id
        return self.backend.get_user_profile(user_id)
    
    def update_user_profile(self, profile: UniversalUserProfile) -> bool:
        """Update user profile"""
        return self.backend.store_user_profile(profile)
    
    def _find_semantic_duplicate(self, fact: UniversalFact) -> Optional[UniversalFact]:
        """Find semantically similar fact that might be a duplicate"""
        # Simple implementation - could be enhanced with embeddings
        semantic_hash = fact.get_semantic_hash()
        
        # Search for facts with same semantic hash
        similar_facts = self.backend.retrieve_facts(fact.content[:50], limit=10)
        
        for similar_fact in similar_facts:
            if (similar_fact.get_semantic_hash() == semantic_hash and 
                similar_fact.fact_type == fact.fact_type and
                similar_fact.id != fact.id):
                return similar_fact
        
        return None
    
    def _group_facts_by_similarity(self, facts: List[UniversalFact]) -> List[List[UniversalFact]]:
        """Group facts by semantic similarity"""
        groups = []
        processed = set()
        
        for fact in facts:
            if fact.id in processed:
                continue
                
            # Start new group
            group = [fact]
            processed.add(fact.id)
            
            # Find similar facts
            fact_hash = fact.get_semantic_hash()
            for other_fact in facts:
                if (other_fact.id not in processed and 
                    other_fact.get_semantic_hash() == fact_hash and
                    other_fact.fact_type == fact.fact_type):
                    group.append(other_fact)
                    processed.add(other_fact.id)
            
            groups.append(group)
        
        return groups
    
    def _detect_contradictions(self, facts: List[UniversalFact]) -> int:
        """Detect contradictions between facts"""
        # Placeholder implementation
        # Would implement sophisticated contradiction detection
        return 0
    
    def _detect_new_patterns(self, facts: List[UniversalFact], 
                           user_profile: Optional[UniversalUserProfile]) -> List[UserPattern]:
        """Detect new user patterns from facts"""
        # Placeholder implementation
        # Would implement pattern detection algorithms
        return []
    
    def _update_user_profile_with_session(self, user_id: str, session_id: str, 
                                        facts: List[UniversalFact]):
        """Update user profile with new session data"""
        profile = self.backend.get_user_profile(user_id)
        if not profile:
            profile = UniversalUserProfile.create_empty(user_id)
        
        # Add session if not already present
        if session_id not in profile.sessions:
            profile.sessions.append(session_id)
        
        # Update interaction count
        profile.total_interactions += len(facts)
        
        # Get all facts from all sessions for complete consolidation
        all_session_facts = []
        for session in profile.sessions:
            session_facts = self.backend.get_facts_by_session(session)
            all_session_facts.extend(session_facts)
        
        # Consolidate all facts into profile
        profile.consolidate_from_sessions(all_session_facts)
        
        # Store updated profile
        self.backend.store_user_profile(profile)


# Factory function for easy instantiation
def create_universal_memory(backend_type: str = "sqlite", 
                          config: Dict[str, Any] = None, 
                          user_id: str = "default") -> UniversalMemoryInterface:
    """Create a Universal Memory Interface with specified backend"""
    config = config or {}
    
    if backend_type == "sqlite":
        db_path = config.get('db_path', 'universal_memory.db')
        backend = SQLiteMemoryBackend(db_path)
    else:
        raise ValueError(f"Unsupported backend type: {backend_type}")
    
    return UniversalMemoryInterface(backend, user_id)


if __name__ == "__main__":
    # Example usage
    umi = create_universal_memory()
    
    # Create some test facts
    fact1 = UniversalFact.create(
        content="User prefers Python programming language",
        fact_type=FactType.PREFERENCE,
        provider="test_provider",
        session_id="session_1",
        confidence=0.8,
        entities=["Python", "programming"],
        tags=["technology", "preference"]
    )
    
    fact2 = UniversalFact.create(
        content="User is a data scientist",
        fact_type=FactType.PERSONAL,
        provider="test_provider", 
        session_id="session_1",
        confidence=0.9,
        entities=["data scientist"],
        tags=["profession", "personal"]
    )
    
    # Store facts
    umi.store_knowledge([fact1, fact2], "session_1")
    
    # Retrieve relevant knowledge
    result = umi.retrieve_relevant("Python programming")
    print(f"Found {len(result.facts)} relevant facts")
    
    for fact in result.facts:
        print(f"- {fact.content} (confidence: {fact.confidence_score})")
    
    # Get user profile
    profile = umi.get_user_profile()
    if profile:
        print(f"\nUser profile:")
        print(f"- Knowledge domains: {profile.knowledge_domains}")
        print(f"- Preferences: {profile.preferences}")
        print(f"- Total interactions: {profile.total_interactions}")