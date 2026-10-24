"""
tools/quiz_tools.py - Quiz generation, persistence, and answer evaluation tools.
"""
import uuid
import json
import re
from typing import Dict, Any, List
import ollama
from config import DEFAULT_MODEL
from database.db import save_quiz, get_quiz_by_id, save_attempt

def generate_quiz(topic: str, num_questions: int = 3) -> Dict[str, Any]:
    """
    Generate a multiple-choice quiz on a topic using the local LLM and save it persistently.

    Args:
        topic: The subject to test (e.g., 'Python functions', 'While loops').
        num_questions: Number of questions to generate (1 to 5). Default is 3.

    Returns:
        Dictionary containing quiz_id and questions (without answers).
    """
    if not isinstance(topic, str) or not topic.strip():
        return {"status": "error", "message": "Topic must be a non-empty string."}

    if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 5:
        return {"status": "error", "message": "num_questions must be an integer between 1 and 5."}

    prompt = f"""
You are a computer science quiz generator. Create a {num_questions}-question multiple-choice quiz about "{topic}".
Return ONLY a valid JSON object with no markdown formatting, backticks, or extra commentary.
The JSON must follow this exact schema:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
      "correct_answer": "A",
      "explanation": "Why A is correct"
    }}
  ]
}}
"""

    try:
        response = ollama.chat(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )
        raw_text = response["message"]["content"].strip()
        
        # Strip out code block delimiters if model outputs them
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            return {"status": "error", "message": "Model failed to generate structured quiz JSON."}
        
        data = json.loads(json_match.group(0))
        raw_questions = data.get("questions", [])
        if not raw_questions:
            return {"status": "error", "message": "No questions could be parsed from generator."}

        quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
        public_questions = []
        secret_keys = []

        for q in raw_questions[:num_questions]:
            public_questions.append({
                "id": q.get("id"),
                "question": q.get("question"),
                "options": q.get("options")
            })
            secret_keys.append({
                "id": q.get("id"),
                "correct_answer": q.get("correct_answer", "").strip().upper()[:1],
                "explanation": q.get("explanation", "")
            })

        # Persist questions and answers in SQLite
        save_quiz(quiz_id, topic, public_questions, secret_keys)

        return {
            "status": "success",
            "quiz_id": quiz_id,
            "topic": topic,
            "total_questions": len(public_questions),
            "questions": public_questions,
            "instructions": "Present these questions to the student. Do not mark as finished until evaluate_answers is called."
        }

    except Exception as e:
        return {"status": "error", "message": f"Quiz generation failed: {str(e)}"}


def evaluate_answers(quiz_id: str, answers: List[str]) -> Dict[str, Any]:
    """
    Evaluate submitted answers against the stored quiz answer key and persist score.

    Args:
        quiz_id: The unique identifier of the saved quiz (e.g., 'quiz_a1b2c3d4').
        answers: List of single-letter answers submitted by student (e.g., ['A', 'B', 'C']).

    Returns:
        Evaluation summary, calculated score, and per-question explanations.
    """
    if not isinstance(quiz_id, str) or not quiz_id.strip():
        return {"status": "error", "message": "quiz_id must be a non-empty string."}

    if not isinstance(answers, list) or len(answers) == 0:
        return {"status": "error", "message": "answers must be a non-empty list of strings."}

    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return {"status": "error", "message": f"Quiz with ID '{quiz_id}' not found in database."}

    secret_keys = quiz["answer_keys"]
    total = len(secret_keys)
    clean_answers = [str(a).strip().upper()[:1] for a in answers]

    score = 0
    evaluations = []

    for idx, key_data in enumerate(secret_keys):
        correct = key_data["correct_answer"]
        user_ans = clean_answers[idx] if idx < len(clean_answers) else "NOT_PROVIDED"
        is_correct = (user_ans == correct)
        if is_correct:
            score += 1

        evaluations.append({
            "question_id": key_data["id"],
            "submitted": user_ans,
            "correct_answer": correct,
            "is_correct": is_correct,
            "explanation": key_data.get("explanation", "")
        })

    # Persist attempt
    attempt_id = save_attempt(
        quiz_id=quiz_id,
        topic=quiz["topic"],
        score=score,
        total_questions=total,
        submitted_answers=clean_answers,
        evaluations=evaluations
    )

    return {
        "status": "success",
        "attempt_id": attempt_id,
        "quiz_id": quiz_id,
        "topic": quiz["topic"],
        "score": score,
        "total": total,
        "percentage": round((score / total) * 100, 1),
        "results": evaluations
    }
