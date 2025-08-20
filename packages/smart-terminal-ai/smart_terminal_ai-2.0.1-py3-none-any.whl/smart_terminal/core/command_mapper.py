"""
Core command mapping and processing logic
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CommandIntent:
    action: str
    target: str
    flags: List[str]
    destination: Optional[str] = None
    recursive: bool = False
    hidden: bool = False
    detailed: bool = False

class CommandMapper:
    def __init__(self):
        self.action_patterns = {
            "create": ["make", "create", "new", "add", "build", "mkdir", "touch"],
            "delete": ["delete", "remove", "rm", "del", "trash", "erase"],
            "copy": ["copy", "cp", "duplicate", "clone", "backup"],
            "move": ["move", "mv", "relocate", "transfer", "rename"],
            "list": ["list", "show", "display", "ls", "dir", "view"],
            "read": ["read", "show", "display", "cat", "type", "view", "open"],
            "search": ["search", "find", "locate", "grep", "look"],
            "compress": ["compress", "zip", "archive", "pack", "tar"],
            "extract": ["extract", "unzip", "unpack", "untar", "decompress"],
            "git": ["git", "commit", "push", "pull", "clone", "branch", "checkout", "init"],
            "system": ["system", "process", "memory", "disk", "cpu", "uptime", "service"],
            "network": ["network", "ping", "download", "curl", "wget", "ip", "port"],
            "text": ["edit", "grep", "count", "head", "tail", "nano", "vim"],
            "permission": ["chmod", "chown", "permission", "owner", "access"]
        }
        
        self.target_patterns = {
            "folder": ["folder", "directory", "dir"],
            "file": ["file", "document", "doc"],
            "archive": ["archive", "zip", "tar", "compressed"],
            "project": ["project", "app", "application"],
            "git": ["repository", "repo", "branch", "commit"],
            "system": ["process", "memory", "disk", "cpu", "service"],
            "network": ["url", "website", "server", "host", "ip"],
            "text": ["content", "text", "string", "pattern"]
        }
        
        self.flag_patterns = {
            "recursive": ["recursive", "recursively", "all", "everything", "subfolders", "-r"],
            "hidden": ["hidden", "all files", "including hidden", "-a"],
            "detailed": ["detailed", "long format", "full info", "with details", "-l"],
            "force": ["force", "forced", "without asking", "yes", "-f"]
        }

        # Git-specific patterns
        self.git_patterns = {
            "init": ["initialize", "init", "start", "begin"],
            "status": ["status", "state", "check"],
            "add": ["add", "stage"],
            "commit": ["commit", "save"],
            "push": ["push", "upload", "send"],
            "pull": ["pull", "download", "fetch"],
            "clone": ["clone", "copy", "download"],
            "branch": ["branch", "create branch"],
            "checkout": ["checkout", "switch"]
        }

        # System command patterns
        self.system_patterns = {
            "processes": ["processes", "running", "tasks"],
            "memory": ["memory", "ram", "usage"],
            "disk": ["disk", "storage", "space"],
            "cpu": ["cpu", "processor", "load"],
            "uptime": ["uptime", "running time"],
            "environment": ["environment", "env", "variables"]
        }

        # Network command patterns
        self.network_patterns = {
            "ping": ["ping", "test connection"],
            "download": ["download", "fetch", "get"],
            "ports": ["ports", "connections", "listening"],
            "ip": ["ip", "address", "network info"]
        }

    def parse_intent(self, user_input: str) -> CommandIntent:
        """Parse natural language input into structured command intent"""
        user_input = user_input.lower().strip()
        
        # Extract action
        action = self._extract_action(user_input)
        
        # Extract target
        target = self._extract_target(user_input, action)
        
        # Extract flags
        flags = self._extract_flags(user_input)
        
        # Extract destination (for copy/move operations)
        destination = self._extract_destination(user_input)
        
        # Determine if recursive
        recursive = any(flag in flags for flag in ["recursive", "all", "everything"])
        
        # Determine if hidden files should be shown
        hidden = any(flag in flags for flag in ["hidden", "all files"])
        
        # Determine if detailed output is requested
        detailed = any(flag in flags for flag in ["detailed", "long format", "full info"])
        
        return CommandIntent(
            action=action,
            target=target,
            flags=flags,
            destination=destination,
            recursive=recursive,
            hidden=hidden,
            detailed=detailed
        )

    def _extract_action(self, user_input: str) -> str:
        """Extract the main action from user input"""
        # Check for git commands first
        if any(word in user_input for word in ["git", "commit", "push", "pull", "clone", "branch", "checkout", "init"]):
            return "git"
        
        # Check for system commands
        if any(word in user_input for word in ["system", "process", "memory", "disk", "cpu", "uptime", "service"]):
            return "system"
        
        # Check for network commands
        if any(word in user_input for word in ["ping", "download", "curl", "wget", "ip", "port", "network"]):
            return "network"
        
        # Check for text commands
        if any(word in user_input for word in ["edit", "grep", "count", "head", "tail", "nano", "vim"]):
            return "text"
        
        # Check for permission commands
        if any(word in user_input for word in ["chmod", "chown", "permission", "owner", "access"]):
            return "permission"
        
        # Check for compression commands
        if any(word in user_input for word in ["compress", "zip", "archive", "pack", "tar"]):
            return "compress"
        
        if any(word in user_input for word in ["extract", "unzip", "unpack", "untar", "decompress"]):
            return "extract"
        
        # Check for regular actions
        for action, patterns in self.action_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                return action
        
        return "list"  # Default action

    def _extract_target(self, user_input: str, action: str) -> str:
        """Extract the target object from user input"""
        
        # Special handling for git commands
        if action == "git":
            return self._extract_git_target(user_input)
        
        # Special handling for system commands
        if action == "system":
            return self._extract_system_target(user_input)
        
        # Special handling for network commands
        if action == "network":
            return self._extract_network_target(user_input)
        
        # Special handling for text commands
        if action == "text":
            return self._extract_text_target(user_input)
        
        # Special handling for list commands
        if action == "list":
            # For list commands, check if user wants to list specific items
            if any(word in user_input for word in ["files", "folders", "directories", "contents"]):
                return "."  # Current directory
            elif "in" in user_input:
                # Extract location after "in"
                match = re.search(r"in\s+([a-zA-Z0-9_./-]+)", user_input)
                if match:
                    return match.group(1)
                return "."
            else:
                return "."  # Default to current directory
        
        # Look for patterns like "folder called X", "file named Y", etc.
        patterns = [
            r"(?:folder|directory|dir)\s+(?:called|named|with\s+name)\s+([a-zA-Z0-9_-]+)",
            r"(?:file|document)\s+(?:called|named|with\s+name)\s+([a-zA-Z0-9_.-]+)",
            r"(?:create|make|new)\s+(?:a\s+)?(?:folder|directory|file)\s+(?:called\s+)?([a-zA-Z0-9_.-]+)",
            r"(?:delete|remove|rm)\s+([a-zA-Z0-9_./-]+)",
            r"(?:copy|move)\s+([a-zA-Z0-9_./-]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1)
        
        # Fallback: look for words that might be names
        words = user_input.split()
        for i, word in enumerate(words):
            if word in ["called", "named", "with"] and i + 1 < len(words):
                return words[i + 1]
        
        return "new_item"

    def _extract_git_target(self, user_input: str) -> str:
        """Extract git-specific target"""
        for git_action, patterns in self.git_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                return git_action
        
        # Look for repository URLs or names
        url_match = re.search(r"(https?://[^\s]+|git@[^\s]+)", user_input)
        if url_match:
            return url_match.group(1)
        
        return "status"  # Default git action

    def _extract_system_target(self, user_input: str) -> str:
        """Extract system-specific target"""
        for sys_action, patterns in self.system_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                return sys_action
        
        return "processes"  # Default system action

    def _extract_network_target(self, user_input: str) -> str:
        """Extract network-specific target"""
        for net_action, patterns in self.network_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                return net_action
        
        # Look for URLs or IP addresses
        url_match = re.search(r"(https?://[^\s]+|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", user_input)
        if url_match:
            return url_match.group(1)
        
        return "ip"  # Default network action

    def _extract_text_target(self, user_input: str) -> str:
        """Extract text processing target"""
        if "edit" in user_input:
            # Look for filename after edit
            match = re.search(r"edit\s+([a-zA-Z0-9_./-]+)", user_input)
            if match:
                return match.group(1)
            return "edit"
        elif "grep" in user_input or "search" in user_input:
            # Look for search pattern
            match = re.search(r"(?:grep|search)\s+(?:for\s+)?([a-zA-Z0-9_.-]+)", user_input)
            if match:
                return match.group(1)
            return "grep"
        elif any(word in user_input for word in ["count", "lines"]):
            return "count_lines"
        elif "head" in user_input:
            return "head"
        elif "tail" in user_input:
            return "tail"
        
        return "edit"  # Default text action

    def _extract_flags(self, user_input: str) -> List[str]:
        """Extract flags and modifiers from user input"""
        flags = []
        for flag, patterns in self.flag_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                flags.append(flag)
        return flags

    def _extract_destination(self, user_input: str) -> Optional[str]:
        """Extract destination for copy/move operations"""
        # Look for "to" or "into" patterns
        patterns = [
            r"(?:to|into)\s+([a-zA-Z0-9_./-]+)",
            r"(?:copy|move)\s+[a-zA-Z0-9_./-]+\s+(?:to|into)\s+([a-zA-Z0-9_./-]+)",
            r"(?:from\s+[^\s]+\s+)?(?:to|into)\s+([a-zA-Z0-9_./-]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1)
        
        return None