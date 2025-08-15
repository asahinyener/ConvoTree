#!/usr/bin/env python3
"""
Persistent Knowledge Graph for Conversation Context
Maintains conversation memory across ephemeral LLM interactions
"""

import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from openai import OpenAI
import os

@dataclass
class ConversationTurn:
    """Represents a single conversation turn"""
    turn_id: str
    role: str  # user/assistant/system
    content: str
    timestamp: str
    entities: List[str] = None
    relations: List[str] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.relations is None:
            self.relations = []

@dataclass
class KnowledgeTriple:
    """Knowledge graph triple: subject|relation|object"""
    subject: str
    relation: str
    object: str
    source_turn: str
    confidence: float = 1.0
    
    def to_string(self) -> str:
        return f"{self.subject}|{self.relation}|{self.object}"

class PersistentKG:
    """Persistent Knowledge Graph for conversation memory"""
    
    def __init__(self, conversation_id: str, db_path: str = "conversations.db"):
        self.conversation_id = conversation_id
        self.db_path = Path(db_path)
        
        # Validate API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.strip() == "":
            raise ValueError("OpenAI API key is required. Set the OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self._init_db()
        
        # Knowledge extraction prompt
        self.kg_extraction_prompt = """
        Extract structured knowledge from this conversation turn.
        Return JSON with:
        {
            "entities": ["entity1", "entity2", ...],
            "relations": ["subj|relation|obj", ...],
            "key_concepts": ["concept1", "concept2", ...],
            "context_updates": {"key": "value", ...}
        }
        
        Focus on:
        - Named entities (people, places, things)
        - Relationships and facts
        - User preferences and state
        - Important context for future turns
        
        Be concise and factual. No hallucination.
        """
        
        # Context synthesis prompt  
        self.context_prompt = """
        You are a conversation context synthesizer. Given a knowledge graph and user query,
        extract the most relevant context for continuing the conversation.
        
        Return JSON with:
        {{
            "relevant_facts": ["fact1", "fact2", ...],
            "user_context": {{"key": "value", ...}},
            "conversation_summary": "brief summary",
            "suggested_response_tone": "tone description"
        }}
        
        Knowledge Graph Facts:
        {kg_facts}
        
        Recent Context:
        {recent_context}
        
        User Query: {user_query}
        """
    
    def _execute_with_retry(self, func, max_retries: int = 3):
        """Execute database operation with retry logic"""
        for attempt in range(max_retries):
            try:
                return func()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                    continue
                raise e
    
    def _init_db(self):
        """Initialize SQLite database for persistent storage"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            # Enable WAL mode for better concurrency
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=memory')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    last_updated TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS turns (
                    turn_id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    entities TEXT,
                    relations TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_triples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    subject TEXT,
                    relation TEXT,
                    object TEXT,
                    source_turn TEXT,
                    confidence REAL,
                    created_at TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS context_state (
                    conversation_id TEXT PRIMARY KEY,
                    state_json TEXT,
                    last_updated TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            conn.commit()
    
    def add_turn(self, role: str, content: str) -> str:
        """Add a new conversation turn and extract knowledge"""
        turn_id = hashlib.sha256(f"{self.conversation_id}_{role}_{content}_{datetime.now()}".encode()).hexdigest()[:16]
        timestamp = datetime.now().isoformat()
        
        # Extract knowledge from this turn
        knowledge = self._extract_knowledge(content, role)
        
        turn = ConversationTurn(
            turn_id=turn_id,
            role=role,
            content=content,
            timestamp=timestamp,
            entities=knowledge.get("entities", []),
            relations=knowledge.get("relations", [])
        )
        
        # Store turn in database with retry logic
        def store_turn():
            conn = None
            try:
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA busy_timeout=30000")
                
                # Ensure conversation exists
                conn.execute('''
                    INSERT OR REPLACE INTO conversations (id, created_at, last_updated, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (self.conversation_id, timestamp, timestamp, json.dumps({})))
                
                # Insert turn
                conn.execute('''
                    INSERT INTO turns (turn_id, conversation_id, role, content, timestamp, entities, relations)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (turn_id, self.conversation_id, role, content, timestamp, 
                      json.dumps(turn.entities), json.dumps(turn.relations)))
                
                # Insert knowledge triples
                for relation in turn.relations:
                    try:
                        parts = relation.split('|', 2)
                        if len(parts) == 3:
                            subj, rel, obj = parts
                            conn.execute('''
                                INSERT INTO knowledge_triples 
                                (conversation_id, subject, relation, object, source_turn, confidence, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (self.conversation_id, subj.strip(), rel.strip(), obj.strip(), 
                                  turn_id, 1.0, timestamp))
                    except Exception as e:
                        print(f"Error storing triple '{relation}': {e}")
                
                # Update context state within same connection
                context_updates = knowledge.get("context_updates", {})
                if context_updates:
                    # Get current state
                    cursor = conn.execute('''
                        SELECT state_json FROM context_state WHERE conversation_id = ?
                    ''', (self.conversation_id,))
                    
                    row = cursor.fetchone()
                    current_state = json.loads(row[0]) if row else {}
                    
                    # Merge updates
                    current_state.update(context_updates)
                    
                    # Save updated state
                    conn.execute('''
                        INSERT OR REPLACE INTO context_state (conversation_id, state_json, last_updated)
                        VALUES (?, ?, ?)
                    ''', (self.conversation_id, json.dumps(current_state), timestamp))
                
                conn.commit()
            finally:
                if conn:
                    conn.close()
        
        self._execute_with_retry(store_turn)
        
        return turn_id
    
    def _fallback_knowledge_extraction(self, content: str, role: str) -> Dict[str, Any]:
        """Fallback knowledge extraction using simple rules"""
        import re
        
        # Simple rule-based extraction
        entities = []
        relations = []
        key_concepts = []
        context_updates = {}
        
        # Extract potential entities (capitalized words, names)
        potential_entities = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', content)
        entities.extend(potential_entities[:10])  # Limit to 10
        
        # Extract key concepts (important words)
        important_words = re.findall(r'\b(?:project|work|meeting|deadline|problem|issue|solution|technology|framework|library|tool|language|system)\w*\b', content.lower())
        key_concepts.extend(list(set(important_words))[:10])  # Unique, limit to 10
        
        # Extract simple relations based on patterns
        if role == "user":
            # User statements often contain personal information
            name_match = re.search(r"I'm\s+(\w+)", content)
            if name_match:
                name = name_match.group(1)
                entities.append(name)
                relations.append(f"User|is_named|{name}")
                context_updates["user_name"] = name
            
            # Work/company information
            work_match = re.search(r"work(?:ing)?\s+(?:at|for)\s+([A-Z][\w\s]+)", content)
            if work_match:
                company = work_match.group(1).strip()
                entities.append(company)
                relations.append(f"User|works_at|{company}")
                context_updates["user_company"] = company
            
            # Project information
            project_match = re.search(r"(?:working on|building|developing)\s+(?:a\s+)?([\w\s]+(?:project|application|system|tool))", content.lower())
            if project_match:
                project = project_match.group(1).strip()
                key_concepts.append(project)
                context_updates["current_project"] = project
        
        # Clean up duplicates
        entities = list(set(entities))
        key_concepts = list(set(key_concepts))
        
        print(f"📋 Fallback extraction: {len(entities)} entities, {len(relations)} relations, {len(key_concepts)} concepts")
        
        return {
            "entities": entities,
            "relations": relations,
            "key_concepts": key_concepts,
            "context_updates": context_updates
        }
    
    def _extract_knowledge(self, content: str, role: str) -> Dict[str, Any]:
        """Extract structured knowledge from conversation turn with fallback"""
        # First try OpenAI API
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.kg_extraction_prompt},
                    {"role": "user", "content": f"Role: {role}\nContent: {content}"}
                ]
            )
            extracted_data = json.loads(response.choices[0].message.content)
            print(f"✅ Knowledge extracted successfully: {len(extracted_data.get('entities', []))} entities, {len(extracted_data.get('relations', []))} relations")
            return extracted_data
        except Exception as e:
            print(f"⚠️ OpenAI knowledge extraction failed: {e}")
            print("🔄 Falling back to rule-based extraction...")
            return self._fallback_knowledge_extraction(content, role)
    
    def _update_context_state(self, updates: Dict[str, Any]):
        """Update persistent context state"""
        def update_state():
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                # Get current state
                cursor = conn.execute('''
                    SELECT state_json FROM context_state WHERE conversation_id = ?
                ''', (self.conversation_id,))
                
                row = cursor.fetchone()
                current_state = json.loads(row[0]) if row else {}
                
                # Merge updates
                current_state.update(updates)
                
                # Save updated state
                conn.execute('''
                    INSERT OR REPLACE INTO context_state (conversation_id, state_json, last_updated)
                    VALUES (?, ?, ?)
                ''', (self.conversation_id, json.dumps(current_state), datetime.now().isoformat()))
                
                conn.commit()
        
        self._execute_with_retry(update_state)
    
    def get_relevant_context(self, user_query: str, max_facts: int = 10) -> Dict[str, Any]:
        """Extract relevant context for responding to user query"""
        # Get recent knowledge facts
        kg_facts = self._get_recent_knowledge(max_facts)
        
        # Get recent conversation turns for context
        recent_context = self._get_recent_turns(5)
        
        # Get current context state
        context_state = self._get_context_state()
        
        content = None
        try:
            # Use LLM to synthesize relevant context
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
            
            content = response.choices[0].message.content
            # Clean the content in case it has extra whitespace or formatting
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            synthesized_context = json.loads(content)
            
            # Combine with raw data
            return {
                "synthesized": synthesized_context,
                "raw_facts": kg_facts,
                "recent_turns": recent_context,
                "context_state": context_state,
                "conversation_id": self.conversation_id
            }
            
        except Exception as e:
            print(f"Context synthesis failed: {e}")
            if content:
                print(f"Response content: {repr(content)}")
            else:
                print("Response content: None")
            return {
                "raw_facts": kg_facts,
                "recent_turns": recent_context,  
                "context_state": context_state,
                "conversation_id": self.conversation_id
            }
    
    def _get_recent_knowledge(self, limit: int = 10) -> List[str]:
        """Get recent knowledge triples as formatted strings"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.execute('''
                SELECT subject, relation, object FROM knowledge_triples 
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (self.conversation_id, limit))
            
            return [f"{row[0]} → {row[1]} → {row[2]}" for row in cursor.fetchall()]
    
    def _get_recent_turns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation turns"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.execute('''
                SELECT role, content, timestamp FROM turns
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (self.conversation_id, limit))
            
            return [{"role": row[0], "content": row[1], "timestamp": row[2]} 
                   for row in cursor.fetchall()]
    
    def _get_context_state(self) -> Dict[str, Any]:
        """Get current context state"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.execute('''
                SELECT state_json FROM context_state WHERE conversation_id = ?
            ''', (self.conversation_id,))
            
            row = cursor.fetchone()
            return json.loads(row[0]) if row else {}
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary and stats"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            # Get turn count
            cursor = conn.execute('''
                SELECT COUNT(*) FROM turns WHERE conversation_id = ?
            ''', (self.conversation_id,))
            turn_count = cursor.fetchone()[0]
            
            # Get knowledge triple count  
            cursor = conn.execute('''
                SELECT COUNT(*) FROM knowledge_triples WHERE conversation_id = ?
            ''', (self.conversation_id,))
            triple_count = cursor.fetchone()[0]
            
            # Get first and last timestamps
            cursor = conn.execute('''
                SELECT MIN(timestamp), MAX(timestamp) FROM turns WHERE conversation_id = ?
            ''', (self.conversation_id,))
            first_turn, last_turn = cursor.fetchone()
            
            return {
                "conversation_id": self.conversation_id,
                "turn_count": turn_count,
                "knowledge_triples": triple_count,
                "first_turn": first_turn,
                "last_turn": last_turn,
                "context_state": self._get_context_state()
            }