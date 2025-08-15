#!/usr/bin/env python3
"""
ConvoTree CLI v2.0 - Enhanced with Performance, Error Handling, and UX Improvements
Integrates caching, configuration, error handling, and onboarding systems
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..core.chat.enhanced_chat_v2 import EnhancedChatSystemV2, ConversationManagerV2
from ..core.config.config_manager import ConfigManager, ConvoTreeConfig
from ..utils.error_handler import ConvoTreeErrorHandler, handle_error, with_error_handling
from ..utils.onboarding_system import OnboardingSystem
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

class ConvoTreeCLIV2:
    """Enhanced CLI v2.0 with comprehensive improvements"""
    
    def __init__(self, conversation_id: str = None, config: ConvoTreeConfig = None):
        self.console = Console()
        self.config = config or ConfigManager().load_config()
        self.conversation_id = conversation_id or f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize error handler
        self.error_handler = ConvoTreeErrorHandler(
            debug_mode=self.config.ui.debug_mode,
            log_file="convotree.log" if self.config.ui.verbose_logging else None
        )
        
        # Initialize conversation manager
        self.conversation_manager = ConversationManagerV2(
            db_path=self.config.database.path,
            debug_mode=self.config.ui.debug_mode,
            config=self.config.model.to_dict()
        )
        
        # Get conversation instance
        self.chat = self.conversation_manager.get_conversation(self.conversation_id)
        
        # Initialize onboarding system
        self.onboarding = OnboardingSystem(self.console)
        
        # Enhanced command system
        self.commands = {
            # Basic commands
            '/help': self._cmd_help,
            '/h': self._cmd_help,
            '/exit': self._cmd_exit,
            '/quit': self._cmd_exit,
            '/q': self._cmd_exit,
            
            # Status and info
            '/status': self._cmd_status,
            '/version': self._cmd_version,
            '/config': self._cmd_config,
            '/performance': self._cmd_performance,
            
            # Conversation management
            '/conversations': self._cmd_list_conversations,
            '/switch': self._cmd_switch_conversation,
            '/new': self._cmd_new_conversation,
            '/delete': self._cmd_delete_conversation,
            '/clear': self._cmd_clear,
            
            # Knowledge and analysis
            '/history': self._cmd_history,
            '/knowledge': self._cmd_knowledge,
            '/context': self._cmd_context,
            '/search': self._cmd_search,
            '/analyze': self._cmd_analyze,
            '/stats': self._cmd_stats,
            
            # Debug and development
            '/debug': self._cmd_debug,
            '/debug-mode': self._cmd_toggle_debug_mode,
            '/debug-llm': self._cmd_debug_llm,
            '/errors': self._cmd_show_errors,
            '/cache': self._cmd_cache_info,
            
            # Testing and validation
            '/test': self._cmd_semantic_test,
            '/benchmark': self._cmd_benchmark,
            
            # Data management
            '/export': self._cmd_export,
            '/visualize': self._cmd_visualize,
            '/viz': self._cmd_visualize,
            
            # User experience
            '/tutorial': self._cmd_tutorial,
            '/onboarding': self._cmd_onboarding,
            '/shortcuts': self._cmd_shortcuts,
            '/tips': self._cmd_tips,
        }
        
        # Performance tracking
        self.session_start = datetime.now()
        self.command_count = 0
        self.message_count = 0
        self.last_debug_info = None
        
        if self.config.ui.debug_mode:
            self.console.print(f"🚀 ConvoTree CLI v2.0 initialized")
            self.console.print(f"⚙️ Configuration: {self.config.environment}")
            self.console.print(f"🗂️ Conversation: {self.conversation_id}")
    
    def start_chat(self):
        """Start the enhanced chat loop"""
        try:
            # Run onboarding for new users
            if not self.onboarding.is_onboarding_complete():
                if not self.onboarding.start_onboarding():
                    return
            
            self._display_welcome()
            self._main_chat_loop()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Use /exit or /quit to leave gracefully[/yellow]")
        except Exception as e:
            error_info = self.error_handler.handle_error(e, {"location": "start_chat"})
            self.console.print(f"[red]Fatal error: {error_info.user_message}[/red]")
        finally:
            self._cleanup_and_exit()
    
    def _display_welcome(self):
        """Display enhanced welcome message"""
        # Get session info
        session_info = self.chat.get_performance_stats()
        cache_stats = session_info.get("cache_stats", {})
        
        welcome_text = f"""
