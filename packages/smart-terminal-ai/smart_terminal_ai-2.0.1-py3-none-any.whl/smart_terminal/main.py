"""
Main entry point for Smart Terminal
"""

import sys
import click
import time
from pathlib import Path

# Add the src directory to Python path for direct execution
if __name__ == "__main__":
    # When running directly, add src to path
    src_path = Path(__file__).parent.parent
    sys.path.insert(0, str(src_path))

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

from smart_terminal.core.command_mapper import CommandMapper
from smart_terminal.core.command_builder import CommandBuilder
from smart_terminal.core.command_executor import CommandExecutor
from smart_terminal.ai.learning_engine import LearningEngine
from smart_terminal.ai.suggestion_engine import SuggestionEngine
from smart_terminal.utils.config import Config
from smart_terminal.utils.shell_integration import ShellIntegration

console = Console()

class SmartTerminal:
    def __init__(self):
        self.config = Config()
        self.command_mapper = CommandMapper()
        self.command_builder = CommandBuilder()
        self.command_executor = CommandExecutor()
        
        # Initialize learning engine with debug mode from config
        debug_mode = self.config.get("ai.debug_database", False)
        self.learning_engine = LearningEngine(debug_mode=debug_mode)
        self.suggestion_engine = SuggestionEngine(self.learning_engine)
        self.shell_integration = ShellIntegration()
        
        # Command history for session
        self.command_history = []
        
        # Bookmarks for frequently used commands
        self.bookmarks = self._load_bookmarks()
        
        # Show welcome message
        self._show_welcome()
    
    def _load_bookmarks(self) -> dict:
        """Load bookmarks from config"""
        return self.config.get("bookmarks", {})
    
    def _save_bookmarks(self):
        """Save bookmarks to config"""
        self.config.set("bookmarks", self.bookmarks)
    
    def _show_welcome(self):
        """Show welcome message and platform info"""
        if self.config.get("display.verbose_mode", False):
            # Detailed welcome for verbose mode
            platform_info = self.command_builder.get_platform_info()
            
            welcome_text = Text()
            welcome_text.append("🚀 Smart Terminal v2.0", style="bold blue")
            welcome_text.append(f"\nPlatform: {platform_info['os'].title()}")
            welcome_text.append(f"\nShell: {platform_info['shell']}")
            
            if self.shell_integration.check_shell_integration():
                welcome_text.append("\n✅ Shell integration active")
            else:
                welcome_text.append("\n⚠️  Shell integration not installed")
            
            welcome_text.append(f"\n📚 Commands learned: {len(self.command_history)}")
            welcome_text.append(f"\n🔖 Bookmarks: {len(self.bookmarks)}")
            
            console.print(Panel(welcome_text, title="Welcome", box=box.ROUNDED))
        else:
            # Simple welcome for regular users
            welcome_text = Text()
            welcome_text.append("🚀 Smart Terminal", style="bold blue")
            welcome_text.append("\nYour AI-powered command assistant")
            
            console.print(Panel(welcome_text, title="Welcome", box=box.ROUNDED))
    
    def run_interactive(self):
        """Run interactive mode"""
        if not self.config.get("display.verbose_mode", False):
            console.print("\n[bold green]Smart Terminal is ready![/bold green]")
            console.print("Just tell me what you want to do in plain English.")
            console.print("Type 'help' for examples, 'simple' for beginner mode, 'exit' to quit\n")
        else:
            console.print("\n[bold green]Interactive Mode (Verbose)[/bold green]")
            console.print("Type 'help' for available commands, 'exit' to quit\n")
        
        while True:
            try:
                user_input = Prompt.ask("What would you like to do?")
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() == 'stats':
                    self._show_stats()
                elif user_input.lower() == 'config':
                    self._show_config()
                elif user_input.lower() == 'install':
                    self._install_integration()
                elif user_input.lower() == 'history':
                    self._show_history()
                elif user_input.lower().startswith('bookmark'):
                    self._handle_bookmark(user_input)
                elif user_input.lower() == 'clear':
                    console.clear()
                elif user_input.lower() == 'version':
                    self._show_version()
                elif user_input.lower().startswith('alias'):
                    self._handle_alias(user_input)
                elif user_input.lower() == 'verbose':
                    self._toggle_verbose_mode()
                elif user_input.lower() == 'simple':
                    self._set_simple_mode()
                elif user_input.lower() == 'debug':
                    self._toggle_debug_mode()
                else:
                    self._process_command(user_input)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def run_direct(self, user_input: str):
        """Run direct command mode"""
        self._process_command(user_input)
    
    def _process_command(self, user_input: str):
        """Process a user command"""
        try:
            # Add to session history
            self.command_history.append({
                "input": user_input,
                "timestamp": time.time()
            })
            
            # Check if it's a bookmarked command
            if user_input in self.bookmarks:
                user_input = self.bookmarks[user_input]
                console.print(f"[blue]Using bookmark:[/blue] {user_input}")
            
            # Parse user intent
            intent = self.command_mapper.parse_intent(user_input)
            
            # Build command
            command = self.command_builder.build_command(intent)
            
            # Only show technical details if user wants verbose mode
            if self.config.get("display.verbose_mode", False):
                console.print(f"\n[blue]Intent:[/blue] {intent.action} {intent.target}")
                console.print(f"[blue]Command:[/blue] {command}")
                
                # Get suggestions if enabled
                if self.config.get("ai.enable_learning"):
                    suggestions = self.suggestion_engine.get_smart_suggestions(user_input)
                    if suggestions:
                        self._show_suggestions(suggestions)
            
            # Show safety warning if needed
            is_safe, safety_msg = self.command_executor.validate_command(command)
            if not is_safe:
                console.print(f"[red]{safety_msg}[/red]")
                return
            elif "WARNING" in safety_msg:
                console.print(f"[yellow]{safety_msg}[/yellow]")
            
            # Confirm execution for dangerous commands
            if self.config.get("safety.require_confirmation_for_deletion") and intent.action == "delete":
                if not Confirm.ask("This will permanently delete files. Continue?"):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
            
            # Execute command with progress indicator for long operations
            start_time = time.time()
            
            # Show simple working message for user-friendly experience
            if intent.action in ["git", "network", "system"]:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Working...", total=None)
                    success, output, return_code = self.command_executor.execute_command(command, show_command=False)
            else:
                success, output, return_code = self.command_executor.execute_command(command, show_command=False)
            
            execution_time = time.time() - start_time
            
            # Record for learning
            if self.config.get("ai.enable_learning"):
                self.learning_engine.record_command(
                    user_input, command, success, execution_time, 
                    self.command_builder.os_type
                )
            
            # Show execution time only in verbose mode
            if self.config.get("display.verbose_mode", False) and self.config.get("display.show_execution_time"):
                console.print(f"[dim]Execution time: {execution_time:.2f}s[/dim]")
            
            # Show simple success/failure message for regular users
            if not self.config.get("display.verbose_mode", False):
                if success:
                    if intent.action == "create":
                        console.print(f"[green]✅ Created '{intent.target}' successfully[/green]")
                    elif intent.action == "delete":
                        console.print(f"[green]✅ Deleted '{intent.target}' successfully[/green]")
                    elif intent.action == "copy":
                        console.print(f"[green]✅ Copied '{intent.target}' to '{intent.destination}' successfully[/green]")
                    elif intent.action == "move":
                        console.print(f"[green]✅ Moved '{intent.target}' to '{intent.destination}' successfully[/green]")
                    elif intent.action == "list":
                        # For list commands, show the actual output
                        if output and output.strip():
                            console.print(output)
                        else:
                            console.print("[green]✅ Directory contents shown above[/green]")
                    elif intent.action == "git":
                        console.print(f"[green]✅ Git operation completed successfully[/green]")
                    elif intent.action == "system":
                        if output and output.strip():
                            console.print(output)
                        else:
                            console.print("[green]✅ System information displayed[/green]")
                    elif intent.action == "network":
                        if output and output.strip():
                            console.print(output)
                        else:
                            console.print("[green]✅ Network operation completed[/green]")
                    else:
                        console.print("[green]✅ Task completed successfully[/green]")
                else:
                    console.print(f"[red]❌ Failed to complete task[/red]")
                    if output and output.strip():
                        console.print(f"[yellow]Error: {output}[/yellow]")
            
            # Ask if user wants to bookmark successful commands (only in verbose mode)
            if success and len(user_input) > 10 and user_input not in self.bookmarks:
                if self.config.get("general.suggest_bookmarks", True) and self.config.get("display.verbose_mode", False):
                    if Confirm.ask("Would you like to bookmark this command?"):
                        bookmark_name = Prompt.ask("Enter bookmark name", default=user_input[:20])
                        self.bookmarks[bookmark_name] = user_input
                        self._save_bookmarks()
                        console.print(f"[green]Bookmarked as '{bookmark_name}'[/green]")
                
        except Exception as e:
            console.print(f"[red]Error processing command: {e}[/red]")
    
    def _show_suggestions(self, suggestions: list):
        """Show command suggestions"""
        if not suggestions:
            return
        
        console.print("\n[blue]Suggestions:[/blue]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan")
        table.add_column("Confidence", style="green")
        table.add_column("Type", style="yellow")
        
        for suggestion in suggestions[:self.config.get("general.max_suggestions", 5)]:
            table.add_row(
                suggestion.get("command", ""),
                f"{suggestion.get('confidence', 0):.1%}",
                suggestion.get("type", "unknown")
            )
        
        console.print(table)
    
    def _show_help(self):
        """Show help information"""
        help_text = self.suggestion_engine.get_help_suggestions()
        
        console.print("\n[bold blue]Help - Smart Terminal v2.0[/bold blue]")
        for line in help_text:
            console.print(line)
        
        console.print("\n[bold]File Operations:[/bold]")
        console.print("• 'make a folder called project' - Create directory")
        console.print("• 'copy file.txt to backup' - Copy file")
        console.print("• 'delete old files' - Remove files")
        console.print("• 'list all files' - Show directory contents")
        
        console.print("\n[bold]Git Operations:[/bold]")
        console.print("• 'git init' - Initialize repository")
        console.print("• 'git add all files' - Stage all changes")
        console.print("• 'git commit with message' - Commit changes")
        console.print("• 'git push to main' - Push to remote")
        
        console.print("\n[bold]System Operations:[/bold]")
        console.print("• 'show running processes' - List processes")
        console.print("• 'check disk usage' - Show disk space")
        console.print("• 'show memory usage' - Display RAM usage")
        console.print("• 'system uptime' - Show system uptime")
        
        console.print("\n[bold]Network Operations:[/bold]")
        console.print("• 'ping google.com' - Test connectivity")
        console.print("• 'download file from url' - Download files")
        console.print("• 'show network ports' - List open ports")
        console.print("• 'show ip address' - Display network info")
        
        console.print("\n[bold]Text Operations:[/bold]")
        console.print("• 'edit file.txt' - Open text editor")
        console.print("• 'search for pattern in files' - Find text")
        console.print("• 'count lines in file.txt' - Count lines")
        console.print("• 'show first 10 lines of file' - Head command")
        
        console.print("\n[bold]Special Commands:[/bold]")
        console.print("• help - Show this help message")
        console.print("• stats - Show usage statistics")
        console.print("• config - Show configuration")
        console.print("• history - Show command history")
        console.print("• bookmark <name> <command> - Save command")
        console.print("• clear - Clear screen")
        console.print("• version - Show version info")
        console.print("• simple - Enable simple mode (recommended for new users)")
        console.print("• verbose - Toggle technical details on/off")
        console.print("• debug - Toggle database debug mode (for developers)")
        console.print("• install - Install shell integration")
        console.print("• exit/quit - Exit the application")
    
    def _show_stats(self):
        """Show user statistics"""
        stats = self.learning_engine.get_user_stats()
        
        console.print("\n[bold blue]Usage Statistics[/bold blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Commands", str(stats["total_commands"]))
        table.add_row("Success Rate", f"{stats['success_rate']}%")
        table.add_row("Session Commands", str(len(self.command_history)))
        table.add_row("Bookmarks", str(len(self.bookmarks)))
        
        if stats["top_patterns"]:
            table.add_row("Most Used Pattern", stats["top_patterns"][0]["pattern"])
        
        console.print(table)
        
        # Show platform usage
        if stats["platform_usage"]:
            console.print("\n[bold]Platform Usage:[/bold]")
            for platform in stats["platform_usage"]:
                console.print(f"• {platform['platform']}: {platform['count']} commands")
    
    def _show_config(self):
        """Show current configuration"""
        config = self.config.get_all()
        
        console.print("\n[bold blue]Current Configuration[/bold blue]")
        
        for section, values in config.items():
            console.print(f"\n[bold]{section.title()}:[/bold]")
            for key, value in values.items():
                console.print(f"  {key}: {value}")
    
    def _show_history(self):
        """Show command history for this session"""
        console.print("\n[bold blue]Command History[/bold blue]")
        
        if not self.command_history:
            console.print("No commands executed in this session")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Command", style="green")
        table.add_column("Time", style="yellow")
        
        for i, cmd in enumerate(self.command_history[-10:], 1):  # Show last 10
            timestamp = time.strftime("%H:%M:%S", time.localtime(cmd["timestamp"]))
            table.add_row(str(i), cmd["input"], timestamp)
        
        console.print(table)
    
    def _handle_bookmark(self, user_input: str):
        """Handle bookmark operations"""
        parts = user_input.split(" ", 2)
        
        if len(parts) == 1:
            # Show all bookmarks
            if not self.bookmarks:
                console.print("No bookmarks saved")
                return
            
            console.print("\n[bold blue]Bookmarks[/bold blue]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Command", style="green")
            
            for name, command in self.bookmarks.items():
                table.add_row(name, command)
            
            console.print(table)
            
        elif len(parts) >= 3:
            # Add bookmark
            name = parts[1]
            command = " ".join(parts[2:])
            self.bookmarks[name] = command
            self._save_bookmarks()
            console.print(f"[green]Bookmarked '{command}' as '{name}'[/green]")
        else:
            console.print("Usage: bookmark <name> <command> or just 'bookmark' to list all")
    
    def _handle_alias(self, user_input: str):
        """Handle alias operations (same as bookmarks for now)"""
        self._handle_bookmark(user_input.replace("alias", "bookmark", 1))
    
    def _show_version(self):
        """Show version information"""
        from smart_terminal import __version__
        
        console.print(f"\n[bold blue]Smart Terminal v{__version__}[/bold blue]")
        console.print("AI-powered terminal assistant")
        console.print("Platform: " + self.command_builder.get_platform_info()["os"].title())
        console.print("Python: " + sys.version.split()[0])
    
    def _toggle_verbose_mode(self):
        """Toggle verbose mode on/off"""
        current_verbose = self.config.get("display.verbose_mode", False)
        new_verbose = not current_verbose
        self.config.set("display.verbose_mode", new_verbose)
        
        if new_verbose:
            console.print("[green]✅ Verbose mode enabled - showing technical details[/green]")
        else:
            console.print("[green]✅ Verbose mode disabled - showing simple messages[/green]")
    
    def _set_simple_mode(self):
        """Enable simple mode for non-technical users"""
        self.config.set("display.verbose_mode", False)
        self.config.set("display.simple_messages", True)
        self.config.set("general.show_suggestions", False)
        console.print("[green]✅ Simple mode enabled - perfect for everyday use![/green]")
    
    def _toggle_debug_mode(self):
        """Toggle database debug mode for developers"""
        current_debug = self.config.get("ai.debug_database", False)
        new_debug = not current_debug
        self.config.set("ai.debug_database", new_debug)
        
        if new_debug:
            console.print("[yellow]🔧 Database debug mode enabled - showing database operations[/yellow]")
            # Reinitialize learning engine with debug mode
            self.learning_engine = LearningEngine(debug_mode=True)
            self.suggestion_engine = SuggestionEngine(self.learning_engine)
        else:
            console.print("[green]✅ Database debug mode disabled - clean interface[/green]")
            # Reinitialize learning engine without debug mode
            self.learning_engine = LearningEngine(debug_mode=False)
            self.suggestion_engine = SuggestionEngine(self.learning_engine)
    
    def _install_integration(self):
        """Install shell integration"""
        console.print("\n[bold blue]Installing Shell Integration[/bold blue]")
        
        # Get current directory
        current_dir = str(Path.cwd())
        
        if self.shell_integration.install_shell_integration(current_dir):
            console.print("[green]✅ Shell integration installed successfully![/green]")
            console.print("[yellow]Please restart your terminal for changes to take effect.[/yellow]")
        else:
            console.print("[red]❌ Failed to install shell integration[/red]")
            console.print(self.shell_integration.get_installation_instructions())

