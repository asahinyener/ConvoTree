#!/usr/bin/env python3
"""
Interactive Terminal Chat CLI with Knowledge Graph Analysis
Provides persistent conversation with semantic testing and structure inspection
"""

import os
import sys
import json
import sqlite3
import readline
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from ..core.chat.enhanced_chat import EnhancedChatSystem, ConversationManager
from ..core.memory.persistent_kg import PersistentKG
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

class ConvoTreeCLI:
    """Interactive CLI for ConvoTree with semantic testing capabilities"""
    
    def __init__(self, conversation_id: str = None, db_path: str = "conversations.db", debug_mode: bool = False):
        self.console = Console()
        self.conversation_id = conversation_id or f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.db_path = db_path
        self.debug_mode = debug_mode
        self.conversation_manager = ConversationManager(db_path, debug_mode)
        self.chat = self.conversation_manager.get_conversation(self.conversation_id)
        
        # Command history for terminal
        self.command_history = []
        self.session_start = datetime.now()
        
        # Recording functionality
        self.recording = False
        self.recording_start = None
        self.recording_data = []
        self.recording_file = None
        
        # Available commands
        self.commands = {
            '/help': self._cmd_help,
            '/h': self._cmd_help,
            '/exit': self._cmd_exit,
            '/quit': self._cmd_exit,
            '/q': self._cmd_exit,
            '/status': self._cmd_status,
            '/history': self._cmd_history,
            '/knowledge': self._cmd_knowledge,
            '/kg': self._cmd_knowledge,
            '/context': self._cmd_context,
            '/stats': self._cmd_stats,
            '/export': self._cmd_export,
            '/clear': self._cmd_clear,
            '/search': self._cmd_search,
            '/analyze': self._cmd_analyze,
            '/visualize': self._cmd_visualize,
            '/viz': self._cmd_visualize,
            '/db': self._cmd_database,
            '/conversations': self._cmd_list_conversations,
            '/switch': self._cmd_switch_conversation,
            '/new': self._cmd_new_conversation,
            '/delete': self._cmd_delete_conversation,
            '/test': self._cmd_semantic_test,
            '/benchmark': self._cmd_benchmark,
            '/debug': self._cmd_debug,
            '/debug-llm': self._cmd_debug_llm,
            '/debug-mode': self._cmd_toggle_debug_mode,
            '/record': self._cmd_record,
            '/stop': self._cmd_stop_recording,
            '/replay': self._cmd_replay_recording
        }
        
        # Initialize readline for better input handling
        self._setup_readline()
    
    def _setup_readline(self):
        """Setup readline for command history and completion"""
        try:
            # Enable command completion
            readline.set_completer(self._complete_command)
            readline.parse_and_bind('tab: complete')
            
            # Load command history if it exists
            history_file = Path('.convotree_history')
            if history_file.exists():
                readline.read_history_file(str(history_file))
        except Exception as e:
            # Readline might not be available on all systems
            pass
    
    def _complete_command(self, text, state):
        """Auto-completion for commands"""
        options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None
    
    def start_chat(self):
        """Start the interactive chat loop"""
        self._display_welcome()
        
        try:
            while True:
                try:
                    # Get user input with prompt
                    user_input = input(f"\n{self.conversation_id}> ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Add to command history
                    self.command_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'input': user_input,
                        'type': 'command' if user_input.startswith('/') else 'message'
                    })
                    
                    # Check if it's a command
                    if user_input.startswith('/'):
                        self._handle_command(user_input)
                    else:
                        # Regular chat message
                        self._handle_chat_message(user_input)
                        
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Use /exit or /quit to leave the chat[/yellow]")
                    continue
                except EOFError:
                    break
                    
        except Exception as e:
            self.console.print(f"[red]Error in chat loop: {e}[/red]")
        finally:
            self._save_session_history()
            self.console.print("[cyan]Chat session ended. Goodbye! 👋[/cyan]")
    
    def _display_welcome(self):
        """Display welcome message and instructions"""
        welcome_text = f"""
# ConvoTree Interactive CLI 🌳

**Conversation ID:** `{self.conversation_id}`
**Session Started:** `{self.session_start.strftime('%Y-%m-%d %H:%M:%S')}`

## Quick Commands:
- `/help` - Show all available commands
- `/status` - Show conversation status
- `/knowledge` - View knowledge graph
- `/history` - Show conversation history
- `/test` - Run semantic tests
- `/record` - Start recording conversation
- `/exit` - Quit the chat

Type your message to start chatting, or use commands starting with `/`
        """
        
        panel = Panel(
            Markdown(welcome_text),
            title="[bold cyan]Welcome to ConvoTree[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def _handle_chat_message(self, message: str):
        """Handle regular chat messages"""
        start_time = datetime.now()
        
        # Capture pre-message state for recording
        pre_knowledge = []
        pre_context = {}
        if self.recording:
            try:
                pre_knowledge = self.chat.kg._get_recent_knowledge(1000)
                pre_context = self.chat.kg._get_context_state()
            except:
                pass
        
        with self.console.status("[bold green]Thinking...", spinner="dots"):
            try:
                # Process message through the enhanced chat system
                result = self.chat.process_message(message)
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                # Capture post-message state for recording
                if self.recording:
                    try:
                        post_knowledge = self.chat.kg._get_recent_knowledge(1000)
                        post_context = self.chat.kg._get_context_state()
                        
                        # Find new knowledge added
                        new_knowledge = [k for k in post_knowledge if k not in pre_knowledge]
                        
                        # Record this interaction
                        self._record_interaction(
                            message_type="chat",
                            user_input=message,
                            assistant_response=result['response'],
                            response_time=response_time,
                            context_before=pre_context,
                            context_after=post_context,
                            knowledge_before_count=len(pre_knowledge),
                            knowledge_after_count=len(post_knowledge),
                            new_knowledge=new_knowledge,
                            context_used=result.get('context_used', {}),
                            conversation_stats=result.get('conversation_stats', {}),
                            start_time=start_time,
                            end_time=end_time
                        )
                    except Exception as recording_error:
                        self.console.print(f"[dim red]Recording error: {recording_error}[/dim red]")
                
                # Store debug info for later inspection
                if result.get('debug_info'):
                    self.last_debug_info = result['debug_info']
                
                # Display the response
                response_panel = Panel(
                    result['response'],
                    title="[bold green]Assistant[/bold green]",
                    border_style="green"
                )
                self.console.print(response_panel)
                
                # Show context info if verbose
                context_info = result.get('context_used', {})
                if context_info.get('relevant_facts_count', 0) > 0:
                    self.console.print(
                        f"[dim]💡 Used {context_info['relevant_facts_count']} knowledge facts, "
                        f"{context_info['recent_turns_count']} recent turns[/dim]"
                    )
                
                # Show debug mode indicator
                if self.debug_mode:
                    self.console.print(f"[dim cyan]🔍 Debug mode active - Use /debug-llm to see LLM input details[/dim cyan]")
                
                # Show recording indicator
                if self.recording:
                    self.console.print(f"[dim red]🔴 Recording ({response_time:.2f}s)[/dim red]")
                    
            except Exception as e:
                self.console.print(f"[red]Error processing message: {e}[/red]")
                
                # Record error if recording
                if self.recording:
                    self._record_interaction(
                        message_type="error",
                        user_input=message,
                        error=str(e),
                        start_time=start_time,
                        end_time=datetime.now()
                    )
    
    def _handle_command(self, command_input: str):
        """Handle command input"""
        parts = command_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                self.console.print(f"[red]Error executing command '{command}': {e}[/red]")
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("[yellow]Use /help to see available commands[/yellow]")
    
    def _cmd_help(self, args: List[str]):
        """Show help information"""
        help_table = Table(title="ConvoTree CLI Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        help_table.add_column("Usage", style="green")
        
        commands_info = [
            ("/help, /h", "Show this help message", "/help"),
            ("/exit, /quit, /q", "Exit the chat", "/exit"),
            ("/status", "Show conversation status and stats", "/status"),
            ("/history [limit]", "Show conversation history", "/history 10"),
            ("/knowledge [limit]", "Show knowledge graph facts", "/knowledge 20"),
            ("/context", "Show current context state", "/context"),
            ("/stats", "Show detailed statistics", "/stats"),
            ("/export [format]", "Export conversation data", "/export json"),
            ("/clear", "Clear the terminal screen", "/clear"),
            ("/search <query>", "Search knowledge graph", "/search user preferences"),
            ("/analyze", "Analyze conversation patterns", "/analyze"),
            ("/visualize, /viz", "Create knowledge graph visualization", "/viz"),
            ("/db <query>", "Execute database query", "/db SELECT COUNT(*) FROM turns"),
            ("/conversations", "List all conversations", "/conversations"),
            ("/switch <id>", "Switch to different conversation", "/switch other_id"),
            ("/new [id]", "Create new conversation", "/new project_chat"),
            ("/delete <id>", "Delete a conversation", "/delete old_chat"),
            ("/test [type]", "Run semantic tests", "/test memory"),
            ("/benchmark", "Run performance benchmarks", "/benchmark"),
            ("/debug", "Show debug information", "/debug"),
            ("/debug-mode", "Toggle debug mode on/off", "/debug-mode"),
            ("/debug-llm", "Show last LLM input/output details", "/debug-llm"),
            ("/record [name]", "Start recording conversation", "/record test_session"),
            ("/stop", "Stop recording and save", "/stop"),
            ("/replay [file]", "Replay/analyze recording", "/replay recording_test.json")
        ]
        
        for cmd, desc, usage in commands_info:
            help_table.add_row(cmd, desc, usage)
        
        self.console.print(help_table)
    
    def _cmd_exit(self, args: List[str]):
        """Exit the chat"""
        self.console.print("[cyan]Saving session and exiting...[/cyan]")
        self._save_session_history()
        sys.exit(0)
    
    def _cmd_status(self, args: List[str]):
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
**Database:** `{self.db_path}`
            """
            
            panel = Panel(
                Markdown(status_info),
                title="[bold blue]Conversation Status[/bold blue]",
                border_style="blue"
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Error getting status: {e}[/red]")
    
    def _cmd_history(self, args: List[str]):
        """Show conversation history"""
        try:
            limit = int(args[0]) if args and args[0].isdigit() else 20
            history = self.chat.get_conversation_history(limit)
            
            if not history:
                self.console.print("[yellow]No conversation history found[/yellow]")
                return
            
            history_table = Table(title=f"Conversation History (Last {len(history)} turns)")
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
    
    def _cmd_knowledge(self, args: List[str]):
        """Show knowledge graph facts"""
        try:
            limit = int(args[0]) if args and args[0].isdigit() else 20
            facts = self.chat.kg._get_recent_knowledge(limit)
            
            if not facts:
                self.console.print("[yellow]No knowledge facts found[/yellow]")
                return
            
            knowledge_table = Table(title=f"Knowledge Graph Facts (Last {len(facts)})")
            knowledge_table.add_column("Fact", style="green")
            
            for fact in facts:
                knowledge_table.add_row(fact)
            
            self.console.print(knowledge_table)
            
        except Exception as e:
            self.console.print(f"[red]Error getting knowledge: {e}[/red]")
    
    def _cmd_context(self, args: List[str]):
        """Show current context state"""
        try:
            context_state = self.chat.kg._get_context_state()
            
            if not context_state:
                self.console.print("[yellow]No context state found[/yellow]")
                return
            
            context_text = json.dumps(context_state, indent=2)
            panel = Panel(
                context_text,
                title="[bold yellow]Current Context State[/bold yellow]",
                border_style="yellow"
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Error getting context: {e}[/red]")
    
    def _cmd_stats(self, args: List[str]):
        """Show detailed statistics"""
        try:
            # Get database statistics
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM conversations) as total_conversations,
                        (SELECT COUNT(*) FROM turns) as total_turns,
                        (SELECT COUNT(*) FROM knowledge_triples) as total_triples,
                        (SELECT COUNT(*) FROM context_state) as contexts_with_state
                """)
                stats = cursor.fetchone()
            
            # Get conversation-specific stats
            summary = self.chat.kg.get_conversation_summary()
            
            # Get recent activity
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT DATE(timestamp) as date, COUNT(*) as turn_count
                    FROM turns 
                    WHERE conversation_id = ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                    LIMIT 7
                """, (self.conversation_id,))
                recent_activity = cursor.fetchall()
            
            stats_info = f"""
## Global Database Statistics
- **Total Conversations:** {stats[0]}
- **Total Turns:** {stats[1]}
- **Total Knowledge Triples:** {stats[2]}
- **Contexts with State:** {stats[3]}

## Current Conversation Statistics
- **Turn Count:** {summary['turn_count']}
- **Knowledge Triples:** {summary['knowledge_triples']}
- **Active Since:** {summary.get('first_turn', 'N/A')[:19]}

## Recent Activity (Last 7 Days)
            """
            
            for date, count in recent_activity:
                stats_info += f"\n- **{date}:** {count} turns"
            
            panel = Panel(
                Markdown(stats_info),
                title="[bold magenta]Detailed Statistics[/bold magenta]",
                border_style="magenta"
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Error getting statistics: {e}[/red]")
    
    def _cmd_export(self, args: List[str]):
        """Export conversation data"""
        try:
            format_type = args[0] if args else 'json'
            export_data = self.chat.export_conversation_data()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"conversation_export_{self.conversation_id}_{timestamp}.{format_type}"
            
            if format_type.lower() == 'json':
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
            else:
                self.console.print(f"[red]Unsupported format: {format_type}[/red]")
                return
            
            self.console.print(f"[green]Exported conversation to: {filename}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error exporting data: {e}[/red]")
    
    def _cmd_clear(self, args: List[str]):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self._display_welcome()
    
    def _cmd_search(self, args: List[str]):
        """Search knowledge graph"""
        if not args:
            self.console.print("[red]Please provide a search query[/red]")
            return
        
        query = ' '.join(args)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT subject, relation, object, confidence, created_at
                    FROM knowledge_triples
                    WHERE conversation_id = ? AND (
                        subject LIKE ? OR
                        relation LIKE ? OR
                        object LIKE ?
                    )
                    ORDER BY created_at DESC
                    LIMIT 20
                """, (self.conversation_id, f'%{query}%', f'%{query}%', f'%{query}%'))
                
                results = cursor.fetchall()
            
            if not results:
                self.console.print(f"[yellow]No results found for query: {query}[/yellow]")
                return
            
            search_table = Table(title=f"Search Results for '{query}'")
            search_table.add_column("Subject", style="cyan")
            search_table.add_column("Relation", style="yellow")
            search_table.add_column("Object", style="green")
            search_table.add_column("Confidence", style="blue")
            search_table.add_column("Created", style="dim")
            
            for subject, relation, obj, confidence, created in results:
                search_table.add_row(
                    subject, relation, obj, 
                    f"{confidence:.2f}", 
                    created[:19]
                )
            
            self.console.print(search_table)
            
        except Exception as e:
            self.console.print(f"[red]Error searching: {e}[/red]")
    
    def _cmd_analyze(self, args: List[str]):
        """Analyze conversation patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get turn patterns
                cursor = conn.execute("""
                    SELECT role, COUNT(*) as count, AVG(LENGTH(content)) as avg_length
                    FROM turns
                    WHERE conversation_id = ?
                    GROUP BY role
                """, (self.conversation_id,))
                role_stats = cursor.fetchall()
                
                # Get most common relations
                cursor = conn.execute("""
                    SELECT relation, COUNT(*) as count
                    FROM knowledge_triples
                    WHERE conversation_id = ?
                    GROUP BY relation
                    ORDER BY count DESC
                    LIMIT 10
                """, (self.conversation_id,))
                relation_stats = cursor.fetchall()
                
                # Get activity patterns
                cursor = conn.execute("""
                    SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                    FROM turns
                    WHERE conversation_id = ?
                    GROUP BY hour
                    ORDER BY count DESC
                    LIMIT 5
                """, (self.conversation_id,))
                activity_stats = cursor.fetchall()
            
            analysis_info = "## Conversation Analysis\n\n### Turn Patterns\n"
            for role, count, avg_length in role_stats:
                analysis_info += f"- **{role.title()}:** {count} turns, avg {avg_length:.1f} chars\n"
            
            analysis_info += "\n### Most Common Relations\n"
            for relation, count in relation_stats:
                analysis_info += f"- **{relation}:** {count} occurrences\n"
            
            analysis_info += "\n### Most Active Hours\n"
            for hour, count in activity_stats:
                analysis_info += f"- **{hour}:00:** {count} turns\n"
            
            panel = Panel(
                Markdown(analysis_info),
                title="[bold cyan]Conversation Analysis[/bold cyan]",
                border_style="cyan"
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Error analyzing conversation: {e}[/red]")
    
    def _cmd_visualize(self, args: List[str]):
        """Create knowledge graph visualization"""
        try:
            facts = self.chat.kg._get_recent_knowledge(50)
            
            if not facts:
                self.console.print("[yellow]No knowledge facts to visualize[/yellow]")
                return
            
            # Create network graph
            G = nx.DiGraph()
            
            for fact in facts:
                parts = fact.split(' → ')
                if len(parts) == 3:
                    subject, relation, obj = parts
                    G.add_edge(subject.strip(), obj.strip(), label=relation.strip())
            
            if G.number_of_nodes() == 0:
                self.console.print("[yellow]No valid relationships found for visualization[/yellow]")
                return
            
            # Create visualization
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G, k=0.5, iterations=50)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=1000, alpha=0.7)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, edge_color='gray', 
                                 arrows=True, arrowsize=20, alpha=0.5)
            
            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
            
            # Draw edge labels (relations)
            edge_labels = nx.get_edge_attributes(G, 'label')
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
            
            plt.title(f"Knowledge Graph Visualization - {self.conversation_id}")
            plt.axis('off')
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"knowledge_graph_{self.conversation_id}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.console.print(f"[green]Knowledge graph saved to: {filename}[/green]")
            self.console.print(f"[blue]Graph contains {G.number_of_nodes()} nodes and {G.number_of_edges()} relationships[/blue]")
            
        except Exception as e:
            self.console.print(f"[red]Error creating visualization: {e}[/red]")
    
    def _cmd_database(self, args: List[str]):
        """Execute database query"""
        if not args:
            self.console.print("[red]Please provide a SQL query[/red]")
            return
        
        query = ' '.join(args)
        
        # Safety check for destructive operations
        destructive_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
        if any(keyword in query.upper() for keyword in destructive_keywords):
            self.console.print("[red]Destructive queries are not allowed in CLI mode[/red]")
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query)
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
            
            if not results:
                self.console.print("[yellow]Query returned no results[/yellow]")
                return
            
            # Create table for results
            db_table = Table(title="Database Query Results")
            for col in columns:
                db_table.add_column(col, style="white")
            
            for row in results[:20]:  # Limit to 20 rows for display
                db_table.add_row(*[str(cell) for cell in row])
            
            self.console.print(db_table)
            
            if len(results) > 20:
                self.console.print(f"[dim]Showing first 20 of {len(results)} results[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]Database query error: {e}[/red]")
    
    def _cmd_list_conversations(self, args: List[str]):
        """List all conversations"""
        try:
            conversations = self.conversation_manager.list_conversations()
            
            # Also get conversations from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, created_at, last_updated,
                           (SELECT COUNT(*) FROM turns WHERE conversation_id = conversations.id) as turn_count,
                           (SELECT COUNT(*) FROM knowledge_triples WHERE conversation_id = conversations.id) as triple_count
                    FROM conversations
                    ORDER BY last_updated DESC
                """)
                db_conversations = cursor.fetchall()
            
            if not db_conversations:
                self.console.print("[yellow]No conversations found[/yellow]")
                return
            
            conv_table = Table(title="All Conversations")
            conv_table.add_column("ID", style="cyan")
            conv_table.add_column("Created", style="dim")
            conv_table.add_column("Last Updated", style="dim")
            conv_table.add_column("Turns", style="blue")
            conv_table.add_column("Knowledge", style="green")
            conv_table.add_column("Active", style="yellow")
            
            for conv_id, created, updated, turns, triples in db_conversations:
                is_active = "✓" if conv_id in conversations else ""
                is_current = " (current)" if conv_id == self.conversation_id else ""
                
                conv_table.add_row(
                    conv_id + is_current,
                    created[:19] if created else "N/A",
                    updated[:19] if updated else "N/A",
                    str(turns),
                    str(triples),
                    is_active
                )
            
            self.console.print(conv_table)
            
        except Exception as e:
            self.console.print(f"[red]Error listing conversations: {e}[/red]")
    
    def _cmd_switch_conversation(self, args: List[str]):
        """Switch to a different conversation"""
        if not args:
            self.console.print("[red]Please provide a conversation ID[/red]")
            return
        
        new_conversation_id = args[0]
        
        try:
            # Check if conversation exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT id FROM conversations WHERE id = ?", (new_conversation_id,))
                if not cursor.fetchone():
                    self.console.print(f"[red]Conversation '{new_conversation_id}' not found[/red]")
                    return
            
            # Switch to new conversation
            self.conversation_id = new_conversation_id
            self.chat = self.conversation_manager.get_conversation(self.conversation_id)
            
            self.console.print(f"[green]Switched to conversation: {self.conversation_id}[/green]")
            
            # Show brief status of new conversation
            summary = self.chat.kg.get_conversation_summary()
            self.console.print(f"[dim]Turns: {summary['turn_count']}, Knowledge: {summary['knowledge_triples']}[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]Error switching conversation: {e}[/red]")
    
    def _cmd_new_conversation(self, args: List[str]):
        """Create a new conversation"""
        if args:
            new_id = args[0]
        else:
            new_id = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Check if conversation already exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT id FROM conversations WHERE id = ?", (new_id,))
                if cursor.fetchone():
                    self.console.print(f"[red]Conversation '{new_id}' already exists[/red]")
                    return
            
            # Create and switch to new conversation
            self.conversation_id = new_id
            self.chat = self.conversation_manager.get_conversation(self.conversation_id)
            
            self.console.print(f"[green]Created and switched to new conversation: {self.conversation_id}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error creating conversation: {e}[/red]")
    
    def _cmd_delete_conversation(self, args: List[str]):
        """Delete a conversation"""
        if not args:
            self.console.print("[red]Please provide a conversation ID[/red]")
            return
        
        conversation_id = args[0]
        
        if conversation_id == self.conversation_id:
            self.console.print("[red]Cannot delete the current conversation[/red]")
            return
        
        try:
            # Delete from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM knowledge_triples WHERE conversation_id = ?", (conversation_id,))
                conn.execute("DELETE FROM turns WHERE conversation_id = ?", (conversation_id,))
                conn.execute("DELETE FROM context_state WHERE conversation_id = ?", (conversation_id,))
                conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
                conn.commit()
            
            # Remove from active conversations
            self.conversation_manager.close_conversation(conversation_id)
            
            self.console.print(f"[green]Deleted conversation: {conversation_id}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error deleting conversation: {e}[/red]")
    
    def _cmd_semantic_test(self, args: List[str]):
        """Run semantic tests"""
        test_type = args[0] if args else 'memory'
        
        semantic_tests = {
            'memory': self._test_memory_retention,
            'consistency': self._test_consistency,
            'knowledge': self._test_knowledge_integration,
            'context': self._test_context_awareness,
            'all': self._run_all_semantic_tests
        }
        
        if test_type not in semantic_tests:
            self.console.print(f"[red]Unknown test type: {test_type}[/red]")
            self.console.print(f"[yellow]Available tests: {', '.join(semantic_tests.keys())}[/yellow]")
            return
        
        with self.console.status(f"[bold green]Running {test_type} test...", spinner="dots"):
            try:
                result = semantic_tests[test_type]()
                self.console.print(result)
            except Exception as e:
                self.console.print(f"[red]Error running test: {e}[/red]")
    
    def _test_memory_retention(self):
        """Test memory retention across conversation"""
        # Simulate a memory test
        test_facts = [
            "My favorite color is blue",
            "I work as a software engineer",
            "I live in San Francisco"
        ]
        
        results = []
        for fact in test_facts:
            # Send the fact
            self.chat.process_message(fact)
            
            # Ask about it
            query = f"What do you remember about {fact.split()[2]}?"
            response = self.chat.process_message(query)
            
            # Check if the fact is retained
            retained = any(word in response['response'].lower() for word in fact.lower().split())
            results.append({
                'fact': fact,
                'retained': retained,
                'response_length': len(response['response'])
            })
        
        # Format results
        test_table = Table(title="Memory Retention Test Results")
        test_table.add_column("Test Fact", style="cyan")
        test_table.add_column("Retained", style="green")
        test_table.add_column("Response Length", style="blue")
        
        for result in results:
            retained_symbol = "✓" if result['retained'] else "✗"
            test_table.add_row(
                result['fact'],
                retained_symbol,
                str(result['response_length'])
            )
        
        return test_table
    
    def _test_consistency(self):
        """Test response consistency"""
        test_query = "What is your primary function?"
        responses = []
        
        # Ask the same question multiple times
        for i in range(3):
            response = self.chat.process_message(test_query)
            responses.append(response['response'])
        
        # Check for consistency (simplified)
        consistency_score = len(set(responses)) == 1  # All responses are identical
        
        return Panel(
            f"**Test Query:** {test_query}\n\n"
            f"**Responses Generated:** {len(responses)}\n"
            f"**Consistency Score:** {'✓ Identical' if consistency_score else '✗ Variable'}\n\n"
            f"**Sample Response:** {responses[0][:100]}...",
            title="[bold yellow]Consistency Test Results[/bold yellow]",
            border_style="yellow"
        )
    
    def _test_knowledge_integration(self):
        """Test knowledge integration"""
        # Get current knowledge count
        initial_facts = len(self.chat.kg._get_recent_knowledge(1000))
        
        # Add new information
        self.chat.process_message("I am learning about artificial intelligence and machine learning.")
        
        # Check if knowledge increased
        new_facts = len(self.chat.kg._get_recent_knowledge(1000))
        knowledge_added = new_facts > initial_facts
        
        # Test knowledge retrieval
        response = self.chat.process_message("What am I learning about?")
        knowledge_retrieved = "artificial intelligence" in response['response'].lower() or "machine learning" in response['response'].lower()
        
        return Panel(
            f"**Initial Knowledge Facts:** {initial_facts}\n"
            f"**New Knowledge Facts:** {new_facts}\n"
            f"**Knowledge Added:** {'✓' if knowledge_added else '✗'}\n"
            f"**Knowledge Retrieved:** {'✓' if knowledge_retrieved else '✗'}\n\n"
            f"**Test Response:** {response['response'][:150]}...",
            title="[bold green]Knowledge Integration Test Results[/bold green]",
            border_style="green"
        )
    
    def _test_context_awareness(self):
        """Test context awareness"""
        # Set up context
        self.chat.process_message("I'm working on a Python project about web scraping.")
        context_before = self.chat.kg._get_context_state()
        
        # Test context-aware response
        response = self.chat.process_message("Can you suggest some libraries?")
        
        # Check if response is contextually relevant
        relevant_terms = ['python', 'scraping', 'beautiful', 'requests', 'selenium']
        context_aware = any(term in response['response'].lower() for term in relevant_terms)
        
        context_after = self.chat.kg._get_context_state()
        context_updated = len(context_after) >= len(context_before)
        
        return Panel(
            f"**Context Before:** {len(context_before)} items\n"
            f"**Context After:** {len(context_after)} items\n"
            f"**Context Updated:** {'✓' if context_updated else '✗'}\n"
            f"**Response Relevance:** {'✓' if context_aware else '✗'}\n\n"
            f"**Response:** {response['response'][:150]}...",
            title="[bold blue]Context Awareness Test Results[/bold blue]",
            border_style="blue"
        )
    
    def _run_all_semantic_tests(self):
        """Run all semantic tests"""
        self.console.print("[cyan]Running comprehensive semantic test suite...[/cyan]")
        
        tests = [
            ("Memory Retention", self._test_memory_retention),
            ("Consistency", self._test_consistency),
            ("Knowledge Integration", self._test_knowledge_integration),
            ("Context Awareness", self._test_context_awareness)
        ]
        
        results = []
        for test_name, test_func in tests:
            self.console.print(f"[dim]Running {test_name} test...[/dim]")
            try:
                result = test_func()
                results.append((test_name, result, True))
            except Exception as e:
                results.append((test_name, f"Error: {e}", False))
        
        # Display all results
        for test_name, result, success in results:
            if success:
                self.console.print(result)
            else:
                self.console.print(f"[red]{test_name} failed: {result}[/red]")
        
        return f"Completed {len(tests)} semantic tests"
    
    def _cmd_benchmark(self, args: List[str]):
        """Run performance benchmarks"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            # Response time benchmark
            task1 = progress.add_task("Testing response times...", total=10)
            response_times = []
            
            for i in range(10):
                start_time = datetime.now()
                self.chat.process_message(f"Test message {i}")
                end_time = datetime.now()
                response_times.append((end_time - start_time).total_seconds())
                progress.update(task1, advance=1)
            
            # Knowledge retrieval benchmark
            task2 = progress.add_task("Testing knowledge retrieval...", total=5)
            retrieval_times = []
            
            for i in range(5):
                start_time = datetime.now()
                self.chat.kg._get_recent_knowledge(100)
                end_time = datetime.now()
                retrieval_times.append((end_time - start_time).total_seconds())
                progress.update(task2, advance=1)
        
        # Display benchmark results
        benchmark_info = f"""
