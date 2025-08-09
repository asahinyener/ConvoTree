#!/usr/bin/env python3
# Analyze Example Chat Recordings
# ─────────────────────────────────────────────────────────────────────────────
import os
import sys
import json
import datetime
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from kg_utils import normalize_kg

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES_DIR = Path(__file__).parent
OUTPUTS_DIR = EXAMPLES_DIR / "outputs"
ANALYSIS_DIR = EXAMPLES_DIR / "analysis"
METRICS_DIR = EXAMPLES_DIR / "metrics"

# Create directories if they don't exist
METRICS_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Analysis Functions
# ─────────────────────────────────────────────────────────────────────────────
def analyze_kg_growth(snapshots_file):
    """Analyze how the KG grows over time."""
    with open(snapshots_file, "r", encoding="utf-8") as f:
        snapshots = json.load(f)
    
    # Extract KG sizes
    queries = [s["query"] for s in snapshots]
    kg_sizes = [len(s["kg"]) for s in snapshots]
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(kg_sizes) + 1), kg_sizes, marker='o')
    plt.xlabel('Query Number')
    plt.ylabel('Knowledge Graph Size (# of triples)')
    plt.title('Knowledge Graph Growth Over Time')
    plt.xticks(range(1, len(kg_sizes) + 1), [f"Q{i+1}" for i in range(len(kg_sizes))], rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add query labels
    for i, (query, size) in enumerate(zip(queries, kg_sizes)):
        short_query = query[:20] + "..." if len(query) > 20 else query
        plt.annotate(short_query, (i + 1, size), textcoords="offset points", 
                    xytext=(0, 10), ha='center', fontsize=8)
    
    plt.tight_layout()
    
    # Save plot
    output_file = METRICS_DIR / f"{snapshots_file.stem}_growth.png"
    plt.savefig(output_file)
    plt.close()
    
    return output_file

def analyze_entity_distribution(snapshots_file):
    """Analyze the distribution of entities in the KG."""
    with open(snapshots_file, "r", encoding="utf-8") as f:
        snapshots = json.load(f)
    
    # Get the final KG
    final_kg = snapshots[-1]["kg"]
    
    # Extract entities
    entities = []
    for triple in final_kg:
        try:
            s, _, o = triple.split("|", 2)
            entities.append(s)
            entities.append(o)
        except ValueError:
            continue
    
    # Count entity occurrences
    entity_counts = Counter(entities)
    top_entities = entity_counts.most_common(10)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    entities, counts = zip(*top_entities)
    plt.barh(range(len(entities)), counts, align='center')
    plt.yticks(range(len(entities)), entities)
    plt.xlabel('Frequency')
    plt.ylabel('Entity')
    plt.title('Top 10 Entities in Knowledge Graph')
    plt.tight_layout()
    
    # Save plot
    output_file = METRICS_DIR / f"{snapshots_file.stem}_entities.png"
    plt.savefig(output_file)
    plt.close()
    
    return output_file

def analyze_predicate_distribution(snapshots_file):
    """Analyze the distribution of predicates in the KG."""
    with open(snapshots_file, "r", encoding="utf-8") as f:
        snapshots = json.load(f)
    
    # Get the final KG
    final_kg = snapshots[-1]["kg"]
    
    # Extract predicates
    predicates = []
    for triple in final_kg:
        try:
            _, p, _ = triple.split("|", 2)
            predicates.append(p)
        except ValueError:
            continue
    
    # Count predicate occurrences
    predicate_counts = Counter(predicates)
    top_predicates = predicate_counts.most_common(10)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    predicates, counts = zip(*top_predicates)
    plt.barh(range(len(predicates)), counts, align='center')
    plt.yticks(range(len(predicates)), predicates)
    plt.xlabel('Frequency')
    plt.ylabel('Predicate')
    plt.title('Top 10 Predicates in Knowledge Graph')
    plt.tight_layout()
    
    # Save plot
    output_file = METRICS_DIR / f"{snapshots_file.stem}_predicates.png"
    plt.savefig(output_file)
    plt.close()
    
    return output_file

def analyze_topic_relevance(snapshots_file):
    """Analyze how the KG triples relate to the current topic."""
    with open(snapshots_file, "r", encoding="utf-8") as f:
        snapshots = json.load(f)
    
    # Calculate topic relevance scores
    relevance_scores = []
    for snapshot in snapshots:
        topic = snapshot["current_topic"].lower()
        topic_words = set(topic.split())
        
        # Count triples containing topic words
        relevant_triples = 0
        for triple in snapshot["kg"]:
            triple_lower = triple.lower()
            if any(word in triple_lower for word in topic_words):
                relevant_triples += 1
        
        # Calculate relevance score
        if snapshot["kg"]:
            relevance_score = relevant_triples / len(snapshot["kg"])
        else:
            relevance_score = 0
        
        relevance_scores.append(relevance_score)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(relevance_scores) + 1), relevance_scores, marker='o')
    plt.xlabel('Query Number')
    plt.ylabel('Topic Relevance Score')
    plt.title('Knowledge Graph Topic Relevance Over Time')
    plt.xticks(range(1, len(relevance_scores) + 1), [f"Q{i+1}" for i in range(len(relevance_scores))], rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add topic labels
    for i, (snapshot, score) in enumerate(zip(snapshots, relevance_scores)):
        short_topic = snapshot["current_topic"][:20] + "..." if len(snapshot["current_topic"]) > 20 else snapshot["current_topic"]
        plt.annotate(short_topic, (i + 1, score), textcoords="offset points", 
                    xytext=(0, 10), ha='center', fontsize=8)
    
    plt.tight_layout()
    
    # Save plot
    output_file = METRICS_DIR / f"{snapshots_file.stem}_relevance.png"
    plt.savefig(output_file)
    plt.close()
    
    return output_file

def generate_metrics_report(snapshots_file, metrics_files):
    """Generate a metrics report for the example."""
    with open(snapshots_file, "r", encoding="utf-8") as f:
        snapshots = json.load(f)
    
    # Extract example name
    example_name = snapshots_file.stem.split("_kg_snapshots")[0].replace("_", " ").title()
    
    # Create report
    report_file = METRICS_DIR / f"{snapshots_file.stem}_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# {example_name} Metrics Report\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Add metrics
        f.write("## Knowledge Graph Growth\n\n")
        f.write(f"![KG Growth]({metrics_files['growth'].name})\n\n")
        
        f.write("## Entity Distribution\n\n")
        f.write(f"![Entity Distribution]({metrics_files['entities'].name})\n\n")
        
        f.write("## Predicate Distribution\n\n")
        f.write(f"![Predicate Distribution]({metrics_files['predicates'].name})\n\n")
        
        f.write("## Topic Relevance\n\n")
        f.write(f"![Topic Relevance]({metrics_files['relevance'].name})\n\n")
        
        # Add summary statistics
        f.write("## Summary Statistics\n\n")
        
        # Final KG size
        final_kg_size = len(snapshots[-1]["kg"])
        f.write(f"- Final KG size: {final_kg_size} triples\n")
        
        # Unique entities
        entities = set()
        for triple in snapshots[-1]["kg"]:
            try:
                s, _, o = triple.split("|", 2)
                entities.add(s)
                entities.add(o)
            except ValueError:
                continue
        f.write(f"- Unique entities: {len(entities)}\n")
        
        # Unique predicates
        predicates = set()
        for triple in snapshots[-1]["kg"]:
            try:
                _, p, _ = triple.split("|", 2)
                predicates.add(p)
            except ValueError:
                continue
        f.write(f"- Unique predicates: {len(predicates)}\n")
        
        # Average topic relevance
        avg_relevance = sum([len([t for t in s["kg"] if s["current_topic"].lower() in t.lower()]) / max(1, len(s["kg"])) for s in snapshots]) / len(snapshots)
        f.write(f"- Average topic relevance: {avg_relevance:.2f}\n")
        
        # KG growth rate
        if len(snapshots) > 1:
            growth_rate = (final_kg_size - len(snapshots[0]["kg"])) / (len(snapshots) - 1)
            f.write(f"- KG growth rate: {growth_rate:.2f} triples per query\n")
    
    return report_file

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────
def main():
    """Analyze all example chat recordings."""
    # Find all KG snapshots files
    snapshots_files = list(OUTPUTS_DIR.glob("*_kg_snapshots_*.json"))
    
    if not snapshots_files:
        print("No KG snapshots files found. Run generate_examples.py first.")
        return
    
    # Analyze each example
    for snapshots_file in snapshots_files:
        print(f"Analyzing {snapshots_file.name}...")
        
        # Generate metrics
        growth_file = analyze_kg_growth(snapshots_file)
        entities_file = analyze_entity_distribution(snapshots_file)
        predicates_file = analyze_predicate_distribution(snapshots_file)
        relevance_file = analyze_topic_relevance(snapshots_file)
        
        # Generate report
        metrics_files = {
            "growth": growth_file,
            "entities": entities_file,
            "predicates": predicates_file,
            "relevance": relevance_file
        }
        report_file = generate_metrics_report(snapshots_file, metrics_files)
        
        print(f"Metrics report generated: {report_file}")

if __name__ == "__main__":
    main()