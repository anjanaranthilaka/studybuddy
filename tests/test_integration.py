"""
tests/test_integration.py - Live integration tests with running local Ollama instance.
"""
import pytest
import ollama
from agents.agent import StudyBuddyAgent
from config import DEFAULT_MODEL

def is_ollama_online():
    try:
        ollama.list()
        return True
    except Exception:
        return False

@pytest.mark.skipif(not is_ollama_online(), reason="Local Ollama server is not running")
def test_live_agent_search_tool_execution():
    agent = StudyBuddyAgent(model_name=DEFAULT_MODEL)
    query = "Search my notes for loops and tell me what the continue statement does."
    
    events = list(agent.chat_step(query))
    
    # Verify tool call event was yielded
    tool_calls = [e for e in events if e.get("type") == "tool_call"]
    assert len(tool_calls) >= 1
    assert tool_calls[0]["tool"] == "search_notes"
    
    # Verify tool result event was yielded
    tool_results = [e for e in events if e.get("type") == "tool_result"]
    assert len(tool_results) >= 1
    assert tool_results[0]["result"]["status"] == "success"
    
    # Verify final assistant response
    final_res = [e for e in events if e.get("type") == "final_response"]
    assert len(final_res) == 1
    assert len(final_res[0]["content"]) > 20