## Performance Benchmark Results

### Response Time Test (10 messages)
- **Average:** {sum(response_times) / len(response_times):.3f}s
- **Min:** {min(response_times):.3f}s
- **Max:** {max(response_times):.3f}s

### Knowledge Retrieval Test (5 queries)
- **Average:** {sum(retrieval_times) / len(retrieval_times):.3f}s
- **Min:** {min(retrieval_times):.3f}s
- **Max:** {max(retrieval_times):.3f}s
        """
        
        panel = Panel(
            Markdown(benchmark_info),
            title="[bold red]Benchmark Results[/bold red]",
            border_style="red"
        )
        self.console.print(panel)
    
    def _cmd_debug(self, args: List[str]):
        """Show debug information"""
        try:
            debug_info = {
                "conversation_id": self.conversation_id,
                "database_path": str(Path(self.db_path).absolute()),
                "session_start": self.session_start.isoformat(),
                "command_history_count": len(self.command_history),
                "active_conversations": len(self.conversation_manager.list_conversations())
            }
            
            # Check database file
            db_path = Path(self.db_path)
            if db_path.exists():
                debug_info["database_size_mb"] = db_path.stat().st_size / 1024 / 1024
            else:
                debug_info["database_exists"] = False
            
            # Get memory usage
            try:
                import psutil
                process = psutil.Process()
                debug_info["memory_usage_mb"] = process.memory_info().rss / 1024 / 1024
            except ImportError:
                debug_info["memory_usage"] = "psutil not available"
            
            debug_text = json.dumps(debug_info, indent=2)
            panel = Panel(
                debug_text,
                title="[bold red]Debug Information[/bold red]",
                border_style="red"
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Error getting debug info: {e}[/red]")
    
    def _cmd_debug_llm(self, args: List[str]):
        """Show what was sent to LLM in the last interaction"""
        try:
            # Get the last response debug info if available
            if hasattr(self, 'last_debug_info') and self.last_debug_info:
                debug_info = self.last_debug_info
                
                # Display system prompt
                prompt_panel = Panel(
                    debug_info.get("system_prompt", "No system prompt available"),
                    title="[bold cyan]Last System Prompt Sent to LLM[/bold cyan]",
                    border_style="cyan"
                )
                self.console.print(prompt_panel)
                
                # Display user message
                user_msg_panel = Panel(
                    debug_info.get("user_message", "No user message available"),
                    title="[bold green]User Message[/bold green]",
                    border_style="green"
                )
                self.console.print(user_msg_panel)
                
                # Display context breakdown
                context_info = f"""
