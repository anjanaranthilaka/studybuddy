"""
agents/prompts.py - System prompts and Ollama tool schemas for StudyBuddy AI.
"""

SYSTEM_PROMPT = """
You are StudyBuddy AI, a patient, structured, and helpful computer science tutor.
Your goal is to guide students through revision, quiz testing, and study planning.

BEHAVIORAL RULES:
1. When a user asks about programming concepts, check local study notes first using `search_notes`.
2. Base explanations on study notes when available. Clearly state when you are drawing from saved notes versus general concepts.
3. When asked to test the user or make a quiz, call `generate_quiz`. Present questions clearly and wait for the student's answers.
4. NEVER mark a quiz as completed or invent scores before the student has actually submitted answers.
5. When the user submits answers (e.g., 'A, B, C'), call `evaluate_answers` with the quiz_id.
6. When asked for weak areas or historical performance, use `get_learning_progress`.
7. When asked for a revision plan or schedule, use `create_study_plan`.
8. Execute multiple tools sequentially if a request requires it, but always base subsequent actions on real tool outputs.
9. If required details (such as days or minutes for a study plan) are missing, politely ask the user for them.
10. Be polite, concise, structured, and encouraging.
"""

# JSON Tool definitions following the official Ollama specification
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Search local markdown notes for topics, definitions, and code examples.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword or topic to search (e.g., 'functions', 'loops', 'scope')."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_quiz",
            "description": "Create a multiple-choice quiz on a topic and save it for evaluation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Subject for the quiz (e.g., 'Python functions', 'While loops')."
                    },
                    "num_questions": {
                        "type": "integer",
                        "description": "Number of questions to generate (1 to 5). Default is 3."
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_answers",
            "description": "Evaluate student answers against the saved quiz answer key and store the attempt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quiz_id": {
                        "type": "string",
                        "description": "The unique ID of the quiz being evaluated."
                    },
                    "answers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of single-letter answers submitted (e.g., ['A', 'B', 'C'])."
                    }
                },
                "required": ["quiz_id", "answers"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_learning_progress",
            "description": "Retrieve past quiz attempts, average scores, and identify weak topics needing revision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Optional specific topic filter. If omitted, returns all topics."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_study_plan",
            "description": "Generate and persist a structured multi-day study revision plan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of topics to cover in the revision plan."
                    },
                    "available_minutes_per_day": {
                        "type": "integer",
                        "description": "Available study minutes per day (between 15 and 480)."
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days available for the plan (between 1 and 30)."
                    }
                },
                "required": ["topics", "available_minutes_per_day", "days"]
            }
        }
    }
]
