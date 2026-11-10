"""
quiz_db.py — Database layer for the lightweight Quiz app.
Read-only for questions/courses/subjects. Read-write for users and quiz history.
"""

import sqlite3
import os
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "mcq_database.db")


def ensure_dirs():
    """Create data directories if they don't exist."""
    os.makedirs(DB_DIR, exist_ok=True)


def get_connection():
    """Get a database connection with row factory."""
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Ensure the required tables exist (users + quiz_history may need creation
    if the database was exported without them)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE(name, course_id)
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL DEFAULT 'mcq',
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT NOT NULL,
            marks INTEGER NOT NULL DEFAULT 1,
            subject_id INTEGER NOT NULL,
            has_image INTEGER DEFAULT 0,
            image_path TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS quiz_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score REAL NOT NULL,
            total_marks INTEGER NOT NULL,
            obtained_marks INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            subjects TEXT NOT NULL,
            time_taken_seconds INTEGER,
            taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


# ─── User CRUD ───────────────────────────────────────────────────────────────

def create_user(username, password_hash, display_name):
    """Create a new user. Returns user id or None if username exists."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?)",
            (username, password_hash, display_name)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username):
    """Get user by username. Returns dict or None."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Course / Subject (Read-Only) ───────────────────────────────────────────

def get_all_courses():
    """Get all courses as list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_subjects_by_course(course_id):
    """Get all subjects for a given course."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM subjects WHERE course_id = ? ORDER BY name", (course_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_subjects():
    """Get all subjects with course info."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*, c.name as course_name 
        FROM subjects s 
        JOIN courses c ON s.course_id = c.id 
        ORDER BY c.name, s.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Question Queries (Read-Only) ───────────────────────────────────────────

def get_question_stats():
    """Get statistics about the question bank."""
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) as cnt FROM questions").fetchone()['cnt']

    by_course = conn.execute("""
        SELECT c.name, COUNT(*) as cnt 
        FROM questions q 
        JOIN subjects s ON q.subject_id = s.id 
        JOIN courses c ON s.course_id = c.id 
        GROUP BY c.id ORDER BY cnt DESC
    """).fetchall()

    by_subject = conn.execute("""
        SELECT s.name, c.name as course_name, COUNT(*) as cnt 
        FROM questions q 
        JOIN subjects s ON q.subject_id = s.id 
        JOIN courses c ON s.course_id = c.id 
        GROUP BY s.id ORDER BY cnt DESC
    """).fetchall()

    by_marks = conn.execute("""
        SELECT marks, COUNT(*) as cnt FROM questions GROUP BY marks
    """).fetchall()

    by_type = conn.execute("""
        SELECT question_type, COUNT(*) as cnt FROM questions GROUP BY question_type
    """).fetchall()

    conn.close()
    return {
        'total': total,
        'by_course': [dict(r) for r in by_course],
        'by_subject': [dict(r) for r in by_subject],
        'by_marks': [dict(r) for r in by_marks],
        'by_type': [dict(r) for r in by_type],
    }


def get_random_questions(subject_ids, marks=None, question_type=None, count=10):
    """Get random questions for quiz generation."""
    conn = get_connection()
    placeholders = ','.join('?' * len(subject_ids))
    query = f"""
        SELECT q.*, s.name as subject_name, c.name as course_name
        FROM questions q
        JOIN subjects s ON q.subject_id = s.id
        JOIN courses c ON s.course_id = c.id
        WHERE q.subject_id IN ({placeholders})
    """
    params = list(subject_ids)

    if marks is not None:
        query += " AND q.marks = ?"
        params.append(marks)

    if question_type is not None:
        query += " AND q.question_type = ?"
        params.append(question_type)

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(count)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_available_question_count(subject_ids, marks=None, question_type=None):
    """Count available questions matching filters."""
    conn = get_connection()
    placeholders = ','.join('?' * len(subject_ids))
    query = f"""
        SELECT COUNT(*) as cnt FROM questions 
        WHERE subject_id IN ({placeholders})
    """
    params = list(subject_ids)

    if marks is not None:
        query += " AND marks = ?"
        params.append(marks)

    if question_type is not None:
        query += " AND question_type = ?"
        params.append(question_type)

    count = conn.execute(query, params).fetchone()['cnt']
    conn.close()
    return count


# ─── Quiz History ────────────────────────────────────────────────────────────

def save_quiz_result(user_id, score, total_marks, obtained_marks, total_questions,
                     correct_count, subjects, time_taken_seconds=None):
    """Save a quiz attempt result."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO quiz_history 
        (user_id, score, total_marks, obtained_marks, total_questions, correct_count, 
         subjects, time_taken_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, score, total_marks, obtained_marks, total_questions,
          correct_count, subjects, time_taken_seconds))
    conn.commit()
    conn.close()


def get_quiz_history(user_id, limit=20):
    """Get recent quiz history for a user."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM quiz_history 
        WHERE user_id = ? 
        ORDER BY taken_at DESC 
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
