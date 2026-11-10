"""
quiz_styles.py — Custom CSS styling for the lightweight Quiz app.
"""


def get_custom_css():
    """Return custom CSS for the application."""
    return """
    <style>
    /* ─── Import Google Font ───────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Global Styles ────────────────────────────────────────────── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ─── Sidebar Styling ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown label,
    [data-testid="stSidebar"] .stMarkdown span {
        color: #e0e0ff !important;
    }

    /* ─── Page Header ──────────────────────────────────────────────── */
    .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }

    .page-header h1 {
        color: white !important;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0;
        letter-spacing: -0.02em;
    }

    .page-header p {
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }

    /* ─── Metric Cards ─────────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }

    .metric-card .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .metric-card .metric-label {
        font-size: 0.85rem;
        color: #a0a0b8;
        margin-top: 0.3rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ─── Quiz Timer ───────────────────────────────────────────────── */
    .quiz-timer {
        background: linear-gradient(135deg, #1a1a3e 0%, #2a2a4e 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
        font-variant-numeric: tabular-nums;
    }

    .quiz-timer.warning {
        color: #ffa502;
        border-color: rgba(255, 165, 2, 0.4);
    }

    .quiz-timer.danger {
        color: #ff4757;
        border-color: rgba(255, 71, 87, 0.4);
        animation: pulse 1s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* ─── Quiz Progress ────────────────────────────────────────────── */
    .progress-dot {
        display: inline-block;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        margin: 3px;
        text-align: center;
        line-height: 28px;
        font-size: 0.7rem;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.15s ease;
    }

    .progress-dot:hover {
        transform: scale(1.15);
    }

    .dot-unanswered {
        background: rgba(255,255,255,0.08);
        color: #808098;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .dot-answered {
        background: rgba(102, 126, 234, 0.25);
        color: #667eea;
        border: 1px solid rgba(102, 126, 234, 0.5);
    }

    .dot-current {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        box-shadow: 0 3px 12px rgba(102, 126, 234, 0.4);
    }

    .dot-flagged {
        background: rgba(255, 165, 2, 0.2);
        color: #ffa502;
        border: 1px solid rgba(255, 165, 2, 0.5);
    }

    /* ─── Score Display ────────────────────────────────────────────── */
    .score-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .score-percentage {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .score-label {
        font-size: 1rem;
        color: #a0a0b8;
        margin-top: 0.5rem;
    }

    /* ─── Auth Page ────────────────────────────────────────────────── */
    .auth-container {
        max-width: 420px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: linear-gradient(135deg, #1e1e2f 0%, #252540 100%);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 16px 48px rgba(0,0,0,0.3);
    }

    .auth-title {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .auth-subtitle {
        text-align: center;
        color: #808098;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }

    /* ─── Buttons ──────────────────────────────────────────────────── */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
    }

    /* ─── Form Styling ─────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
    }

    .stSelectbox > div > div {
        border-radius: 10px;
    }

    /* ─── Dividers ─────────────────────────────────────────────────── */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent);
        margin: 1.5rem 0;
    }

    /* ─── Empty State ──────────────────────────────────────────────── */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #808098;
    }

    .empty-state .empty-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .empty-state .empty-text {
        font-size: 1.1rem;
        font-weight: 500;
    }

    .empty-state .empty-hint {
        font-size: 0.85rem;
        margin-top: 0.5rem;
        color: #606078;
    }

    /* ─── Animations ───────────────────────────────────────────────── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-in {
        animation: fadeIn 0.4s ease-out;
    }

    /* ─── Scrollbar ────────────────────────────────────────────────── */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }

    /* ─── Responsive Tweaks ────────────────────────────────────────── */
    @media (max-width: 768px) {
        .page-header {
            padding: 1.2rem 1.5rem;
        }
        .page-header h1 {
            font-size: 1.4rem;
        }
        .metric-card .metric-value {
            font-size: 1.6rem;
        }
    }
    </style>
    """


def render_page_header(title, subtitle=""):
    """Return HTML for a styled page header."""
    return f"""
    <div class="page-header animate-in">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """


def render_metric_card(value, label):
    """Return HTML for a metric card."""
    return f"""
    <div class="metric-card animate-in">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def render_empty_state(icon, text, hint=""):
    """Return HTML for an empty state display."""
    return f"""
    <div class="empty-state animate-in">
        <div class="empty-icon">{icon}</div>
        <div class="empty-text">{text}</div>
        <div class="empty-hint">{hint}</div>
    </div>
    """
