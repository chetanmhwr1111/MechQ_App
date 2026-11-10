"""
quiz_utils.py — Minimal utility functions for the lightweight Quiz app.
"""

import os

# Base directories — resolve relative to this script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")


def ensure_dirs():
    """Create data directories if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)


def get_full_image_path(relative_path):
    """Convert a relative image path to full filesystem path."""
    if not relative_path:
        return None
    return os.path.join(DATA_DIR, relative_path)


def format_marks(marks):
    """Format marks for display."""
    return f"{marks} Mark{'s' if marks != 1 else ''}"


def truncate_text(text, max_length=80):
    """Truncate text with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_duration(seconds):
    """Format seconds into human-readable duration."""
    if seconds is None:
        return "N/A"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