**Context Summary:** {debug_info.get('context_summary', 'N/A')}
**Relevant Facts:** {len(debug_info.get('relevant_facts', []))} facts
**Recent Turns:** {len(debug_info.get('recent_turns', []))} turns
**User Context Items:** {len(debug_info.get('user_context', {}))} items
                """
                
                context_panel = Panel(
                    Markdown(context_info),
                    title="[bold yellow]Context Breakdown[/bold yellow]",
                    border_style="yellow"
                )
                self.console.print(context_panel)
                
                # Show facts if any
                if debug_info.get('relevant_facts'):
                    facts_text = "\n".join([f"• {fact}" for fact in debug_info['relevant_facts'][:10]])
                    if len(debug_info['relevant_facts']) > 10:
                        facts_text += f"\n... and {len(debug_info['relevant_facts']) - 10} more facts"
                    
                    facts_panel = Panel(
                        facts_text,
                        title="[bold magenta]Relevant Facts Used[/bold magenta]",
                        border_style="magenta"
                    )
                    self.console.print(facts_panel)
                
            else:
                self.console.print("[yellow]No debug information available. Enable debug mode with /debug-mode and send a message.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Error showing LLM debug info: {e}[/red]")
    
    def _cmd_toggle_debug_mode(self, args: List[str]):
        """Toggle debug mode on/off"""
        try:
            # Toggle debug mode
            self.debug_mode = not self.debug_mode
            
            # Update the conversation manager and chat system
            self.conversation_manager.debug_mode = self.debug_mode
            
            # Update existing chat instance
            if hasattr(self.chat, 'debug_mode'):
                self.chat.debug_mode = self.debug_mode
            
            # Create new chat instance with debug mode (to ensure it's properly set)
            self.chat = self.conversation_manager.get_conversation(self.conversation_id)
            
            status = "ON" if self.debug_mode else "OFF"
            color = "green" if self.debug_mode else "red"
            
            self.console.print(f"[{color}]Debug mode turned {status}[/{color}]")
            
            if self.debug_mode:
                self.console.print("[dim]Debug mode will show detailed LLM input/output for each message.[/dim]")
                self.console.print("[dim]Use /debug-llm to see the last LLM interaction details.[/dim]")
            else:
                self.console.print("[dim]Debug mode disabled. Normal conversation mode.[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]Error toggling debug mode: {e}[/red]")
    
    def _save_session_history(self):
        """Save session command history"""
        try:
            # Save to readline history
            history_file = Path('.convotree_history')
            readline.write_history_file(str(history_file))
            
            # Save session log
            session_log = {
                "conversation_id": self.conversation_id,
                "session_start": self.session_start.isoformat(),
                "session_end": datetime.now().isoformat(),
                "command_history": self.command_history
            }
            
            log_file = f"session_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_file, 'w') as f:
                json.dump(session_log, f, indent=2, default=str)
                
        except Exception as e:
            # Don't show error on exit, just fail silently
            pass
    
    def _record_interaction(self, **interaction_data):
        """Record detailed interaction data"""
        if not self.recording:
            return
        
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": self.conversation_id,
            "interaction_id": len(self.recording_data) + 1,
            **interaction_data
        }
        
        self.recording_data.append(interaction_record)
    
    def _cmd_record(self, args: List[str]):
        """Start recording conversation"""
        if self.recording:
            self.console.print("[yellow]Recording is already active. Use /stop to end current recording.[/yellow]")
            return
        
        # Start recording
        self.recording = True
        self.recording_start = datetime.now()
        self.recording_data = []
        
        # Generate recording filename
        timestamp = self.recording_start.strftime('%Y%m%d_%H%M%S')
        test_name = args[0] if args else "conversation"
        self.recording_file = f"recording_{test_name}_{self.conversation_id}_{timestamp}.json"
        
        # Record session start
        self._record_interaction(
            message_type="recording_start",
            test_name=test_name,
            session_info={
                "conversation_id": self.conversation_id,
                "database_path": self.db_path,
                "recording_file": self.recording_file
            }
        )
        
        self.console.print(f"[green]🔴 Recording started: {self.recording_file}[/green]")
        self.console.print(f"[dim]Test name: {test_name}[/dim]")
        self.console.print(f"[dim]Use /stop to end recording[/dim]")
    
    def _cmd_stop_recording(self, args: List[str]):
        """Stop recording and save data"""
        if not self.recording:
            self.console.print("[yellow]No active recording to stop.[/yellow]")
            return
        
        # Record session end
        recording_end = datetime.now()
        duration = (recording_end - self.recording_start).total_seconds()
        
        self._record_interaction(
            message_type="recording_end",
            recording_duration=duration,
            total_interactions=len(self.recording_data)
        )
        
        # Compile final recording data
        final_recording = {
            "metadata": {
                "conversation_id": self.conversation_id,
                "recording_start": self.recording_start.isoformat(),
                "recording_end": recording_end.isoformat(),
                "duration_seconds": duration,
                "total_interactions": len(self.recording_data),
                "recording_file": self.recording_file
            },
            "conversation_summary": self._get_recording_summary(),
            "interactions": self.recording_data,
            "analysis": self._analyze_recording()
        }
        
        # Save recording to file
        try:
            with open(self.recording_file, 'w') as f:
                json.dump(final_recording, f, indent=2, default=str)
            
            self.console.print(f"[green]🟢 Recording stopped and saved: {self.recording_file}[/green]")
            self.console.print(f"[blue]Duration: {duration:.1f}s, Interactions: {len(self.recording_data)}[/blue]")
            
            # Show quick analysis
            analysis = final_recording["analysis"]
            self.console.print(f"[dim]Knowledge added: {analysis['knowledge_growth']}, "
                             f"Avg response time: {analysis['avg_response_time']:.2f}s[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]Error saving recording: {e}[/red]")
        finally:
            # Reset recording state
            self.recording = False
            self.recording_start = None
            self.recording_data = []
            self.recording_file = None
    
    def _cmd_replay_recording(self, args: List[str]):
        """Replay a saved recording"""
        if not args:
            # List available recordings
            recording_files = list(Path('.').glob('recording_*.json'))
            if not recording_files:
                self.console.print("[yellow]No recordings found[/yellow]")
                return
            
            self.console.print("[cyan]Available recordings:[/cyan]")
            for i, file in enumerate(recording_files, 1):
                try:
                    with open(file) as f:
                        data = json.load(f)
                    metadata = data.get("metadata", {})
                    duration = metadata.get("duration_seconds", 0)
                    interactions = metadata.get("total_interactions", 0)
                    self.console.print(f"  {i}. {file.name} ({duration:.1f}s, {interactions} interactions)")
                except:
                    self.console.print(f"  {i}. {file.name} (error reading)")
            
            self.console.print("[dim]Use: /replay <filename> to replay a recording[/dim]")
            return
        
        recording_file = args[0]
        if not recording_file.endswith('.json'):
            recording_file += '.json'
        
        try:
            with open(recording_file) as f:
                recording_data = json.load(f)
            
            self._display_recording_analysis(recording_data)
            
        except FileNotFoundError:
            self.console.print(f"[red]Recording file not found: {recording_file}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error loading recording: {e}[/red]")
    
    def _get_recording_summary(self):
        """Get summary of current conversation state"""
        try:
            return self.chat.kg.get_conversation_summary()
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_recording(self):
        """Analyze the recorded conversation"""
        if not self.recording_data:
            return {}
        
        # Extract chat interactions
        chat_interactions = [i for i in self.recording_data if i.get('message_type') == 'chat']
        
        if not chat_interactions:
            return {"error": "No chat interactions found"}
        
        # Calculate metrics
        response_times = [i.get('response_time', 0) for i in chat_interactions if 'response_time' in i]
        knowledge_counts = [(i.get('knowledge_after_count', 0) - i.get('knowledge_before_count', 0)) 
                           for i in chat_interactions if 'knowledge_after_count' in i]
        
        analysis = {
            "total_chat_interactions": len(chat_interactions),
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "knowledge_growth": sum(knowledge_counts) if knowledge_counts else 0,
            "new_knowledge_per_interaction": sum(knowledge_counts) / len(knowledge_counts) if knowledge_counts else 0
        }
        
        # Analyze knowledge patterns
        new_knowledge_items = []
        for interaction in chat_interactions:
            new_knowledge_items.extend(interaction.get('new_knowledge', []))
        
        analysis["unique_knowledge_items"] = len(set(new_knowledge_items))
        analysis["total_knowledge_items"] = len(new_knowledge_items)
        
        # Context usage analysis
        context_usage = [i.get('context_used', {}) for i in chat_interactions]
        if context_usage:
            total_facts_used = sum(ctx.get('relevant_facts_count', 0) for ctx in context_usage)
            analysis["total_facts_used"] = total_facts_used
            analysis["avg_facts_per_response"] = total_facts_used / len(context_usage)
        
        return analysis
    
    def _display_recording_analysis(self, recording_data):
        """Display comprehensive analysis of a recording"""
        metadata = recording_data.get("metadata", {})
        analysis = recording_data.get("analysis", {})
        interactions = recording_data.get("interactions", [])
        
        # Metadata panel
        metadata_info = f"""
