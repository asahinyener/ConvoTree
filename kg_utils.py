#!/usr/bin/env python3
# ConvoTree Knowledge Graph Utilities
# ─────────────────────────────────────────────────────────────────────────────
import os
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class EntityNormalizer:
    """Class to normalize entity names in the knowledge graph."""
    
    def __init__(self):
        self.entity_map = {}  # Maps variant forms to canonical form
        self.entity_counts = {}  # Tracks how many times each entity is referenced
    
    def normalize(self, entity: str) -> str:
        """Normalize an entity name to its canonical form."""
        # Remove leading/trailing whitespace and convert to title case for consistency
        entity = entity.strip()
        
        # Skip normalization for very short entities or those that are already normalized
        if len(entity) <= 2 or entity in self.entity_map.values():
            return entity
            
        # Check if this is a variant of an existing entity
        lower_entity = entity.lower()
        
        # Look for existing entities that might be variants
        for canonical in list(self.entity_map.values()):
            # If entities are very similar, map to the canonical form
            if (lower_entity in canonical.lower() or 
                canonical.lower() in lower_entity or
                self._similarity_score(lower_entity, canonical.lower()) > 0.8):
                
                self.entity_map[entity] = canonical
                self.entity_counts[canonical] = self.entity_counts.get(canonical, 0) + 1
                return canonical
        
        # If no match found, this becomes a new canonical entity
        self.entity_map[entity] = entity
        self.entity_counts[entity] = 1
        return entity
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate a simple similarity score between two strings."""
        # Simple implementation - can be replaced with more sophisticated algorithms
        if not str1 or not str2:
            return 0.0
            
        # Count common words
        words1 = set(str1.split())
        words2 = set(str2.split())
        common_words = words1.intersection(words2)
        
        if not words1 or not words2:
            return 0.0
            
        # Jaccard similarity
        return len(common_words) / len(words1.union(words2))
    
    def get_canonical_entities(self) -> List[str]:
        """Get a list of all canonical entities, sorted by frequency."""
        return sorted(self.entity_map.values(), 
                     key=lambda x: self.entity_counts.get(x, 0), 
                     reverse=True)


def normalize_triple(triple: str, normalizer: EntityNormalizer) -> str:
    """Normalize a knowledge graph triple."""
    try:
        s, p, o = (x.strip() for x in triple.split("|", 2))
        
        # Normalize subject and object
        s_norm = normalizer.normalize(s)
        o_norm = normalizer.normalize(o)
        
        # Ensure predicate is lowercase and clean
        p_norm = p.lower().strip()
        
        # Reconstruct the triple
        return f"{s_norm}|{p_norm}|{o_norm}"
    except ValueError:
        # If triple doesn't split properly, return as is
        return triple


def normalize_kg(triples: List[str]) -> List[str]:
    """Normalize all triples in a knowledge graph."""
    normalizer = EntityNormalizer()
    normalized_triples = []
    seen_triples = set()
    
    for triple in triples:
        norm_triple = normalize_triple(triple, normalizer)
        
        # Deduplicate triples
        if norm_triple not in seen_triples:
            normalized_triples.append(norm_triple)
            seen_triples.add(norm_triple)
    
    return normalized_triples


def draw_kg(triples: List[str], outfile: Path) -> None:
    """Render a simple force-layout PNG of the KG triples."""
    if not triples:
        return
        
    # Normalize the triples for better visualization
    normalized_triples = normalize_kg(triples)
    
    G = nx.DiGraph()
    for trip in normalized_triples:
        try:
            s, p, o = (x.strip() for x in trip.split("|", 2))
        except ValueError:
            continue
        G.add_edge(s, o, label=p)
    
    # Use a better layout for more complex graphs
    if len(G.nodes) > 10:
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, k=0.6, seed=42)
    
    plt.figure(figsize=(10, 8))
    
    # Draw nodes with size based on degree centrality
    centrality = nx.degree_centrality(G)
    node_sizes = [300 + 700 * centrality[node] for node in G.nodes()]
    
    # Use different colors for different node types
    node_colors = []
    for node in G.nodes():
        if any(kw in node.lower() for kw in ['quantum', 'qubit', 'algorithm']):
            node_colors.append('lightblue')
        elif any(kw in node.lower() for kw in ['research', 'study', 'science']):
            node_colors.append('lightgreen')
        elif any(kw in node.lower() for kw in ['problem', 'challenge', 'issue']):
            node_colors.append('salmon')
        else:
            node_colors.append('lightyellow')
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="-|>", width=1.5, alpha=0.7)
    
    # Improve label readability
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    
    # Draw edge labels with better positioning
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=8, 
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2)
    )
    
    plt.axis("off")
    plt.tight_layout()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outfile, dpi=200)
    plt.close()


class KnowledgePrioritizer:
    """Class to prioritize knowledge graph triples based on importance."""
    
    def __init__(self):
        self.triple_scores = {}  # Maps triples to their importance scores
        self.recency_factor = 0.8  # Weight for recency in scoring
        self.relevance_factor = 0.6  # Weight for relevance to current topic
        self.confidence_factor = 0.4  # Weight for confidence in the triple
    
    def score_triple(self, triple: str, recency: float = 0.5, 
                    relevance: float = 0.5, confidence: float = 1.0) -> float:
        """Score a triple based on recency, relevance, and confidence."""
        # Recency: How recently was this triple added/updated (0-1)
        # Relevance: How relevant is this triple to current conversation (0-1)
        # Confidence: How confident are we in this triple (0-1)
        
        score = (self.recency_factor * recency + 
                self.relevance_factor * relevance + 
                self.confidence_factor * confidence)
        
        # Normalize to 0-1 range
        max_score = self.recency_factor + self.relevance_factor + self.confidence_factor
        normalized_score = score / max_score
        
        # Store the score
        self.triple_scores[triple] = normalized_score
        
        return normalized_score
    
    def prioritize_kg(self, triples: List[str], current_topic: str = "", 
                     max_triples: int = 50) -> List[str]:
        """Prioritize knowledge graph triples based on importance."""
        # Score all triples
        scored_triples = []
        for i, triple in enumerate(triples):
            # Calculate recency based on position in the list (newer triples at the end)
            recency = i / max(1, len(triples) - 1)
            
            # Calculate relevance based on similarity to current topic
            relevance = 0.5  # Default relevance
            if current_topic:
                try:
                    s, p, o = (x.strip().lower() for x in triple.split("|", 2))
                    topic_words = set(current_topic.lower().split())
                    triple_words = set(s.split() + p.split() + o.split())
                    common_words = topic_words.intersection(triple_words)
                    relevance = len(common_words) / max(1, len(topic_words))
                except ValueError:
                    pass
            
            # Use default confidence for now
            confidence = 1.0
            
            # Score the triple
            score = self.score_triple(triple, recency, relevance, confidence)
            scored_triples.append((triple, score))
        
        # Sort by score (descending) and return top N
        scored_triples.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in scored_triples[:max_triples]]