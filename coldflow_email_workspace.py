import os
import re
import math
import html
import streamlit as st


# ============================================================
# COLDFLOW | Email writing workspace
# ============================================================

st.set_page_config(
    page_title="ColdFlow | Email Writing Workspace",
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
    "natural_replaced": [],
    "input_stats": {},
    "sanitized_stats": {},
    "humanized_stats": {},
    "deliverability_score": 0,
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
        background:transparent; border:0; border-radius:0;
        padding:2px 4px; box-shadow:none; position:relative;
    }
    [data-testid="stVerticalBlockBorderWrapper"] { overflow:visible !important; box-sizing:border-box !important; }
    .token-row { background:transparent !important; }
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

NATURAL_WORDING_REFINEMENTS = {
    # Common stiff or overly formal phrases
    "I hope this email finds you well": "I hope you're doing well",
    "I am writing to inform you": "I'm writing to let you know",
    "we would like to inform you": "we wanted to let you know",
    "we are pleased to announce": "we're glad to share",
    "please do not hesitate to": "feel free to",
    "do not hesitate to": "feel free to",
    "at your earliest convenience": "when you have a moment",
    "at this point in time": "now",
    "due to the fact that": "because",
    "for the purpose of": "to",
    "with regard to": "about",
    "in order to": "to",
    "as per": "based on",
    "prior to": "before",
    "subsequent to": "after",
    "make a decision": "decide",
    "provide assistance": "help",
    "I am reaching out": "I'm getting in touch",
    "the purpose of this email is to": "I'm writing to",
    "this email is to let you know that": "I wanted to let you know",
    "we would appreciate it if you could": "could you",
    "please find attached": "I've attached",
    "it is important to note that": "please note",
    "this will enable you to": "this can help you",
    "we kindly request that you": "please",
    "kindly be informed": "please note",
    "delve into": "take a closer look at",
    "delve": "look into",
    "delving": "looking into",
    "testament": "clear example",
    "tapestry": "mix",
    "crucial": "important",
    "moreover": "also",
    "elevate": "improve",
    "leverage": "use",
    "utilize": "use",
    "seamless": "smooth",
    "in summary": "overall",
    "furthermore": "also",
    "pivotal": "important",
    "paramount": "important",
}

# -------------------- CORE FUNCTIONS ------------------------
def calc_height(text: str, split: bool = False) -> int:
    chars_per_line = 42 if split else 92
    lines = sum(max(1, math.ceil(len(p) / chars_per_line)) for p in text.splitlines())
    return min(900, max(190, lines * 25 + 55))


