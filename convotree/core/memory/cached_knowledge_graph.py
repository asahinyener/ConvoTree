#!/usr/bin/env python3
"""
High-Performance Cached Knowledge Graph
Adds intelligent caching to dramatically improve knowledge retrieval performance
"""

import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import lru_cache
import threading
from .persistent_kg import PersistentKG, ConversationTurn, KnowledgeTriple

class CachedKnowledgeGraph(PersistentKG):
    """Enhanced Knowledge Graph with intelligent caching for performance"""
    
    def __init__(self, conversation_id: str, db_path: str = "conversations.db", cache_size: int = 1000):
        super().__init__(conversation_id, db_path)
        
        # Cache configuration
        self.cache_size = cache_size
        self.cache_ttl = 300  # 5 minutes default TTL
        
        # Memory caches
        self._fact_cache = {}
        self._turn_cache = {}
        self._context_cache = {}
        self._synthesis_cache = {}
        
        # Cache metadata
        self._cache_timestamps = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_lock = threading.RLock()
        
        # Performance tracking
        self._query_times = []
        self._synthesis_times = []
        
        print(f"🚀 Initialized cached knowledge graph for {conversation_id}")
    
    def get_relevant_context(self, user_query: str, max_facts: int = 10) -> Dict[str, Any]:
        """Enhanced context retrieval with intelligent caching"""
        start_time = time.time()
        
        # Create cache key based on query and current conversation state
        cache_key = self._create_context_cache_key(user_query, max_facts)
        
        # Try cache first
        cached_result = self._get_cached_context(cache_key)
        if cached_result:
            self._record_cache_hit()
            return cached_result
        
        # Cache miss - compute context
        self._record_cache_miss()
        
        # Get data with caching
        kg_facts = self._get_recent_knowledge_cached(max_facts)
        recent_context = self._get_recent_turns_cached(5)
        context_state = self._get_context_state_cached()
        
        # Try cached synthesis first
        synthesis_key = self._create_synthesis_cache_key(user_query, kg_facts)
        synthesized_context = self._get_cached_synthesis(synthesis_key)
        
        if not synthesized_context:
            # Perform expensive LLM synthesis
            synthesized_context = self._synthesize_context_with_timing(
                user_query, kg_facts, recent_context
            )
            self._cache_synthesis(synthesis_key, synthesized_context)
        
        # Build result
        result = {
            "synthesized": synthesized_context,
            "raw_facts": kg_facts,
            "recent_turns": recent_context,
            "context_state": context_state,
            "conversation_id": self.conversation_id,
            "cache_info": {
                "cache_hit": False,
                "synthesis_cached": synthesis_key in self._synthesis_cache
            }
        }
        
        # Cache the complete result
        self._cache_context(cache_key, result)
        
        # Track performance
        query_time = time.time() - start_time
        self._query_times.append(query_time)
        
        return result
    
    def _get_recent_knowledge_cached(self, limit: int = 10) -> List[str]:
        """Get recent knowledge with caching"""
        cache_key = f"knowledge_{self.conversation_id}_{limit}"
        
        with self._cache_lock:
            if self._is_cache_valid(cache_key):
                return self._fact_cache[cache_key]
            
            # Cache miss - query database
            facts = super()._get_recent_knowledge(limit)
            self._fact_cache[cache_key] = facts
            self._cache_timestamps[cache_key] = time.time()
            
            return facts
    
    def _get_recent_turns_cached(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent turns with caching"""
        cache_key = f"turns_{self.conversation_id}_{limit}"
        
        with self._cache_lock:
            if self._is_cache_valid(cache_key):
                return self._turn_cache[cache_key]
            
            # Cache miss - query database
            turns = super()._get_recent_turns(limit)
            self._turn_cache[cache_key] = turns
            self._cache_timestamps[cache_key] = time.time()
            
            return turns
    
    def _get_context_state_cached(self) -> Dict[str, Any]:
        """Get context state with caching"""
        cache_key = f"context_state_{self.conversation_id}"
        
        with self._cache_lock:
            if self._is_cache_valid(cache_key):
                return self._context_cache[cache_key]
            
            # Cache miss - query database
            state = super()._get_context_state()
            self._context_cache[cache_key] = state
            self._cache_timestamps[cache_key] = time.time()
            
            return state
    
    def _synthesize_context_with_timing(self, user_query: str, kg_facts: List[str], 
                                      recent_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform context synthesis with performance tracking"""
        start_time = time.time()
        
        try:
            # Use parent class synthesis logic
            prompt = self.context_prompt.format(
                kg_facts="\n".join([f"• {fact}" for fact in kg_facts]),
                recent_context="\n".join([f"{turn['role']}: {turn['content'][:100]}..." for turn in recent_context]),
                user_query=user_query
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            synthesized = json.loads(content)
            
            # Track synthesis time
            synthesis_time = time.time() - start_time
            self._synthesis_times.append(synthesis_time)
            
            return synthesized
            
        except Exception as e:
            print(f"⚠️ Context synthesis failed: {e}")
            return {
                "relevant_facts": kg_facts[:5],  # Fallback to raw facts
                "user_context": {},
                "conversation_summary": "Recent conversation context",
                "suggested_response_tone": "helpful"
            }
    
    def add_turn(self, role: str, content: str) -> str:
        """Add turn and invalidate relevant caches"""
        turn_id = super().add_turn(role, content)
        
        # Invalidate caches that depend on recent data
        self._invalidate_caches_for_new_turn()
        
        return turn_id
    
    def _invalidate_caches_for_new_turn(self):
        """Invalidate caches when new data is added"""
        with self._cache_lock:
            # Invalidate turn and knowledge caches
            keys_to_remove = []
            for key in self._cache_timestamps:
                if key.startswith(f"turns_{self.conversation_id}") or \
                   key.startswith(f"knowledge_{self.conversation_id}") or \
                   key.startswith(f"context_state_{self.conversation_id}"):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._remove_from_cache(key)
            
            # Clear synthesis cache (it depends on current state)
            self._synthesis_cache.clear()
            self._context_cache.clear()
    
    def _create_context_cache_key(self, user_query: str, max_facts: int) -> str:
        """Create cache key for context retrieval"""
        # Include conversation state to ensure cache validity
        state_hash = hashlib.md5(f"{self.conversation_id}_{max_facts}".encode()).hexdigest()[:8]
        query_hash = hashlib.md5(user_query.encode()).hexdigest()[:8]
        return f"context_{state_hash}_{query_hash}"
    
    def _create_synthesis_cache_key(self, user_query: str, kg_facts: List[str]) -> str:
        """Create cache key for LLM synthesis"""
        facts_str = "|".join(kg_facts)
        combined = f"{user_query}|{facts_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cached_context(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached context result"""
        with self._cache_lock:
            if self._is_cache_valid(cache_key):
                result = self._context_cache[cache_key].copy()
                result["cache_info"]["cache_hit"] = True
                return result
            return None
    
    def _cache_context(self, cache_key: str, result: Dict[str, Any]):
        """Cache context result"""
        with self._cache_lock:
            self._context_cache[cache_key] = result.copy()
            self._cache_timestamps[cache_key] = time.time()
            self._cleanup_cache_if_needed()
    
    def _get_cached_synthesis(self, synthesis_key: str) -> Optional[Dict[str, Any]]:
        """Get cached synthesis result"""
        with self._cache_lock:
            if synthesis_key in self._synthesis_cache:
                timestamp = self._cache_timestamps.get(synthesis_key, 0)
                if time.time() - timestamp < self.cache_ttl:
                    return self._synthesis_cache[synthesis_key]
            return None
    
    def _cache_synthesis(self, synthesis_key: str, synthesized_context: Dict[str, Any]):
        """Cache synthesis result"""
        with self._cache_lock:
            self._synthesis_cache[synthesis_key] = synthesized_context
            self._cache_timestamps[synthesis_key] = time.time()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached item is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        age = time.time() - self._cache_timestamps[cache_key]
        return age < self.cache_ttl
    
    def _remove_from_cache(self, cache_key: str):
        """Remove item from all relevant caches"""
        self._fact_cache.pop(cache_key, None)
        self._turn_cache.pop(cache_key, None)
        self._context_cache.pop(cache_key, None)
        self._synthesis_cache.pop(cache_key, None)
        self._cache_timestamps.pop(cache_key, None)
    
    def _cleanup_cache_if_needed(self):
        """Clean up cache if it's getting too large"""
        total_items = len(self._cache_timestamps)
        if total_items > self.cache_size:
            # Remove oldest items
            sorted_items = sorted(self._cache_timestamps.items(), key=lambda x: x[1])
            items_to_remove = sorted_items[:total_items - self.cache_size + 100]  # Remove extra for efficiency
            
            for cache_key, _ in items_to_remove:
                self._remove_from_cache(cache_key)
    
    def _record_cache_hit(self):
        """Record cache hit for statistics"""
        self._cache_hits += 1
    
    def _record_cache_miss(self):
        """Record cache miss for statistics"""
        self._cache_misses += 1
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        avg_query_time = sum(self._query_times) / len(self._query_times) if self._query_times else 0
        avg_synthesis_time = sum(self._synthesis_times) / len(self._synthesis_times) if self._synthesis_times else 0
        
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_cached_items": len(self._cache_timestamps),
            "avg_query_time_ms": round(avg_query_time * 1000, 2),
            "avg_synthesis_time_ms": round(avg_synthesis_time * 1000, 2),
            "cache_size_limit": self.cache_size,
            "cache_ttl_seconds": self.cache_ttl
        }
    
    def clear_cache(self):
        """Clear all caches (useful for testing or debugging)"""
        with self._cache_lock:
            self._fact_cache.clear()
            self._turn_cache.clear()
            self._context_cache.clear()
            self._synthesis_cache.clear()
            self._cache_timestamps.clear()
            print("🧹 All caches cleared")
    
    def warm_cache(self):
        """Pre-populate cache with common queries"""
        print("🔥 Warming up cache...")
        
        # Pre-load recent knowledge and turns
        self._get_recent_knowledge_cached(10)
        self._get_recent_knowledge_cached(20)
        self._get_recent_turns_cached(5)
        self._get_recent_turns_cached(10)
        self._get_context_state_cached()
        
        print("✅ Cache warmed up")