@click.command()
@click.argument('command', nargs=-1)
@click.option('--platform', '-p', help='Target platform (windows, macos, linux)')
@click.option('--dry-run', is_flag=True, help='Show what would be executed without running')
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--config-file', help='Use custom config file')
@click.option('--no-learning', is_flag=True, help='Disable AI learning for this session')
@click.option('--simple', is_flag=True, help='Start in simple mode (recommended for new users)')
def main(command, platform, dry_run, version, config_file, no_learning, simple):
    """Smart Terminal - AI-powered terminal assistant with enhanced features"""
    
    if version:
        from smart_terminal import __version__
        console.print(f"Smart Terminal v{__version__}")
        return
    
    # Initialize Smart Terminal
    smart_terminal = SmartTerminal()
    
    # Apply command line options
    if no_learning:
        smart_terminal.config.set("ai.enable_learning", False)
    
    if simple:
        smart_terminal.config.set("display.verbose_mode", False)
        smart_terminal.config.set("display.simple_messages", True)
        smart_terminal.config.set("general.show_suggestions", False)
        console.print("[green]✅ Simple mode enabled - perfect for everyday use![/green]")
    
    if not command:
        # Interactive mode
        smart_terminal.run_interactive()
    else:
        # Direct command mode
        user_input = ' '.join(command)
        smart_terminal.run_direct(user_input)

if __name__ == "__main__":
    main()