"""
Configuration management for Smart Terminal
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".smart_terminal"
        self.config_file = self.config_dir / "config.json"
        self.default_config = self._get_default_config()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create configuration
        self.config = self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "general": {
                "confirm_dangerous_commands": True,
                "show_suggestions": True,
                "max_suggestions": 5,
                "auto_learn": True,
                "theme": "default",
                "suggest_bookmarks": True,
                "auto_update_check": True,
                "command_timeout": 30
            },
            "ai": {
                "enable_learning": True,
                "suggestion_threshold": 0.5,
                "max_history_size": 1000,
                "enable_context_suggestions": True,
                "learning_rate": 0.1,
                "debug_database": False
            },
            "display": {
                "show_platform_info": True,
                "show_execution_time": True,
                "color_output": True,
                "compact_mode": False,
                "show_progress_bars": True,
                "animation_speed": "normal",
                "verbose_mode": False,
                "simple_messages": True
            },
            "safety": {
                "check_dangerous_patterns": True,
                "require_confirmation_for_deletion": True,
                "max_file_size_for_deletion": "1GB",
                "sandbox_mode": False,
                "backup_before_delete": False
            },
            "git": {
                "auto_add_gitignore": True,
                "default_branch": "main",
                "auto_push_after_commit": False,
                "show_git_status": True
            },
            "network": {
                "timeout": 10,
                "retry_count": 3,
                "user_agent": "Smart-Terminal/2.0"
            },
            "bookmarks": {},
            "aliases": {},
            "plugins": {
                "enabled": [],
                "auto_load": True
            },
            "shortcuts": {
                "quick_git_commit": "gc",
                "quick_list": "ll",
                "quick_edit": "e"
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    return self._merge_configs(self.default_config, user_config)
            except (json.JSONDecodeError, IOError):
                # If config file is corrupted, use default
                return self.default_config.copy()
        else:
            # Create default config file
            self._save_config(self.default_config)
            return self.default_config.copy()
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Merge user configuration with defaults"""
        merged = default.copy()
        
        def merge_dict(d1, d2):
            for key, value in d2.items():
                if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
                    merge_dict(d1[key], value)
                else:
                    d1[key] = value
        
        merge_dict(merged, user)
        return merged
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set a configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        self._save_config(self.config)
    
    def reset_to_default(self):
        """Reset configuration to default values"""
        self.config = self.default_config.copy()
        self._save_config(self.config)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self.config.copy()
    
    def export_config(self, file_path: str):
        """Export configuration to a file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to export config: {e}")
    
    def import_config(self, file_path: str):
        """Import configuration from a file"""
        try:
            with open(file_path, 'r') as f:
                imported_config = json.load(f)
                self.config = self._merge_configs(self.default_config, imported_config)
                self._save_config(self.config)
        except (IOError, json.JSONDecodeError) as e:
            raise IOError(f"Failed to import config: {e}")
    
    def add_bookmark(self, name: str, command: str):
        """Add a bookmark"""
        if "bookmarks" not in self.config:
            self.config["bookmarks"] = {}
        self.config["bookmarks"][name] = command
        self._save_config(self.config)
    
    def remove_bookmark(self, name: str):
        """Remove a bookmark"""
        if "bookmarks" in self.config and name in self.config["bookmarks"]:
            del self.config["bookmarks"][name]
            self._save_config(self.config)
    
    def get_bookmarks(self) -> Dict[str, str]:
        """Get all bookmarks"""
        return self.config.get("bookmarks", {})
    
    def add_alias(self, name: str, command: str):
        """Add an alias"""
        if "aliases" not in self.config:
            self.config["aliases"] = {}
        self.config["aliases"][name] = command
        self._save_config(self.config)
    
    def get_aliases(self) -> Dict[str, str]:
        """Get all aliases"""
        return self.config.get("aliases", {})
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin"""
        if "plugins" not in self.config:
            self.config["plugins"] = {"enabled": []}
        if plugin_name not in self.config["plugins"]["enabled"]:
            self.config["plugins"]["enabled"].append(plugin_name)
            self._save_config(self.config)
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin"""
        if "plugins" in self.config and plugin_name in self.config["plugins"]["enabled"]:
            self.config["plugins"]["enabled"].remove(plugin_name)
            self._save_config(self.config)
    
    def get_enabled_plugins(self) -> list:
        """Get list of enabled plugins"""
        return self.config.get("plugins", {}).get("enabled", [])
    
    def update_setting(self, section: str, key: str, value: Any):
        """Update a specific setting"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config(self.config)
    
    def get_theme(self) -> str:
        """Get current theme"""
        return self.config.get("general", {}).get("theme", "default")
    
    def set_theme(self, theme: str):
        """Set theme"""
        self.update_setting("general", "theme", theme)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(feature, False)
    
    def get_safety_level(self) -> str:
        """Get safety level (low, medium, high)"""
        if not self.get("safety.check_dangerous_patterns", True):
            return "low"
        elif self.get("safety.sandbox_mode", False):
            return "high"
        else:
            return "medium"