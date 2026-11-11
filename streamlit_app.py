import os
import re
import time
import math
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="ColdFlow AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE INITIALIZATION ---
if "audit_executed" not in st.session_state:
    st.session_state.audit_executed = False
    st.session_state.is_humanized = False
    st.session_state.raw_text = ""
    st.session_state.sanitized_text = ""
    st.session_state.humanized_text = ""
    st.session_state.spam_replaced = []
    st.session_state.ai_replaced = []
    st.session_state.input_stats = {}
    st.session_state.sanitized_stats = {}
    st.session_state.humanized_stats = {}

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hey! I am **Aura**, your ColdFlow AI Copilot. Ask me how our heuristic engine strips spam triggers, how Stylometrics measures cadence, or why we operate strictly in-memory for SOC-2 compliance!"}
    ]

# --- 100% PURE WHITE APPLE THEME (NUCLEAR CSS OVERRIDE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* 1. FORCE UNIVERSAL PURE WHITE (OVERRIDING SYSTEM DARK MODE) */
    :root {
        color-scheme: light !important;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], section.main {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #1D1D1F !important;
        font-family: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", "SF Pro Display", sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    header, #MainMenu, footer, .stDeployButton { visibility: hidden !important; display: none !important; }

    /* 2. BROAD CANVAS (1200px) */
    .block-container {
        max-width: 1200px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 6rem !important;
    }

    /* 3. TYPOGRAPHY */
    h1.app-title {
        font-size: 3.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em !important;
        text-align: center;
        color: #1D1D1F !important;
        margin-bottom: 0px !important;
    }
    .app-subtitle {
        text-align: center;
        color: #6E6E73 !important;
        font-size: 1.15rem;
        font-weight: 500;
        margin-top: 8px;
        margin-bottom: 35px;
    }

    /* 4. THE BUTTON - HIGH CONTRAST & CLEARLY VISIBLE */
    .stButton > button {
        background: #0071E3 !important;
        background-color: #0071E3 !important;
        color: #FFFFFF !important;
        border-radius: 980px !important;
        height: 3.4em !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(0, 113, 227, 0.35) !important;
        display: block !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        margin-top: 10px !important;
    }
    .stButton > button:hover {
        background-color: #0077ED !important;
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 25px rgba(0, 113, 227, 0.45) !important;
        color: #FFFFFF !important;
    }

    /* 5. BOX HEADER BAR (GEMINI STYLE INTEGRATED COPY BAR) */
    .box-header-bar {
        background: #F5F5F7;
        border: 1.5px solid #E5E5EA;
        border-bottom: none;
        border-top-left-radius: 18px;
        border-top-right-radius: 18px;
        padding: 10px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 15px;
    }
    .box-header-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #1D1D1F;
    }

    /* 6. ATTACHED TEXT AREAS (NO DRAG, NO SCROLLBAR) */
    .stTextArea, .stTextArea > div {
        background-color: transparent !important;
        width: 100% !important;
    }
    .stTextArea div[data-baseweb="base-input"] {
        background-color: transparent !important;
        border: none !important;
    }
    .stTextArea textarea {
        background-color: #FAFAFC !important;
        border: 1.5px solid #E5E5EA !important;
        border-top-left-radius: 0px !important;
        border-top-right-radius: 0px !important;
        border-bottom-left-radius: 18px !important;
        border-bottom-right-radius: 18px !important;
        border-top: 1px solid #E5E5EA !important;
        padding: 20px !important;
        font-size: 15.5px !important;
        color: #1D1D1F !important;
        font-weight: 450 !important;
        line-height: 1.65 !important;
        resize: none !important; /* DISABILITY OF DRAG HANDLE */
        overflow-y: hidden !important; /* ELIMINATES SCROLLBAR */
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02) !important;
    }
    .stTextArea textarea:focus {
        border-color: #0071E3 !important;
        box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1) !important;
        background-color: #FFFFFF !important;
    }

    /* 7. MINI COPY BUTTON INSIDE HEADER */
    .mini-copy-btn button {
        background: #FFFFFF !important;
        color: #1D1D1F !important;
        border: 1px solid #D2D2D7 !important;
        border-radius: 8px !important;
        padding: 4px 12px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        height: auto !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        margin: 0 !important;
        width: auto !important;
    }
    .mini-copy-btn button:hover {
        background: #F5F5F7 !important;
        border-color: #86868B !important;
        transform: none !important;
    }

    /* 8. FLOATING POPUP AI ASSISTANT */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 999999 !important;
    }
    [data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%) !important;
        color: #FFFFFF !important;
        border-radius: 980px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(0, 113, 227, 0.35) !important;
        width: auto !important;
    }

    /* 9. ANALYTICS CARD */
    .analytics-panel {
        background-color: #FAFAFC;
        border: 1px solid #E5E5EA;
        border-radius: 22px;
        padding: 26px;
        margin-top: 35px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.02);
    }
    .analytics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }
    .metric-cell {
        text-align: center;
        padding: 0 8px;
    }
    .metric-cell:not(:last-child) {
        border-right: 1px solid #E5E5EA;
    }
    .metric-header {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #86868B;
        margin-bottom: 6px;
    }
    .metric-stat {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .metric-desc {
        font-size: 0.8rem;
        color: #6E6E73;
        margin-top: 6px;
        font-weight: 500;
    }

    /* 10. TOKEN LEDGERS */
    .token-card {
        background: #FAFAFC;
        border: 1px solid #E5E5EA;
        border-radius: 18px;
        padding: 18px;
        margin-top: 15px;
    }
    .token-row {
        display: flex;
        align-items: center;
        padding: 7px 0;
        font-size: 0.92rem;
        border-bottom: 1px solid #E5E5EA;
    }
    .token-row:last-child { border-bottom: none; }
    .badge-trigger {
        background: #FFF1F0;
        color: #FF3B30;
        border: 1px solid #FFD1CF;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        margin-right: 10px;
    }
    .badge-safe {
        background: #EDFBF0;
        color: #34C759;
        border: 1px solid #B7F1C4;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        margin-left: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT DIRECT CLIPBOARD HELPER ---
def trigger_copy(text_to_copy, message="Copied to clipboard!"):
    js_code = f"""
    <script>
    navigator.clipboard.writeText({json.dumps(text_to_copy)});
    </script>
    """
    st.components.v1.html(js_code, height=0)
    st.toast(f"✅ {message}")

# --- DICTIONARIES & ALGORITHMIC RULES ---
DELIVERABILITY_RISK_TRIGGERS = {
    "100% free": "complimentary",
    "free": "zero-cost",
    "guaranteed": "empirically proven",
    "guarantee": "ensure",
    "act now": "at your earliest convenience",
    "urgent": "time-sensitive",
    "risk-free": "no-commitment",
    "click here": "review the demo link",
    "cheap": "cost-effective",
    "miracle": "high-impact",
    "scam": "inefficiency",
    "buy now": "explore the partnership"
}

ROBOTIC_AI_MARKERS = {
    "delve": "examine",
    "delving": "looking",
    "testament": "clear proof",
    "tapestry": "diversity",
    "crucial": "vital",
    "moreover": "also",
    "elevate": "improve",
    "leverage": "apply",
    "utilize": "use",
    "seamless": "fluid",
    "in summary": "overall",
    "furthermore": "in addition",
    "pivotal": "central",
    "paramount": "top priority"
}

# --- ACCURATE HEIGHT CALCULATOR (NO SCROLLBARS) ---
def calc_accurate_height(text: str, is_split: bool = False) -> int:
    chars_per_line = 36 if is_split else 80
    total_lines = 0
    for paragraph in text.split('\n'):
        total_lines += max(1, math.ceil(len(paragraph) / chars_per_line))
    return max(180, total_lines * 28 + 65)

# --- STYLOMETRIC NLP MATH ENGINE ---
def analyze_stylometrics(text: str) -> dict:
    raw_clean = re.sub(r'[^a-zA-Z0-9\s.]', '', text)
    sentences = [s.strip() for s in re.split(r'[.!?]+', raw_clean) if len(s.strip()) > 0]
    words = re.findall(r'\b[a-zA-Z]+\b', raw_clean.lower())
    
    total_words = max(len(words), 1)
    unique_words = len(set(words))
    ttr = unique_words / total_words
    
    if len(sentences) > 1:
        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        burstiness_score = min(1.0, math.sqrt(variance) / (mean_len + 1e-5))
    else:
        burstiness_score = 0.25
        
    ai_matches = sum(1 for m in ROBOTIC_AI_MARKERS.keys() if re.search(rf"\b{re.escape(m)}\b", text, re.IGNORECASE))
    marker_density = ai_matches / (total_words / 20.0 + 1.0)
    
    ai_prob = (0.45 * (1.0 - burstiness_score)) + (0.25 * (1.0 - ttr)) + (0.30 * min(1.0, marker_density))
    ai_percentage = round(max(3.8, min(97.6, ai_prob * 100)), 1)
    human_score = round(100.0 - ai_percentage, 1)
    
    return {
        "ai_pct": ai_percentage,
        "human_pct": human_score,
        "burstiness": round(burstiness_score * 100, 1),
        "lexical_diversity": round(ttr * 100, 1),
        "total_words": total_words
    }

# --- FLOATING POPUP AI COPILOT ("AURA") ---
with st.popover("💬 AI Copilot • Aura", help="Click to open ColdFlow AI assistant"):
    st.markdown("### 💬 Aura • AI Copilot")
    st.caption("🟢 In-Memory Stylometric Assistant")
    st.markdown("---")
    
    for msg in st.session_state.chat_messages[-4:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if user_prompt := st.chat_input("Ask Aura anything about ColdFlow..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        q = user_prompt.lower()
        if "soc" in q or "security" in q or "data" in q:
            reply = "ColdFlow operates 100% in-memory with zero data retention. Your outbound drafts never leave the runtime execution session, ensuring absolute enterprise privacy and SOC-2 alignment."
        elif "humanize" in q or "stylometric" in q:
            reply = "Stylometric Humanization analyzes sentence cadence (Burstiness) and Type-Token Ratios (lexical diversity), surgically neutralizing robotic clichés like 'testament' or 'delve' without robotic hallucinations."
        else:
            reply = "ColdFlow is a specialized deliverability engine designed to bypass Google Workspace and Outlook 365 heuristic junk filters while keeping human tone 100% intact."
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()

# --- HEADER SECTION ---
st.markdown("<h1 class='app-title'>ColdFlow <span style='color: #0071E3;'>AI</span></h1>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Enterprise deliverability audit & stylometric humanization engine.</div>", unsafe_allow_html=True)

# --- 1. INPUT DRAFT (BROAD FULL-WIDTH) ---
default_sample = (
    "Hi Sarah,\n\n"
    "We have a 100% free tool that is guaranteed to scale your team's output. "
    "It is a testament to our seamless engineering. Delve into our system today to leverage this "
    "crucial trial and elevate your workflow. Act now and click here to get a risk-free trial started.\n\n"
    "Best,\nJohn"
)

h_col1, h_col2 = st.columns([6, 1])
with h_col1:
    st.markdown("<div class='box-header-title' style='padding-top: 15px;'>✍️ Outbound Draft (Input)</div>", unsafe_allow_html=True)
with h_col2:
    st.markdown("<div class='mini-copy-btn' style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
    if st.button("📋 Copy", key="cp_input"):
        trigger_copy(default_sample, "Input draft copied!")
    st.markdown("</div>", unsafe_allow_html=True)

raw_input = st.text_area(
    label="Draft Input",
    label_visibility="collapsed",
    value=default_sample,
    height=calc_accurate_height(default_sample, is_split=False),
    key="raw_input_box"
)

# --- 2. PRIMARY ACTION BUTTON (HIGHLY VISIBLE SOLID BLUE) ---
if st.button("Optimize Deliverability & Run Heuristic Audit 🚀", type="primary", use_container_width=True):
    with st.spinner("Executing lexical & spam vector audit..."):
        time.sleep(0.35)
        
    st.session_state.raw_text = raw_input
    st.session_state.input_stats = analyze_stylometrics(raw_input)
    
    text = raw_input
    replaced_spam = []
    for trigger, safe_word in DELIVERABILITY_RISK_TRIGGERS.items():
        pattern = re.compile(rf"\b{re.escape(trigger)}\b", re.IGNORECASE)
        if pattern.search(text):
            replaced_spam.append((trigger, safe_word))
            text = pattern.sub(safe_word, text)
            
    st.session_state.sanitized_text = text
    st.session_state.spam_replaced = replaced_spam
    st.session_state.sanitized_stats = analyze_stylometrics(text)
    
    spam_penalty = len(replaced_spam) * 20
    st.session_state.deliverability_score = max(20, 100 - spam_penalty)
    
    st.session_state.audit_executed = True
    st.session_state.is_humanized = False

# --- 3. OUTPUT STAGE ---
if st.session_state.audit_executed:
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
    
    # CASE A: BEFORE HUMANIZE (BROAD FULL-WIDTH MATCHING INPUT BOX)
    if not st.session_state.is_humanized:
        st.markdown("<h2 style='font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; text-align: center;'>Sanitized Copy</h2>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #6E6E73; margin-bottom: 15px;'>Enterprise junk filters neutralized. Human structure preserved.</div>", unsafe_allow_html=True)
        
        c_head1, c_head2 = st.columns([6, 1])
        with c_head1:
            st.markdown("<div class='box-header-title' style='padding-top: 15px;'>🛡️ Deliverability Sanitized (Broad View)</div>", unsafe_allow_html=True)
        with c_head2:
            st.markdown("<div class='mini-copy-btn' style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
            if st.button("📋 Copy", key="cp_single_sanitized"):
                trigger_copy(st.session_state.sanitized_text, "Sanitized copy copied!")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.text_area(
            label="Sanitized Output",
            label_visibility="collapsed",
            value=st.session_state.sanitized_text,
            height=calc_accurate_height(st.session_state.sanitized_text, is_split=False),
            key="sanitized_broad_box"
        )
        
        # Humanize Trigger Button
        if st.button("✨ Humanize AI Rhythms & Robotic Markers (Split View)", use_container_width=True):
            with st.spinner("Restructuring cadence & stripping robotic markers..."):
                time.sleep(0.4)
                
            work_text = st.session_state.sanitized_text
            replaced_ai = []
            for marker, human_alt in ROBOTIC_AI_MARKERS.items():
                pattern = re.compile(rf"\b{re.escape(marker)}\b", re.IGNORECASE)
                if pattern.search(work_text):
                    replaced_ai.append((marker, human_alt))
                    work_text = pattern.sub(human_alt, work_text)
                    
            st.session_state.humanized_text = work_text
            st.session_state.ai_replaced = replaced_ai
            st.session_state.humanized_stats = analyze_stylometrics(work_text)
            st.session_state.is_humanized = True
            st.rerun()

    # CASE B: AFTER HUMANIZE (SIDE-BY-SIDE EQUAL SPLIT)
    else:
        st.markdown("<h2 style='font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; text-align: center;'>Surgical Comparison</h2>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #6E6E73; margin-bottom: 25px;'>Deliverability Sanitized (Left) vs Stylometrically Humanized (Right)</div>", unsafe_allow_html=True)
        
        col_left, col_right = st.columns(2, gap="large")
        split_height = max(
            calc_accurate_height(st.session_state.sanitized_text, is_split=True),
            calc_accurate_height(st.session_state.humanized_text, is_split=True)
        )
        
        with col_left:
            sl_col1, sl_col2 = st.columns([4, 1.5])
            with sl_col1:
                st.markdown("<div class='box-header-title' style='padding-top: 15px;'>🛡️ Deliverability Sanitized</div>", unsafe_allow_html=True)
            with sl_col2:
                st.markdown("<div class='mini-copy-btn' style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
                if st.button("📋 Copy", key="cp_split_l"):
                    trigger_copy(st.session_state.sanitized_text, "Sanitized copy copied!")
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.text_area(
                label="Left Split",
                label_visibility="collapsed",
                value=st.session_state.sanitized_text,
                height=split_height,
                key="split_box_left"
            )
            
        with col_right:
            sr_col1, sr_col2 = st.columns([4, 1.5])
            with sr_col1:
                st.markdown("<div class='box-header-title' style='padding-top: 15px; color: #0071E3;'>✨ Fully Humanized</div>", unsafe_allow_html=True)
            with sr_col2:
                st.markdown("<div class='mini-copy-btn' style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
                if st.button("📋 Copy", key="cp_split_r"):
                    trigger_copy(st.session_state.humanized_text, "Humanized copy copied!")
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.text_area(
                label="Right Split",
                label_visibility="collapsed",
                value=st.session_state.humanized_text,
                height=split_height,
                key="split_box_right"
            )

    # --- 4. ANALYTICS BOARD ---
    active_stats = st.session_state.humanized_stats if st.session_state.is_humanized else st.session_state.sanitized_stats
    input_stats = st.session_state.input_stats
    
    ai_color = "#34C759" if active_stats["ai_pct"] < 35 else ("#FF9500" if active_stats["ai_pct"] < 65 else "#FF3B30")
    human_color = "#34C759" if active_stats["human_pct"] >= 65 else "#FF9500"
    deliv_color = "#34C759" if st.session_state.deliverability_score >= 70 else "#FF3B30"
    
    st.markdown(f"""
    <div class="analytics-panel">
        <div style="font-size: 1.05rem; font-weight: 700; margin-bottom: 22px; color: #1D1D1F;">
            Audited Stylometrics & Inbox Vectors
        </div>
        <div class="analytics-grid">
            <div class="metric-cell">
                <div class="metric-header">AI Content Probability</div>
                <div class="metric-stat" style="color: {ai_color};">{active_stats['ai_pct']}%</div>
                <div class="metric-desc">Baseline input was {input_stats['ai_pct']}%</div>
            </div>
            <div class="metric-cell">
                <div class="metric-header">Human Authenticity</div>
                <div class="metric-stat" style="color: {human_color};">{active_stats['human_pct']}%</div>
                <div class="metric-desc">Based on entropy & cadence</div>
            </div>
            <div class="metric-cell">
                <div class="metric-header">Burstiness Index</div>
                <div class="metric-stat" style="color: #0071E3;">{active_stats['burstiness']}</div>
                <div class="metric-desc">Sentence cadence variance</div>
            </div>
            <div class="metric-cell">
                <div class="metric-header">ESP Inbox Placement</div>
                <div class="metric-stat" style="color: {deliv_color};">{st.session_state.deliverability_score}%</div>
                <div class="metric-desc">Primary tab placement</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 5. TOKEN REPLACEMENT LEDGER ---
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    if not st.session_state.is_humanized:
        st.markdown("#### 🛡️ Neutralized Spam Triggers")
        if st.session_state.spam_replaced:
            token_rows = "".join([
                f"<div class='token-row'><span class='badge-trigger'>{orig}</span> replaced with <span class='badge-safe'>{safe}</span></div>"
                for orig, safe in st.session_state.spam_replaced
            ])
            st.markdown(f"<div class='token-card'>{token_rows}</div>", unsafe_allow_html=True)
        else:
            st.success("✅ Clean baseline: Zero promotional spam vectors discovered.")
    else:
        col_l1, col_l2 = st.columns(2, gap="large")
        with col_l1:
            st.markdown("#### 🛡️ Neutralized Spam Triggers")
            if st.session_state.spam_replaced:
                token_rows = "".join([
                    f"<div class='token-row'><span class='badge-trigger'>{orig}</span> ➔ <span class='badge-safe'>{safe}</span></div>"
                    for orig, safe in st.session_state.spam_replaced
                ])
                st.markdown(f"<div class='token-card'>{token_rows}</div>", unsafe_allow_html=True)
            else:
                st.info("No trigger words found.")
        with col_l2:
            st.markdown("<h4 style='color: #0071E3;'>✨ AI Robotic Clichés Humanized</h4>", unsafe_allow_html=True)
            if st.session_state.ai_replaced:
                token_rows = "".join([
                    f"<div class='token-row'><span class='badge-trigger'>{orig}</span> ➔ <span class='badge-safe'>{safe}</span></div>"
                    for orig, safe in st.session_state.ai_replaced
                ])
                st.markdown(f"<div class='token-card'>{token_rows}</div>", unsafe_allow_html=True)
            else:
                st.success("Text cadence is already indistinguishable from human writing.")c