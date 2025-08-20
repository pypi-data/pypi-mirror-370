"""
Basic tests for Smart Terminal
"""

import pytest
from ..core.command_mapper import CommandMapper, CommandIntent

def test_command_mapper_creation():
    """Test that CommandMapper can be created"""
    mapper = CommandMapper()
    assert mapper is not None

def test_parse_intent_basic():
    """Test basic intent parsing"""
    mapper = CommandMapper()
    intent = mapper.parse_intent("make a folder called test")
    
    assert intent.action == "create"
    assert intent.target == "test"
    assert "recursive" in intent.flags

def test_parse_intent_delete():
    """Test delete intent parsing"""
    mapper = CommandMapper()
    intent = mapper.parse_intent("delete old backup folder")
    
    assert intent.action == "delete"
    assert intent.target == "old"
    assert "recursive" in intent.flags

def test_parse_intent_list():
    """Test list intent parsing"""
    mapper = CommandMapper()
    intent = mapper.parse_intent("show all files")
    
    assert intent.action == "list"
    assert intent.hidden == True

def test_parse_intent_copy():
    """Test copy intent parsing"""
    mapper = CommandMapper()
    intent = mapper.parse_intent("copy file.txt to documents")
    
    assert intent.action == "copy"
    assert intent.target == "file.txt"
    assert intent.destination == "documents" 