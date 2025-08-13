#!/usr/bin/env python3
"""
Enhanced Chat System with Persistent Knowledge Graph
Provides consistent conversation experience without context rot
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
from persistent_kg import PersistentKG

class EnhancedChatSystem:
    """Chat system with persistent knowledge graph memory"""
    
    def __init__(self, conversation_id: str, db_path: str = "conversations.db"):
        self.conversation_id = conversation_id
        self.kg = PersistentKG(conversation_id, db_path)
        
        # Validate API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.strip() == "":
            raise ValueError("OpenAI API key is required. Set the OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        
        # System prompt template for chat continuation
        self.chat_prompt_template = """
You are an AI assistant continuing a conversation. You have access to persistent context from previous interactions.

CONVERSATION CONTEXT:
{context_summary}

RELEVANT FACTS:
{relevant_facts}

RECENT CONVERSATION:
{recent_context}

USER STATE/PREFERENCES:
{user_context}

IMPORTANT:
- Respond naturally as if you remember the entire conversation history
- Reference previous topics and user preferences when relevant
- Maintain conversation continuity and personality consistency
- Don't mention that you're using a knowledge graph or external memory
- Ask follow-up questions to deepen understanding when appropriate

Continue the conversation naturally based on the user's new message.
"""
    
    def process_message(self, user_message: str, role: str = "user") -> Dict[str, Any]:
        """Process a new message and generate response with full context"""
        
        # Step 1: Add user message to knowledge graph
        user_turn_id = self.kg.add_turn(role, user_message)
        
        # Step 2: Get relevant context for this query
        context = self.kg.get_relevant_context(user_message)
        
        # Step 3: Generate contextual response
        response_data = self._generate_contextual_response(user_message, context)
        
        # Step 4: Add assistant response to knowledge graph
        assistant_turn_id = self.kg.add_turn("assistant", response_data["response"])
        
        return {
            "response": response_data["response"],
            "conversation_id": self.conversation_id,
            "user_turn_id": user_turn_id,
            "assistant_turn_id": assistant_turn_id,
            "context_used": {
                "relevant_facts_count": len(context.get("raw_facts", [])),
                "recent_turns_count": len(context.get("recent_turns", [])),
                "has_synthesized_context": "synthesized" in context
            },
            "conversation_stats": self.kg.get_conversation_summary()
        }
    
    def _generate_contextual_response(self, user_message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate response using full conversation context"""
        
        # Format context for the prompt
        synthesized = context.get("synthesized", {})
        
        context_summary = synthesized.get("conversation_summary", "Ongoing conversation")
        relevant_facts = "\n".join([f"• {fact}" for fact in synthesized.get("relevant_facts", context.get("raw_facts", []))])
        recent_context = "\n".join([f"{turn['role']}: {turn['content'][:150]}..." for turn in context.get("recent_turns", [])])
        user_context = json.dumps(synthesized.get("user_context", context.get("context_state", {})), indent=2)
        
        # Build the prompt
        system_prompt = self.chat_prompt_template.format(
            context_summary=context_summary,
            relevant_facts=relevant_facts or "(no relevant facts found)",
            recent_context=recent_context or "(no recent context)",
            user_context=user_context or "{}"
        )
        
        try:
            # Generate response with context
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            return {"response": response.choices[0].message.content}
            
        except Exception as e:
            return {"response": f"I apologize, but I encountered an error processing your message: {str(e)}"}
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get formatted conversation history"""
        return self.kg._get_recent_turns(limit)
    
    def export_conversation_data(self) -> Dict[str, Any]:
        """Export complete conversation data for analysis or backup"""
        summary = self.kg.get_conversation_summary()
        recent_knowledge = self.kg._get_recent_knowledge(50)
        context_state = self.kg._get_context_state()
        
        return {
            "conversation_summary": summary,
            "knowledge_facts": recent_knowledge,
            "context_state": context_state,
            "export_timestamp": datetime.now().isoformat()
        }

class ConversationManager:
    """Manages multiple conversations and their persistent state"""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.active_conversations: Dict[str, EnhancedChatSystem] = {}
        self.db_path = db_path
    
    def get_conversation(self, conversation_id: str) -> EnhancedChatSystem:
        """Get or create a conversation instance"""
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = EnhancedChatSystem(conversation_id, self.db_path)
        return self.active_conversations[conversation_id]
    
    def send_message(self, conversation_id: str, message: str, role: str = "user") -> Dict[str, Any]:
        """Send a message to a specific conversation"""
        chat = self.get_conversation(conversation_id)
        return chat.process_message(message, role)
    
    def list_conversations(self) -> List[str]:
        """List all active conversation IDs"""
        return list(self.active_conversations.keys())
    
    def close_conversation(self, conversation_id: str):
        """Close and cleanup a conversation"""
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]

# Utility functions for easy usage
def create_conversation(conversation_id: str, db_path: str = "conversations.db") -> EnhancedChatSystem:
    """Create a new enhanced chat conversation"""
    return EnhancedChatSystem(conversation_id, db_path)

def continue_conversation(conversation_id: str, user_message: str, db_path: str = "conversations.db") -> str:
    """Simple interface for continuing a conversation"""
    chat = EnhancedChatSystem(conversation_id, db_path)
    result = chat.process_message(user_message)
    return result["response"]