# ConvoTree v2.0 - Enhanced Persistent AI 🌳

**Session**: `{self.conversation_id}`  
**Started**: `{self.session_start.strftime('%Y-%m-%d %H:%M:%S')}`  
**Cache**: `{cache_stats.get('total_cached_items', 0)} items ready`  
**Performance**: `{cache_stats.get('hit_rate_percent', 0):.1f}% cache hit rate`

## Quick Commands
- `/help` - Show all commands  
- `/debug-mode` - Toggle debug mode ({self.config.ui.debug_mode})
- `/knowledge` - View your knowledge graph  
- `/tutorial` - Review tutorial anytime

## 🎯 Pro Tips
- Chat naturally - ConvoTree remembers everything automatically
- Use debug mode to see exactly how context is processed
- Try `/test memory` to validate knowledge retention

Type your message or use a command starting with `/`
        """
        
        panel = Panel(
            Markdown(welcome_text),
            title="[bold cyan]Welcome to ConvoTree v2.0[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def _get_user_input(self):
        """Get user input with proper prompt"""
        return input(f"\n{self.conversation_id}> ").strip()
    
    def _handle_chat_message(self, message: str):
        """Handle regular chat messages with v2.0 enhancements"""
        start_time = datetime.now()
        
        with self.console.status("[bold green]💭 Thinking...", spinner="dots"):
            try:
                # Process message through the enhanced chat system v2
                result = self.chat.process_message(message)
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                # Store debug info for later inspection
                if result.get('debug_info'):
                    self.last_debug_info = result['debug_info']
                
                # Display the response
                response_panel = Panel(
                    result['response'],
                    title="[bold green]💬 ConvoTree[/bold green]",
                    border_style="green"
                )
                self.console.print(response_panel)
                
                # Show context info
                if self.config.ui.debug_mode:
                    self._show_context_info(result)
                
                # Show performance info
                if self.config.ui.verbose_logging:
                    self._show_performance_info(result)
                    
            except Exception as e:
                error_info = self.error_handler.handle_error(e, {
                    "message": message,
                    "conversation_id": self.conversation_id
                })
                self.console.print(f"[red]💥 {error_info.user_message}[/red]")
    
    def _main_chat_loop(self):
        """Enhanced main chat loop with error handling"""
        while True:
            try:
                # Get user input
                user_input = self._get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Handle commands vs chat messages
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    self.command_count += 1
                else:
                    self._handle_chat_message(user_input)
                    self.message_count += 1
                    
            except KeyboardInterrupt:
                if Confirm.ask("\n🤔 Do you want to exit ConvoTree?"):
                    break
                continue
            except EOFError:
                break
            except Exception as e:
                error_info = self.error_handler.handle_error(e, {"location": "main_loop"})
                self.console.print(f"[red]Error: {error_info.user_message}[/red]")
                if error_info.recovery_suggestions:
                    self.console.print("💡 Suggestions:")
                    for suggestion in error_info.recovery_suggestions[:3]:
                        self.console.print(f"  • {suggestion}")
    
    def _get_user_input(self) -> str:
        """Get user input with enhanced prompt"""
        # Show cache hit rate if available
        perf_indicator = ""
        if self.config.ui.show_performance_stats:
            stats = self.chat.get_performance_stats()
            cache_stats = stats.get("cache_stats", {})
            hit_rate = cache_stats.get("hit_rate_percent", 0)
            perf_indicator = f" [{hit_rate:.0f}%]" if hit_rate > 0 else ""
        
        prompt = f"\n{self.conversation_id}{perf_indicator}> "
        return input(prompt).strip()
    
    @with_error_handling
    def _handle_chat_message(self, message: str):
        """Handle chat messages with enhanced error handling and performance tracking"""
        start_time = datetime.now()
        
        with self.console.status("[bold green]🤔 Thinking...", spinner="dots"):
            try:
                result = self.chat.process_message(message)
                
                # Display response
                response_panel = Panel(
                    result['response'],
                    title="[bold green]💬 ConvoTree[/bold green]",
                    border_style="green"
                )
                self.console.print(response_panel)
                
                # Show context info
                self._show_context_info(result)
                
                # Show performance info if enabled
                if self.config.ui.show_performance_stats:
                    self._show_performance_info(result)
                
                # Store debug info for /debug-llm command
                if result.get('debug_info'):
                    self.last_debug_info = result['debug_info']
                
            except Exception as e:
                error_info = self.error_handler.handle_error(e, {
                    "message": message[:100],
                    "conversation_id": self.conversation_id
                })
                self.console.print(f"[red]💥 {error_info.user_message}[/red]")
    
    def _show_context_info(self, result: Dict[str, Any]):
        """Show context information in a user-friendly way"""
        context_used = result.get('context_used', {})
        
        if context_used.get('relevant_facts_count', 0) > 0:
            facts_count = context_used['relevant_facts_count']
            turns_count = context_used['recent_turns_count'] 
            cache_hit = context_used.get('cache_hit', False)
            
            cache_indicator = "⚡" if cache_hit else "🔄"
            
            self.console.print(
                f"[dim]{cache_indicator} Used {facts_count} knowledge facts, "
                f"{turns_count} recent turns[/dim]"
            )
    
    def _show_performance_info(self, result: Dict[str, Any]):
        """Show performance information"""
        performance = result.get('performance', {})
        total_time = performance.get('total_time', 0)
        context_time = performance.get('context_time', 0)
        
        self.console.print(
            f"[dim blue]⏱️ Response: {total_time:.2f}s "
            f"(context: {context_time:.2f}s)[/dim blue]"
        )
    
    @with_error_handling
    def _handle_command(self, command_input: str):
        """Handle command input with better error messages"""
        parts = command_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                error_info = self.error_handler.handle_error(e, {
                    "command": command,
                    "args": args
                })
                self.console.print(f"[red]Command error: {error_info.user_message}[/red]")
        else:
            self.console.print(f"[red]❓ Unknown command: {command}[/red]")
            self.console.print("[yellow]💡 Use /help to see available commands[/yellow]")
            
            # Suggest similar commands
            similar = self._find_similar_commands(command)
            if similar:
                self.console.print(f"[dim]Did you mean: {', '.join(similar)}?[/dim]")
    
    def _find_similar_commands(self, command: str) -> List[str]:
        """Find similar commands for typo suggestions"""
        # Simple similarity check
        similar = []
        for cmd in self.commands.keys():
            if cmd.startswith(command) or command in cmd:
                similar.append(cmd)
        return similar[:3]
    
    # Enhanced command implementations
    def _cmd_help(self, args: List[str]):
        """Enhanced help command with categories"""
        if args and args[0] in ["basic", "advanced", "debug", "all"]:
            category = args[0]
        else:
            category = "basic"
        
        help_commands = {
            "basic": [
                ("/help", "Show this help", "/help [basic|advanced|debug|all]"),
                ("/status", "Show conversation status", "/status"),
                ("/knowledge", "View knowledge graph", "/knowledge [limit]"),
                ("/history", "Show conversation history", "/history [limit]"),
                ("/clear", "Clear screen", "/clear"),
                ("/exit", "Exit ConvoTree", "/exit")
            ],
            "advanced": [
                ("/conversations", "List all conversations", "/conversations"),
                ("/switch <id>", "Switch conversation", "/switch other_conversation"),
                ("/new [id]", "Create conversation", "/new project_chat"),
                ("/export", "Export conversation", "/export [format]"),
                ("/visualize", "Create knowledge graph", "/visualize"),
                ("/search <query>", "Search knowledge", "/search python")
            ],
            "debug": [
                ("/debug-mode", "Toggle debug mode", "/debug-mode"),
                ("/debug-llm", "Show LLM input", "/debug-llm"),
                ("/cache", "Cache information", "/cache [clear|stats]"),
                ("/errors", "Show error log", "/errors"),
                ("/performance", "Performance stats", "/performance"),
                ("/test", "Run tests", "/test [memory|all]")
            ]
        }
        
        if category == "all":
            commands = []
            for cat_commands in help_commands.values():
                commands.extend(cat_commands)
        else:
            commands = help_commands.get(category, help_commands["basic"])
        
        help_table = Table(title=f"ConvoTree Commands ({category.title()})")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        help_table.add_column("Usage", style="green")
        
        for cmd, desc, usage in commands:
            help_table.add_row(cmd, desc, usage)
        
        self.console.print(help_table)
        
        if category == "basic":
            self.console.print("\n💡 Use `/help advanced` or `/help debug` for more commands")
    
    def _cmd_performance(self, args: List[str]):
        """Show comprehensive performance statistics"""
        # Get chat system stats
        chat_stats = self.chat.get_performance_stats()
        
        # Get system-wide stats
        system_stats = self.conversation_manager.get_system_stats()
        
        # Get error stats
        error_stats = self.error_handler.get_error_stats()
        
        # Session stats
        session_duration = datetime.now() - self.session_start
        
        perf_info = f"""
