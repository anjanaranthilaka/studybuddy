"""
tools/progress_tools.py - Retrieve student quiz attempts and pinpoint weak topics.
"""
from typing import Dict, Any, Optional
from database.db import get_topic_analytics

def get_learning_progress(topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve historical quiz scores and identify weak topics requiring revision.

    Args:
        topic: Optional topic filter (e.g., 'functions'). If omitted, retrieves all topics.

    Returns:
        Dictionary of topic analytics, average percentages, and flagged weak areas.
    """
    try:
        analytics = get_topic_analytics(topic)
        if not analytics:
            return {
                "status": "empty",
                "message": "No learning history recorded yet. Complete quizzes to generate analytics."
            }

        weak_topics = [
            row["topic"] for row in analytics
            if row["avg_pct_score"] is not None and row["avg_pct_score"] < 70.0
        ]

        return {
            "status": "success",
            "total_topics_tracked": len(analytics),
            "topic_summaries": analytics,
            "weak_topics_needing_revision": weak_topics
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve progress: {str(e)}"}
