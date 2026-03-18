"""
Custom CSS injection for a premium dark-theme Streamlit UI.
"""

import streamlit as st


def inject_custom_css():
    """Inject custom CSS for the entire app."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
/* ── Import Google Font ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root variables ─────────────────────────────────────────────── */
:root {
    --primary:   #6C63FF;
    --secondary: #00D2FF;
    --accent:    #FF6B6B;
    --success:   #00E676;
    --warning:   #FFD600;
    --bg-dark:   #0E1117;
    --bg-card:   #161B22;
    --bg-card-2: #1A1D24;
    --text-1:    #FAFAFA;
    --text-2:    #8B949E;
    --border:    #30363D;
    --glow:      rgba(108, 99, 255, 0.3);
}

/* ── Global reset ───────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-1);
}

/* ── Header banner ──────────────────────────────────────────────── */
.app-header {
    background: linear-gradient(135deg, #6C63FF 0%, #00D2FF 50%, #6C63FF 100%);
    background-size: 200% 200%;
    animation: gradientShift 6s ease infinite;
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    animation: rotateBg 10s linear infinite;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes rotateBg {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
.app-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    position: relative;
    z-index: 1;
}
.app-header p {
    margin: 0.4rem 0 0 0;
    font-size: 1rem;
    opacity: 0.9;
    font-weight: 400;
    position: relative;
    z-index: 1;
}

/* ── Glassmorphism metric cards ─────────────────────────────────── */
.metric-card {
    background: rgba(22, 27, 34, 0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.metric-card:hover {
    border-color: var(--primary);
    box-shadow: 0 0 20px var(--glow);
    transform: translateY(-2px);
}
.metric-card .label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-2);
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-card .delta {
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.2rem;
}
.delta-positive { color: var(--success) !important; }
.delta-negative { color: var(--accent) !important; }
.delta-neutral  { color: var(--text-2) !important; }

/* ── Section headers ────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--border);
}
.section-header h3 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-1);
}

/* ── Info card (AI advisor, explanations) ────────────────────────── */
.info-card {
    background: linear-gradient(135deg, rgba(108,99,255,0.08), rgba(0,210,255,0.05));
    border: 1px solid rgba(108, 99, 255, 0.25);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin: 0.8rem 0;
}
.info-card h4 {
    margin: 0 0 0.6rem 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--primary);
}

/* ── Comparison panel ───────────────────────────────────────────── */
.compare-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem;
    transition: border-color 0.3s ease;
}
.compare-panel:hover {
    border-color: var(--primary);
}
.compare-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 0.3rem 0.8rem;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 0.8rem;
}
.label-original {
    background: rgba(255, 107, 107, 0.15);
    color: var(--accent);
}
.label-optimized {
    background: rgba(0, 230, 118, 0.15);
    color: var(--success);
}

/* ── Score badge (AI advisor) ───────────────────────────────────── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 800;
    padding: 0.5rem 1.2rem;
    border-radius: 12px;
    border: 2px solid;
}
.score-low    { border-color: var(--success); color: var(--success); background: rgba(0,230,118,0.08); }
.score-medium { border-color: var(--warning); color: var(--warning); background: rgba(255,214,0,0.08); }
.score-high   { border-color: var(--accent);  color: var(--accent);  background: rgba(255,107,107,0.08); }

/* ── Progress bar ───────────────────────────────────────────────── */
.improvement-bar {
    height: 8px;
    border-radius: 4px;
    background: var(--border);
    overflow: hidden;
    margin-top: 0.4rem;
}
.improvement-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--primary), var(--success));
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Sidebar styling ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0D1117 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stCheckbox label {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* ── Hide Streamlit chrome ──────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Scrollbar ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── Tabs ───────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg-card);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.85rem;
}

/* ── Animation keyframes ────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeInUp 0.5s ease-out forwards;
}
</style>
"""
