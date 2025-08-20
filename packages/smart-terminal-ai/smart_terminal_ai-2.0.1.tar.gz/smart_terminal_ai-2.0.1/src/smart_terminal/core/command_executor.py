"""
Command execution and safety validation
"""

import subprocess
import os
import shlex
from typing import Tuple, Optional
from rich.console import Console

console = Console()

class CommandExecutor:
    def __init__(self):
        self.dangerous_patterns = [
            "rm -rf /",
            "rm -rf /*",
            "rm -rf /home",
            "rm -rf /etc",
            "rm -rf /var",
            "rm -rf /usr",
            "Remove-Item C:\\",
            "Remove-Item D:\\",
            "Remove-Item E:\\",
            "format",
            "diskpart",
            "del C:\\",
            "del D:\\",
            "del E:\\"
        ]
        
        self.warning_patterns = [
            "rm -rf",
            "Remove-Item -Recurse",
            "del /s",
            "Remove-Item -Recurse -Force"
        ]

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate if a command is safe to execute"""
        command_lower = command.lower()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.lower() in command_lower:
                return False, f"⚠️  DANGEROUS COMMAND DETECTED: {pattern}"
        
        # Check for warning patterns
        for pattern in self.warning_patterns:
            if pattern.lower() in command_lower:
                return True, f"⚠️  WARNING: This command will permanently delete files"
        
        return True, "✅ Command validated"

    def execute_command(self, command: str, dry_run: bool = False, show_command: bool = True) -> Tuple[bool, str, Optional[int]]:
        """Execute a command and return results"""
        # Validate command first
        is_safe, validation_msg = self.validate_command(command)
        
        if not is_safe:
            return False, validation_msg, None
        
        if dry_run:
            console.print(f"[yellow]DRY RUN: {command}[/yellow]")
            return True, f"Would execute: {command}", None
        
        try:
            # Show the command being executed only if requested
            if show_command:
                console.print(f"[green]Executing: {command}[/green]")
            
            # Execute the command
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:  # Unix-like systems
                result = subprocess.run(
                    shlex.split(command),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            # Check if command was successful
            if result.returncode == 0:
                output = result.stdout.strip() if result.stdout else "Command executed successfully"
                # Only show output details if show_command is True
                if output and show_command:
                    console.print(f"[green]Output:[/green]\n{output}")
                return True, output, result.returncode
            else:
                error = result.stderr.strip() if result.stderr else "Unknown error"
                # Only show error details if show_command is True
                if show_command:
                    console.print(f"[red]Error:[/red]\n{error}")
                return False, error, result.returncode
                
        except subprocess.TimeoutExpired:
            error_msg = "Command timed out after 30 seconds"
            console.print(f"[red]{error_msg}[/red]")
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return False, error_msg, None

    def suggest_safe_alternative(self, dangerous_command: str) -> str:
        """Suggest a safer alternative to a dangerous command"""
        if "rm -rf" in dangerous_command:
            return dangerous_command.replace("rm -rf", "rm -i")
        elif "Remove-Item -Recurse" in dangerous_command:
            return dangerous_command.replace("-Recurse", "-Recurse -Confirm")
        elif "del /s" in dangerous_command:
            return dangerous_command.replace("/s", "/s /p")
        else:
            return "Please review the command before executing" 