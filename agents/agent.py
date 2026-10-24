"""
agents/agent.py - Core ReAct Agent loop for StudyBuddy AI.
Manages LLM interaction, tool calling, validation, and multi-step execution.
"""
import json
import logging
from typing import Dict, Any, List, Callable, Generator
import ollama
from config import DEFAULT_MODEL, MAX_AGENT_ROUNDS, LOGS_DIR
from agents.prompts import SYSTEM_PROMPT, TOOLS_SCHEMA
from tools.notes_tools import search_notes
from tools.quiz_tools import generate_quiz, evaluate_answers
from tools.progress_tools import get_learning_progress
from tools.study_plan_tools import create_study_plan

# Configure file and stream logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "agent.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StudyBuddyAgent")

class StudyBuddyAgent:
    """Core autonomous agent coordinating local LLM calls and tool executions."""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.tool_registry: Dict[str, Callable] = {
            "search_notes": search_notes,
            "generate_quiz": generate_quiz,
            "evaluate_answers": evaluate_answers,
            "get_learning_progress": get_learning_progress,
            "create_study_plan": create_study_plan
        }
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def reset_conversation(self) -> None:
        """Reset conversation memory while preserving database records."""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        logger.info("Conversation history reset to initial system prompt.")

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and safely dispatch tool call through explicit registry."""
        if tool_name not in self.tool_registry:
            logger.error(f"Unregistered tool called: '{tool_name}'")
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' does not exist. Available tools: {list(self.tool_registry.keys())}"
            }

        func = self.tool_registry[tool_name]
        try:
            logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")
            result = func(**arguments)
            logger.info(f"Tool '{tool_name}' execution succeeded.")
            return result
        except TypeError as te:
            logger.error(f"Invalid arguments for '{tool_name}': {te}")
            return {
                "status": "error",
                "message": f"Invalid arguments supplied for '{tool_name}': {str(te)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error executing '{tool_name}': {e}")
            return {
                "status": "error",
                "message": f"Execution error in tool '{tool_name}': {str(e)}"
            }

    def chat_step(self, user_input: str) -> Generator[Dict[str, Any], None, str]:
        """
        Execute user request through the ReAct agent loop.
        Yields status updates and logs for the UI/CLI trace, then returns final answer.
        """
        self.conversation_history.append({"role": "user", "content": user_input})
        rounds = 0

        while rounds < MAX_AGENT_ROUNDS:
            rounds += 1
            yield {"type": "status", "content": f"Thinking (Step {rounds}/{MAX_AGENT_ROUNDS})..."}

            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=self.conversation_history,
                    tools=TOOLS_SCHEMA,
                    options={"temperature": 0.2}
                )
            except Exception as e:
                err_msg = f"Failed to connect to Ollama model '{self.model_name}': {str(e)}"
                logger.error(err_msg)
                yield {"type": "error", "content": err_msg}
                return err_msg

            message = response.get("message", {})
            self.conversation_history.append(message)

            # Check if model requested tool calls
            tool_calls = message.get("tool_calls", [])
            if not tool_calls:
                # No tool calls needed; final answer generated
                final_content = message.get("content", "")
                yield {"type": "final_response", "content": final_content}
                return final_content

            # Process each requested tool call
            for call in tool_calls:
                func_data = call.get("function", {})
                name = func_data.get("name", "")
                args = func_data.get("arguments", {})

                yield {
                    "type": "tool_call",
                    "tool": name,
                    "arguments": args
                }

                result = self.execute_tool(name, args)

                yield {
                    "type": "tool_result",
                    "tool": name,
                    "result": result
                }

                # Append tool result in Ollama's expected format
                self.conversation_history.append({
                    "role": "tool",
                    "name": name,
                    "content": json.dumps(result)
                })

        # Step limit exceeded
        limit_msg = "Reached maximum tool execution limit (8 rounds). Here is what was completed so far."
        yield {"type": "warning", "content": limit_msg}
        return limit_msg
