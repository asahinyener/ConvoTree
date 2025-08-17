"""
Chat and conversation modules for ConvoTree.
"""

from .enhanced_chat_v2 import EnhancedChatSystemV2, ConversationManagerV2

# Alias v2 classes for backward compatibility
EnhancedChatSystem = EnhancedChatSystemV2
ConversationManager = ConversationManagerV2

__all__ = [
    "EnhancedChatSystem",
    "ConversationManager",
    "EnhancedChatSystemV2", 
    "ConversationManagerV2"
]