"""
tests/test_agent.py - Automated tests for StudyBuddyAgent loop and tool dispatcher.
"""
import pytest
from agents.agent import StudyBuddyAgent
from agents.prompts import SYSTEM_PROMPT

def test_agent_initialization():
    agent = StudyBuddyAgent()
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0]["role"] == "system"
    assert "search_notes" in agent.tool_registry

def test_execute_tool_safety_unknown_tool():
    agent = StudyBuddyAgent()
    result = agent.execute_tool("nonexistent_tool", {})
    assert result["status"] == "error"
    assert "does not exist" in result["message"]

def test_execute_tool_invalid_argument_type():
    agent = StudyBuddyAgent()
    # search_notes expects string query; invalid keyword arg should return error
    result = agent.execute_tool("search_notes", {"invalid_param": 123})
    assert result["status"] == "error"
    assert "Invalid arguments" in result["message"]

def test_reset_conversation():
    agent = StudyBuddyAgent()
    agent.conversation_history.append({"role": "user", "content": "Hello"})
    agent.conversation_history.append({"role": "assistant", "content": "Hi there!"})
    assert len(agent.conversation_history) == 3

    agent.reset_conversation()
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0]["role"] == "system"