# 📊 Performance Dashboard

## Session Statistics
- **Duration**: {str(session_duration).split('.')[0]}
- **Messages Sent**: {self.message_count}
- **Commands Used**: {self.command_count}
- **Error Rate**: {error_stats.get('error_rate', 0):.2f}/min

## Response Performance
- **Average Response Time**: {chat_stats.get('avg_response_time', 0):.3f}s
- **Fastest Response**: {chat_stats.get('min_response_time', 0):.3f}s
- **Slowest Response**: {chat_stats.get('max_response_time', 0):.3f}s

## Cache Performance
- **Cache Hit Rate**: {chat_stats.get('cache_stats', {}).get('hit_rate_percent', 0):.1f}%
- **Cached Items**: {chat_stats.get('cache_stats', {}).get('total_cached_items', 0)}
- **Cache Size Limit**: {chat_stats.get('cache_stats', {}).get('cache_size_limit', 0)}

## System Health
- **Total Errors**: {error_stats.get('total_errors', 0)}
- **Recent Errors**: {error_stats.get('recent_errors', 0)}
- **Active Conversations**: {system_stats.get('active_conversations', 0)}
        """
        
        panel = Panel(
            Markdown(perf_info),
            title="[bold blue]📊 Performance Dashboard[/bold blue]",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _cmd_cache_info(self, args: List[str]):
        """Cache management and information"""
        if args and args[0] == "clear":
            self.chat.kg.clear_cache()
            self.console.print("[green]🧹 Cache cleared successfully[/green]")
            return
        
        cache_stats = self.chat.kg.get_cache_stats()
        
        cache_table = Table(title="🗄️ Cache Statistics")
        cache_table.add_column("Metric", style="cyan")
        cache_table.add_column("Value", style="white")
        
        metrics = [
            ("Hit Rate", f"{cache_stats.get('hit_rate_percent', 0):.1f}%"),
            ("Total Hits", str(cache_stats.get('cache_hits', 0))),
            ("Total Misses", str(cache_stats.get('cache_misses', 0))),
            ("Cached Items", str(cache_stats.get('total_cached_items', 0))),
            ("Size Limit", str(cache_stats.get('cache_size_limit', 0))),
            ("TTL", f"{cache_stats.get('cache_ttl_seconds', 0)}s"),
            ("Avg Query Time", f"{cache_stats.get('avg_query_time_ms', 0):.1f}ms"),
            ("Avg Synthesis Time", f"{cache_stats.get('avg_synthesis_time_ms', 0):.1f}ms")
        ]
        
        for metric, value in metrics:
            cache_table.add_row(metric, value)
        
        self.console.print(cache_table)
        self.console.print("\n💡 Use `/cache clear` to clear cache")
    
    def _cmd_show_errors(self, args: List[str]):
        """Show error statistics and recent errors"""
        error_stats = self.error_handler.get_error_stats()
        
        if error_stats['total_errors'] == 0:
            self.console.print("[green]✅ No errors recorded this session![/green]")
            return
        
        # Error statistics
        stats_table = Table(title="🚨 Error Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_data = [
            ("Total Errors", str(error_stats['total_errors'])),
            ("Recent Errors (1h)", str(error_stats['recent_errors'])),
            ("Error Rate", f"{error_stats['error_rate']:.2f}/min")
        ]
        
        for metric, value in stats_data:
            stats_table.add_row(metric, value)
        
        self.console.print(stats_table)
        
        # Category breakdown
        if error_stats.get('category_breakdown'):
            category_table = Table(title="Error Categories")
            category_table.add_column("Category", style="yellow")
            category_table.add_column("Count", style="red")
            
            for category, count in error_stats['category_breakdown'].items():
                category_table.add_row(category.title(), str(count))
            
            self.console.print(category_table)
        
        # Last error details
        if error_stats.get('last_error'):
            last_error = error_stats['last_error']
            error_panel = Panel(
                f"**Message**: {last_error['message']}\n"
                f"**Category**: {last_error['category']}\n"
                f"**Time**: {last_error['timestamp']}\n"
                f"**Severity**: {last_error['severity']}",
                title="[bold red]Last Error[/bold red]",
                border_style="red"
            )
            self.console.print(error_panel)
    
    def _cmd_tutorial(self, args: List[str]):
        """Restart the tutorial system"""
        force_restart = args and args[0] == "restart"
        self.onboarding.start_onboarding(force_restart=force_restart)
    
    def _cmd_onboarding(self, args: List[str]):
        """Show onboarding progress and options"""
        if args and args[0] == "reset":
            self.onboarding.reset_progress()
            return
        
        progress = self.onboarding.get_progress_summary()
        
        progress_info = f"""
