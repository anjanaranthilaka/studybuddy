"""
tools/notes_tools.py - Search engine for local markdown study notes.
"""
from typing import Dict, Any, List
from config import NOTES_DIR

def search_notes(query: str) -> Dict[str, Any]:
    """
    Search local study notes for a specific topic, keyword, or programming concept.

    Args:
        query: The search term or topic (e.g., 'functions', 'loops', 'scope').

    Returns:
        A dictionary containing matched notes and snippets, or an error/empty status.
    """
    if not isinstance(query, str) or not query.strip():
        return {
            "status": "error",
            "message": "Query parameter must be a non-empty string."
        }

    clean_query = query.strip().lower()
    keywords = [w for w in clean_query.split() if len(w) > 3] or [clean_query]
    matches: List[Dict[str, str]] = []

    if not NOTES_DIR.exists():
        return {
            "status": "error",
            "message": f"Notes directory '{NOTES_DIR}' does not exist."
        }

    for note_path in NOTES_DIR.glob("*.md"):
        try:
            with open(note_path, "r", encoding="utf-8") as f:
                content = f.read()

            content_lower = content.lower()
            stem_lower = note_path.stem.lower()

            # Match exact query OR any primary keyword
            is_match = (clean_query in content_lower or clean_query in stem_lower) or any(
                kw in content_lower or kw in stem_lower for kw in keywords
            )

            if is_match:
                lines = content.splitlines()
                snippet_lines = [
                    line.strip() for line in lines
                    if any(kw in line.lower() for kw in keywords) and line.strip()
                ]

                matches.append({
                    "filename": note_path.name,
                    "title": lines[0].replace("#", "").strip() if lines else note_path.stem,
                    "snippets": snippet_lines[:3],
                    "content_preview": content[:400] + ("..." if len(content) > 400 else "")
                })
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error reading note file '{note_path.name}': {str(e)}"
            }

    if not matches:
        return {
            "status": "not_found",
            "query": query,
            "message": f"No notes found matching '{query}'."
        }

    return {
        "status": "success",
        "query": query,
        "count": len(matches),
        "results": matches
    }
