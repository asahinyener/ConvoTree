#!/usr/bin/env python3
"""
Enhanced Chat System v2 with Performance Optimizations
Includes caching, better error handling, and improved user experience
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
from cached_knowledge_graph import CachedKnowledgeGraph

class EnhancedChatSystemV2:
    """Next-generation chat system with performance optimizations"""
    
    def __init__(self, conversation_id: str, db_path: str = "conversations.db", 
                 debug_mode: bool = False, config: Dict[str, Any] = None):
        self.conversation_id = conversation_id
        self.debug_mode = debug_mode
        self.config = config or self._default_config()
        
        # Initialize cached knowledge graph
        self.kg = CachedKnowledgeGraph(
            conversation_id, 
            db_path, 
            cache_size=self.config.get('cache_size', 1000)
        )
        
        # Validate API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.strip() == "":
            raise ValueError("OpenAI API key is required. Set the OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        
        # Performance tracking
        self.response_times = []
        self.error_count = 0
        self.total_requests = 0
        
        # Enhanced prompts with better instructions
        self.chat_prompt_template = """
You are an AI assistant continuing a conversation with excellent memory and context awareness.

CONVERSATION CONTEXT:
{context_summary}

RELEVANT KNOWLEDGE:
{relevant_facts}

RECENT CONVERSATION:
{recent_context}

USER PROFILE & PREFERENCES:
{user_context}

RESPONSE GUIDELINES:
- Respond naturally and conversationally
- Reference relevant past information when appropriate
- Maintain consistency with previous interactions
- Be helpful, accurate, and engaging
- Ask clarifying questions when needed
- Adapt your tone to match the conversation style