# 🎓 Onboarding Progress

**Status**: {"✅ Complete" if progress['onboarding_complete'] else "⏳ In Progress"}
**Tutorial Progress**: {progress['tutorial_steps_completed']}/{progress['total_tutorial_steps']} steps
**Completion**: {progress['progress_percentage']:.1f}%

## Available Actions
- `/tutorial` - Review tutorial
- `/tutorial restart` - Restart from beginning
- `/onboarding reset` - Reset all progress
        """
        
        panel = Panel(
            Markdown(progress_info),
            title="[bold cyan]🎓 Onboarding Status[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def _cmd_shortcuts(self, args: List[str]):
        """Show keyboard shortcuts and quick commands"""
        shortcuts_info = """
# ⌨️ Shortcuts & Quick Commands

## Essential Shortcuts
- `Ctrl+C` - Interrupt operation (ask to exit)
- `Ctrl+D` - Exit ConvoTree
- `Tab` - Command completion (future feature)
- `↑/↓` - Command history (future feature)

## Quick Commands
- `/h` - Quick help
- `/q` - Quick exit  
- `/s` - Status (alias for `/status`)
- `/k` - Knowledge (alias for `/knowledge`)
- `/d` - Debug mode toggle

## Pro Tips
- Use `/help basic` for essential commands
- Commands are case-insensitive
- Partial command matching (future feature)
- Use `/performance` to check system health
        """
        
        panel = Panel(
            Markdown(shortcuts_info),
            title="[bold yellow]⌨️ Shortcuts & Tips[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(panel)
    
    def _cmd_tips(self, args: List[str]):
        """Show usage tips and best practices"""
        tips_info = """
