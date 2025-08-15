"""
ConvoTree: A persistent conversational AI with knowledge graph integration.

This package provides a comprehensive system for building conversational AI
applications with persistent memory, knowledge graphs, and optimization capabilities.
"""

__version__ = "2.0.0"
__author__ = "ConvoTree Team"

from .core.memory.universal_memory_interface import UniversalMemoryInterface
from .core.chat.enhanced_chat_v2 import EnhancedChatSystemV2
from .core.config.config_manager import ConfigManager

__all__ = [
    "UniversalMemoryInterface",
    "EnhancedChatSystemV2", 
    "ConfigManager"
]