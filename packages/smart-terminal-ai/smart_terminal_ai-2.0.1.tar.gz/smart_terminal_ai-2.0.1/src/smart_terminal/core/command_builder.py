"""
Command generation for different platforms
"""

import os
import platform
from typing import Dict, List, Optional
from .command_mapper import CommandIntent

class CommandBuilder:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == "windows"
        self.is_macos = self.os_type == "darwin"
        self.is_linux = self.os_type == "linux"
        
        # Platform-specific command templates
        self.command_templates = self._get_command_templates()
        
    def _get_command_templates(self) -> Dict[str, Dict[str, str]]:
        """Get command templates for different platforms"""
        if self.is_windows:
            return {
                "create": {
                    "folder": "New-Item -ItemType Directory -Name '{target}'",
                    "file": "New-Item -ItemType File -Name '{target}'",
                    "recursive": "New-Item -ItemType Directory -Name '{target}' -Force"
                },
                "delete": {
                    "file": "Remove-Item -Force '{target}'",
                    "folder": "Remove-Item -Recurse -Force '{target}'"
                },
                "copy": {
                    "file": "Copy-Item '{target}' '{destination}'",
                    "folder": "Copy-Item -Recurse '{target}' '{destination}'"
                },
                "move": {
                    "file": "Move-Item '{target}' '{destination}'",
                    "folder": "Move-Item '{target}' '{destination}'"
                },
                "list": {
                    "basic": "Get-ChildItem '{target}'",
                    "hidden": "Get-ChildItem '{target}' -Force",
                    "detailed": "Get-ChildItem '{target}' | Format-Table Name, Length, LastWriteTime"
                },
                "read": {
                    "file": "Get-Content '{target}'"
                },
                "search": {
                    "files": "Get-ChildItem -Recurse -Filter '{target}'",
                    "content": "Select-String -Pattern '{target}' -Path *"
                },
                "git": {
                    "init": "git init",
                    "status": "git status",
                    "add": "git add '{target}'",
                    "commit": "git commit -m '{target}'",
                    "push": "git push origin '{target}'",
                    "pull": "git pull origin '{target}'",
                    "clone": "git clone '{target}'",
                    "branch": "git branch '{target}'",
                    "checkout": "git checkout '{target}'"
                },
                "system": {
                    "processes": "Get-Process",
                    "services": "Get-Service",
                    "disk_usage": "Get-WmiObject -Class Win32_LogicalDisk",
                    "memory": "Get-WmiObject -Class Win32_ComputerSystem",
                    "uptime": "Get-Uptime",
                    "environment": "Get-ChildItem Env:"
                },
                "network": {
                    "ping": "ping '{target}'",
                    "download": "Invoke-WebRequest -Uri '{target}' -OutFile '{destination}'",
                    "ports": "netstat -an",
                    "ip": "ipconfig"
                },
                "text": {
                    "edit": "notepad '{target}'",
                    "grep": "Select-String -Pattern '{target}' -Path '{destination}'",
                    "count_lines": "Get-Content '{target}' | Measure-Object -Line"
                },
                "compress": {
                    "zip": "Compress-Archive -Path '{target}' -DestinationPath '{destination}'",
                    "unzip": "Expand-Archive -Path '{target}' -DestinationPath '{destination}'"
                }
            }
        else:  # macOS and Linux
            return {
                "create": {
                    "folder": "mkdir '{target}'",
                    "file": "touch '{target}'",
                    "recursive": "mkdir -p '{target}'"
                },
                "delete": {
                    "file": "rm '{target}'",
                    "folder": "rm -rf '{target}'"
                },
                "copy": {
                    "file": "cp '{target}' '{destination}'",
                    "folder": "cp -r '{target}' '{destination}'"
                },
                "move": {
                    "file": "mv '{target}' '{destination}'",
                    "folder": "mv '{target}' '{destination}'"
                },
                "list": {
                    "basic": "ls '{target}'",
                    "hidden": "ls -a '{target}'",
                    "detailed": "ls -la '{target}'"
                },
                "read": {
                    "file": "cat '{target}'"
                },
                "search": {
                    "files": "find . -name '{target}'",
                    "content": "grep -r '{target}' ."
                },
                "git": {
                    "init": "git init",
                    "status": "git status",
                    "add": "git add '{target}'",
                    "commit": "git commit -m '{target}'",
                    "push": "git push origin '{target}'",
                    "pull": "git pull origin '{target}'",
                    "clone": "git clone '{target}'",
                    "branch": "git branch '{target}'",
                    "checkout": "git checkout '{target}'"
                },
                "system": {
                    "processes": "ps aux",
                    "disk_usage": "df -h",
                    "memory": "free -h",
                    "uptime": "uptime",
                    "environment": "env",
                    "cpu_info": "lscpu" if self.is_linux else "sysctl -n machdep.cpu.brand_string"
                },
                "network": {
                    "ping": "ping -c 4 '{target}'",
                    "download": "curl -o '{destination}' '{target}'",
                    "ports": "netstat -tuln",
                    "ip": "ifconfig" if self.is_macos else "ip addr show"
                },
                "text": {
                    "edit": "nano '{target}'" if self.is_linux else "open -e '{target}'",
                    "grep": "grep '{target}' '{destination}'",
                    "count_lines": "wc -l '{target}'",
                    "head": "head -n 10 '{target}'",
                    "tail": "tail -n 10 '{target}'"
                },
                "compress": {
                    "tar": "tar -czf '{destination}' '{target}'",
                    "untar": "tar -xzf '{target}'",
                    "zip": "zip -r '{destination}' '{target}'",
                    "unzip": "unzip '{target}'"
                },
                "permission": {
                    "chmod": "chmod '{target}' '{destination}'",
                    "chown": "chown '{target}' '{destination}'"
                }
            }

    def build_command(self, intent: CommandIntent) -> str:
        """Build the appropriate command based on intent and platform"""
        action = intent.action
        target = intent.target
        destination = intent.destination
        
        # Handle all command types
        if action == "create":
            return self._build_create_command(intent)
        elif action == "delete":
            return self._build_delete_command(intent)
        elif action == "copy":
            return self._build_copy_command(intent)
        elif action == "move":
            return self._build_move_command(intent)
        elif action == "list":
            return self._build_list_command(intent)
        elif action == "read":
            return self._build_read_command(intent)
        elif action == "search":
            return self._build_search_command(intent)
        elif action == "git":
            return self._build_git_command(intent)
        elif action == "system":
            return self._build_system_command(intent)
        elif action == "network":
            return self._build_network_command(intent)
        elif action == "text":
            return self._build_text_command(intent)
        elif action == "compress":
            return self._build_compress_command(intent)
        elif action == "permission":
            return self._build_permission_command(intent)
        else:
            return self._build_list_command(intent)

    def _build_create_command(self, intent: CommandIntent) -> str:
        """Build create command based on target type and flags"""
        if "folder" in intent.target or intent.recursive:
            template = self.command_templates["create"]["recursive" if intent.recursive else "folder"]
        else:
            template = self.command_templates["create"]["file"]
        
        return template.format(target=intent.target)

    def _build_delete_command(self, intent: CommandIntent) -> str:
        """Build delete command"""
        if os.path.isdir(intent.target) or intent.recursive:
            template = self.command_templates["delete"]["folder"]
        else:
            template = self.command_templates["delete"]["file"]
        
        return template.format(target=intent.target)

    def _build_copy_command(self, intent: CommandIntent) -> str:
        """Build copy command"""
        if not intent.destination:
            raise ValueError("Destination required for copy operation")
        
        if os.path.isdir(intent.target) or intent.recursive:
            template = self.command_templates["copy"]["folder"]
        else:
            template = self.command_templates["copy"]["file"]
        
        return template.format(target=intent.target, destination=intent.destination)

    def _build_move_command(self, intent: CommandIntent) -> str:
        """Build move command"""
        if not intent.destination:
            raise ValueError("Destination required for move operation")
        
        if os.path.isdir(intent.target):
            template = self.command_templates["move"]["folder"]
        else:
            template = self.command_templates["move"]["file"]
        
        return template.format(target=intent.target, destination=intent.destination)

    def _build_list_command(self, intent: CommandIntent) -> str:
        """Build list command"""
        if intent.hidden and intent.detailed:
            template = self.command_templates["list"]["detailed"]
        elif intent.hidden:
            template = self.command_templates["list"]["hidden"]
        else:
            template = self.command_templates["list"]["basic"]
        
        return template.format(target=intent.target or ".")

    def _build_read_command(self, intent: CommandIntent) -> str:
        """Build read command"""
        template = self.command_templates["read"]["file"]
        return template.format(target=intent.target)

    def _build_search_command(self, intent: CommandIntent) -> str:
        """Build search command"""
        if intent.destination:  # Search content in files
            template = self.command_templates["search"]["content"]
            return template.format(target=intent.target, destination=intent.destination)
        else:  # Search for files
            template = self.command_templates["search"]["files"]
            return template.format(target=intent.target)

    def _build_git_command(self, intent: CommandIntent) -> str:
        """Build git command"""
        git_action = intent.target.lower()
        
        if git_action in self.command_templates["git"]:
            template = self.command_templates["git"][git_action]
            if "{target}" in template:
                return template.format(target=intent.destination or "main")
            return template
        else:
            return f"git {intent.target}"

    def _build_system_command(self, intent: CommandIntent) -> str:
        """Build system command"""
        system_action = intent.target.lower().replace(" ", "_")
        
        if system_action in self.command_templates["system"]:
            return self.command_templates["system"][system_action]
        else:
            return self.command_templates["system"]["processes"]

    def _build_network_command(self, intent: CommandIntent) -> str:
        """Build network command"""
        network_action = intent.target.lower()
        
        if network_action == "ping" and intent.destination:
            return self.command_templates["network"]["ping"].format(target=intent.destination)
        elif network_action == "download" and intent.destination:
            return self.command_templates["network"]["download"].format(
                target=intent.destination, 
                destination=intent.target or "downloaded_file"
            )
        elif network_action in self.command_templates["network"]:
            return self.command_templates["network"][network_action]
        else:
            return self.command_templates["network"]["ip"]

    def _build_text_command(self, intent: CommandIntent) -> str:
        """Build text processing command"""
        text_action = intent.target.lower()
        
        if text_action in self.command_templates["text"]:
            template = self.command_templates["text"][text_action]
            if "{destination}" in template:
                return template.format(target=intent.destination, destination=intent.target)
            return template.format(target=intent.destination or intent.target)
        else:
            return self.command_templates["text"]["edit"].format(target=intent.target)

    def _build_compress_command(self, intent: CommandIntent) -> str:
        """Build compression command"""
        if not intent.destination:
            intent.destination = f"{intent.target}.tar.gz" if not self.is_windows else f"{intent.target}.zip"
        
        if "unzip" in intent.target or "extract" in intent.target:
            if self.is_windows:
                return self.command_templates["compress"]["unzip"].format(
                    target=intent.destination, destination=intent.target or "."
                )
            else:
                if intent.destination.endswith('.tar.gz') or intent.destination.endswith('.tgz'):
                    return self.command_templates["compress"]["untar"].format(target=intent.destination)
                else:
                    return self.command_templates["compress"]["unzip"].format(target=intent.destination)
        else:
            if self.is_windows:
                return self.command_templates["compress"]["zip"].format(
                    target=intent.target, destination=intent.destination
                )
            else:
                if intent.destination.endswith('.tar.gz') or intent.destination.endswith('.tgz'):
                    return self.command_templates["compress"]["tar"].format(
                        target=intent.target, destination=intent.destination
                    )
                else:
                    return self.command_templates["compress"]["zip"].format(
                        target=intent.target, destination=intent.destination
                    )

    def _build_permission_command(self, intent: CommandIntent) -> str:
        """Build permission command (Unix only)"""
        if self.is_windows:
            return "echo 'Permission commands not available on Windows'"
        
        if "chmod" in intent.target:
            return self.command_templates["permission"]["chmod"].format(
                target=intent.destination or "755", destination=intent.target
            )
        elif "chown" in intent.target:
            return self.command_templates["permission"]["chown"].format(
                target=intent.destination or "$USER", destination=intent.target
            )
        else:
            return f"ls -la '{intent.target}'"

    def get_platform_info(self) -> Dict[str, str]:
        """Get information about the current platform"""
        return {
            "os": self.os_type,
            "is_windows": str(self.is_windows),
            "is_macos": str(self.is_macos),
            "is_linux": str(self.is_linux),
            "shell": os.environ.get("SHELL", "unknown")
        }