"""
tools/study_plan_tools.py - Generate and persist structured study revision schedules.
"""
import math
from typing import Dict, Any, List, Optional
from database.db import save_study_plan, get_latest_study_plan

def create_study_plan(topics: List[str], available_minutes_per_day: int, days: int) -> Dict[str, Any]:
    """
    Create a personalized multi-day revision schedule based on topics, daily minutes, and timeframe.

    Args:
        topics: List of topic names (e.g., ['Python functions', 'Loops']).
        available_minutes_per_day: Daily study minutes (minimum 15, maximum 480).
        days: Number of days available (minimum 1, maximum 30).

    Returns:
        Structured day-by-day plan with topics and task breakdowns.
    """
    if not isinstance(topics, list) or len(topics) == 0:
        return {"status": "error", "message": "topics must be a non-empty list of topic names."}

    if not isinstance(available_minutes_per_day, int) or available_minutes_per_day < 15 or available_minutes_per_day > 480:
        return {"status": "error", "message": "available_minutes_per_day must be between 15 and 480."}

    if not isinstance(days, int) or days < 1 or days > 30:
        return {"status": "error", "message": "days must be an integer between 1 and 30."}

    schedule = []
    topics_count = len(topics)

    for day_num in range(1, days + 1):
        topic_idx = (day_num - 1) % topics_count
        current_topic = topics[topic_idx]

        reading_time = math.floor(available_minutes_per_day * 0.4)
        practice_time = math.floor(available_minutes_per_day * 0.4)
        review_time = available_minutes_per_day - reading_time - practice_time

        schedule.append({
            "day": day_num,
            "primary_topic": current_topic,
            "allocated_minutes": available_minutes_per_day,
            "tasks": [
                f"Read study notes on {current_topic} ({reading_time} mins)",
                f"Active coding practice & exercise implementation ({practice_time} mins)",
                f"Self-quiz review & weak point correction ({review_time} mins)"
            ]
        })

    plan_id = save_study_plan(topics, available_minutes_per_day, days, schedule)

    return {
        "status": "success",
        "plan_id": plan_id,
        "total_days": days,
        "daily_minutes": available_minutes_per_day,
        "schedule": schedule
    }

def get_active_study_plan() -> Dict[str, Any]:
    """Retrieve the latest active study plan from database."""
    plan = get_latest_study_plan()
    if not plan:
        return {"status": "not_found", "message": "No active study plan found."}
    return {"status": "success", "plan": plan}
