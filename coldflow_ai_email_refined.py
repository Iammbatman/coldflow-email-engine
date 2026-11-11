import os
import re
import math
import html
import streamlit as st


# ============================================================
# COLDflow AI | Enterprise-style Streamlit application
# ============================================================

st.set_page_config(
    page_title="ColdFlow AI",
    page_icon="❄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- SESSION STATE -------------------------
DEFAULTS = {
    "audit_executed": False,
    "is_humanized": False,
    "raw_text": "",
    "sanitized_text": "",
    "humanized_text": "",
    "spam_replaced": [],
    "ai_replaced": [],
    "input_stats": {},
    "sanitized_stats": {},
    "humanized_stats": {},
    "deliverability_score": 0,
    "chat_messages": [
        {
            "role": "assistant",
            "content": (
                "Hi, I'm Aura, your ColdFlow assistant. I can explain "
                "deliverability checks, text analysis, comparison results, "
                "and how to use this workspace. What would you like to know?"
            ),
        }
    ],
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- DESIGN SYSTEM -------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        color-scheme: light;
        --navy: #172B3A;
        --navy-2: #203B50;
        --blue: #2864C5;
        --blue-soft: #EAF1FC;
        --canvas: #F4F6F9;
        --surface: #FFFFFF;
        --border: #E1E7EF;
        --muted: #718096;
        --text: #1D2939;
        --green: #16836B;
        --green-soft: #E8F5F0;
        --red: #C84B55;
        --red-soft: #FCEDEF;
        --amber: #B7791F;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: var(--canvas) !important;
        color: var(--text) !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    #MainMenu, footer, .stDeployButton, [data-testid="stDeployButton"] {
        display:none !important; visibility:hidden !important;
    }
    [data-testid="stToolbar"] { visibility:hidden !important; height:0 !important; }
    .block-container {
        max-width: 1440px !important;
        padding: 2rem 2.4rem 4rem !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--navy) !important;
        border-right: 1px solid rgba(255,255,255,.08);
    }
    [data-testid="stSidebar"] * { color: #E7EEF7 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #B9C7D8 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: .55rem .7rem;
        border-radius: 9px;
        margin: .12rem 0;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,.08);
    }
    .sidebar-brand {
        display:flex; align-items:center; gap:11px;
        padding: 8px 4px 24px;
        color:#fff; font-size:1.18rem; font-weight:750;
        letter-spacing:-.035em;
    }
    .brand-mark {
        width:38px; height:38px; border-radius:11px;
        display:flex; align-items:center; justify-content:center;
        background:rgba(83,139,222,.18);
        color:#8DB8FF; font-size:22px; font-weight:700;
        border:1px solid rgba(141,184,255,.2);
    }
    .sidebar-footer {
        margin-top: 3rem; padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,.12);
        color:#91A4BA; font-size:.78rem;
    }

    /* Typography */
    h1, h2, h3, h4 { color:var(--navy) !important; letter-spacing:-.035em !important; }
    .page-title {
        font-size:2.25rem; line-height:1.15; font-weight:800;
        color:var(--navy); letter-spacing:-.055em;
        margin:0 0 .45rem 0;
    }
    .page-subtitle { color:var(--muted); font-size:.96rem; margin-bottom:1.7rem; }
    .section-title {
        color:var(--navy); font-size:1.12rem; font-weight:750;
        letter-spacing:-.025em; margin:0 0 .2rem 0;
    }
    .section-caption { color:var(--muted); font-size:.82rem; margin-bottom:1rem; }

    /* Cards and panels */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background:var(--surface) !important;
        border:1px solid var(--border) !important;
        border-radius:14px !important;
        box-shadow:0 2px 8px rgba(20,40,70,.025);
    }
    .panel {
        background:var(--surface); border:1px solid var(--border);
        border-radius:14px; padding:20px 22px;
        box-shadow:0 2px 8px rgba(20,40,70,.025);
    }
    .panel-heading {
        display:flex; align-items:center; gap:10px;
        color:var(--navy); font-weight:750; font-size:1rem;
        margin-bottom:14px;
    }
    .heading-mark {
        width:4px; height:22px; background:var(--blue);
        border-radius:4px; display:inline-block;
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        background:#FFFFFF !important;
        color:#1D2939 !important;
        -webkit-text-fill-color:#1D2939 !important;
        opacity:1 !important;
        border:1px solid #D8E0EA !important;
        border-radius:9px !important;
        font-family:'Inter',sans-serif !important;
        line-height:1.65 !important;
        font-size:.94rem !important;
    }
    /* Disabled result fields must remain fully readable in light or dark browser themes. */
    [data-testid="stTextArea"] textarea:disabled,
    [data-testid="stTextArea"] textarea[aria-disabled="true"] {
        background:#F8FAFC !important;
        color:#1D2939 !important;
        -webkit-text-fill-color:#1D2939 !important;
        opacity:1 !important;
        cursor:text !important;
    }
    [data-testid="stTextArea"] textarea::placeholder {
        color:#7B8797 !important;
        -webkit-text-fill-color:#7B8797 !important;
        opacity:1 !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color:var(--blue) !important;
        box-shadow:0 0 0 3px rgba(40,100,197,.10) !important;
    }
    [data-testid="stWidgetLabel"] label {
        color:#344054 !important; font-weight:600 !important;
    }

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button {
        background:var(--navy) !important;
        color:#fff !important; border:1px solid var(--navy) !important;
        border-radius:9px !important; min-height:2.7rem;
        font-weight:650 !important; transition:all .16s ease;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background:#25465F !important; border-color:#25465F !important;
        transform:translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background:#fff !important; color:var(--navy) !important;
        border:1px solid var(--border) !important;
    }

    /* Metrics */
    .metrics-panel {
        background:#fff; border:1px solid var(--border);
        border-radius:14px; padding:18px 20px;
        box-shadow:0 2px 8px rgba(20,40,70,.025);
    }
    .metrics-grid {
        display:grid; grid-template-columns:repeat(4,minmax(0,1fr));
        gap:0;
    }
    .metric { text-align:center; padding:5px 12px; }
    .metric:not(:last-child) { border-right:1px solid var(--border); }
    .metric-label {
        color:#778397; font-size:.69rem; font-weight:700;
        text-transform:uppercase; letter-spacing:.075em;
        margin-bottom:8px;
    }
    .metric-value {
        font-family:'JetBrains Mono',monospace;
        font-size:1.85rem; font-weight:700; letter-spacing:-.06em;
        line-height:1.2;
    }
    .metric-note { color:var(--muted); font-size:.75rem; margin-top:6px; }

    /* Token ledger */
    .token-card {
        background:#fff; border:1px solid var(--border);
        border-radius:12px; padding:10px 16px;
    }
    .token-row {
        display:flex; align-items:center; flex-wrap:wrap; gap:9px;
        padding:10px 0; border-bottom:1px solid #EDF0F4;
        color:#526174; font-size:.86rem;
    }
    .token-row:last-child { border-bottom:0; }
    .token-old {
        color:var(--red); background:var(--red-soft);
        border:1px solid #F5D5D9; border-radius:6px;
        padding:4px 8px; font-weight:650;
    }
    .token-new {
        color:var(--green); background:var(--green-soft);
        border:1px solid #CDEBDD; border-radius:6px;
        padding:4px 8px; font-weight:650;
    }
    .muted-note { color:var(--muted); font-size:.82rem; }

    /* Responsive */
    @media(max-width:850px) {
        .block-container { padding:1.2rem 1rem 5rem !important; }
        .page-title { font-size:1.8rem; }
        .metrics-grid { grid-template-columns:repeat(2,minmax(0,1fr)); row-gap:16px; }
        .metric:nth-child(2) { border-right:0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- RULE SETS -----------------------------
DELIVERABILITY_RISK_TRIGGERS = {
    "100% free": "complimentary",
    "free": "zero-cost",
    "guaranteed": "empirically supported",
    "guarantee": "aim",
    "act now": "at your earliest convenience",
    "urgent": "time-sensitive",
    "risk-free": "low-commitment",
    "click here": "view the resource",
    "cheap": "cost-effective",
    "miracle": "high-impact",
    "scam": "inefficiency",
    "buy now": "explore the option",
}

ROBOTIC_AI_MARKERS = {
    "delve": "examine",
    "delving": "looking",
    "testament": "clear example",
    "tapestry": "range",
    "crucial": "important",
    "moreover": "also",
    "elevate": "improve",
    "leverage": "use",
    "utilize": "use",
    "seamless": "smooth",
    "in summary": "overall",
    "furthermore": "also",
    "pivotal": "central",
    "paramount": "important",
}

# -------------------- CORE FUNCTIONS ------------------------
def calc_height(text: str, split: bool = False) -> int:
    chars_per_line = 42 if split else 92
    lines = sum(max(1, math.ceil(len(p) / chars_per_line)) for p in text.splitlines())
    return min(900, max(190, lines * 25 + 55))


def analyze_stylometrics(text: str) -> dict:
    cleaned = re.sub(r"[^a-zA-Z0-9\s.]", "", text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", cleaned) if s.strip()]
    words = re.findall(r"\b[a-zA-Z]+\b", cleaned.lower())
    total_words = max(len(words), 1)
    lexical_diversity = len(set(words)) / total_words

    if len(sentences) > 1:
        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((length - mean_len) ** 2 for length in lengths) / len(lengths)
        burstiness = min(1.0, math.sqrt(variance) / (mean_len + 1e-5))
    else:
        burstiness = 0.25

    marker_count = sum(
        1 for marker in ROBOTIC_AI_MARKERS
        if re.search(rf"\b{re.escape(marker)}\b", text, re.IGNORECASE)
    )
    marker_density = marker_count / (total_words / 20.0 + 1.0)
    estimate = (0.45 * (1 - burstiness)) + (0.25 * (1 - lexical_diversity)) + (0.30 * min(1, marker_density))
    ai_pct = round(max(3.8, min(97.6, estimate * 100)), 1)

    return {
        "ai_pct": ai_pct,
        "human_pct": round(100 - ai_pct, 1),
        "burstiness": round(burstiness * 100, 1),
        "lexical_diversity": round(lexical_diversity * 100, 1),
        "total_words": len(words),
    }


def replace_terms(text: str, mapping: dict):
    updated = text
    replaced = []
    for original, replacement in mapping.items():
        pattern = re.compile(rf"\b{re.escape(original)}\b", re.IGNORECASE)
        if pattern.search(updated):
            replaced.append((original, replacement))
            updated = pattern.sub(replacement, updated)
    return updated, replaced




def render_token_ledger(items):
    if not items:
        st.info("No matching terms were found in this pass.")
        return
    rows = "".join(
        "<div class='token-row'>"
        f"<span class='token-old'>{html.escape(old)}</span>"
        "<span>replaced with</span>"
        f"<span class='token-new'>{html.escape(new)}</span>"
        "</div>"
        for old, new in items
    )
    st.markdown(f"<div class='token-card'>{rows}</div>", unsafe_allow_html=True)


def run_audit(text: str):
    st.session_state.raw_text = text
    st.session_state.input_stats = analyze_stylometrics(text)

    sanitized, spam_items = replace_terms(text, DELIVERABILITY_RISK_TRIGGERS)
    st.session_state.sanitized_text = sanitized
    st.session_state.spam_replaced = spam_items
    st.session_state.sanitized_stats = analyze_stylometrics(sanitized)

    # This is a transparent heuristic indicator, not a real inbox-placement test.
    st.session_state.deliverability_score = max(20, 100 - len(spam_items) * 12)
    st.session_state.audit_executed = True
    st.session_state.is_humanized = False
    st.session_state.humanized_text = ""
    st.session_state.ai_replaced = []
    st.session_state.humanized_stats = {}


def run_humanization():
    updated, replacements = replace_terms(
        st.session_state.sanitized_text, ROBOTIC_AI_MARKERS
    )
    st.session_state.humanized_text = updated
    st.session_state.ai_replaced = replacements
    st.session_state.humanized_stats = analyze_stylometrics(updated)
    st.session_state.is_humanized = True


# -------------------- SIDEBAR -------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">❄</div>
            <span>ColdFlow AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Workspace navigation",
        ["Workspace", "How it works"],
        label_visibility="collapsed",
        format_func=lambda x: "⌂   Workspace" if x == "Workspace" else "ⓘ   How it works",
    )
    st.markdown(
        """
        <div class="sidebar-footer">
            <strong>ColdFlow AI</strong><br>
            Clearer outbound email, before you send
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------- TOP HEADER --------------------------
header_left = st.container()
with header_left:
    st.markdown("<div class='page-title'>ColdFlow <span style='color:#2864C5'>AI</span></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>A focused workspace for clearer, more thoughtful outbound email.</div>",
        unsafe_allow_html=True,
    )

# -------------------- GUIDE PAGE ----------------------------
if page == "How it works":
    st.markdown("## How ColdFlow works")
    st.markdown(
        "ColdFlow is a lightweight writing-review workspace. It applies transparent "
        "phrase substitutions and simple text statistics to help you inspect a draft."
    )
    with st.container(border=True):
        st.markdown("### 1. Run a text audit")
        st.write("Paste an outbound message. ColdFlow checks it against a local list of promotional phrases.")
        st.markdown("### 2. Review the suggestions")
        st.write("Inspect each suggested replacement. A replacement is only a suggestion; keep the original when it better expresses your meaning.")
        st.markdown("### 3. Make wording more natural")
        st.write("Optionally replace selected formulaic phrases, then compare the two versions.")
        st.markdown("### 4. Read the metrics carefully")
        st.warning(
            "Scores are experimental heuristics. They do not prove authorship, "
            "predict inbox placement, or guarantee that a message will avoid spam."
        )

# -------------------- MAIN WORKSPACE ------------------------
else:
    sample_text = (
        "Hi Sarah,\n\n"
        "We have a 100% free tool that is guaranteed to scale your team's output. "
        "It is a testament to our seamless engineering. Delve into our system today "
        "to leverage this crucial trial and elevate your workflow. Act now and click "
        "here to get a risk-free trial started.\n\n"
        "Best,\nJohn"
    )

    with st.container(border=True):
        st.markdown(
            "<div class='panel-heading'><span class='heading-mark'></span>Email draft</div>",
            unsafe_allow_html=True,
        )
        st.caption("Paste an email you plan to send. ColdFlow checks wording and suggests clearer alternatives.")
        raw_input = st.text_area(
            "Draft text",
            value=st.session_state.raw_text or sample_text,
            height=210,
            label_visibility="collapsed",
            max_chars=None,
            placeholder="Paste your outbound message here...",
            key="raw_input_box",
        )
        count_col, action_col = st.columns([3, 2])
        with count_col:
            word_count = len(re.findall(r"\b\w+\b", raw_input))
            st.caption(f"{word_count} words · {len(raw_input)} characters")
        with action_col:
            run_clicked = st.button(
                "Run text audit",
                type="primary",
                use_container_width=True,
            )
        if run_clicked:
            if raw_input.strip():
                with st.spinner("Reviewing wording and text patterns..."):
                    run_audit(raw_input)
                st.success("Text audit complete.")
            else:
                st.error("Enter some text before running the audit.")

    if st.session_state.audit_executed:
        st.markdown("")
        if not st.session_state.is_humanized:
            with st.container(border=True):
                st.markdown(
                    "<div class='panel-heading'><span class='heading-mark'></span>Suggested email</div>",
                    unsafe_allow_html=True,
                )
                st.caption("Review the suggested edits below. Keep any original wording that better fits your message.")
                st.text_area(
                    "Sanitized output",
                    value=st.session_state.sanitized_text,
                    height=calc_height(st.session_state.sanitized_text),
                    key="sanitized_output",
                    label_visibility="collapsed",
                    max_chars=None,
                    disabled=True,
                )
                if st.button("Make wording more natural", type="primary", use_container_width=True):
                    with st.spinner("Applying the phrase refinement pass..."):
                        run_humanization()
                    st.rerun()
        else:
            st.markdown(
                "<div class='section-title'>Compare your email versions</div>"
                "<div class='section-caption'>See the phrase-reviewed version beside the more natural version.</div>",
                unsafe_allow_html=True,
            )
            left, right = st.columns(2, gap="large")
            with left:
                with st.container(border=True):
                    st.markdown("**After phrase review**")
                    st.text_area(
                        "Sanitized version",
                        value=st.session_state.sanitized_text,
                        height=280,
                        key="compare_sanitized",
                        label_visibility="collapsed",
                        max_chars=None,
                        disabled=True,
                    )
            with right:
                with st.container(border=True):
                    st.markdown("**After natural wording pass**")
                    st.text_area(
                        "Humanized version",
                        value=st.session_state.humanized_text,
                        height=280,
                        key="compare_humanized",
                        label_visibility="collapsed",
                        max_chars=None,
                        disabled=True,
                    )

        active_stats = (
            st.session_state.humanized_stats
            if st.session_state.is_humanized
            else st.session_state.sanitized_stats
        )
        original_stats = st.session_state.input_stats

        ai_color = "#16836B" if active_stats["ai_pct"] < 35 else (
            "#B7791F" if active_stats["ai_pct"] < 65 else "#C84B55"
        )
        human_color = "#16836B" if active_stats["human_pct"] >= 65 else "#B7791F"
        delivery_color = "#16836B" if st.session_state.deliverability_score >= 70 else "#B7791F"

        st.markdown("")
        metrics_html = f"""<div class="metrics-panel">
          <div class="panel-heading"><span class="heading-mark"></span>Writing review</div>
          <div class="metrics-grid">
            <div class="metric">
              <div class="metric-label">Writing pattern estimate</div>
              <div class="metric-value" style="color:{ai_color}">{active_stats['ai_pct']}%</div>
              <div class="metric-note">Original draft: {original_stats['ai_pct']}%</div>
            </div>
            <div class="metric">
              <div class="metric-label">Word variety</div>
              <div class="metric-value" style="color:{human_color}">{active_stats['human_pct']}%</div>
              <div class="metric-note">A simple variety measure</div>
            </div>
            <div class="metric">
              <div class="metric-label">Sentence rhythm</div>
              <div class="metric-value" style="color:#2864C5">{active_stats['burstiness']}</div>
              <div class="metric-note">How sentence lengths vary</div>
            </div>
            <div class="metric">
              <div class="metric-label">Promotional wording check</div>
              <div class="metric-value" style="color:{delivery_color}">{st.session_state.deliverability_score}%</div>
              <div class="metric-note">Based on phrases found in this draft</div>
            </div>
          </div>
        </div>"""
        st.markdown(metrics_html, unsafe_allow_html=True)
        st.caption(
            "These are simple wording and writing-pattern indicators, not an AI detector or a test of whether an email will reach the inbox."
        )

        st.markdown("")
        if st.session_state.is_humanized:
            ledger_left, ledger_right = st.columns(2, gap="large")
            with ledger_left:
                with st.container(border=True):
                    st.markdown("**Promotional wording suggestions**")
                    render_token_ledger(st.session_state.spam_replaced)
            with ledger_right:
                with st.container(border=True):
                    st.markdown("**Wording made simpler**")
                    render_token_ledger(st.session_state.ai_replaced)
        else:
            with st.container(border=True):
                st.markdown("**Promotional wording suggestions**")
                render_token_ledger(st.session_state.spam_replaced)

        if st.button("Start a new audit", key="reset_audit"):
            for key in [
                "audit_executed", "is_humanized", "raw_text", "sanitized_text",
                "humanized_text", "spam_replaced", "ai_replaced", "input_stats",
                "sanitized_stats", "humanized_stats", "deliverability_score",
            ]:
                st.session_state[key] = DEFAULTS[key]
            st.rerun()

    else:
        st.markdown("")
        with st.container(border=True):
            st.markdown("**Your workspace is ready**")
            st.write(
                "Add an outbound draft above and run an audit to see phrase suggestions, "
                "text statistics, and an optional comparison."
            )

# -------------------- FOOTNOTE ------------------------------
st.markdown(
    "<div style='text-align:center;color:#98A2B3;font-size:.74rem;padding:28px 0 4px'>"
    "ColdFlow AI · Writing assistance and heuristic analysis"
    "</div>",
    unsafe_allow_html=True,
)
