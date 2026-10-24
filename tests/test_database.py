import pytest
from database.db import (
    init_db,
    save_quiz,
    get_quiz_by_id,
    save_attempt,
    get_topic_analytics,
    save_study_plan,
    get_latest_study_plan
)

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_studybuddy.db"
    init_db(str(db_file))
    return str(db_file)

def test_init_db_creates_tables(temp_db):
    analytics = get_topic_analytics(db_path=temp_db)
    assert analytics == []

def test_quiz_persistence_and_retrieval(temp_db):
    sample_questions = [
        {"id": 1, "question": "What is LEGB?", "options": ["A", "B", "C", "D"]}
    ]
    sample_keys = [
        {"id": 1, "correct": "A", "explanation": "Local, Enclosing, Global, Built-in"}
    ]

    save_quiz("quiz_001", "python functions", sample_questions, sample_keys, db_path=temp_db)
    retrieved = get_quiz_by_id("quiz_001", db_path=temp_db)

    assert retrieved is not None
    assert retrieved["quiz_id"] == "quiz_001"
    assert retrieved["topic"] == "python functions"
    assert len(retrieved["questions"]) == 1
    assert retrieved["answer_keys"][0]["correct"] == "A"

def test_quiz_attempt_analytics(temp_db):
    save_quiz("q1", "loops", [{"id": 1}], [{"id": 1, "correct": "A"}], db_path=temp_db)

    save_attempt("q1", "loops", 1, 2, ["A", "B"], [{"is_correct": True}], db_path=temp_db)
    save_attempt("q1", "loops", 2, 2, ["A", "A"], [{"is_correct": True}], db_path=temp_db)

    analytics = get_topic_analytics("loops", db_path=temp_db)
    assert len(analytics) == 1
    assert analytics[0]["attempts_count"] == 2
    assert analytics[0]["avg_pct_score"] == 75.0
    assert analytics[0]["best_score"] == 2

def test_study_plan_persistence(temp_db):
    schedule = [
        {"day": 1, "topic": "Functions", "tasks": ["Review LEGB", "Write 2 functions"]}
    ]
    plan_id = save_study_plan(["Functions"], 45, 1, schedule, db_path=temp_db)
    assert plan_id is not None

    latest = get_latest_study_plan(db_path=temp_db)
    assert latest is not None
    assert latest["plan_id"] == plan_id
    assert latest["available_minutes_per_day"] == 45
    assert len(latest["schedule"]) == 1