# 💡 ConvoTree Pro Tips

## Conversation Best Practices
- **Be Specific**: More detailed messages create better knowledge extraction
- **Use Names**: Mention names, places, and specific terms for better memory
- **Ask Follow-ups**: Reference previous topics to test memory retention
- **Stay Organized**: Use descriptive conversation IDs for different projects

## Performance Optimization
- **Enable Caching**: Keep cache enabled for better performance
- **Monitor Stats**: Check `/performance` periodically
- **Use Debug Mode**: Understand what context is being used
- **Clean Up**: Archive old conversations occasionally

## Advanced Features
- **Export Important Chats**: Use `/export` for critical conversations
- **Visualize Growth**: Try `/visualize` to see your knowledge graph
- **Test Memory**: Use `/test memory` to validate retention
- **Custom Configuration**: Create `.convotree.yaml` for personalization

## Troubleshooting
- **Check Errors**: Use `/errors` to see any issues
- **Clear Cache**: Try `/cache clear` if responses seem off
- **Restart Tutorial**: Use `/tutorial restart` for refresher
- **Monitor Performance**: Watch cache hit rates and response times
        """
        
        panel = Panel(
            Markdown(tips_info),
            title="[bold green]💡 Pro Tips & Best Practices[/bold green]",
            border_style="green"
        )
        self.console.print(panel)
    
    def _cmd_config(self, args: List[str]):
        """Show current configuration"""
        config_info = f"""
