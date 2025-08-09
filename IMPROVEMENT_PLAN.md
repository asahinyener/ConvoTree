# ConvoTree Improvement Plan

Based on the analysis of the current implementation, this document outlines a plan to improve the conversation-aware Knowledge Graph (KG) in ConvoTree.

## Issues Identified

### 1. Knowledge Graph Format Inconsistency
- The KG format changes throughout the conversation
- Different representations for the same entities and relationships
- Inconsistent use of entity references (e.g., "E1", "E2")

### 2. Entity Reference Problems
- Generic entity references make the KG less readable
- References don't capture semantic meaning
- Lack of entity normalization

### 3. Conversation Context Loss
- Assistant sometimes loses context of the conversation
- Previous topics are forgotten in subsequent exchanges

### 4. Knowledge Retention Issues
- KG doesn't properly build upon previous knowledge
- Important details are lost in sequential updates
- No prioritization of important facts

### 5. Triple Format Inconsistency
- Subject|predicate|object format isn't consistently maintained
- Some entries have long subjects with embedded relationships

### 6. Entity Normalization Problems
- Same concepts appear with different representations
- Prevents proper knowledge accumulation and linking

### 7. Response Quality Issues
- Assistant's responses don't fully leverage KG information
- Responses sometimes seem generic despite available context

## Implementation Plan

### Phase 1: KG Structure and Entity Normalization
- [x] Create this improvement plan
- [x] Implement EntityNormalizer class for consistent entity naming
- [x] Modify normalize_triple function to standardize triple format
- [x] Update normalize_kg function to deduplicate and clean triples
- [x] Enhance draw_kg function for better visualization

### Phase 2: Knowledge Retention and Prioritization
- [x] Implement KnowledgePrioritizer class to rank facts by importance
- [x] Add recency and relevance scoring for KG triples
- [ ] Modify compress_chat to preserve important knowledge
- [x] Add confidence scores for KG triples
- [ ] Implement hierarchical knowledge representation

### Phase 3: Conversation Context Tracking
- [x] Add conversation topic tracking to TerminalChat class
- [x] Implement topic detection and tracking
- [x] Modify generate_response to maintain conversation context
- [x] Add explicit context references in assistant responses
- [x] Enhance sequential compression to prioritize current context

### Phase 4: Response Generation Improvements
- [x] Modify resume_chat to better utilize KG information
- [x] Add explicit KG fact references in responses
- [ ] Implement response templates based on conversation state
- [ ] Add follow-up question generation based on KG
- [ ] Enhance fallback mechanisms with KG awareness

### Phase 5: Testing and Refinement
- [x] Create comprehensive test cases for different conversation scenarios
- [x] Implement metrics for KG quality and conversation coherence
- [x] Add example chat recordings with analysis
- [ ] Add logging for KG updates and conversation state changes
- [ ] Refine parameters based on test results
- [ ] Document best practices for conversation-aware KG usage

## Progress Tracking

Each phase will be implemented sequentially, with commits after each significant improvement. The progress will be tracked by checking off completed items in this plan.