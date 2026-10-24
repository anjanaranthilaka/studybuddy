"""
config.py - Centralized configuration settings for StudyBuddy AI.
"""
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTES_DIR = DATA_DIR / "sample_notes"
LOGS_DIR = BASE_DIR / "logs"

# Database Configuration
DB_PATH = DATA_DIR / "studybuddy.db"

# LLM Configuration
DEFAULT_MODEL = "qwen2.5:3b"
MAX_AGENT_ROUNDS = 8
REQUEST_TIMEOUT = 60.0  # seconds

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)