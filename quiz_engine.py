"""
quiz_engine.py — Interactive quiz session management with timer support, scoring, and review.
"""

import time
import random
import streamlit as st
from quiz_utils import format_duration


def init_quiz_session():
    """Initialize quiz session state keys if not present."""
    defaults = {
        'quiz_active': False,
        'quiz_questions': [],
        'quiz_current_idx': 0,
        'quiz_answers': {},
        'quiz_flagged': set(),
        'quiz_start_time': None,
        'quiz_timer_mode_active': 'none',
        'quiz_time_limit': 60,
        'quiz_question_start_time': None,
        'quiz_submitted': False,
        'quiz_results': None,
    }

    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def start_quiz(questions, timer_mode='none', time_limit=60):
    """
    Start a new quiz session.

    Args:
        questions: List of question dicts (already shuffled).
        timer_mode: 'none', 'per_question', or 'total'.
        time_limit: Time limit in seconds.
    """
    st.session_state.quiz_active = True
    st.session_state.quiz_questions = questions
    st.session_state.quiz_current_idx = 0
    st.session_state.quiz_answers = {}
    st.session_state.quiz_flagged = set()
    st.session_state.quiz_start_time = time.time()
    st.session_state.quiz_timer_mode_active= timer_mode
    st.session_state.quiz_time_limit = time_limit
    st.session_state.quiz_question_start_time = time.time()
    st.session_state.quiz_submitted = False
    st.session_state.quiz_results = None


def end_quiz():
    """End the current quiz and reset state."""
    st.session_state.quiz_active = False
    st.session_state.quiz_questions = []
    st.session_state.quiz_current_idx = 0
    st.session_state.quiz_answers = {}
    st.session_state.quiz_flagged = set()
    st.session_state.quiz_submitted = False
    st.session_state.quiz_results = None


def go_to_question(idx):
    """Navigate to a specific question index."""
    if 0 <= idx < len(st.session_state.quiz_questions):
        st.session_state.quiz_current_idx = idx
        st.session_state.quiz_question_start_time = time.time()


def save_answer(question_idx, answer):
    """Save an answer for a question."""
    st.session_state.quiz_answers[question_idx] = answer


def toggle_flag(question_idx):
    """Toggle the flagged state of a question."""
    if question_idx in st.session_state.quiz_flagged:
        st.session_state.quiz_flagged.discard(question_idx)
    else:
        st.session_state.quiz_flagged.add(question_idx)


def get_remaining_time():
    """
    Get remaining time in seconds based on timer mode.
    Returns None if no timer, or remaining seconds (can be negative if expired).
    """
    mode = st.session_state.quiz_timer_mode_active
    if mode == 'none':
        return None

    if mode == 'total':
        elapsed = time.time() - st.session_state.quiz_start_time
        return max(0, st.session_state.quiz_time_limit - elapsed)

    if mode == 'per_question':
        elapsed = time.time() - st.session_state.quiz_question_start_time
        return max(0, st.session_state.quiz_time_limit - elapsed)

    return None


def is_time_up():
    """Check if time is up for the current timer mode."""
    remaining = get_remaining_time()
    if remaining is None:
        return False
    return remaining <= 0


def calculate_results():
    """
    Calculate quiz results.

    Returns:
        dict with keys: score, total_marks, obtained_marks, correct_count,
        total_questions, time_taken, per_question_results
    """
    questions = st.session_state.quiz_questions
    answers = st.session_state.quiz_answers
    start_time = st.session_state.quiz_start_time

    total_marks = 0
    obtained_marks = 0
    correct_count = 0
    per_question = []

    for idx, q in enumerate(questions):
        marks = q.get('marks', 1)
        total_marks += marks
        user_answer = answers.get(idx, "")
        correct_answer = q.get('correct_answer', '')

        # Check correctness
        is_correct = False
        if q.get('question_type') == 'mcq':
            is_correct = str(user_answer).strip().upper() == str(correct_answer).strip().upper()
        else:
            # Fill-in-blank: case-insensitive comparison
            is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()

        if is_correct:
            correct_count += 1
            obtained_marks += marks

        per_question.append({
            'question': q,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'marks': marks,
        })

    time_taken = time.time() - start_time if start_time else 0
    score = (obtained_marks / total_marks * 100) if total_marks > 0 else 0

    results = {
        'score': score,
        'total_marks': total_marks,
        'obtained_marks': obtained_marks,
        'correct_count': correct_count,
        'total_questions': len(questions),
        'time_taken': time_taken,
        'per_question': per_question,
    }

    st.session_state.quiz_results = results
    st.session_state.quiz_submitted = True

    return results


def render_question_palette():
    """Render the question navigation palette with status indicators."""
    questions = st.session_state.quiz_questions
    current = st.session_state.quiz_current_idx
    answers = st.session_state.quiz_answers
    flagged = st.session_state.quiz_flagged

    dots_html = ""
    for i in range(len(questions)):
        if i == current:
            css_class = "dot-current"
        elif i in flagged:
            css_class = "dot-flagged"
        elif i in answers:
            css_class = "dot-answered"
        else:
            css_class = "dot-unanswered"
        dots_html += f'<span class="progress-dot {css_class}">{i + 1}</span>'

    st.markdown(f'<div style="margin: 0.5rem 0;">{dots_html}</div>', unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div style="font-size: 0.7rem; color: #808098; margin-top: 0.3rem;">
        🟣 Current &nbsp; 🔵 Answered &nbsp; 🟡 Flagged &nbsp; ⚫ Unanswered
    </div>
    """, unsafe_allow_html=True)


def render_timer():
    """Render the quiz timer display."""
    remaining = get_remaining_time()
    if remaining is None:
        return

    minutes, secs = divmod(int(remaining), 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        time_str = f"{minutes:02d}:{secs:02d}"

    # Determine urgency class
    css_class = "quiz-timer"
    if remaining < 30:
        css_class += " danger"
    elif remaining < 120:
        css_class += " warning"

    mode_label = "Per Question" if st.session_state.quiz_timer_mode_active == 'per_question' else "Total Time"
    st.markdown(f"""
    <div class="{css_class}">
        ⏱ {time_str}
        <div style="font-size: 0.7rem; color: #808098; margin-top: 0.2rem;">{mode_label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_results(results):
    """Render the quiz results display."""
    score = results['score']
    obtained = results['obtained_marks']
    total = results['total_marks']
    correct = results['correct_count']
    total_q = results['total_questions']
    time_taken = results['time_taken']

    # Score card
    st.markdown(f"""
    <div class="score-card animate-in">
        <div class="score-percentage">{score:.1f}%</div>
        <div class="score-label">
            {obtained}/{total} marks &nbsp;•&nbsp; {correct}/{total_q} correct &nbsp;•&nbsp;
            Time: {format_duration(time_taken)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Performance message
    st.markdown("<br>", unsafe_allow_html=True)
    if score >= 90:
        st.success("🌟 Outstanding performance! Excellent work!")
    elif score >= 70:
        st.success("👏 Great job! Keep up the good work!")
    elif score >= 50:
        st.warning("📚 Good effort! Some areas need review.")
    else:
        st.error("💪 Keep practicing! Review the topics and try again.")
