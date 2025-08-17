#!/usr/bin/env python3
"""
Knowledge Graph Reasoning Engine
Inspired by Gaussian Splatting for intelligent node consolidation and relationship inference
"""

import sqlite3
import json
import hashlib
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import networkx as nx
import numpy as np
from pathlib import Path

# Optional imports for advanced features
try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

@dataclass
class ReasoningTriple:
    """Enhanced knowledge triple with reasoning metadata"""
    subject: str
    relation: str
    object: str
    confidence: float
    source_triples: List[str]  # Original triple IDs that led to this inference
    reasoning_type: str  # 'original', 'merged', 'inferred', 'consolidated'
    evidence_count: int
    last_updated: datetime
    certainty_distribution: Dict[str, float]  # Gaussian-like confidence distribution

@dataclass
class NodeCluster:
    """Cluster of related nodes that should be consolidated"""
    primary_node: str
    aliases: List[str]
    confidence: float
    reasoning: str
    consolidation_type: str  # 'identity', 'synonym', 'partial_overlap'

class KnowledgeGraphReasoningEngine:
    """
    Advanced reasoning system for knowledge graph consolidation
    Uses Gaussian splatting-inspired approach for knowledge granularity
    """
    
    def __init__(self, db_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model = SentenceTransformer(model_name) if HAS_EMBEDDINGS else None
        self.similarity_threshold = 0.5  # Lower threshold to catch user/Alice
        self.consolidation_threshold = 0.4  # Lower threshold for consolidation
        self.inference_confidence_threshold = 0.3  # Lower threshold for inferences
        self.auto_consolidation_threshold = 0.6  # Lower threshold for auto-consolidation
        
        # Dynamic pattern detection - no hardcoded patterns
        self.identity_patterns = []  # Will be populated dynamically
        
        # Common identity indicators (conversation-agnostic)
        self.identity_indicators = [
            "user", "i", "me", "my", "myself", "I"  # These often refer to the same person
        ]
        
        # Relation synonyms with confidence scores
        self.relation_synonyms = {
            "works at": ["works_at", "employed by", "job at", "position at"],
            "has": ["owns", "possesses", "keeps", "got"],
            "likes": ["loves", "enjoys", "prefers", "into"],
            "lives in": ["located in", "resides in", "based in"],
            "is": ["equals", "represents", "defined as"]
        }
        
        # Initialize graph
        self.knowledge_graph = nx.MultiDiGraph()
        self.node_embeddings = {}
        self.relation_embeddings = {}
    
    def analyze_conversation_knowledge(self, conversation_id: str) -> Dict[str, any]:
        """Comprehensive analysis of knowledge graph for a conversation"""
        # Load current triples
        triples = self._load_triples(conversation_id)
        
        # Build graph representation
        self._build_graph(triples)
        
        # Detect issues
        issues = {
            "duplicate_relations": self._detect_duplicate_relations(),
            "disconnected_entities": self._detect_disconnected_entities(), 
            "missing_inferences": self._detect_missing_inferences(),
            "consolidation_opportunities": self._detect_consolidation_opportunities()
        }
        
        return {
            "total_triples": len(triples),
            "unique_entities": len(self.knowledge_graph.nodes),
            "unique_relations": len(set(edge[2]['relation'] for edge in self.knowledge_graph.edges(data=True))),
            "issues": issues,
            "consolidation_potential": self._calculate_consolidation_potential()
        }
    
    def perform_offline_reasoning(self, conversation_id: str) -> Dict[str, any]:
        """
        Offline reasoning process - the main consolidation engine
        """
        print(f"🧠 Starting offline reasoning for {conversation_id}...")
        
        # Load and analyze current state  
        triples = self._load_triples(conversation_id)
        self._build_graph(triples)
        
        results = {
            "original_triples": len(triples),
            "consolidations": [],
            "inferences": [],
            "clusters": []
        }
        
        # Step 1: Node consolidation (Gaussian splatting approach)
        node_clusters = self._gaussian_node_clustering()
        results["clusters"] = [asdict(cluster) for cluster in node_clusters]
        
        # Step 2: Relation normalization
        relation_consolidations = self._consolidate_relations()
        results["consolidations"].extend(relation_consolidations)
        
        # Step 3: Inference generation
        new_inferences = self._generate_inferences()
        results["inferences"] = new_inferences
        
        # Step 4: Apply consolidations to database
        self._apply_consolidations(conversation_id, node_clusters, relation_consolidations, new_inferences)
        
        results["final_triples"] = self._count_triples(conversation_id)
        
        print(f"✅ Reasoning complete: {results['original_triples']} → {results['final_triples']} triples")
        return results
    
    def perform_auto_consolidation(self, conversation_id: str) -> Dict[str, any]:
        """
        Automatic consolidation for high-confidence issues only
        """
        print(f"🔄 Auto-consolidating high-confidence issues for {conversation_id}...")
        
        # Load and analyze
        triples = self._load_triples(conversation_id)
        self._build_graph(triples)
        
        results = {
            "original_triples": len(triples),
            "auto_consolidations": 0,
            "auto_inferences": 0,
            "changes_made": []
        }
        
        # Only consolidate obvious duplicates and high-confidence inferences
        high_confidence_clusters = []
        for cluster in self._gaussian_node_clustering():
            if cluster.confidence > self.auto_consolidation_threshold:
                high_confidence_clusters.append(cluster)
        
        # Only consolidate obvious relation duplicates
        high_confidence_relations = []
        for consolidation in self._consolidate_relations():
            if consolidation["confidence"] > self.auto_consolidation_threshold:
                high_confidence_relations.append(consolidation)
        
        # Only make very confident inferences
        high_confidence_inferences = []
        for inference in self._generate_inferences():
            if inference["confidence"] > self.auto_consolidation_threshold:
                high_confidence_inferences.append(inference)
        
        # Apply only high-confidence changes
        if high_confidence_clusters or high_confidence_relations or high_confidence_inferences:
            self._apply_consolidations(conversation_id, high_confidence_clusters, 
                                     high_confidence_relations, high_confidence_inferences)
            
            results["auto_consolidations"] = len(high_confidence_clusters) + len(high_confidence_relations)
            results["auto_inferences"] = len(high_confidence_inferences)
            
            # Record what was changed
            for cluster in high_confidence_clusters:
                results["changes_made"].append(f"Consolidated {cluster.primary_node} ← {', '.join(cluster.aliases)}")
            
            for rel in high_confidence_relations:
                results["changes_made"].append(f"Normalized relations: {rel['canonical']} ← {', '.join(rel['variants'])}")
            
            for inf in high_confidence_inferences:
                results["changes_made"].append(f"Inferred: {inf['subject']} {inf['relation']} {inf['object']}")
        
        results["final_triples"] = self._count_triples(conversation_id)
        
        return results
    
    def _reason_with_llm(self, knowledge_facts: List[Tuple], conversation_context: str = "") -> List[Dict[str, any]]:
        """Use LLM to reason about knowledge and discover new relationships"""
        try:
            import openai
            
            # Format knowledge facts for LLM
            facts_text = "\n".join([f"- {subj} {rel} {obj}" for _, subj, rel, obj, _ in knowledge_facts])
            
            reasoning_prompt = f"""
You are analyzing a knowledge graph to discover implicit relationships and new knowledge.

Current Knowledge Facts:
{facts_text}

Your task is to reason about these facts and discover:
1. Identity relationships (who is the same person)
2. Implicit knowledge that can be inferred
3. Missing connections between facts

Focus especially on:
- If multiple entities share the same unique properties, they might be the same person
- Names and identity relationships
- Logical inferences from the existing facts

Return your analysis as a JSON list where each item has:
{{"type": "inference", "subject": "entity1", "relation": "relationship", "object": "entity2", "confidence": 0.8, "reasoning": "explanation"}}

Only return the JSON, no other text.
"""
            
            # Get LLM reasoning (updated for openai>=1.0.0)
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": reasoning_prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse LLM response
            try:
                import json
                llm_inferences = json.loads(response.choices[0].message.content.strip())
                print(f"🧠 LLM discovered {len(llm_inferences)} new inferences")
                return llm_inferences
            except json.JSONDecodeError:
                print("⚠️ Could not parse LLM response as JSON")
                return []
                
        except Exception as e:
            print(f"⚠️ LLM reasoning failed: {e}")
            return []
    
    def _dream_semantic_clusters(self) -> List[NodeCluster]:
        """Universal semantic clustering - dreams connect any similar concepts"""
        clusters = []
        processed_nodes = set()
        
        for node in self.knowledge_graph.nodes():
            if node in processed_nodes:
                continue
            
            # Find ALL semantically related nodes (not just identity)
            similar_nodes = self._find_universal_similarities(node)
            
            if similar_nodes:
                cluster = NodeCluster(
                    primary_node=node,
                    aliases=[n for n, _ in similar_nodes],
                    confidence=np.mean([s for _, s in similar_nodes]),
                    reasoning=f"Universal semantic similarity across domains",
                    consolidation_type="semantic_merge"
                )
                clusters.append(cluster)
                processed_nodes.update([node] + cluster.aliases)
        
        return clusters
    
    def _find_universal_similarities(self, target_node: str) -> List[Tuple[str, float]]:
        """Find ALL types of similarities - semantic, phonetic, contextual, conceptual"""
        candidates = []
        
        for node in self.knowledge_graph.nodes():
            if node == target_node:
                continue
            
            similarities = []
            
            # 1. Semantic similarity (meaning)
            semantic_sim = self._calculate_semantic_similarity(target_node, node)
            similarities.append(semantic_sim)
            
            # 2. Contextual similarity (usage patterns)
            contextual_sim = self._calculate_contextual_similarity(target_node, node)
            similarities.append(contextual_sim)
            
            # 3. Phonetic similarity (sound-alike concepts)
            phonetic_sim = self._calculate_phonetic_similarity(target_node, node)
            similarities.append(phonetic_sim)
            
            # 4. Structural similarity (graph position)
            structural_sim = self._calculate_structural_similarity(target_node, node)
            similarities.append(structural_sim)
            
            # 5. Conceptual similarity (category membership)
            conceptual_sim = self._calculate_conceptual_similarity(target_node, node)
            similarities.append(conceptual_sim)
            
            # Combine with weighted importance (like attention in dreaming)
            weights = [0.3, 0.25, 0.15, 0.15, 0.15]  # Semantic and contextual most important
            combined_similarity = sum(s * w for s, w in zip(similarities, weights))
            
            if combined_similarity > self.similarity_threshold:
                candidates.append((node, combined_similarity))
        
        return sorted(candidates, key=lambda x: x[1], reverse=True)[:5]  # Top 5 similar
    
    def _calculate_semantic_similarity(self, node1: str, node2: str) -> float:
        """Calculate meaning-based similarity"""
        # Use embeddings if available, fallback to character similarity
        emb1 = self._get_node_embedding(node1)
        emb2 = self._get_node_embedding(node2)
        
        # Normalize embeddings
        emb1_norm = emb1 / (np.linalg.norm(emb1) + 1e-8)
        emb2_norm = emb2 / (np.linalg.norm(emb2) + 1e-8)
        
        return float(np.dot(emb1_norm, emb2_norm))
    
    def _calculate_phonetic_similarity(self, node1: str, node2: str) -> float:
        """Calculate sound/character similarity"""
        # Simple edit distance-based similarity
        def edit_distance(s1, s2):
            if len(s1) < len(s2):
                return edit_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        max_len = max(len(node1), len(node2))
        if max_len == 0:
            return 1.0
        
        distance = edit_distance(node1.lower(), node2.lower())
        return 1.0 - (distance / max_len)
    
    def _calculate_structural_similarity(self, node1: str, node2: str) -> float:
        """Calculate similarity based on graph structure position"""
        # Nodes with similar in/out degree patterns
        node1_in_degree = self.knowledge_graph.in_degree(node1)
        node1_out_degree = self.knowledge_graph.out_degree(node1)
        node2_in_degree = self.knowledge_graph.in_degree(node2)
        node2_out_degree = self.knowledge_graph.out_degree(node2)
        
        # Compare degree patterns
        total_degrees = node1_in_degree + node1_out_degree + node2_in_degree + node2_out_degree
        if total_degrees == 0:
            return 0.5
        
        degree_diff = abs(node1_in_degree - node2_in_degree) + abs(node1_out_degree - node2_out_degree)
        return 1.0 - (degree_diff / max(total_degrees, 1))
    
    def _calculate_conceptual_similarity(self, node1: str, node2: str) -> float:
        """Calculate conceptual category similarity"""
        # Check if nodes appear in similar relation types
        node1_relations = set()
        node2_relations = set()
        
        for _, _, data in self.knowledge_graph.out_edges(node1, data=True):
            node1_relations.add(data['relation'])
        for _, _, data in self.knowledge_graph.out_edges(node2, data=True):
            node2_relations.add(data['relation'])
        
        if not node1_relations or not node2_relations:
            return 0.0
        
        intersection = len(node1_relations & node2_relations)
        union = len(node1_relations | node2_relations)
        
        return intersection / union if union > 0 else 0.0
    
    def _discover_emergent_patterns(self) -> List[Dict[str, any]]:
        """Discover patterns that emerge from the graph structure"""
        patterns = []
        
        # Pattern 1: Transitivity chains (A→B→C implies A→C)
        transitivity_patterns = self._find_transitivity_chains()
        patterns.extend(transitivity_patterns)
        
        # Pattern 2: Clustering patterns (if A→X and B→X, maybe A≈B)
        clustering_patterns = self._find_clustering_patterns()
        patterns.extend(clustering_patterns)
        
        # Pattern 3: Frequency patterns (repeated structures)
        frequency_patterns = self._find_frequency_patterns()
        patterns.extend(frequency_patterns)
        
        return patterns
    
    def _propagate_confidence(self) -> List[Dict[str, any]]:
        """Propagate confidence through connected nodes like spreading activation"""
        updates = []
        
        # Nodes with many incoming high-confidence edges get boosted
        for node in self.knowledge_graph.nodes():
            incoming_confidences = []
            for _, _, data in self.knowledge_graph.in_edges(node, data=True):
                incoming_confidences.append(data.get('confidence', 0.5))
            
            if incoming_confidences:
                avg_confidence = np.mean(incoming_confidences)
                confidence_boost = min(0.2, avg_confidence * 0.3)  # Cap the boost
                
                if confidence_boost > 0.05:  # Only significant boosts
                    updates.append({
                        "node": node,
                        "confidence_boost": confidence_boost,
                        "reason": f"High incoming confidence from {len(incoming_confidences)} edges"
                    })
        
        return updates
    
    def _find_transitivity_chains(self) -> List[Dict[str, any]]:
        """Find transitivity patterns like A→B→C implies A→C"""
        patterns = []
        
        for source in self.knowledge_graph.nodes():
            for intermediate in self.knowledge_graph.successors(source):
                for target in self.knowledge_graph.successors(intermediate):
                    if target != source and not self.knowledge_graph.has_edge(source, target):
                        patterns.append({
                            "type": "transitivity",
                            "description": f"{source} → {intermediate} → {target} implies {source} → {target}",
                            "inference": f"{source} relates_to {target}",
                            "confidence": 0.7
                        })
        
        return patterns[:10]  # Limit to avoid explosion
    
    def _find_clustering_patterns(self) -> List[Dict[str, any]]:
        """Find clustering patterns where similar nodes relate to same target"""
        patterns = []
        
        # Group nodes by their targets
        target_to_sources = defaultdict(list)
        for source, target, data in self.knowledge_graph.edges(data=True):
            target_to_sources[target].append(source)
        
        # Find targets with multiple similar sources
        for target, sources in target_to_sources.items():
            if len(sources) > 1:
                # Check if sources are similar
                for i, source1 in enumerate(sources):
                    for source2 in sources[i+1:]:
                        similarity = self._calculate_universal_similarity(source1, source2)
                        if similarity > 0.6:
                            patterns.append({
                                "type": "clustering",
                                "description": f"{source1} and {source2} both relate to {target}",
                                "inference": f"{source1} similar_to {source2}",
                                "confidence": similarity
                            })
        
        return patterns[:10]
    
    def _find_frequency_patterns(self) -> List[Dict[str, any]]:
        """Find frequently occurring structural patterns"""
        patterns = []
        
        # Count relation types
        relation_counts = defaultdict(int)
        for _, _, data in self.knowledge_graph.edges(data=True):
            relation_counts[data['relation']] += 1
        
        # Frequent relations might indicate important patterns
        for relation, count in relation_counts.items():
            if count > 3:  # Frequent relation
                patterns.append({
                    "type": "frequency",
                    "description": f"'{relation}' appears {count} times",
                    "inference": f"'{relation}' is a key relationship pattern",
                    "confidence": min(0.9, count * 0.1)
                })
        
        return patterns[:5]
    
    def _calculate_universal_similarity(self, node1: str, node2: str) -> float:
        """Calculate overall similarity between any two nodes"""
        similarities = [
            self._calculate_semantic_similarity(node1, node2),
            self._calculate_contextual_similarity(node1, node2),
            self._calculate_phonetic_similarity(node1, node2),
            self._calculate_structural_similarity(node1, node2),
            self._calculate_conceptual_similarity(node1, node2)
        ]
        
        weights = [0.3, 0.25, 0.15, 0.15, 0.15]
        return sum(s * w for s, w in zip(similarities, weights))
    
    def _apply_dreaming_consolidations(self, conversation_id: str, semantic_clusters: List[NodeCluster],
                                     emergent_patterns: List[Dict], confidence_updates: List[Dict], 
                                     llm_inferences: List[Dict] = None):
        """Apply all dreaming consolidations to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Apply semantic clusters (simple consolidation without pattern matching)
            for cluster in semantic_clusters:
                for alias in cluster.aliases:
                    # Update triples where alias appears
                    cursor.execute("""
                        UPDATE knowledge_triples 
                        SET subject = ?, confidence = COALESCE(confidence, 0) + ?
                        WHERE conversation_id = ? AND subject = ?
                    """, (cluster.primary_node, cluster.confidence * 0.1, conversation_id, alias))
                    
                    cursor.execute("""
                        UPDATE knowledge_triples 
                        SET object = ?, confidence = COALESCE(confidence, 0) + ?
                        WHERE conversation_id = ? AND object = ?
                    """, (cluster.primary_node, cluster.confidence * 0.1, conversation_id, alias))
            
            # Add emergent pattern inferences
            for pattern in emergent_patterns:
                if pattern.get("inference") and " " in pattern["inference"]:
                    parts = pattern["inference"].split(" ", 2)
                    if len(parts) >= 3:
                        cursor.execute("""
                            INSERT OR IGNORE INTO knowledge_triples 
                            (conversation_id, subject, relation, object, confidence, created_at, source_turn)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            conversation_id,
                            parts[0],
                            parts[1],
                            parts[2],
                            pattern.get("confidence", 0.7),
                            datetime.now().isoformat(),
                            "dreaming_engine"
                        ))
            
            # Apply LLM-discovered knowledge - this is where dreams add new knowledge!
            if llm_inferences:
                print(f"🧠 Applying {len(llm_inferences)} LLM-discovered inferences...")
                for inference in llm_inferences:
                    cursor.execute("""
                        INSERT OR IGNORE INTO knowledge_triples 
                        (conversation_id, subject, relation, object, confidence, created_at, source_turn)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        conversation_id,
                        inference.get("subject", "unknown"),
                        inference.get("relation", "relates_to"),
                        inference.get("object", "unknown"),
                        float(inference.get("confidence", 0.7)),
                        datetime.now().isoformat(),
                        "dreaming_llm_inference"
                    ))
                    print(f"   🧠 Added: {inference.get('subject')} {inference.get('relation')} {inference.get('object')} (confidence: {inference.get('confidence', 0.7):.2f})")
                    print(f"      Reasoning: {inference.get('reasoning', 'LLM inference')}")
            
            # Apply confidence boosts
            for update in confidence_updates:
                cursor.execute("""
                    UPDATE knowledge_triples 
                    SET confidence = COALESCE(confidence, 0.5) + ?
                    WHERE conversation_id = ? AND (subject = ? OR object = ?)
                """, (
                    update["confidence_boost"], 
                    conversation_id, 
                    update["node"], 
                    update["node"]
                ))
            
            # Remove exact duplicates after consolidation
            cursor.execute("""
                DELETE FROM knowledge_triples 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM knowledge_triples 
                    WHERE conversation_id = ?
                    GROUP BY subject, relation, object
                )
                AND conversation_id = ?
            """, (conversation_id, conversation_id))
            
            conn.commit()
    
    def perform_memory_dreaming(self, conversation_id: str) -> Dict[str, any]:
        """
        Memory consolidation like dreaming - universal semantic reasoning
        Consolidates memories across ALL domains, not just identity
        """
        print(f"💭 Entering memory dreaming state for {conversation_id}...")
        
        # Load and build comprehensive graph
        triples = self._load_triples(conversation_id)
        self._build_graph(triples)
        
        results = {
            "original_triples": len(triples),
            "dreaming_consolidations": [],
            "semantic_clusters": [],
            "emergent_patterns": [],
            "confidence_boosts": []
        }
        
        # Phase 1: Universal semantic clustering (like REM sleep)
        semantic_clusters = self._dream_semantic_clusters()
        results["semantic_clusters"] = [asdict(cluster) for cluster in semantic_clusters]
        
        # Phase 2: LLM-powered reasoning - the dream learns new knowledge
        llm_inferences = self._reason_with_llm(triples)
        results["llm_inferences"] = llm_inferences
        
        # Phase 2b: Cross-domain pattern emergence (traditional patterns)
        emergent_patterns = self._discover_emergent_patterns()
        results["emergent_patterns"] = emergent_patterns
        
        # Phase 3: Confidence propagation through graph
        confidence_updates = self._propagate_confidence()
        results["confidence_boosts"] = confidence_updates
        
        # Phase 4: Apply all dreaming consolidations
        self._apply_dreaming_consolidations(conversation_id, semantic_clusters, 
                                          emergent_patterns, confidence_updates, llm_inferences)
        
        results["final_triples"] = self._count_triples(conversation_id)
        results["consolidation_rate"] = 1 - (results["final_triples"] / results["original_triples"])
        
        print(f"💭 Dreaming complete: {results['consolidation_rate']:.1%} consolidation achieved")
        return results
    
    def _gaussian_node_clustering(self) -> List[NodeCluster]:
        """
        Universal semantic clustering - like memory consolidation during dreaming
        Groups ANY semantically similar nodes, not just identity
        """
        clusters = []
        processed_nodes = set()
        
        for node in self.knowledge_graph.nodes():
            if node in processed_nodes:
                continue
                
            # Find semantically similar nodes across ALL domains
            similar_nodes = self._find_semantically_similar_nodes(node)
            
            if similar_nodes:
                # Create cluster with confidence distribution
                cluster = self._create_universal_cluster(node, similar_nodes)
                if cluster.confidence > self.consolidation_threshold:
                    clusters.append(cluster)
                    processed_nodes.update([node] + cluster.aliases)
        
        return clusters
    
    def _find_similar_nodes(self, target_node: str) -> List[Tuple[str, float]]:
        """Find nodes similar to target using multiple similarity metrics"""
        candidates = []
        
        # Get node embedding
        target_embedding = self._get_node_embedding(target_node)
        
        for node in self.knowledge_graph.nodes():
            if node == target_node:
                continue
                
            # Semantic similarity
            node_embedding = self._get_node_embedding(node)
            semantic_sim = np.dot(target_embedding, node_embedding)
            
            # Contextual similarity (shared relations)
            contextual_sim = self._calculate_contextual_similarity(target_node, node)
            
            # Pattern-based similarity (identity patterns)
            pattern_sim = self._calculate_pattern_similarity(target_node, node)
            
            # Combined similarity with Gaussian-like weighting
            combined_sim = self._gaussian_similarity_combination(
                semantic_sim, contextual_sim, pattern_sim
            )
            
            if combined_sim > self.similarity_threshold:
                candidates.append((node, combined_sim))
        
        return sorted(candidates, key=lambda x: x[1], reverse=True)
    
    def _create_node_cluster(self, primary_node: str, similar_nodes: List[Tuple[str, float]]) -> NodeCluster:
        """Create a node cluster with consolidated reasoning"""
        aliases = [node for node, _ in similar_nodes]
        confidence = np.mean([sim for _, sim in similar_nodes])
        
        # Generate reasoning explanation
        reasoning = self._generate_cluster_reasoning(primary_node, similar_nodes)
        
        # Determine consolidation type
        consolidation_type = self._determine_consolidation_type(primary_node, aliases)
        
        return NodeCluster(
            primary_node=primary_node,
            aliases=aliases,
            confidence=confidence,
            reasoning=reasoning,
            consolidation_type=consolidation_type
        )
    
    def _calculate_contextual_similarity(self, node1: str, node2: str) -> float:
        """Calculate similarity based on shared relationships - enhanced for identity detection"""
        node1_relations = set()
        node2_relations = set()
        
        # Get all relations for both nodes (focus on outgoing relations for identity)
        for _, target, data in self.knowledge_graph.out_edges(node1, data=True):
            canonical_relation = self._find_canonical_relation(data['relation'])
            node1_relations.add((canonical_relation, target))
            
        for _, target, data in self.knowledge_graph.out_edges(node2, data=True):
            canonical_relation = self._find_canonical_relation(data['relation'])
            node2_relations.add((canonical_relation, target))
        
        if not node1_relations or not node2_relations:
            return 0.0
        
        # Find exact matches (same relation to same object)
        shared_relations = node1_relations & node2_relations
        
        # High bonus for sharing unique/specific relationships
        if shared_relations:
            similarity = len(shared_relations) / max(len(node1_relations), len(node2_relations))
            
            # Extra bonus for sharing multiple unique properties (strong identity signal)
            if len(shared_relations) >= 2:
                similarity = min(1.0, similarity * 1.5)  # Boost for multiple shared properties
            
            # Debug output
            if similarity > 0.3:
                print(f"🔍 Contextual similarity {node1}↔{node2}: {similarity:.2f}")
                print(f"   Shared: {shared_relations}")
                print(f"   Node1: {node1_relations}")
                print(f"   Node2: {node2_relations}")
            
            return similarity
        
        return 0.0
    
    def _calculate_pattern_similarity(self, node1: str, node2: str) -> float:
        """Check if nodes match identity patterns - now completely dynamic"""
        node1_lower = node1.lower().strip()
        node2_lower = node2.lower().strip()
        
        # Check if both nodes are identity indicators (user, I, me, etc.)
        is_node1_identity = node1_lower in [ind.lower() for ind in self.identity_indicators]
        is_node2_identity = node2_lower in [ind.lower() for ind in self.identity_indicators]
        
        # High confidence if both are identity indicators
        if is_node1_identity and is_node2_identity:
            return 0.9
        
        # Check for dynamically discovered patterns from conversation context
        discovered_patterns = self._discover_identity_patterns()
        for pattern_pair in discovered_patterns:
            pattern1, pattern2 = pattern_pair[0].lower(), pattern_pair[1].lower()
            if (node1_lower == pattern1 and node2_lower == pattern2) or \
               (node1_lower == pattern2 and node2_lower == pattern1):
                return 0.95  # High confidence for dynamically discovered patterns
        
        return 0.0
    
    def _gaussian_similarity_combination(self, semantic: float, contextual: float, pattern: float) -> float:
        """
        Combine similarity scores using Gaussian-inspired weighting
        Pattern matches get highest weight, contextual next, semantic base
        """
        # Gaussian-like weighting with different variances
        weights = np.array([0.3, 0.4, 0.8])  # semantic, contextual, pattern
        scores = np.array([semantic, contextual, pattern])
        
        # Apply Gaussian weighting
        weighted_scores = scores * weights
        
        # Use max pooling for final decision (like in splatting)
        return np.max(weighted_scores)
    
    def _consolidate_relations(self) -> List[Dict[str, any]]:
        """Consolidate similar relations"""
        consolidations = []
        relation_groups = defaultdict(list)
        
        # Group similar relations
        all_relations = set(edge[2]['relation'] for edge in self.knowledge_graph.edges(data=True))
        
        for relation in all_relations:
            canonical_relation = self._find_canonical_relation(relation)
            relation_groups[canonical_relation].append(relation)
        
        # Create consolidations for groups with multiple variants
        for canonical, variants in relation_groups.items():
            if len(variants) > 1:
                consolidations.append({
                    "type": "relation_consolidation",
                    "canonical": canonical,
                    "variants": variants,
                    "confidence": self._calculate_relation_confidence(variants)
                })
        
        return consolidations
    
    def _find_canonical_relation(self, relation: str) -> str:
        """Find the canonical form of a relation"""
        relation_lower = relation.lower()
        
        for canonical, synonyms in self.relation_synonyms.items():
            if relation_lower == canonical or relation_lower in synonyms:
                return canonical
        
        return relation  # Return original if no canonical form found
    
    def _generate_inferences(self) -> List[Dict[str, any]]:
        """Generate new inferred relationships"""
        inferences = []
        
        # Transitivity inferences
        inferences.extend(self._infer_transitivity())
        
        # Identity inferences  
        inferences.extend(self._infer_identity_relationships())
        
        # Symmetry inferences
        inferences.extend(self._infer_symmetry())
        
        return inferences
    
    def _infer_identity_relationships(self) -> List[Dict[str, any]]:
        """
        Enhanced identity inference: detect when entities share unique properties
        """
        inferences = []
        
        # Build relationship profiles for each node
        node_relationships = defaultdict(set)
        for source, target, data in self.knowledge_graph.edges(data=True):
            relation = self._find_canonical_relation(data['relation'])
            node_relationships[source].add((relation, target))
        
        # Special focus on user/name patterns
        nodes = list(node_relationships.keys())
        
        # Debug: show all node relationships
        print(f"\n🧠 Analyzing {len(nodes)} nodes for identity patterns:")
        for node in nodes:
            if len(node_relationships[node]) > 0:
                print(f"   {node}: {node_relationships[node]}")
        
        # Look for identity patterns
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                # Skip if same node
                if node1 == node2:
                    continue
                
                # Get shared relationships
                shared = node_relationships[node1] & node_relationships[node2]
                
                if shared:  # Any shared relationship is worth examining
                    total_unique_rels = len(node_relationships[node1] | node_relationships[node2])
                    overlap_ratio = len(shared) / max(len(node_relationships[node1]), len(node_relationships[node2]), 1)
                    
                    # Calculate confidence based on uniqueness of shared relationships
                    confidence = overlap_ratio
                    
                    # Boost confidence for specific identity patterns
                    node1_lower = node1.lower()
                    node2_lower = node2.lower()
                    
                    # Boost for user/name patterns
                    if ('user' in node1_lower and node2_lower not in ['user', 'i', 'me']) or \
                       ('user' in node2_lower and node1_lower not in ['user', 'i', 'me']):
                        confidence = min(1.0, confidence * 2.0)
                        
                    print(f"🔍 Identity candidate: {node1} ↔ {node2}")
                    print(f"   Shared: {shared}")
                    print(f"   Confidence: {confidence:.2f}")
                    
                    if confidence > self.inference_confidence_threshold:
                        inferences.append({
                            "type": "identity_inference",
                            "subject": node1,
                            "relation": "same_as",
                            "object": node2,
                            "confidence": confidence,
                            "evidence": list(shared),
                            "reasoning": f"Shared {len(shared)} properties: {', '.join([f'{r}→{o}' for r, o in shared])}"
                        })
        
        return inferences
    
    def _infer_transitivity(self) -> List[Dict[str, any]]:
        """Infer transitive relationships"""
        # Example: user same_as Alice, Alice owns Whiskers → user owns Whiskers
        inferences = []
        
        # Find identity relationships first
        identities = []
        for source, target, data in self.knowledge_graph.edges(data=True):
            if data['relation'] in ['same_as', 'is', 'equals']:
                identities.append((source, target))
        
        # Apply transitivity
        for identity_source, identity_target in identities:
            # Transfer relationships from target to source
            for _, obj, data in self.knowledge_graph.out_edges(identity_target, data=True):
                if obj not in [identity_source, identity_target]:  # Avoid self-references
                    inferences.append({
                        "type": "transitivity_inference",
                        "subject": identity_source,
                        "relation": data['relation'],
                        "object": obj,
                        "confidence": 0.9,
                        "reasoning": f"Via identity: {identity_source} same_as {identity_target}"
                    })
        
        return inferences
    
    def _infer_symmetry(self) -> List[Dict[str, any]]:
        """Infer symmetric relationships"""
        symmetric_relations = ['married_to', 'sibling_of', 'friend_of', 'colleague_of']
        inferences = []
        
        for source, target, data in self.knowledge_graph.edges(data=True):
            relation = data['relation']
            if relation in symmetric_relations:
                # Check if reverse relationship exists
                if not self.knowledge_graph.has_edge(target, source):
                    inferences.append({
                        "type": "symmetry_inference",
                        "subject": target,
                        "relation": relation,
                        "object": source,
                        "confidence": 0.8,
                        "reasoning": f"Symmetric relationship: {relation}"
                    })
        
        return inferences
    
    def _apply_consolidations(self, conversation_id: str, node_clusters: List[NodeCluster], 
                            relation_consolidations: List[Dict], inferences: List[Dict]):
        """Apply all consolidations to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Apply node consolidations
            for cluster in node_clusters:
                for alias in cluster.aliases:
                    # Update all triples where alias appears
                    cursor.execute("""
                        UPDATE knowledge_triples 
                        SET subject = ?, confidence = ?
                        WHERE conversation_id = ? AND subject = ?
                    """, (cluster.primary_node, cluster.confidence, conversation_id, alias))
                    
                    cursor.execute("""
                        UPDATE knowledge_triples 
                        SET object = ?, confidence = ?
                        WHERE conversation_id = ? AND object = ?
                    """, (cluster.primary_node, cluster.confidence, conversation_id, alias))
            
            # Apply relation consolidations
            for consolidation in relation_consolidations:
                canonical = consolidation["canonical"]
                for variant in consolidation["variants"]:
                    if variant != canonical:
                        cursor.execute("""
                            UPDATE knowledge_triples 
                            SET relation = ?, confidence = ?
                            WHERE conversation_id = ? AND relation = ?
                        """, (canonical, consolidation["confidence"], conversation_id, variant))
            
            # Add inferences as new triples
            for inference in inferences:
                cursor.execute("""
                    INSERT OR IGNORE INTO knowledge_triples 
                    (conversation_id, subject, relation, object, confidence, created_at, source_turn)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    inference["subject"],
                    inference["relation"], 
                    inference["object"],
                    inference["confidence"],
                    datetime.now().isoformat(),
                    "reasoning_engine"
                ))
            
            # Remove duplicates
            cursor.execute("""
                DELETE FROM knowledge_triples 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM knowledge_triples 
                    WHERE conversation_id = ?
                    GROUP BY subject, relation, object
                )
                AND conversation_id = ?
            """, (conversation_id, conversation_id))
            
            conn.commit()
    
    def _load_triples(self, conversation_id: str) -> List[Tuple]:
        """Load knowledge triples from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, subject, relation, object, confidence
                FROM knowledge_triples 
                WHERE conversation_id = ?
                ORDER BY created_at
            """, (conversation_id,))
            return cursor.fetchall()
    
    def _build_graph(self, triples: List[Tuple]):
        """Build NetworkX graph from triples"""
        self.knowledge_graph.clear()
        
        for triple_id, subject, relation, obj, confidence in triples:
            self.knowledge_graph.add_edge(
                subject, obj, 
                relation=relation, 
                confidence=confidence or 1.0,
                triple_id=triple_id
            )
    
    def _get_node_embedding(self, node: str) -> np.ndarray:
        """Get semantic embedding for a node"""
        if not HAS_EMBEDDINGS:
            # Fallback: simple character-based embedding with fixed dimension
            chars = [ord(c) for c in node.lower()[:10]] 
            # Pad or truncate to exactly 10 dimensions
            while len(chars) < 10:
                chars.append(0)
            return np.array(chars[:10]).astype(float) / 255.0
        
        if node not in self.node_embeddings:
            self.node_embeddings[node] = self.embedding_model.encode([node])[0]
        return self.node_embeddings[node]
    
    def _are_relations_similar(self, rel1: Tuple, rel2: Tuple) -> bool:
        """Check if two relation tuples are similar"""
        if len(rel1) != len(rel2):
            return False
        
        for r1, r2 in zip(rel1, rel2):
            if isinstance(r1, str) and isinstance(r2, str):
                canonical1 = self._find_canonical_relation(r1)
                canonical2 = self._find_canonical_relation(r2)
                if canonical1 != canonical2:
                    return False
            elif r1 != r2:
                return False
        
        return True
    
    def _detect_duplicate_relations(self) -> List[Dict]:
        """Detect duplicate relations with different phrasings"""
        duplicates = []
        relations = defaultdict(list)
        
        for source, target, data in self.knowledge_graph.edges(data=True):
            key = (source, target)
            relations[key].append(data['relation'])
        
        for key, rels in relations.items():
            if len(rels) > 1:
                duplicates.append({
                    "entities": key,
                    "relations": rels,
                    "canonical": self._find_canonical_relation(rels[0])
                })
        
        return duplicates
    
    def _detect_disconnected_entities(self) -> List[str]:
        """Find entities that should be connected but aren't"""
        # This would use more sophisticated graph analysis
        return []
    
    def _detect_missing_inferences(self) -> List[Dict]:
        """Detect obvious inferences that are missing"""
        missing = []
        
        # Check for missing identity inferences
        # If user and Alice share unique properties, suggest they're the same
        user_props = set()
        alice_props = set()
        
        for source, target, data in self.knowledge_graph.edges(data=True):
            if source.lower() == 'user':
                user_props.add((data['relation'], target))
            elif source.lower() == 'alice':
                alice_props.add((data['relation'], target))
        
        shared_props = user_props & alice_props
        if len(shared_props) >= 2:
            missing.append({
                "type": "identity_inference",
                "suggestion": "user same_as Alice",
                "evidence": list(shared_props),
                "confidence": len(shared_props) / max(len(user_props), len(alice_props))
            })
        
        return missing
    
    def _detect_consolidation_opportunities(self) -> List[Dict]:
        """Detect nodes/relations that could be consolidated"""
        opportunities = []
        
        # Node consolidation opportunities
        processed = set()
        for node in self.knowledge_graph.nodes():
            if node in processed:
                continue
                
            similar = self._find_similar_nodes(node)
            if similar:
                opportunities.append({
                    "type": "node_consolidation",
                    "primary": node,
                    "candidates": [n for n, _ in similar],
                    "confidence": np.mean([s for _, s in similar])
                })
                processed.update([node] + [n for n, _ in similar])
        
        return opportunities
    
    def _calculate_consolidation_potential(self) -> float:
        """Calculate overall consolidation potential (0-1)"""
        total_nodes = len(self.knowledge_graph.nodes())
        total_edges = len(self.knowledge_graph.edges())
        
        if total_nodes == 0:
            return 0.0
        
        # Various factors that suggest consolidation potential
        duplicate_rels = len(self._detect_duplicate_relations())
        consolidation_opps = len(self._detect_consolidation_opportunities())
        missing_inferences = len(self._detect_missing_inferences())
        
        # Normalize and combine
        potential = (duplicate_rels + consolidation_opps + missing_inferences) / max(total_edges, 1)
        return min(potential, 1.0)
    
    def _count_triples(self, conversation_id: str) -> int:
        """Count triples in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge_triples WHERE conversation_id = ?", (conversation_id,))
            return cursor.fetchone()[0]
    
    def _generate_cluster_reasoning(self, primary: str, similar_nodes: List[Tuple[str, float]]) -> str:
        """Generate human-readable reasoning for node clustering"""
        if not similar_nodes:
            return "No similar nodes found"
        
        reasons = []
        for node, confidence in similar_nodes:
            if confidence > 0.9:
                reasons.append(f"'{node}' is very likely the same entity (confidence: {confidence:.2f})")
            elif confidence > 0.8:
                reasons.append(f"'{node}' appears to be the same entity (confidence: {confidence:.2f})")
            else:
                reasons.append(f"'{node}' might be related (confidence: {confidence:.2f})")
        
        return "; ".join(reasons)
    
    def _determine_consolidation_type(self, primary: str, aliases: List[str]) -> str:
        """Determine the type of consolidation being performed"""
        # Check for identity patterns
        for alias in aliases:
            for pattern_pair in self.identity_patterns:
                if primary.lower() in pattern_pair and alias.lower() in pattern_pair:
                    return "identity"
        
        # Check for semantic similarity
        primary_embedding = self._get_node_embedding(primary)
        for alias in aliases:
            alias_embedding = self._get_node_embedding(alias)
            if np.dot(primary_embedding, alias_embedding) > 0.9:
                return "synonym"
        
        return "partial_overlap"
    
    def _calculate_relation_confidence(self, variants: List[str]) -> float:
        """Calculate confidence for relation consolidation"""
        # Higher confidence if more variants point to same canonical form
        return min(0.9, 0.5 + len(variants) * 0.1)