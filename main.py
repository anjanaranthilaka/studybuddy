"""
main.py - Interactive Command-Line Interface for StudyBuddy AI.
Allows testing of tool execution, multi-turn follow-ups, and live traces.
"""
import sys
import json
from agents.agent import StudyBuddyAgent
from database.db import init_db

def print_separator():
    print("-" * 65)

def main():
    # Ensure database schema exists
    init_db()

    print("=" * 65)
    print("  StudyBuddy AI - Local LLM Study Assistant (CLI Mode)")
    print("=" * 65)
    print("Commands:")
    print("  'exit' or 'quit' -> Close application")
    print("  'reset'          -> Clear conversation history (keeps DB records)")
    print("=" * 65)

    agent = StudyBuddyAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye! Happy studying.")
                sys.exit(0)

            if user_input.lower() == "reset":
                agent.reset_conversation()
                print("\n[System]: Conversation memory cleared. Database history preserved.")
                continue

            print("\n[Agent Activity]")
            # Consume the generator loop step-by-step
            for step in agent.chat_step(user_input):
                step_type = step.get("type")

                if step_type == "status":
                    print(f"  --> {step.get('content')}")
                elif step_type == "tool_call":
                    print(f"\n  [TOOL CALL] -> {step.get('tool')}")
                    print(f"      Arguments: {json.dumps(step.get('arguments'), indent=8)}")
                elif step_type == "tool_result":
                    print(f"  [TOOL RESULT] <- {step.get('tool')}")
                    print(f"      Status: {step.get('result', {}).get('status', 'complete')}")
                elif step_type == "final_response":
                    print_separator()
                    print(f"StudyBuddy: {step.get('content')}")
                    print_separator()
                elif step_type == "error":
                    print(f"\n[ERROR]: {step.get('content')}")

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()