# ⚙️ Current Configuration

## Environment
- **Version**: {self.config.version}
- **Environment**: {self.config.environment}
- **Debug Mode**: {self.config.ui.debug_mode}

## Model Settings
- **Model**: {self.config.model.name}
- **Temperature**: {self.config.model.temperature}
- **Max Tokens**: {self.config.model.max_tokens}
- **Timeout**: {self.config.model.timeout}s

## Cache Settings
- **Enabled**: {self.config.cache.enabled}
- **Size**: {self.config.cache.size}
- **TTL**: {self.config.cache.ttl}s

## Database
- **Path**: {self.config.database.path}
- **Timeout**: {self.config.database.timeout}s
        """
        
        panel = Panel(
            Markdown(config_info),
            title="[bold blue]⚙️ Configuration[/bold blue]",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _cmd_version(self, args: List[str]):
        """Show version information"""
        version_info = f"""
# 🌳 ConvoTree Version Information

**Version**: {self.config.version}  
**Environment**: {self.config.environment}  
**Build Date**: {datetime.now().strftime('%Y-%m-%d')}

## Features Enabled
- ✅ Persistent Knowledge Graph
- ✅ Ephemeral Context Processing  
- ✅ Intelligent Caching System
- ✅ Comprehensive Error Handling
- ✅ Interactive Onboarding
- ✅ Performance Monitoring
- ✅ Debug and Transparency Tools

## System Status
- **Session Duration**: {str(datetime.now() - self.session_start).split('.')[0]}
- **Messages Processed**: {self.message_count}
- **Commands Executed**: {self.command_count}
- **Cache Hit Rate**: {self.chat.kg.get_cache_stats().get('hit_rate_percent', 0):.1f}%
        """
        
        panel = Panel(
            Markdown(version_info),
            title="[bold cyan]🌳 ConvoTree v2.0[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def _cleanup_and_exit(self):
        """Enhanced cleanup on exit"""
        session_duration = datetime.now() - self.session_start
        
        # Show session summary
        summary_info = f"""
# 👋 Session Summary

**Duration**: {str(session_duration).split('.')[0]}  
**Messages**: {self.message_count}  
**Commands**: {self.command_count}  
**Errors**: {self.error_handler.error_count}

Thanks for using ConvoTree! Your conversation is safely stored. 🌳
        """
        
        panel = Panel(
            Markdown(summary_info),
            title="[bold green]Session Complete[/bold green]",
            border_style="green"
        )
        self.console.print(panel)
    
    # Implement remaining command methods (simplified versions of existing ones)
    def _cmd_exit(self, args): sys.exit(0)
    def _cmd_status(self, args):
        """Show conversation status"""
        try:
            summary = self.chat.kg.get_conversation_summary()
            
            status_info = f"""
