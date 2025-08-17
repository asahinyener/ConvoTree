# Knowledge Graphs for Dialogue State Tracking - Grep Points

## Paper Structure Overview

### TITLE
- TITLE: "Knowledge Graphs for Dialogue State Tracking"
- AUTHOR: Ahmet Şahin Yener (B.Sc. TUM)

### ABSTRACT_SUMMARY
- DST: Dialogue State Tracking extracts context from user turns
- KG_BENEFIT: Knowledge Graphs enrich dialogue context with structured databases
- GOAL: Review KG usage for DST in robust dialogue systems

### SECTION_1_INTRODUCTION
- MODERN_NLP: Chat interface with sequential turns
- CONTEXT_GROWTH: Input context growth increases computational load
- TASK_ORIENTED: Domain-specific ontologies with slots and values
- BELIEF_STATE: Probabilistic hypothesis over slot-value pairs
- KG_DEFINITION: Directed graphs with semantic edge labels
- MULTI_HOP: Multi-hop reasoning over connected nodes

### SECTION_2_RELATED_WORK
- DST_COMPONENT: Structured snapshot of user goals and constraints
- RULE_BASED: Early handcrafted finite-state machines
- STATISTICAL: Bayesian belief tracking and RL policies
- DSTC_CHALLENGES: Dialogue State Tracking Challenges (2013-)
- NEURAL_DST: Three methodological umbrellas:
  - ENCODER_CLASSIFIER: Independent slot value prediction
  - SEQ2SEQ: Full belief state generation
  - GRAPH_ENHANCED: Inter-slot and external knowledge relations
- KG_ORIGINS: WordNet lexical network foundation
- RDF_TRIPLE: (subject, predicate, object) paradigm

### SECTION_3_METHODS (CURRENT - NEEDS TAXONOMY)
- GRAPH_ENHANCED_DST: Graph-structured representations
- SINGLE_DOMAIN: GraphDialog with dependency parses
- MULTI_DOMAIN: DSTQA, SST, DSGFNet approaches
- DYNAMIC_GRAPHS: Turn-level evolution (HS2DG-DST, HFSG-DST)
- HYBRID_SYSTEMS: LLM + graph reasoning combinations

### SECTION_4_DISCUSSION
- EVALUATION_METRICS: JGA, SA, RS-F1, AIA, AGA
- BENCHMARKS: MultiWOZ, Schema-Guided Dialogue
- GRAPH_VS_NONGRAPH: Relational inductive bias benefits
- FUTURE_DIRECTIONS: Continual expansion, cross-lingual, multimodal

### SECTION_5_LIMITATIONS
- CONSTRUCTION_OVERHEAD: Latency for dynamic graphs
- BIASED_RELATIONS: Human-curated vs learned graphs
- SCALABILITY: O(|S|²) message passing complexity
- MULTIMODAL_MATURITY: Synthetic dataset limitations

### SECTION_6_DEMO
- CONVOCOMPRESSOR_R: Lightweight server proof-of-concept
- CONTEXT_ROT: Progressive loss prevention
- KG_EXTRACTION: Triple representation
- JSON_STATE: Structured dialogue state

## Key Terms for Grep Searches

### TECHNICAL_TERMS
- DIALOGUE_STATE_TRACKING, DST
- KNOWLEDGE_GRAPH, KG
- BELIEF_STATE
- SLOT_VALUE_PAIRS
- MULTI_HOP_REASONING
- GRAPH_ATTENTION_NETWORKS
- SCHEMA_GRAPH
- DYNAMIC_GRAPHS

### MODEL_NAMES
- DSTQA, SST, DSGFNet, GCDST
- HS2DG_DST, HFSG_DST, NOETIC_GRAPH_DST
- BREAK_T5, METAASSIST
- GRAPHDIALOG, TRIPPY

### DATASETS_BENCHMARKS
- MULTIWOZ, SGD
- DSTC_CHALLENGES
- JOINT_GOAL_ACCURACY, JGA
- SLOT_ACCURACY, SA

### METHODS_TAXONOMY (PROPOSED)
- STATIC_SCHEMA_GRAPHS
- DYNAMIC_TURN_GRAPHS  
- HIERARCHICAL_GRAPHS
- HYBRID_LLM_GRAPH
- MULTIMODAL_GRAPHS

## Restructuring Plan for Section 3

### CURRENT_ISSUE
- Chronological listing of approaches
- Lacks clear organization principles
- Missing systematic comparison

### PROPOSED_TAXONOMY
1. GRAPH_CONSTRUCTION_METHOD
   - Static predefined schemas
   - Dynamic turn-level construction
   - Learned graph structures

2. GRAPH_SCOPE
   - Single-domain applications
   - Multi-domain scenarios
   - Cross-lingual settings

3. INTEGRATION_STRATEGY
   - Pure graph-based methods
   - Hybrid LLM-graph approaches
   - Graph-augmented transformers

4. ARCHITECTURAL_PATTERNS
   - Schema-scoping trackers
   - State-copying mechanisms
   - Hierarchical node typing

## ConvoTree Demo Integration Points

### DEMO_REPLACEMENT
- Replace ConvoCompressor-R with ConvoTree
- Add neural consolidation engine
- Include memory management features

### SYSTEM_COMPONENTS
- ConvoTree API integration
- Memory consolidation through dreaming
- LLM-powered reasoning system
- Long-term context management

### PERFORMANCE_METRICS
- Context compression ratios
- Memory retrieval accuracy
- Inference speed improvements
- Long conversation handling