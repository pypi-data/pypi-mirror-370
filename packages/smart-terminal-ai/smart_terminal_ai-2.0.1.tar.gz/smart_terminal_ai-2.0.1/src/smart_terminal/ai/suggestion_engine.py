"""
AI-powered suggestion and recommendation engine
"""

import re
from typing import List, Dict, Optional
from .learning_engine import LearningEngine

class SuggestionEngine:
    def __init__(self, learning_engine: LearningEngine):
        self.learning_engine = learning_engine
        
        # Common command patterns and their variations
        self.command_variations = {
            "list_files": [
                "show files", "display files", "list contents", "what's in this folder",
                "ls", "dir", "list directory", "show directory contents"
            ],
            "create_folder": [
                "make folder", "create directory", "new folder", "add folder",
                "mkdir", "create folder", "make directory", "new directory"
            ],
            "delete_item": [
                "delete", "remove", "trash", "delete file", "remove folder",
                "rm", "del", "remove item", "delete item"
            ],
            "copy_item": [
                "copy", "duplicate", "clone", "copy file", "copy folder",
                "cp", "duplicate item", "clone item"
            ],
            "move_item": [
                "move", "relocate", "transfer", "move file", "move folder",
                "mv", "relocate item", "transfer item"
            ],
            "git_operations": [
                "git init", "git add", "git commit", "git push", "git pull",
                "git clone", "git branch", "git checkout", "git status"
            ],
            "system_info": [
                "show processes", "memory usage", "disk space", "system uptime",
                "cpu info", "running services", "environment variables"
            ],
            "network_operations": [
                "ping", "download", "curl", "wget", "network info", "ip address",
                "open ports", "test connection"
            ],
            "text_processing": [
                "edit file", "search text", "count lines", "show first lines",
                "show last lines", "find pattern", "grep"
            ]
        }
        
        # Context-aware suggestions
        self.context_suggestions = {
            "git": [
                "git init - Initialize a new git repository",
                "git add . - Stage all files for commit",
                "git commit -m 'message' - Commit staged changes",
                "git status - Check repository status",
                "git log - View commit history",
                "git branch - List or create branches",
                "git push origin main - Push to remote repository",
                "git pull origin main - Pull latest changes"
            ],
            "python": [
                "python -m venv venv - Create virtual environment",
                "pip install package - Install Python package",
                "python script.py - Run Python script",
                "pip freeze > requirements.txt - Save dependencies",
                "python -m pip list - List installed packages",
                "python -c 'code' - Execute Python code"
            ],
            "node": [
                "npm init - Initialize Node.js project",
                "npm install package - Install package",
                "npm run script - Run npm script",
                "node script.js - Run Node.js script",
                "npm start - Start the application",
                "npm test - Run tests"
            ],
            "docker": [
                "docker build -t name . - Build Docker image",
                "docker run -it image - Run container interactively",
                "docker ps - List running containers",
                "docker images - List Docker images",
                "docker-compose up - Start services",
                "docker stop container - Stop container"
            ],
            "system": [
                "ps aux - Show running processes",
                "df -h - Show disk usage",
                "free -h - Show memory usage",
                "top - Show system activity",
                "uptime - Show system uptime",
                "whoami - Show current user"
            ],
            "network": [
                "ping google.com - Test internet connection",
                "curl -I url - Check website headers",
                "netstat -tuln - Show network connections",
                "ifconfig - Show network interfaces",
                "wget url - Download file",
                "ssh user@host - Connect via SSH"
            ]
        }

        # Smart completion suggestions
        self.smart_completions = {
            "git": {
                "commit": ["git commit -m 'Initial commit'", "git commit -m 'Fix bug'", "git commit -m 'Add feature'"],
                "branch": ["git branch feature/", "git branch bugfix/", "git branch release/"],
                "push": ["git push origin main", "git push origin develop", "git push --set-upstream origin"]
            },
            "file": {
                "create": ["touch README.md", "touch .gitignore", "touch requirements.txt"],
                "edit": ["nano file.txt", "vim file.txt", "code file.txt"]
            },
            "system": {
                "install": ["sudo apt install", "brew install", "pip install"],
                "update": ["sudo apt update", "brew update", "pip install --upgrade"]
            }
        }

    def get_smart_suggestions(self, user_input: str, context: str = None) -> List[Dict]:
        """Get intelligent suggestions based on user input and context"""
        suggestions = []
        
        # Get learning-based suggestions
        learning_suggestions = self.learning_engine.get_suggestions(user_input, limit=3)
        suggestions.extend(learning_suggestions)
        
        # Get pattern-based suggestions
        pattern_suggestions = self._get_pattern_suggestions(user_input)
        suggestions.extend(pattern_suggestions)
        
        # Get context-based suggestions
        if context:
            context_suggestions = self._get_context_suggestions(context)
            suggestions.extend(context_suggestions)
        
        # Get smart completions
        completion_suggestions = self._get_completion_suggestions(user_input)
        suggestions.extend(completion_suggestions)
        
        # Get workflow suggestions
        workflow_suggestions = self._get_workflow_suggestions(user_input)
        suggestions.extend(workflow_suggestions)
        
        # Remove duplicates and sort by confidence
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        return sorted(unique_suggestions, key=lambda x: x.get('confidence', 0), reverse=True)

    def _get_pattern_suggestions(self, user_input: str) -> List[Dict]:
        """Get suggestions based on command patterns"""
        suggestions = []
        user_input_lower = user_input.lower()
        
        for intent, variations in self.command_variations.items():
            for variation in variations:
                if any(word in user_input_lower for word in variation.split()):
                    suggestions.append({
                        "command": variation,
                        "confidence": 0.8,
                        "type": "pattern_match",
                        "intent": intent
                    })
                    break  # Only add one suggestion per intent
        
        return suggestions

    def _get_context_suggestions(self, context: str) -> List[Dict]:
        """Get context-aware suggestions"""
        suggestions = []
        context_lower = context.lower()
        
        for tool, commands in self.context_suggestions.items():
            if tool in context_lower:
                for command in commands[:3]:  # Limit to 3 suggestions per context
                    suggestions.append({
                        "command": command,
                        "confidence": 0.7,
                        "type": "context_aware",
                        "context": tool
                    })
        
        return suggestions

    def _get_completion_suggestions(self, user_input: str) -> List[Dict]:
        """Get smart completion suggestions"""
        suggestions = []
        user_input_lower = user_input.lower()
        
        for category, subcategories in self.smart_completions.items():
            if category in user_input_lower:
                for subcat, completions in subcategories.items():
                    if subcat in user_input_lower:
                        for completion in completions:
                            suggestions.append({
                                "command": completion,
                                "confidence": 0.9,
                                "type": "smart_completion",
                                "category": category
                            })
        
        return suggestions

    def _get_workflow_suggestions(self, user_input: str) -> List[Dict]:
        """Get workflow-based suggestions"""
        suggestions = []
        user_input_lower = user_input.lower()
        
        # Git workflow suggestions
        if "git" in user_input_lower:
            if "init" in user_input_lower:
                suggestions.extend([
                    {"command": "git add .", "confidence": 0.8, "type": "workflow", "next_step": "stage_files"},
                    {"command": "git commit -m 'Initial commit'", "confidence": 0.8, "type": "workflow", "next_step": "first_commit"}
                ])
            elif "add" in user_input_lower:
                suggestions.append({
                    "command": "git commit -m 'Your commit message'",
                    "confidence": 0.9,
                    "type": "workflow",
                    "next_step": "commit_changes"
                })
            elif "commit" in user_input_lower:
                suggestions.append({
                    "command": "git push origin main",
                    "confidence": 0.8,
                    "type": "workflow",
                    "next_step": "push_changes"
                })
        
        # File operation workflows
        if "create" in user_input_lower or "make" in user_input_lower:
            if "folder" in user_input_lower:
                suggestions.append({
                    "command": "cd into the new folder",
                    "confidence": 0.6,
                    "type": "workflow",
                    "next_step": "navigate_to_folder"
                })
        
        # System administration workflows
        if "install" in user_input_lower:
            suggestions.extend([
                {"command": "which package_name", "confidence": 0.6, "type": "workflow", "next_step": "verify_installation"},
                {"command": "package_name --version", "confidence": 0.6, "type": "workflow", "next_step": "check_version"}
            ])
        
        return suggestions

    def _deduplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Remove duplicate suggestions and merge confidence scores"""
        seen = {}
        
        for suggestion in suggestions:
            command = suggestion['command']
            if command in seen:
                # Merge confidence scores (take the higher one)
                seen[command]['confidence'] = max(seen[command]['confidence'], suggestion['confidence'])
                # Update type if current one is more specific
                if suggestion.get('type') in ['smart_completion', 'workflow']:
                    seen[command]['type'] = suggestion.get('type', 'unknown')
            else:
                seen[command] = suggestion.copy()
        
        return list(seen.values())

    def get_help_suggestions(self, topic: str = None) -> List[str]:
        """Get help suggestions for a specific topic"""
        if topic is None:
            return [
                "Try these common commands:",
                "• 'make a folder called project' - Create directory",
                "• 'list files in current directory' - Show contents",
                "• 'delete old backup folder' - Remove directory",
                "• 'copy file.txt to documents' - Copy file",
                "• 'move project to new_location' - Move item",
                "• 'git init' - Initialize git repository",
                "• 'show running processes' - List system processes",
                "• 'ping google.com' - Test network connection"
            ]
        
        topic_lower = topic.lower()
        
        if "folder" in topic_lower or "directory" in topic_lower:
            return [
                "Folder operations:",
                "• 'make folder called name' - Create directory",
                "• 'delete folder name' - Remove directory",
                "• 'list folders' - Show directories",
                "• 'move folder to destination' - Relocate directory",
                "• 'copy folder to backup' - Backup directory"
            ]
        elif "file" in topic_lower:
            return [
                "File operations:",
                "• 'create file called name.txt' - Create file",
                "• 'delete file.txt' - Remove file",
                "• 'copy file.txt to folder' - Copy file",
                "• 'read file.txt' - Display file contents",
                "• 'edit file.txt' - Open in editor"
            ]
        elif "git" in topic_lower:
            return self.context_suggestions.get("git", [])
        elif "python" in topic_lower:
            return self.context_suggestions.get("python", [])
        elif "system" in topic_lower:
            return self.context_suggestions.get("system", [])
        elif "network" in topic_lower:
            return self.context_suggestions.get("network", [])
        else:
            return ["Type 'help' for general help or specify a topic like 'help files'"]

    def get_command_explanation(self, command: str) -> str:
        """Get explanation for a command"""
        explanations = {
            "ls": "List directory contents",
            "mkdir": "Create directories",
            "rm": "Remove files and directories",
            "cp": "Copy files and directories",
            "mv": "Move/rename files and directories",
            "cat": "Display file contents",
            "grep": "Search text patterns in files",
            "find": "Search for files and directories",
            "git init": "Initialize a new Git repository",
            "git add": "Add files to staging area",
            "git commit": "Create a commit with staged changes",
            "git push": "Upload commits to remote repository",
            "git pull": "Download and merge changes from remote",
            "ps": "Show running processes",
            "df": "Show disk space usage",
            "free": "Show memory usage",
            "ping": "Test network connectivity"
        }
        
        return explanations.get(command.split()[0], "Command not found in explanations")

    def suggest_alternatives(self, failed_command: str) -> List[str]:
        """Suggest alternatives for failed commands"""
        alternatives = {
            "dir": ["ls", "ls -la", "find . -type f"],
            "type": ["cat", "less", "head", "tail"],
            "del": ["rm", "rm -rf"],
            "copy": ["cp", "cp -r"],
            "ren": ["mv"],
            "md": ["mkdir", "mkdir -p"]
        }
        
        command_base = failed_command.split()[0]
        return alternatives.get(command_base, [])

    def get_contextual_help(self, current_directory: str, recent_commands: List[str]) -> List[str]:
        """Get contextual help based on current state"""
        help_suggestions = []
        
        # Check if in git repository
        if ".git" in current_directory or any("git" in cmd for cmd in recent_commands[-5:]):
            help_suggestions.extend([
                "Git repository detected:",
                "• 'git status' - Check repository status",
                "• 'git add .' - Stage all changes",
                "• 'git commit -m \"message\"' - Commit changes"
            ])
        
        # Check for common project files
        if "package.json" in current_directory:
            help_suggestions.extend([
                "Node.js project detected:",
                "• 'npm install' - Install dependencies",
                "• 'npm start' - Start the application",
                "• 'npm test' - Run tests"
            ])
        
        if "requirements.txt" in current_directory or "setup.py" in current_directory:
            help_suggestions.extend([
                "Python project detected:",
                "• 'pip install -r requirements.txt' - Install dependencies",
                "• 'python -m venv venv' - Create virtual environment",
                "• 'python script.py' - Run Python script"
            ])
        
        return help_suggestions