**Recording File:** `{metadata.get('recording_file', 'Unknown')}`
**Conversation ID:** `{metadata.get('conversation_id', 'Unknown')}`
**Duration:** `{metadata.get('duration_seconds', 0):.1f} seconds`
**Total Interactions:** `{metadata.get('total_interactions', 0)}`
**Start Time:** `{metadata.get('recording_start', 'Unknown')}`
        """
        
        metadata_panel = Panel(
            Markdown(metadata_info),
            title="[bold cyan]Recording Metadata[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(metadata_panel)
        
        # Analysis panel
        if analysis:
            analysis_info = f"""
## Performance Metrics
- **Chat Interactions:** {analysis.get('total_chat_interactions', 0)}
- **Avg Response Time:** {analysis.get('avg_response_time', 0):.2f}s
- **Response Time Range:** {analysis.get('min_response_time', 0):.2f}s - {analysis.get('max_response_time', 0):.2f}s

## Knowledge Metrics
- **Knowledge Growth:** {analysis.get('knowledge_growth', 0)} new facts
- **Unique Knowledge Items:** {analysis.get('unique_knowledge_items', 0)}
- **Knowledge per Interaction:** {analysis.get('new_knowledge_per_interaction', 0):.1f}

## Context Usage
- **Total Facts Used:** {analysis.get('total_facts_used', 0)}
- **Avg Facts per Response:** {analysis.get('avg_facts_per_response', 0):.1f}
            """
            
            analysis_panel = Panel(
                Markdown(analysis_info),
                title="[bold green]Analysis Results[/bold green]",
                border_style="green"
            )
            self.console.print(analysis_panel)
        
        # Interaction timeline
        chat_interactions = [i for i in interactions if i.get('message_type') == 'chat'][:10]  # Show first 10
        
        if chat_interactions:
            timeline_table = Table(title="Interaction Timeline (First 10)")
            timeline_table.add_column("Time", style="dim")
            timeline_table.add_column("User Input", style="cyan", max_width=30)
            timeline_table.add_column("Response Time", style="blue")
            timeline_table.add_column("Knowledge Added", style="green")
            
            for interaction in chat_interactions:
                timestamp = interaction.get('timestamp', '')[:19]
                user_input = interaction.get('user_input', '')[:50]
                if len(interaction.get('user_input', '')) > 50:
                    user_input += "..."
                response_time = f"{interaction.get('response_time', 0):.2f}s"
                knowledge_added = len(interaction.get('new_knowledge', []))
                
                timeline_table.add_row(timestamp, user_input, response_time, str(knowledge_added))
            
            self.console.print(timeline_table)

def main():
    """Main CLI entry point"""
    # Load environment variables if not already loaded
    try:
        from dotenv import load_dotenv
        if not os.getenv("OPENAI_API_KEY"):
            load_dotenv()
            if os.getenv("OPENAI_API_KEY"):
                print("✅ Loaded environment variables from .env")
    except ImportError:
        pass
    
    parser = argparse.ArgumentParser(description="ConvoTree Interactive CLI")
    parser.add_argument("--conversation-id", "-c", type=str,
                       help="Conversation ID to use or resume")
    parser.add_argument("--database", "-d", type=str, default="conversations.db",
                       help="Database file path")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode to show LLM input/output details")
    
    args = parser.parse_args()
    
    try:
        cli = ConvoTreeCLI(
            conversation_id=args.conversation_id,
            db_path=args.database,
            debug_mode=args.debug
        )
        cli.start_chat()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
    except Exception as e:
        print(f"Error starting CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()