"""
tests/test_tools.py - Automated unit tests for all StudyBuddy tools.
"""
import pytest
from tools.notes_tools import search_notes
from tools.quiz_tools import evaluate_answers
from tools.progress_tools import get_learning_progress
from tools.study_plan_tools import create_study_plan
from database.db import init_db, save_quiz

@pytest.fixture(autouse=True)
def setup_test_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test_tools.db"
    init_db(str(test_db))
    # Direct database operations to our temporary test database
    monkeypatch.setattr("database.db.DB_PATH", test_db)
    monkeypatch.setattr("config.DB_PATH", test_db)
    
    # Insert the parent quiz so foreign key constraint is satisfied
    sample_questions = [
        {"id": 1, "question": "What is LEGB?", "options": ["A) Local", "B) None"]},
        {"id": 2, "question": "What is def?", "options": ["A) Class", "B) Function"]}
    ]
    sample_keys = [
        {"id": 1, "correct_answer": "A", "explanation": "A is correct."},
        {"id": 2, "correct_answer": "B", "explanation": "B is correct."}
    ]
    save_quiz("valid_quiz", "Python functions", sample_questions, sample_keys, db_path=str(test_db))

def test_search_notes_success():
    res = search_notes("functions")
    assert res["status"] == "success"
    assert res["count"] >= 1
    assert any("python_functions.md" in r["filename"] for r in res["results"])

def test_search_notes_invalid_query():
    res = search_notes("")
    assert res["status"] == "error"

def test_evaluate_answers_scoring():
    res = evaluate_answers("valid_quiz", ["A", "B"])
    assert res["status"] == "success"
    assert res["score"] == 2
    assert res["percentage"] == 100.0

def test_evaluate_answers_partial():
    res = evaluate_answers("valid_quiz", ["A", "C"])
    assert res["status"] == "success"
    assert res["score"] == 1
    assert res["percentage"] == 50.0

def test_evaluate_answers_nonexistent_quiz():
    res = evaluate_answers("fake_quiz_id", ["A"])
    assert res["status"] == "error"
    assert "not found" in res["message"]

def test_create_study_plan_valid():
    res = create_study_plan(["Functions", "Loops"], 60, 2)
    assert res["status"] == "success"
    assert len(res["schedule"]) == 2
    assert res["schedule"][0]["allocated_minutes"] == 60

def test_create_study_plan_invalid_inputs():
    res = create_study_plan([], 60, 2)
    assert res["status"] == "error"

    res_mins = create_study_plan(["Functions"], 5, 2)
    assert res_mins["status"] == "error"

    res_days = create_study_plan(["Functions"], 60, 0)
    assert res_days["status"] == "error"
