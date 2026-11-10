"""
quiz_app.py — Lightweight Streamlit Quiz App.
Contains only Dashboard + Quiz Mode (reads from pre-built database).
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime

import quiz_db as db
import quiz_auth as auth
import quiz_engine as qe
from quiz_styles import get_custom_css, render_page_header, render_metric_card, render_empty_state
from quiz_utils import get_full_image_path, truncate_text, format_marks, format_duration, ensure_dirs

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MCQ Quiz App",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Initialize ──────────────────────────────────────────────────────────────
db.init_db()
ensure_dirs()
st.markdown(get_custom_css(), unsafe_allow_html=True)
qe.init_quiz_session()

# ─── Authentication Gate ─────────────────────────────────────────────────────
if not auth.render_auth_page():
    st.stop()

# ─── Sidebar Navigation ─────────────────────────────────────────────────────
with st.sidebar:
    user = auth.get_current_user()
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size: 2rem;">🎯</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e0e0ff; margin-top: 0.3rem;">
            MCQ Quiz App
        </div>
        <div style="font-size: 0.8rem; color: #808098; margin-top: 0.2rem;">
            Welcome, {user['display_name']}
        </div>
    </div>
    <hr style="border-color: rgba(255,255,255,0.1); margin: 0.5rem 0 1rem 0;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "🎯 Quiz Mode"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        auth.logout()
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 🏠  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown(render_page_header("🏠 Dashboard", "Overview of your question bank"), unsafe_allow_html=True)

    stats = db.get_question_stats()

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_metric_card(stats['total'], "Total Questions"), unsafe_allow_html=True)
    with col2:
        courses = db.get_all_courses()
        st.markdown(render_metric_card(len(courses), "Courses"), unsafe_allow_html=True)
    with col3:
        subjects = db.get_all_subjects()
        st.markdown(render_metric_card(len(subjects), "Subjects"), unsafe_allow_html=True)
    with col4:
        history = db.get_quiz_history(auth.get_current_user_id(), limit=100)
        st.markdown(render_metric_card(len(history), "Quizzes Taken"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if stats['total'] == 0:
        st.markdown(render_empty_state(
            "📭",
            "No questions in the database!",
            "Please ensure the data/mcq_database.db file is present with questions."
        ), unsafe_allow_html=True)
        return

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Questions by Subject")
        if stats['by_subject']:
            df = pd.DataFrame(stats['by_subject'])
            st.bar_chart(df.set_index('name')['cnt'], color="#667eea")
        else:
            st.info("No subject data available.")

    with col_right:
        st.subheader("📈 Distribution")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**By Marks**")
            for item in stats['by_marks']:
                label = format_marks(item['marks'])
                st.markdown(f"- {label}: **{item['cnt']}** questions")
        with col_b:
            st.markdown("**By Type**")
            for item in stats['by_type']:
                label = "MCQ" if item['question_type'] == 'mcq' else 'Fill in Blank'
                st.markdown(f"- {label}: **{item['cnt']}** questions")

    # Recent quiz history
    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🕐 Recent Quizzes")
        for h in history[:5]:
            score_color = "🟢" if h['score'] >= 70 else ("🟡" if h['score'] >= 50 else "🔴")
            st.markdown(
                f"{score_color} **{h['score']:.1f}%** — {h['subjects']} — "
                f"{h['correct_count']}/{h['total_questions']} correct — "
                f"_{h['taken_at']}_"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯  QUIZ MODE
# ═══════════════════════════════════════════════════════════════════════════════
def page_quiz_mode():
    # If quiz is submitted, show results
    if st.session_state.quiz_submitted and st.session_state.quiz_results:
        _render_quiz_results()
        return

    # If quiz is active, show quiz
    if st.session_state.quiz_active:
        _render_active_quiz()
        return

    # Otherwise show quiz setup
    _render_quiz_setup()


def _render_quiz_setup():
    st.markdown(render_page_header(
        "🎯 Quiz Mode",
        "Test yourself with a customized quiz"
    ), unsafe_allow_html=True)

    courses = db.get_all_courses()
    if not courses:
        st.warning("⚠️ No courses found in the database.")
        return

    col1, col2 = st.columns(2)
    with col1:
        course_names = [c['name'] for c in courses]
        selected_course = st.selectbox("Select Course", course_names, key="quiz_course")
        course_id = next(c['id'] for c in courses if c['name'] == selected_course)

    with col2:
        subjects = db.get_subjects_by_course(course_id)
        if not subjects:
            st.warning("No subjects for this course.")
            return

        subject_names = [s['name'] for s in subjects]
        selected_subjects = st.multiselect(
            "Select Subject(s)",
            subject_names,
            default=[],
            key="quiz_subjects",
            placeholder="Choose subject(s)..."
        )

        selected_subject_ids = [
            subject['id'] for subject in subjects
            if subject['name'] in selected_subjects
        ]

        # Check each selected subject independently, without applying the
        # question-type or marks filters. A subject with no questions at all
        # should not be selectable for starting a quiz.
        empty_subjects = []
        for subject in subjects:
            if subject['name'] in selected_subjects:
                subject_question_count = db.get_available_question_count(
                    [subject['id']]
                )
                if subject_question_count == 0:
                    empty_subjects.append(subject['name'])

        if not selected_subjects:
            st.info("Select at least one subject to continue.")
        elif empty_subjects:
            st.warning(
                "No questions are available for: **"
                + ", ".join(empty_subjects)
                + "**. Deselect these subject(s) to start the quiz."
            )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        q_type = st.selectbox("Question Type", ["Both", "MCQ Only", "Fill in Blank Only"], key="quiz_q_type")
    with col_b:
        marks_choice = st.selectbox("Marks", ["Both", "1 Mark Only", "2 Marks Only"], key="quiz_marks")
    with col_c:
        # Count available
        q_type_param = None
        if q_type == "MCQ Only":
            q_type_param = "mcq"
        elif q_type == "Fill in Blank Only":
            q_type_param = "fill_in_blank"
        marks_param = None
        if marks_choice == "1 Mark Only":
            marks_param = 1
        elif marks_choice == "2 Marks Only":
            marks_param = 2

        avail = (
            db.get_available_question_count(
                selected_subject_ids,
                marks=marks_param,
                question_type=q_type_param
            )
            if selected_subject_ids else 0
        )
        num_questions = st.number_input(f"Number of Questions (Max: {avail})", min_value=1,
                                        max_value=max(1, avail), value=min(10, max(1, avail)), key="quiz_num")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Timer settings
    st.subheader("⏱️ Timer Settings")
    timer_mode = st.radio(
        "Timer Mode",
        ["🚫 No Timer", "⏱️ Per Question Timer", "⏱️ Total Quiz Timer"],
        horizontal=True,
        key="quiz_timer_mode"
    )

    time_limit = 60
    if "Per Question" in timer_mode:
        time_limit = st.slider("Seconds per question", 15, 300, 60, 15, key="quiz_pq_time")
    elif "Total Quiz" in timer_mode:
        time_limit = st.slider("Total time (minutes)", 1, 120, 15, 1, key="quiz_total_time") * 60

    st.markdown("<br>", unsafe_allow_html=True)

    disable_start = (
        not selected_subjects
        or bool(empty_subjects)
        or avail == 0
    )

    if st.button(
        "🚀 Start Quiz",
        type="primary",
        use_container_width=True,
        disabled=disable_start
    ):
        questions = db.get_random_questions(
            selected_subject_ids, marks=marks_param,
            question_type=q_type_param, count=num_questions
        )
        if not questions:
            st.error("No questions available.")
        else:
            tm = 'none'
            if "Per Question" in timer_mode:
                tm = 'per_question'
            elif "Total Quiz" in timer_mode:
                tm = 'total'

            qe.start_quiz(questions, timer_mode=tm, time_limit=time_limit)
            st.rerun()


def _render_active_quiz():
    questions = st.session_state.quiz_questions
    current = st.session_state.quiz_current_idx
    q = questions[current]

    # Header
    st.markdown(render_page_header(
        f"🎯 Question {current + 1} of {len(questions)}",
        f"{q.get('subject_name', '')} • {format_marks(q.get('marks', 1))}"
    ), unsafe_allow_html=True)

    # Timer and palette in sidebar-like columns
    col_main, col_side = st.columns([3, 1])

    with col_side:
        qe.render_timer()
        st.markdown("<br>", unsafe_allow_html=True)
        qe.render_question_palette()

    with col_main:
        # Question text
        st.markdown(f"### {q['question_text']}")

        # Image
        if q.get('has_image') and q.get('image_path'):
            full_path = get_full_image_path(q['image_path'])
            if full_path and os.path.exists(full_path):
                st.image(full_path, width=400)

        # Answer input
        existing_answer = st.session_state.quiz_answers.get(current, None)

        if q['question_type'] == 'mcq':
            options = [
                f"A) {q.get('option_a', '')}",
                f"B) {q.get('option_b', '')}",
                f"C) {q.get('option_c', '')}",
                f"D) {q.get('option_d', '')}",
            ]
            # Find existing selection index
            idx_default = None
            if existing_answer:
                letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                idx_default = letter_map.get(existing_answer, None)

            selected = st.radio(
                "Select your answer:",
                options,
                index=idx_default,
                key=f"quiz_ans_{current}"
            )
            if selected:
                answer_letter = selected[0]  # Get A, B, C, or D
                qe.save_answer(current, answer_letter)
        else:
            fib_answer = st.text_input(
                "Your Answer:",
                value=existing_answer or "",
                key=f"quiz_fib_{current}",
                placeholder="Type your answer here..."
            )
            if fib_answer:
                qe.save_answer(current, fib_answer)

        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation buttons
        col_prev, col_flag, col_next, col_submit = st.columns(4)

        with col_prev:
            if st.button("◀ Previous", disabled=(current == 0), use_container_width=True):
                qe.go_to_question(current - 1)
                st.rerun()

        with col_flag:
            flag_label = "🚩 Unflag" if current in st.session_state.quiz_flagged else "🚩 Flag"
            if st.button(flag_label, use_container_width=True):
                qe.toggle_flag(current)
                st.rerun()

        with col_next:
            if st.button("Next ▶", disabled=(current >= len(questions) - 1), use_container_width=True):
                qe.go_to_question(current + 1)
                st.rerun()

        with col_submit:
            answered = len(st.session_state.quiz_answers)
            if st.button(f"✅ Submit ({answered}/{len(questions)})", use_container_width=True,
                         type="primary"):
                if answered < len(questions):
                    st.warning(f"⚠️ You have {len(questions) - answered} unanswered question(s).")
                results = qe.calculate_results()
                # Save to history
                db.save_quiz_result(
                    user_id=auth.get_current_user_id(),
                    score=results['score'],
                    total_marks=results['total_marks'],
                    obtained_marks=results['obtained_marks'],
                    total_questions=results['total_questions'],
                    correct_count=results['correct_count'],
                    subjects=", ".join(set(q.get('subject_name', '') for q in questions)),
                    time_taken_seconds=int(results['time_taken'])
                )
                st.rerun()

    # Auto-submit on time up (total timer)
    if qe.is_time_up() and st.session_state.quiz_timer_mode_active == 'total':
        results = qe.calculate_results()
        db.save_quiz_result(
            user_id=auth.get_current_user_id(),
            score=results['score'],
            total_marks=results['total_marks'],
            obtained_marks=results['obtained_marks'],
            total_questions=results['total_questions'],
            correct_count=results['correct_count'],
            subjects=", ".join(set(q.get('subject_name', '') for q in questions)),
            time_taken_seconds=int(results['time_taken'])
        )
        st.rerun()


def _render_quiz_results():
    results = st.session_state.quiz_results
    st.markdown(render_page_header("🎯 Quiz Results", "Here's how you did!"), unsafe_allow_html=True)

    qe.render_results(results)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed review
    st.subheader("📋 Question Review")
    for idx, pq in enumerate(results['per_question']):
        q = pq['question']
        icon = "✅" if pq['is_correct'] else "❌"
        with st.expander(f"{icon} Q{idx + 1}. {truncate_text(q['question_text'], 80)} ({q.get('marks', 1)}M)"):
            st.markdown(f"**{q['question_text']}**")

            if q.get('has_image') and q.get('image_path'):
                full_path = get_full_image_path(q['image_path'])
                if full_path and os.path.exists(full_path):
                    st.image(full_path, width=350)

            if q['question_type'] == 'mcq':
                for label, key in [('A', 'option_a'), ('B', 'option_b'),
                                   ('C', 'option_c'), ('D', 'option_d')]:
                    opt = q.get(key, '')
                    prefix = ""
                    if label == pq['correct_answer']:
                        prefix = "✅ "
                    elif label == str(pq['user_answer']).upper():
                        prefix = "❌ "
                    st.markdown(f"{prefix}**({label})** {opt}")
            else:
                st.markdown(f"**Correct Answer:** {pq['correct_answer']}")

            st.markdown(f"**Your Answer:** {pq['user_answer'] or 'Not answered'}")
            if pq['is_correct']:
                st.success("Correct!")
            else:
                st.error(f"Incorrect — correct answer is: {pq['correct_answer']}")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Take Another Quiz", use_container_width=True, type="primary"):
        qe.end_quiz()
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

page_map = {
    "🏠 Dashboard": page_dashboard,
    "🎯 Quiz Mode": page_quiz_mode,
}

page_fn = page_map.get(page, page_dashboard)
page_fn()
