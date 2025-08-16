#!/usr/bin/env python3
"""
Interactive Onboarding and Tutorial System for ConvoTree
Provides guided introduction and feature discovery for new users
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.markdown import Markdown
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn

class OnboardingSystem:
    """Interactive onboarding and tutorial system"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.user_progress = {}
        self.progress_file = Path(".convotree_progress.json")
        self.load_progress()
        
        # Tutorial steps definition
        self.tutorial_steps = {
            "welcome": {
                "title": "Welcome to ConvoTree! 🌳",
                "description": "Learn the basics of ConvoTree's persistent conversation system",
                "required": True,
                "estimated_time": "2 minutes"
            },
            "basic_chat": {
                "title": "Basic Conversation",
                "description": "Learn how to have natural conversations with memory",
                "required": True,
                "estimated_time": "3 minutes"
            },
            "knowledge_graph": {
                "title": "Knowledge Graph Features",
                "description": "Understand how ConvoTree remembers and uses information",
                "required": True,
                "estimated_time": "4 minutes"
            },
            "debug_features": {
                "title": "Debug and Analysis Tools",
                "description": "Learn debugging and conversation analysis features",
                "required": False,
                "estimated_time": "5 minutes"
            },
            "advanced_features": {
                "title": "Advanced Features",
                "description": "Explore conversation management, testing, and customization",
                "required": False,
                "estimated_time": "7 minutes"
            }
        }
    
    def start_onboarding(self, force_restart: bool = False) -> bool:
        """Start the interactive onboarding process"""
        if not force_restart and self.is_onboarding_complete():
            return self._handle_returning_user()
        
        self.console.print("\n" + "🌳" * 25)
        self.console.print("🌳" + " " * 23 + "🌳")
        self.console.print("🌳   Welcome to ConvoTree!   🌳")
        self.console.print("🌳" + " " * 23 + "🌳")
        self.console.print("🌳" * 25 + "\n")
        
        welcome_text = """
# ConvoTree: Persistent Conversational AI 🌳

ConvoTree is a revolutionary chat system that **remembers everything** while using **ephemeral context**. 

## What makes ConvoTree special?

✨ **Persistent Memory**: Never lose conversation context  
🧠 **Knowledge Graph**: Extracts and stores semantic knowledge  
⚡ **Ephemeral Context**: Constant performance regardless of conversation length  
🔍 **Transparency**: See exactly what's sent to the AI  
🚀 **Performance**: Advanced caching and optimization  

Let's get you started with a quick tutorial!
        """
        
        panel = Panel(
            Markdown(welcome_text),
            title="[bold cyan]Welcome to ConvoTree[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
        
        if not Confirm.ask("\n🚀 Would you like to start the interactive tutorial?"):
            self.console.print("You can always start the tutorial later with: [cyan]/tutorial[/cyan]")
            return False
        
        return self._run_tutorial()
    
    def _handle_returning_user(self) -> bool:
        """Handle users who have completed onboarding"""
        self.console.print("👋 Welcome back to ConvoTree!")
        
        options = [
            "Start chatting immediately",
            "Review tutorial",
            "Show me what's new",
            "Quick help reference"
        ]
        
        self.console.print("\nWhat would you like to do?")
        for i, option in enumerate(options, 1):
            self.console.print(f"  {i}. {option}")
        
        choice = IntPrompt.ask("Choose an option", choices=[str(i) for i in range(1, len(options) + 1)])
        
        if choice == 1:
            return True  # Start chatting
        elif choice == 2:
            return self._run_tutorial()
        elif choice == 3:
            self._show_whats_new()
            return True
        elif choice == 4:
            self._show_quick_help()
            return True
        
        return True
    
    def _run_tutorial(self) -> bool:
        """Run the complete tutorial"""
        total_steps = len(self.tutorial_steps)
        current_step = 1
        
        for step_id, step_info in self.tutorial_steps.items():
            self.console.print(f"\n📚 Tutorial Step {current_step}/{total_steps}")
            
            if not self._run_tutorial_step(step_id, step_info):
                # User wants to skip/exit
                break
            
            self._mark_step_complete(step_id)
            current_step += 1
        
        self._show_tutorial_completion()
        return True
    
    def _run_tutorial_step(self, step_id: str, step_info: Dict[str, Any]) -> bool:
        """Run a single tutorial step"""
        title = step_info["title"]
        description = step_info["description"]
        estimated_time = step_info["estimated_time"]
        
        step_panel = Panel(
            f"**{description}**\n\nEstimated time: {estimated_time}",
            title=f"[bold yellow]{title}[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(step_panel)
        
        if step_info.get("required", False):
            if not Confirm.ask("Ready to continue?"):
                return False
        else:
            if not Confirm.ask("Would you like to learn about this? (optional)"):
                return True
        
        # Run the specific tutorial content
        tutorial_method = getattr(self, f"_tutorial_{step_id}", None)
        if tutorial_method:
            tutorial_method()
        
        return True
    
    def _tutorial_welcome(self):
        """Welcome tutorial step"""
        self.console.print("\n🎯 **Core Concepts**\n")
        
        concepts = [
            ("Persistent Knowledge", "ConvoTree remembers facts, preferences, and context across sessions"),
            ("Ephemeral Context", "Only relevant information is sent to the AI, keeping responses fast"),
            ("Knowledge Graph", "Information is stored as semantic relationships, not raw text"),
            ("Debug Transparency", "See exactly what context is used for each response")
        ]
        
        for concept, explanation in concepts:
            self.console.print(f"🔹 **{concept}**: {explanation}")
        
        self.console.print("\n💡 Think of ConvoTree as giving AI a 'brain' that grows smarter over time!")
        input("\nPress Enter when ready to continue...")
    
    def _tutorial_basic_chat(self):
        """Basic chat tutorial step"""
        self.console.print("\n🗣️ **Basic Conversation**\n")
        
        chat_examples = [
            "Hello, I'm Alex and I work as a data scientist",
            "I love Python programming and machine learning",
            "What do you remember about me?",
            "Can you help me with a pandas question?"
        ]
        
        self.console.print("Here's how a typical conversation might look:")
        
        for i, example in enumerate(chat_examples, 1):
            self.console.print(f"\n{i}. **You**: {example}")
            
            if i == 1:
                self.console.print("   **ConvoTree**: Nice to meet you, Alex! I'll remember that you're a data scientist.")
            elif i == 2:
                self.console.print("   **ConvoTree**: Great! I've noted your interests in Python and ML.")
            elif i == 3:
                self.console.print("   **ConvoTree**: You're Alex, a data scientist who loves Python programming and machine learning!")
            elif i == 4:
                self.console.print("   **ConvoTree**: Absolutely! As a Python-loving data scientist, what specific pandas issue are you facing?")
        
        self.console.print("\n✨ Notice how ConvoTree:")
        self.console.print("  • Remembers your name and profession")
        self.console.print("  • Builds on previous context")
        self.console.print("  • Maintains conversation continuity")
        
        input("\nPress Enter to continue...")
    
    def _tutorial_knowledge_graph(self):
        """Knowledge graph tutorial step"""
        self.console.print("\n🧠 **Knowledge Graph Magic**\n")
        
        self.console.print("ConvoTree extracts semantic knowledge from conversations:")
        
        knowledge_tree = Tree("🌳 Knowledge Graph")
        user_branch = knowledge_tree.add("👤 User Profile")
        user_branch.add("Name: Alex")
        user_branch.add("Profession: Data Scientist") 
        user_branch.add("Interests: Python, Machine Learning")
        
        tech_branch = knowledge_tree.add("💻 Technical Context")
        tech_branch.add("Preferred Language: Python")
        tech_branch.add("Framework Interest: pandas")
        tech_branch.add("Domain: Data Science")
        
        self.console.print(knowledge_tree)
        
        self.console.print("\n🔍 **Key Features:**")
        features = [
            ("Fact Extraction", "Automatically identifies and stores important information"),
            ("Relationship Mapping", "Connects related concepts and preferences"),
            ("Context Synthesis", "Intelligently selects relevant facts for responses"),
            ("Memory Persistence", "Information survives across sessions and restarts")
        ]
        
        for feature, description in features:
            self.console.print(f"  • **{feature}**: {description}")
        
        self.console.print("\n💡 Use `/knowledge` command to see extracted facts anytime!")
        input("\nPress Enter to continue...")
    
    def _tutorial_debug_features(self):
        """Debug features tutorial step"""
        self.console.print("\n🔍 **Debug and Transparency Tools**\n")
        
        self.console.print("ConvoTree offers powerful debugging to show exactly how it works:")
        
        debug_table = Table(title="Debug Commands")
        debug_table.add_column("Command", style="cyan")
        debug_table.add_column("Purpose", style="white")
        debug_table.add_column("What You See", style="green")
        
        debug_commands = [
            ("/debug-mode", "Toggle debug mode", "Detailed processing info for every message"),
            ("/debug-llm", "Show LLM input", "Exact prompt sent to AI with all context"),
            ("/knowledge", "View facts", "All extracted semantic knowledge"),
            ("/context", "Show context", "Current conversation state and memory")
        ]
        
        for cmd, purpose, result in debug_commands:
            debug_table.add_row(cmd, purpose, result)
        
        self.console.print(debug_table)
        
        self.console.print("\n🎯 **Why This Matters:**")
        benefits = [
            "**Transparency**: See exactly what context influences responses",
            "**Verification**: Confirm that raw history isn't sent to AI",
            "**Optimization**: Understand performance and caching effects",
            "**Learning**: Discover how knowledge extraction works"
        ]
        
        for benefit in benefits:
            self.console.print(f"  • {benefit}")
        
        input("\nPress Enter to continue...")
    
    def _tutorial_advanced_features(self):
        """Advanced features tutorial step"""
        self.console.print("\n🚀 **Advanced Features**\n")
        
        feature_categories = {
            "Conversation Management": [
                "/conversations - List all conversations",
                "/switch <id> - Switch between conversations", 
                "/new <id> - Create new conversation",
                "/export - Export conversation data"
            ],
            "Testing & Analysis": [
                "/test memory - Test knowledge retention",
                "/test all - Run comprehensive tests",
                "/benchmark - Performance testing",
                "/analyze - Conversation pattern analysis"
            ],
            "Visualization": [
                "/visualize - Generate knowledge graph PNG",
                "/stats - Detailed statistics",
                "/search <query> - Search knowledge base"
            ],
            "Configuration": [
                "--debug flag - Start with debug mode",
                "Config files - YAML/JSON configuration",
                "Environment variables - Flexible setup"
            ]
        }
        
        for category, commands in feature_categories.items():
            self.console.print(f"\n📂 **{category}**")
            for command in commands:
                self.console.print(f"  • {command}")
        
        self.console.print("\n💡 **Pro Tips:**")
        tips = [
            "Use descriptive conversation IDs for better organization",
            "Run `/test all` periodically to validate system health",
            "Export important conversations with `/export` for backup",
            "Try `/visualize` to see your knowledge graph grow"
        ]
        
        for tip in tips:
            self.console.print(f"  🎯 {tip}")
        
        input("\nPress Enter to continue...")
    
    def _show_tutorial_completion(self):
        """Show tutorial completion summary"""
        completed_steps = len([step for step in self.user_progress.get("tutorial_steps", {}).values() if step])
        total_steps = len(self.tutorial_steps)
        
        completion_text = f"""
# 🎉 Tutorial Complete!

You've completed **{completed_steps}/{total_steps}** tutorial steps.

## 🚀 You're ready to:
- Have persistent conversations that remember everything
- Use debug tools to understand how ConvoTree works  
- Manage multiple conversations efficiently
- Explore advanced features at your own pace

## 🎯 Quick Start Commands:
- Start chatting naturally - ConvoTree will remember everything!
- `/help` - See all available commands
- `/debug-mode` - Enable detailed processing info
- `/knowledge` - View your growing knowledge graph

## 📚 Need Help?
- `/help` - Command reference
- `/tutorial` - Restart this tutorial
- `/status` - Check conversation status

**Happy chatting! Your journey with persistent AI begins now.** 🌳
        """
        
        panel = Panel(
            Markdown(completion_text),
            title="[bold green]🌳 Welcome to the ConvoTree Community! 🌳[/bold green]",
            border_style="green"
        )
        self.console.print(panel)
        
        self._mark_onboarding_complete()
        input("\nPress Enter to start your first conversation...")
    
    def _show_whats_new(self):
        """Show what's new in this version"""
        whats_new = """
# 🆕 What's New in ConvoTree v2.0

## 🚀 Performance Improvements
- **Intelligent Caching**: 10x faster knowledge retrieval
- **Optimized Database**: Better indexing and query optimization
- **Memory Management**: Constant memory usage regardless of conversation length

## 🔍 Enhanced Debug Tools
- **Debug Mode**: See exactly what's sent to the AI
- **LLM Input Inspector**: Full transparency into context processing
- **Performance Metrics**: Track response times and cache efficiency

## ⚙️ Configuration System
- **YAML/JSON Config**: Flexible configuration files
- **Environment Variables**: Easy deployment configuration
- **User Profiles**: Personalized settings and preferences

## 🛡️ Robust Error Handling
- **Smart Recovery**: Automatic error recovery with exponential backoff
- **User-Friendly Messages**: Clear error explanations
- **Comprehensive Logging**: Detailed error tracking and analysis

## 🎨 Better User Experience
- **Interactive Onboarding**: This tutorial system!
- **Command Auto-completion**: Faster command discovery
- **Progress Indicators**: Visual feedback for long operations
        """
        
        panel = Panel(
            Markdown(whats_new),
            title="[bold blue]ConvoTree v2.0 Updates[/bold blue]",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _show_quick_help(self):
        """Show quick help reference"""
        help_sections = {
            "Essential Commands": [
                "/help - Show all commands",
                "/status - Conversation status", 
                "/knowledge - View knowledge graph",
                "/debug-mode - Toggle debug mode"
            ],
            "Conversation Management": [
                "/conversations - List conversations",
                "/switch <id> - Change conversation",
                "/new <id> - Create conversation",
                "/clear - Clear screen"
            ],
            "Analysis & Debug": [
                "/debug-llm - Show LLM input",
                "/stats - Detailed statistics",
                "/test memory - Test retention",
                "/visualize - Create graph PNG"
            ]
        }
        
        for section, commands in help_sections.items():
            self.console.print(f"\n📚 **{section}**")
            for command in commands:
                self.console.print(f"  • {command}")
        
        self.console.print(f"\n💡 **Remember**: ConvoTree remembers everything automatically!")
        self.console.print(f"Just chat naturally and use commands when you need them.")
    
    def load_progress(self):
        """Load user progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    self.user_progress = json.load(f)
            except Exception:
                self.user_progress = {}
    
    def save_progress(self):
        """Save user progress to file"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.user_progress, f, indent=2)
        except Exception:
            pass  # Fail silently
    
    def _mark_step_complete(self, step_id: str):
        """Mark a tutorial step as complete"""
        if "tutorial_steps" not in self.user_progress:
            self.user_progress["tutorial_steps"] = {}
        
        self.user_progress["tutorial_steps"][step_id] = {
            "completed": True,
            "completed_at": datetime.now().isoformat()
        }
        self.save_progress()
    
    def _mark_onboarding_complete(self):
        """Mark onboarding as complete"""
        self.user_progress["onboarding_complete"] = True
        self.user_progress["onboarding_completed_at"] = datetime.now().isoformat()
        self.save_progress()
    
    def is_onboarding_complete(self) -> bool:
        """Check if user has completed onboarding"""
        return self.user_progress.get("onboarding_complete", False)
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get user progress summary"""
        completed_steps = len([
            step for step in self.user_progress.get("tutorial_steps", {}).values() 
            if step.get("completed", False)
        ])
        
        return {
            "onboarding_complete": self.is_onboarding_complete(),
            "tutorial_steps_completed": completed_steps,
            "total_tutorial_steps": len(self.tutorial_steps),
            "progress_percentage": (completed_steps / len(self.tutorial_steps)) * 100,
            "last_activity": self.user_progress.get("onboarding_completed_at")
        }
    
    def reset_progress(self):
        """Reset user progress (for testing/debugging)"""
        self.user_progress = {}
        if self.progress_file.exists():
            self.progress_file.unlink()
        self.console.print("🔄 User progress reset. Tutorial will run on next startup.")