"""
Tests for enhanced Smart Terminal features
"""

import pytest
from ..core.command_mapper import CommandMapper, CommandIntent
from ..core.command_builder import CommandBuilder
from ..ai.suggestion_engine import SuggestionEngine
from ..ai.learning_engine import LearningEngine
from ..utils.config import Config

def test_enhanced_command_mapping():
    """Test enhanced command mapping with new action types"""
    mapper = CommandMapper()
    
    # Test git commands
    intent = mapper.parse_intent("git init new repository")
    assert intent.action == "git"
    assert intent.target == "init"
    
    # Test system commands
    intent = mapper.parse_intent("show running processes")
    assert intent.action == "system"
    assert intent.target == "processes"
    
    # Test network commands
    intent = mapper.parse_intent("ping google.com")
    assert intent.action == "network"
    assert intent.target == "ping"

def test_enhanced_command_building():
    """Test enhanced command building with new command types"""
    builder = CommandBuilder()
    
    # Test git command building
    intent = CommandIntent(action="git", target="status", flags=[], destination=None)
    command = builder.build_command(intent)
    assert "git status" in command
    
    # Test system command building
    intent = CommandIntent(action="system", target="processes", flags=[], destination=None)
    command = builder.build_command(intent)
    if builder.is_windows:
        assert "Get-Process" in command
    else:
        assert "ps aux" in command

def test_enhanced_suggestions():
    """Test enhanced suggestion engine"""
    learning_engine = LearningEngine()
    suggestion_engine = SuggestionEngine(learning_engine)
    
    # Test git suggestions
    suggestions = suggestion_engine.get_smart_suggestions("git commit")
    assert len(suggestions) > 0
    assert any("git" in suggestion["command"] for suggestion in suggestions)
    
    # Test workflow suggestions
    suggestions = suggestion_engine.get_smart_suggestions("git add")
    workflow_suggestions = [s for s in suggestions if s.get("type") == "workflow"]
    assert len(workflow_suggestions) > 0

def test_config_enhancements():
    """Test enhanced configuration features"""
    config = Config()
    
    # Test bookmark functionality
    config.add_bookmark("test", "ls -la")
    bookmarks = config.get_bookmarks()
    assert "test" in bookmarks
    assert bookmarks["test"] == "ls -la"
    
    # Test alias functionality
    config.add_alias("ll", "ls -la")
    aliases = config.get_aliases()
    assert "ll" in aliases
    
    # Test plugin management
    config.enable_plugin("test_plugin")
    enabled_plugins = config.get_enabled_plugins()
    assert "test_plugin" in enabled_plugins

def test_advanced_parsing():
    """Test advanced parsing capabilities"""
    mapper = CommandMapper()
    
    # Test complex git commands
    intent = mapper.parse_intent("commit changes with message 'fix bug'")
    assert intent.action == "git"
    
    # Test system monitoring commands
    intent = mapper.parse_intent("check memory usage")
    assert intent.action == "system"
    assert intent.target == "memory"
    
    # Test network operations
    intent = mapper.parse_intent("download file from https://example.com")
    assert intent.action == "network"
    assert intent.target == "download"

def test_contextual_suggestions():
    """Test contextual suggestion system"""
    learning_engine = LearningEngine()
    suggestion_engine = SuggestionEngine(learning_engine)
    
    # Test git context suggestions
    suggestions = suggestion_engine._get_context_suggestions("git")
    assert len(suggestions) > 0
    assert all("git" in suggestion["command"] for suggestion in suggestions)
    
    # Test system context suggestions
    suggestions = suggestion_engine._get_context_suggestions("system")
    assert len(suggestions) > 0

def test_workflow_suggestions():
    """Test workflow-based suggestions"""
    learning_engine = LearningEngine()
    suggestion_engine = SuggestionEngine(learning_engine)
    
    # Test git workflow
    suggestions = suggestion_engine._get_workflow_suggestions("git init")
    workflow_suggestions = [s for s in suggestions if s.get("type") == "workflow"]
    assert len(workflow_suggestions) > 0
    
    # Check for logical next steps
    next_steps = [s.get("next_step") for s in workflow_suggestions]
    assert "stage_files" in next_steps or "first_commit" in next_steps

def test_command_explanations():
    """Test command explanation feature"""
    learning_engine = LearningEngine()
    suggestion_engine = SuggestionEngine(learning_engine)
    
    explanation = suggestion_engine.get_command_explanation("ls")
    assert "List directory contents" in explanation
    
    explanation = suggestion_engine.get_command_explanation("git init")
    assert "Initialize" in explanation

def test_alternative_suggestions():
    """Test alternative command suggestions"""
    learning_engine = LearningEngine()
    suggestion_engine = SuggestionEngine(learning_engine)
    
    alternatives = suggestion_engine.suggest_alternatives("dir")
    assert "ls" in alternatives
    
    alternatives = suggestion_engine.suggest_alternatives("type")
    assert "cat" in alternatives

def test_safety_enhancements():
    """Test enhanced safety features"""
    config = Config()
    
    # Test safety level detection
    safety_level = config.get_safety_level()
    assert safety_level in ["low", "medium", "high"]
    
    # Test feature enablement checks
    assert isinstance(config.is_feature_enabled("ai.enable_learning"), bool)

if __name__ == "__main__":
    pytest.main([__file__])