def analyze_stylometrics(text: str) -> dict:
    cleaned = re.sub(r"[^a-zA-Z0-9\s.]", "", text)
    sentences = [part.strip() for part in re.split(r"[.!?]+", cleaned) if part.strip()]
    words = re.findall(r"\b[a-zA-Z]+\b", cleaned.lower())
    total_words = len(words)
    lexical_diversity = (len(set(words)) / total_words) if total_words else 0.0

    if len(sentences) > 1:
        lengths = [len(sentence.split()) for sentence in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((length - mean_len) ** 2 for length in lengths) / len(lengths)
        rhythm = min(1.0, math.sqrt(variance) / (mean_len + 1e-5))
    else:
        mean_len = float(total_words)
        rhythm = 0.0

    return {
        "word_variety": round(lexical_diversity * 100, 1),
        "burstiness": round(rhythm * 100, 1),
        "average_sentence_words": round(mean_len, 1),
        "sentence_count": len(sentences),
        "total_words": total_words,
    }



def replace_terms(text: str, mapping: dict):
    updated = text
    replaced = []
    for original, replacement in mapping.items():
        pattern = re.compile(rf"\b{re.escape(original)}\b", re.IGNORECASE)
        if pattern.search(updated):
            replaced.append((original, replacement))
            def preserve_sentence_case(match):
                found = match.group(0)
                if found[:1].isupper():
                    return replacement[:1].upper() + replacement[1:]
                return replacement
            updated = pattern.sub(preserve_sentence_case, updated)
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
    st.session_state.natural_replaced = []
    st.session_state.humanized_stats = {}


def run_humanization():
    updated, replacements = replace_terms(
        st.session_state.sanitized_text, NATURAL_WORDING_REFINEMENTS
    )
    st.session_state.humanized_text = updated
    st.session_state.natural_replaced = replacements
    st.session_state.humanized_stats = analyze_stylometrics(updated)
    st.session_state.is_humanized = True


# -------------------- SIDEBAR -------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">❄</div>
            <span>ColdFlow</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Workspace navigation",
        ["Workspace", "Why ColdFlow", "How to use", "FAQ"],
        label_visibility="collapsed",
        format_func=lambda x: {
            "Workspace": "⌂   Workspace",
            "Why ColdFlow": "◎   Why ColdFlow",
            "How to use": "☷   How to use",
            "FAQ": "?   FAQ",
        }[x],
    )
    st.markdown(
        """
        <div class="sidebar-footer">
            <strong>ColdFlow</strong><br>
            Review. Refine. Send with clarity.
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------- TOP HEADER --------------------------
header_left = st.container()
with header_left:
    st.markdown("<div class='page-title'>ColdFlow</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Review promotional wording, then make your email sound natural.</div>",
        unsafe_allow_html=True,
    )

# -------------------- INFORMATION PAGES ----------------------
if page == "Why ColdFlow":
    st.markdown("## Why use ColdFlow?")
    st.markdown(
        "ColdFlow helps you review an outbound email in two deliberate passes: "
        "first check promotional wording that can look overly sales-heavy, then "
        "smooth stiff phrases so the message reads naturally."
    )
    with st.container(border=True):
        st.markdown("### A clearer message, without the salesy noise")
        st.write("Promotional wording suggestions point out phrases that may feel pushy or exaggerated. You decide which alternatives fit your message.")
        st.markdown("### A natural voice that still sounds like you")
        st.write("The natural wording pass refines words and common sentence phrases across the draft. It is designed to keep your original point, not turn your email into generic marketing copy.")
        st.markdown("### A transparent, local workflow")
        st.write("The checks use built-in wording rules and simple text statistics. Your draft is processed in this app session; there is no external writing service or API key required.")
    st.info("No wording tool can guarantee inbox placement. Sender reputation, recipient engagement, authentication, links, attachments, and sending practices also matter.")

elif page == "How to use":
    st.markdown("## How to use ColdFlow")
    steps = [
        ("1. Paste your email", "Add the full message, including the subject or sign-off if you want those reviewed too."),
        ("2. Review promotional wording", "Select Run text audit. Read each suggested alternative and keep the wording that best matches your intent."),
        ("3. Make the wording more natural", "Select Make wording more natural. ColdFlow smooths common stiff phrases across words and sentences while keeping the message's meaning."),
        ("4. Compare and decide", "Compare the phrase-reviewed draft with the natural version. Copy the version you prefer from the text area."),
    ]
    with st.container(border=True):
        for title, detail in steps:
            st.markdown(f"### {title}")
            st.write(detail)
    st.caption("Tip: Read the final email aloud once. If a sentence does not sound like something you would say, edit it before sending.")

elif page == "FAQ":
    st.markdown("## Frequently asked questions")
    faqs = [
        ("Does ColdFlow guarantee that my email avoids junk mail?", "No. It highlights wording that may look overly promotional, but inbox placement also depends on sender reputation, authentication, recipient engagement, links, attachments, and provider-specific filtering."),
        ("What does the natural wording pass do?", "It replaces selected formal or stiff words and common sentence phrases with simpler, more conversational alternatives across your paragraphs. It does not invent new claims or rewrite your message from scratch."),
        ("Will it change the meaning of my email?", "The substitutions are designed to preserve the point, but wording is context-dependent. Always review the result and change any suggestion that does not fit."),
        ("Does ColdFlow use an external writing service or need an API key?", "No. This version uses local phrase rules and basic text statistics. No API key or paid subscription is needed."),
        ("What do the writing metrics mean?", "Word variety is the share of unique words. Sentence rhythm describes how much sentence lengths vary. Average sentence length is the mean number of words per sentence. These are descriptive indicators, not quality grades."),
        ("Is my email guaranteed to stay private?", "This version does not send your draft to an external text-generation API. If you deploy the app on a hosted service, review that host's data and logging settings."),
    ]
    for question, answer in faqs:
        with st.expander(question):
            st.write(answer)

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
        st.caption("First review promotional wording. Then refine the message so the full email reads naturally.")
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
                    "<div class='panel-heading'><span class='heading-mark'></span>After promotional wording review</div>",
                    unsafe_allow_html=True,
                )
                st.caption("Review the revised draft. This first pass focuses on promotional phrases that may feel too sales-heavy.")
                st.text_area(
                    "Sanitized output",
                    value=st.session_state.sanitized_text,
                    height=calc_height(st.session_state.sanitized_text),
                    key="sanitized_output",
                    label_visibility="collapsed",
                    max_chars=None,
                    disabled=True,
                )
                if st.button("Make the email sound more natural", type="primary", use_container_width=True):
                    with st.spinner("Refining stiff wording across the message..."):
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
                    st.markdown("**After promotional wording review**")
                    st.text_area(
                        "Promotional wording review",
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
                        "Natural wording version",
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
        delivery_color = "#16836B" if st.session_state.deliverability_score >= 70 else "#B7791F"

        st.markdown("")
        metrics_html = f"""<div class="metrics-panel">
          <div class="panel-heading"><span class="heading-mark"></span>Writing overview</div>
          <div class="metrics-grid">
            <div class="metric">
              <div class="metric-label">Word count</div>
              <div class="metric-value" style="color:#2864C5">{active_stats['total_words']}</div>
              <div class="metric-note">Words in this version</div>
            </div>
            <div class="metric">
              <div class="metric-label">Word variety</div>
              <div class="metric-value" style="color:#16836B">{active_stats['word_variety']}%</div>
              <div class="metric-note">Unique words in the draft</div>
            </div>
            <div class="metric">
              <div class="metric-label">Average sentence</div>
              <div class="metric-value" style="color:#2864C5">{active_stats['average_sentence_words']}</div>
              <div class="metric-note">Words per sentence</div>
            </div>
            <div class="metric">
              <div class="metric-label">Promotional wording check</div>
              <div class="metric-value" style="color:{delivery_color}">{st.session_state.deliverability_score}%</div>
              <div class="metric-note">Phrase-based indicator, not an inbox score</div>
            </div>
          </div>
        </div>"""
        st.markdown(metrics_html, unsafe_allow_html=True)
        st.caption(
            "These figures describe the text only. They do not predict inbox placement or guarantee that a message will avoid spam filters."
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
                    st.markdown("**Natural wording changes**")
                    render_token_ledger(st.session_state.natural_replaced)
        else:
            with st.container(border=True):
                st.markdown("**Promotional wording suggestions**")
                render_token_ledger(st.session_state.spam_replaced)

        if st.button("Start a new audit", key="reset_audit"):
            for key in [
                "audit_executed", "is_humanized", "raw_text", "sanitized_text",
                "humanized_text", "spam_replaced", "natural_replaced", "input_stats",
                "sanitized_stats", "humanized_stats", "deliverability_score",
            ]:
                st.session_state[key] = DEFAULTS[key]
            st.rerun()

    else:
        st.markdown("")
        with st.container(border=True):
            st.markdown("**Your workspace is ready**")
            st.write(
                "Paste an email above to review promotional wording, then refine the full message so it reads naturally."
            )

# -------------------- FOOTNOTE ------------------------------
st.markdown(
    "<div style='text-align:center;color:#98A2B3;font-size:.74rem;padding:28px 0 4px'>"
    "ColdFlow · Clearer emails, more natural wording"
    "</div>",
    unsafe_allow_html=True,
)
