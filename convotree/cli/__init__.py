"""
Command-line interface modules for ConvoTree.
"""

from .cli_v2 import ConvoTreeCLIV2

# Alias for backward compatibility
ConvoTreeCLI = ConvoTreeCLIV2

__all__ = [
    "ConvoTreeCLI",
    "ConvoTreeCLIV2"
]