Current message to respond to:
"""
        
        if self.debug_mode:
            print(f"🚀 Enhanced Chat System V2 initialized for {conversation_id}")
            print(f"⚙️ Config: {self.config}")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration settings"""
        return {
            'model': 'gpt-4o-mini',
            'temperature': 0.7,
            'max_tokens': 1000,
            'cache_size': 1000,
            'cache_ttl': 300,
            'max_retries': 3,
            'retry_delay': 1.0,
            'timeout': 30.0,
            'enable_performance_tracking': True
        }
    
    def process_message(self, user_message: str, role: str = "user") -> Dict[str, Any]:
        """Process message with enhanced error handling and performance tracking"""
        start_time = time.time()
        self.total_requests += 1
        
        if self.debug_mode:
            print(f"\n🔍 [DEBUG] Processing message: '{user_message[:100]}{'...' if len(user_message) > 100 else ''}'")
        
        try:
            # Step 1: Add user message to knowledge graph
            user_turn_id = self.kg.add_turn(role, user_message)
            if self.debug_mode:
                print(f"📝 [DEBUG] Added user turn ID: {user_turn_id}")
            
            # Step 2: Get relevant context with caching
            context_start = time.time()
            context = self.kg.get_relevant_context(user_message)
            context_time = time.time() - context_start
            
            if self.debug_mode:
                cache_info = context.get('cache_info', {})
                print(f"🧠 [DEBUG] Context retrieved in {context_time:.3f}s")
                print(f"📊 [DEBUG] Cache hit: {cache_info.get('cache_hit', False)}")
                print(f"🔗 [DEBUG] Synthesis cached: {cache_info.get('synthesis_cached', False)}")
            
            # Step 3: Generate contextual response with retry logic
            response_data = self._generate_contextual_response_with_retry(user_message, context)
            
            # Step 4: Add assistant response to knowledge graph
            assistant_turn_id = self.kg.add_turn("assistant", response_data["response"])
            if self.debug_mode:
                print(f"📝 [DEBUG] Added assistant turn ID: {assistant_turn_id}")
            
            # Track performance
            total_time = time.time() - start_time
            self.response_times.append(total_time)
            
            # Build enhanced result
            result = {
                "response": response_data["response"],
                "conversation_id": self.conversation_id,
                "user_turn_id": user_turn_id,
                "assistant_turn_id": assistant_turn_id,
                "context_used": {
                    "relevant_facts_count": len(context.get("raw_facts", [])),
                    "recent_turns_count": len(context.get("recent_turns", [])),
                    "has_synthesized_context": "synthesized" in context,
                    "context_retrieval_time": context_time,
                    "cache_hit": context.get('cache_info', {}).get('cache_hit', False)
                },
                "performance": {
                    "total_time": total_time,
                    "context_time": context_time,
                    "generation_time": response_data.get("generation_time", 0)
                },
                "conversation_stats": self.kg.get_conversation_summary(),
                "debug_info": response_data.get("debug_info") if self.debug_mode else None
            }
            
            return result
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"I apologize, but I encountered an error processing your message: {str(e)}"
            
            if self.debug_mode:
                print(f"❌ [DEBUG] Error in process_message: {e}")
                import traceback
                traceback.print_exc()
            
            return {
                "response": error_msg,
                "conversation_id": self.conversation_id,
                "error": str(e),
                "error_count": self.error_count,
                "performance": {
                    "total_time": time.time() - start_time,
                    "error": True
                }
            }
    
    def _generate_contextual_response_with_retry(self, user_message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate response with retry logic and enhanced error handling"""
        max_retries = self.config.get('max_retries', 3)
        retry_delay = self.config.get('retry_delay', 1.0)
        
        for attempt in range(max_retries):
            try:
                return self._generate_contextual_response(user_message, context)
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                
                if self.debug_mode:
                    print(f"⚠️ [DEBUG] Attempt {attempt + 1} failed: {e}")
                    print(f"🔄 [DEBUG] Retrying in {retry_delay}s...")
                
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
        
        # Should never reach here, but just in case
        raise Exception("All retry attempts failed")
    
    def _generate_contextual_response(self, user_message: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate response using enhanced context processing"""
        generation_start = time.time()
        
        # Enhanced context formatting
        synthesized = context.get("synthesized", {})
        
        context_summary = synthesized.get("conversation_summary", "Ongoing conversation")
        
        # Better fact presentation
        relevant_facts = self._format_facts(synthesized.get("relevant_facts", context.get("raw_facts", [])))
        
        # Improved recent context formatting
        recent_context = self._format_recent_context(context.get("recent_turns", []))
        
        # Enhanced user context
        user_context = self._format_user_context(synthesized.get("user_context", context.get("context_state", {})))
        
        # Build the enhanced prompt
        system_prompt = self.chat_prompt_template.format(
            context_summary=context_summary,
            relevant_facts=relevant_facts,
            recent_context=recent_context,
            user_context=user_context
        )
        
        # Debug logging with enhanced details
        debug_info = None
        if self.debug_mode:
            print(f"\n🎯 [DEBUG] === ENHANCED LLM INPUT ===")
            print(f"📊 Context Summary: {context_summary}")
            print(f"💡 Relevant Facts ({len(synthesized.get('relevant_facts', context.get('raw_facts', [])))} facts):")
            self._debug_print_facts(synthesized.get('relevant_facts', context.get('raw_facts', [])))
            print(f"📝 Recent Context ({len(context.get('recent_turns', []))} turns):")
            self._debug_print_recent_context(context.get('recent_turns', []))
            print(f"👤 User Context: {user_context[:200]}{'...' if len(user_context) > 200 else ''}")
            print(f"\n📤 [DEBUG] === SYSTEM PROMPT (Enhanced) ===")
            print("=" * 80)
            print(system_prompt)
            print("=" * 80)
            print(f"📤 [DEBUG] User message: {user_message}")
            print("=" * 80)
            
            # Store comprehensive debug info
            debug_info = {
                "context_summary": context_summary,
                "relevant_facts": synthesized.get("relevant_facts", context.get("raw_facts", [])),
                "recent_turns": context.get("recent_turns", []),
                "user_context": synthesized.get("user_context", context.get("context_state", {})),
                "system_prompt": system_prompt,
                "user_message": user_message,
                "raw_context": context,
                "model_config": {
                    "model": self.config.get('model'),
                    "temperature": self.config.get('temperature'),
                    "max_tokens": self.config.get('max_tokens')
                }
            }
        
        try:
            # Generate response with enhanced parameters
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4o-mini'),
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 1000),
                timeout=self.config.get('timeout', 30.0),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            response_content = response.choices[0].message.content
            generation_time = time.time() - generation_start
            
            if self.debug_mode:
                print(f"\n📥 [DEBUG] === ENHANCED LLM RESPONSE ===")
                print(f"Response length: {len(response_content)} characters")
                print(f"Model used: {response.model}")
                print(f"Generation time: {generation_time:.3f}s")
                print(f"Usage: {response.usage}")
                finish_reason = response.choices[0].finish_reason
                print(f"Finish reason: {finish_reason}")
                if finish_reason == "length":
                    print("⚠️ Response was truncated due to max_tokens limit")
                print("=" * 50)
            
            result = {
                "response": response_content,
                "generation_time": generation_time,
                "model_info": {
                    "model": response.model,
                    "usage": dict(response.usage) if response.usage else {},
                    "finish_reason": response.choices[0].finish_reason
                }
            }
            
            if debug_info:
                result["debug_info"] = debug_info
                
            return result
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error generating a response: {str(e)}"
            if self.debug_mode:
                print(f"❌ [DEBUG] OpenAI API Error: {e}")
            
            return {
                "response": error_msg,
                "generation_time": time.time() - generation_start,
                "error": str(e)
            }
    
    def _format_facts(self, facts: List[str]) -> str:
        """Enhanced fact formatting"""
        if not facts:
            return "(no relevant facts found)"
        
        formatted_facts = []
        for i, fact in enumerate(facts[:10], 1):  # Limit to top 10 facts
            formatted_facts.append(f"{i}. {fact}")
        
        if len(facts) > 10:
            formatted_facts.append(f"... and {len(facts) - 10} more facts")
        
        return "\n".join(formatted_facts)
    
    def _format_recent_context(self, turns: List[Dict[str, Any]]) -> str:
        """Enhanced recent context formatting"""
        if not turns:
            return "(no recent context)"
        
        formatted_turns = []
        for turn in turns[:5]:  # Limit to 5 most recent
            role = turn.get('role', 'unknown').title()
            content = turn.get('content', '')[:200]  # Increased limit
            if len(turn.get('content', '')) > 200:
                content += "..."
            formatted_turns.append(f"**{role}:** {content}")
        
        return "\n".join(formatted_turns)
    
    def _format_user_context(self, context: Dict[str, Any]) -> str:
        """Enhanced user context formatting"""
        if not context:
            return "{}"
        
        # Pretty print with better formatting
        return json.dumps(context, indent=2, ensure_ascii=False)
    
    def _debug_print_facts(self, facts: List[str]):
        """Debug print facts with better formatting"""
        if not facts:
            print("   (no relevant facts)")
            return
        
        for i, fact in enumerate(facts[:5], 1):
            print(f"   {i}. {fact}")
        if len(facts) > 5:
            print(f"   ... and {len(facts) - 5} more")
    
    def _debug_print_recent_context(self, turns: List[Dict[str, Any]]):
        """Debug print recent context with better formatting"""
        if not turns:
            print("   (no recent context)")
            return
        
        for turn in turns[:3]:
            role = turn.get('role', 'unknown')
            content = turn.get('content', '')[:100]
            if len(turn.get('content', '')) > 100:
                content += "..."
            print(f"   {role}: {content}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_stats = self.kg.get_cache_stats()
        
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "error_rate_percent": (self.error_count / self.total_requests * 100) if self.total_requests > 0 else 0,
            "avg_response_time": avg_response_time,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "cache_stats": cache_stats,
            "config": self.config
        }
    
    def warm_up(self):
        """Warm up the system for better initial performance"""
        if self.debug_mode:
            print("🔥 Warming up Enhanced Chat System V2...")
        
        self.kg.warm_cache()
        
        if self.debug_mode:
            print("✅ System warmed up and ready")
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get formatted conversation history"""
        return self.kg._get_recent_turns(limit)
    
    def export_conversation_data(self) -> Dict[str, Any]:
        """Export complete conversation data with performance metrics"""
        base_data = {
            "conversation_summary": self.kg.get_conversation_summary(),
            "knowledge_facts": self.kg._get_recent_knowledge(50),
            "context_state": self.kg._get_context_state(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Add performance data
        base_data["performance_stats"] = self.get_performance_stats()
        
        return base_data

class ConversationManagerV2:
    """Enhanced conversation manager with performance optimizations"""
    
    def __init__(self, db_path: str = "conversations.db", debug_mode: bool = False, 
                 config: Dict[str, Any] = None):
        self.active_conversations: Dict[str, EnhancedChatSystemV2] = {}
        self.db_path = db_path
        self.debug_mode = debug_mode
        self.config = config or {}
    
    def get_conversation(self, conversation_id: str) -> EnhancedChatSystemV2:
        """Get or create a conversation instance with caching"""
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = EnhancedChatSystemV2(
                conversation_id, self.db_path, self.debug_mode, self.config
            )
            # Warm up new conversations for better performance
            self.active_conversations[conversation_id].warm_up()
            
        return self.active_conversations[conversation_id]
    
    def send_message(self, conversation_id: str, message: str, role: str = "user") -> Dict[str, Any]:
        """Send a message to a specific conversation"""
        chat = self.get_conversation(conversation_id)
        return chat.process_message(message, role)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide performance statistics"""
        total_conversations = len(self.active_conversations)
        total_requests = sum(chat.total_requests for chat in self.active_conversations.values())
        total_errors = sum(chat.error_count for chat in self.active_conversations.values())
        
        return {
            "active_conversations": total_conversations,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "system_error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "conversations": {
                conv_id: chat.get_performance_stats() 
                for conv_id, chat in self.active_conversations.items()
            }
        }
    
    def close_conversation(self, conversation_id: str):
        """Close and clean up a conversation"""
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
    
    def list_conversations(self) -> List[str]:
        """List active conversation IDs"""
        return list(self.active_conversations.keys())