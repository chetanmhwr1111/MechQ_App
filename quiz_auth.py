"""
quiz_auth.py — Authentication module for the lightweight Quiz app.
Uses SHA-256 password hashing with SQLite storage.
"""

import hashlib
import streamlit as st
import quiz_db as db


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def register_user(username, password, display_name):
    """Register a new user. Returns (success, message)."""
    if not username or not password or not display_name:
        return False, "All fields are required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    password_hash = hash_password(password)
    user_id = db.create_user(username.strip().lower(), password_hash, display_name.strip())

    if user_id is None:
        return False, "Username already exists. Please choose another."
    return True, "Registration successful! You can now log in."


def login_user(username, password):
    """Authenticate a user. Returns (success, message, user_dict)."""
    if not username or not password:
        return False, "Please enter both username and password.", None

    user = db.get_user_by_username(username.strip().lower())
    if user is None:
        return False, "Invalid username or password.", None

    if user['password_hash'] != hash_password(password):
        return False, "Invalid username or password.", None

    return True, f"Welcome back, {user['display_name']}!", user


def is_logged_in():
    """Check if a user is currently logged in."""
    return st.session_state.get('logged_in', False)


def get_current_user():
    """Get the current logged-in user dict from session state."""
    return st.session_state.get('current_user', None)


def get_current_user_id():
    """Get the current logged-in user's ID."""
    user = get_current_user()
    return user['id'] if user else None


def logout():
    """Log out the current user."""
    keys_to_clear = ['logged_in', 'current_user']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def render_auth_page():
    """Render the login/register page. Returns True if user is authenticated."""
    if is_logged_in():
        return True

    st.markdown("""
    <div style="text-align:center; margin-top: 2rem;">
        <div style="font-size: 3.5rem; margin-bottom: 0.5rem;">🎯</div>
        <div class="auth-title">MCQ Quiz App</div>
        <div class="auth-subtitle">Sign in to start your quiz practice</div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                success, message, user = login_user(username, password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = user
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with tab_register:
        with st.form("register_form", clear_on_submit=True):
            display_name = st.text_input("Display Name", placeholder="Your full name", key="reg_name")
            new_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
            new_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password",
                                             placeholder="Confirm your password", key="reg_confirm")
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(new_username, new_password, display_name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    return False