**Conversation ID:** `{self.conversation_id}`
**Turn Count:** `{summary['turn_count']}`
**Knowledge Triples:** `{summary['knowledge_triples']}`
**First Turn:** `{summary.get('first_turn', 'N/A')}`
**Last Turn:** `{summary.get('last_turn', 'N/A')}`
**Session Duration:** `{str(datetime.now() - self.session_start).split('.')[0]}`
**Database:** `{self.config.database.path}`
**Debug Mode:** `{'Enabled' if self.config.ui.debug_mode else 'Disabled'}`
            """
            
            panel = Panel(
                Markdown(status_info),
                title="[bold blue]📊 Conversation Status[/bold blue]",
                border_style="blue"
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Error getting status: {e}[/red]")
    def _cmd_history(self, args):
        """Show conversation history"""
        try:
            limit = int(args[0]) if args and args[0].isdigit() else 20
            history = self.chat.get_conversation_history(limit)
            
            if not history:
                self.console.print("[yellow]📜 No conversation history found[/yellow]")
                return
            
            history_table = Table(title=f"📜 Conversation History (Last {len(history)} turns)")
            history_table.add_column("Time", style="dim")
            history_table.add_column("Role", style="cyan")
            history_table.add_column("Content", style="white", max_width=60)
            
            for turn in reversed(history):  # Show most recent first
                timestamp = turn.get('timestamp', '')[:19]  # Remove microseconds
                role = turn.get('role', 'unknown').capitalize()
                content = turn.get('content', '')[:100] + ('...' if len(turn.get('content', '')) > 100 else '')
                
                history_table.add_row(timestamp, role, content)
            
            self.console.print(history_table)
            
        except Exception as e:
            self.console.print(f"[red]Error getting history: {e}[/red]")
    def _cmd_knowledge(self, args):
        """Show knowledge graph facts"""
        try:
            limit = int(args[0]) if args and args[0].isdigit() else 20
            facts = self.chat.kg._get_recent_knowledge(limit)
            
            if not facts:
                self.console.print("[yellow]🧠 No knowledge facts found[/yellow]")
                return
            
            knowledge_table = Table(title=f"🧠 Knowledge Graph Facts (Last {len(facts)})")
            knowledge_table.add_column("Fact", style="green")
            
            for fact in facts:
                knowledge_table.add_row(fact)
            
            self.console.print(knowledge_table)
            
        except Exception as e:
            self.console.print(f"[red]Error getting knowledge: {e}[/red]")
    def _cmd_context(self, args): pass  # Implement similar to original
    def _cmd_search(self, args): pass  # Implement similar to original
    def _cmd_analyze(self, args): pass  # Implement similar to original
    def _cmd_stats(self, args): pass  # Implement similar to original
    def _cmd_debug(self, args): pass  # Implement similar to original
    def _cmd_toggle_debug_mode(self, args):
        """Toggle debug mode on/off"""
        try:
            self.config.ui.debug_mode = not self.config.ui.debug_mode
            self.chat.debug_mode = self.config.ui.debug_mode
            
            status = "enabled" if self.config.ui.debug_mode else "disabled"
            emoji = "🔍" if self.config.ui.debug_mode else "🙈"
            color = "green" if self.config.ui.debug_mode else "yellow"
            
            self.console.print(f"[{color}]{emoji} Debug mode {status}[/{color}]")
            
        except Exception as e:
            self.console.print(f"[red]Error toggling debug mode: {e}[/red]")
    def _cmd_debug_llm(self, args): pass  # Implement similar to original
    def _cmd_semantic_test(self, args): pass  # Implement similar to original
    def _cmd_benchmark(self, args): pass  # Implement similar to original
    def _cmd_export(self, args): pass  # Implement similar to original
    def _cmd_visualize(self, args): pass  # Implement similar to original
    def _cmd_list_conversations(self, args): pass  # Implement similar to original
    def _cmd_switch_conversation(self, args): pass  # Implement similar to original
    def _cmd_new_conversation(self, args): pass  # Implement similar to original
    def _cmd_delete_conversation(self, args): pass  # Implement similar to original
    def _cmd_clear(self, args): os.system('clear' if os.name == 'posix' else 'cls')

def main(conversation_id=None, config_path=None, debug=False):
    """Enhanced main function with configuration and error handling"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        if not os.getenv("OPENAI_API_KEY"):
            load_dotenv()
            if os.getenv("OPENAI_API_KEY"):
                print("✅ Loaded environment variables from .env")
    except ImportError:
        pass
    
    try:
        # Load configuration
        config_manager = ConfigManager(config_path)
        config = config_manager.load_config()
        
        # Override debug mode if specified
        if debug:
            config.ui.debug_mode = True
        
        # Create and start CLI
        cli = ConvoTreeCLIV2(
            conversation_id=conversation_id,
            config=config
        )
        cli.start_chat()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if debug:
            import traceback
            traceback.print_exc()

def main_standalone():
    """Standalone main function with argument parsing for direct execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ConvoTree CLI v2.0 - Enhanced Persistent AI Chat")
    parser.add_argument("--conversation-id", "-c", type=str, help="Conversation ID to use or resume")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    args = parser.parse_args()
    
    if args.version:
        print("ConvoTree v2.0 - Enhanced Persistent AI Chat")
        return
        
    main(
        conversation_id=args.conversation_id,
        config_path=args.config,
        debug=args.debug
    )

if __name__ == "__main__":
    main_standalone()