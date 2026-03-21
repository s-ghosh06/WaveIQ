"""
utils/styles.py — WaveIQ complete CSS, all issues fixed at once:
  1. Sidebar collapse button hidden (all known selectors)
  2. Header title much bigger, banner full width
  3. Number input text always white/visible
  4. Min/max tick bars hidden (plain text used instead)
  5. Display Options checkbox styling preserved
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Page background ── */
.stApp { background-color: #F8F9FA !important; }
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* ═══════════════════════════════════════════════════
   HIDE SIDEBAR COLLAPSE BUTTON — all known selectors
   covering Streamlit 1.28 through 1.40+
═══════════════════════════════════════════════════ */
[data-testid="collapsedControl"]                         { display: none !important; }
[data-testid="stSidebarCollapseButton"]                  { display: none !important; }
[data-testid="stSidebarNavCollapseIcon"]                 { display: none !important; }
button[aria-label="Collapse sidebar"]                    { display: none !important; }
button[aria-label="collapse sidebar"]                    { display: none !important; }
button[aria-label="Close sidebar"]                       { display: none !important; }
.css-1d391kg button                                      { display: none !important; }
section[data-testid="stSidebar"] > div > button          { display: none !important; }
section[data-testid="stSidebar"] button[kind="header"]   { display: none !important; }
/* The arrow chevron that sits just outside the sidebar */
div[data-testid="stSidebarUserContent"] ~ button         { display: none !important; }
div[class*="sidebar"] button[kind="header"]              { display: none !important; }

/* ═══════════════════════════════════════
   SIDEBAR — dark navy, always visible, never collapsed
═══════════════════════════════════════ */
/* Force sidebar to always be open — overrides collapsed state */
section[data-testid="stSidebar"][aria-expanded="false"] {
    display: flex !important;
    transform: none !important;
    width: 300px !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #1B2A3B 0%, #1e3a5f 60%, #0d2137 100%) !important;
    min-width: 300px !important;
    max-width: 300px !important;
    transform: none !important;
    display: flex !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.8rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
/* All sidebar text white */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] small { color: #E8F4FD !important; }

/* Slider thumb */
section[data-testid="stSidebar"] [data-baseweb="slider"] [data-testid="stThumb"] {
    background-color: #2E86C1 !important;
}

/* Radio buttons */
section[data-testid="stSidebar"] [data-baseweb="radio"] label {
    color: #E8F4FD !important;
    font-size: 0.85rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {
    color: #E8F4FD !important;
}

/* Number inputs — dark bg, WHITE text, centred, no ghost label */
section[data-testid="stSidebar"] input[type="number"],
section[data-testid="stSidebar"] .stNumberInput input {
    background: #1a3a5c !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    text-align: center !important;
    caret-color: #F39C12 !important;
    padding: 0.4rem 0.5rem !important;
}
/* Hide any ghost placeholder text inside number input */
section[data-testid="stSidebar"] input[type="number"]::placeholder {
    color: transparent !important;
    -webkit-text-fill-color: transparent !important;
}
/* Remove the inner label Streamlit sometimes renders inside the input wrapper */
section[data-testid="stSidebar"] .stNumberInput label {
    display: none !important;
}

/* Sidebar captions */
section[data-testid="stSidebar"] .stCaption p {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: #7FB3D3 !important;
}

/* Slider labels */
section[data-testid="stSidebar"] .stSlider label p {
    font-size: 0.8rem !important;
    color: #AED6F1 !important;
    white-space: normal !important;
    line-height: 1.4 !important;
}
section[data-testid="stSidebar"] .stSlider {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Hide Streamlit's own tick bar — we show plain text instead */
section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
section[data-testid="stSidebar"] [data-testid="stTickBarMax"] {
    display: none !important;
}

/* Number input label */
section[data-testid="stSidebar"] .stNumberInput label p {
    font-size: 0.7rem !important;
    color: #7FB3D3 !important;
    font-weight: 400 !important;
}
section[data-testid="stSidebar"] .stNumberInput {
    margin-top: 0.1rem !important;
    margin-bottom: 0.1rem !important;
}

/* Dividers */
section[data-testid="stSidebar"] hr {
    margin: 0.5rem 0 !important;
    border-color: rgba(255,255,255,0.1) !important;
}

/* Checkboxes */
section[data-testid="stSidebar"] .stCheckbox { margin-bottom: 0.1rem !important; }
section[data-testid="stSidebar"] .stCheckbox label {
    font-size: 0.83rem !important;
    color: #E8F4FD !important;
}

/* ═══════════════════════════════════════════════════
   HEADER BANNER — bigger title, full width, left+right
═══════════════════════════════════════════════════ */
.waveiq-banner {
    background: linear-gradient(135deg, #1A5276 0%, #2E86C1 100%);
    border-radius: 14px;
    padding: 1.8rem 2.8rem;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    width: 100%;
    box-sizing: border-box;
}
.waveiq-banner-left { display: flex; flex-direction: column; }
.waveiq-banner-title {
    font-size: 5rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0;
}
.waveiq-banner-title span { color: #F39C12; }
.waveiq-banner-sub {
    margin: 0.5rem 0 0;
    color: #AED6F1;
    font-size: 1.15rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}
.waveiq-mode-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 999px;
    padding: 0.5rem 1.3rem;
    color: #fff !important;
    font-size: 0.88rem;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
}

/* ═══════════════════════════════════════
   SECTION HEADERS
═══════════════════════════════════════ */
.sec-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.3rem 0 0.8rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid #E2E8F0;
}
.sec-header-icon { font-size: 1.15rem; }
.sec-header-text {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #2E86C1;
}

/* ═══════════════════════════════════════
   STATUS ALERTS
═══════════════════════════════════════ */
.alert-ok {
    background: #EAFAF1; border-left: 4px solid #27AE60;
    border-radius: 8px; padding: 0.85rem 1.1rem; margin-bottom: 0.7rem;
}
.alert-ok h4 { margin: 0 0 0.25rem; color: #1E8449; font-size: 0.92rem; }
.alert-ok p  { margin: 0; color: #1E8449; font-size: 0.84rem; line-height: 1.6; }

.alert-danger {
    background: #FDEDEC; border-left: 4px solid #E74C3C;
    border-radius: 8px; padding: 0.85rem 1.1rem; margin-bottom: 0.7rem;
}
.alert-danger h4 { margin: 0 0 0.25rem; color: #C0392B; font-size: 0.92rem; }
.alert-danger p  { margin: 0; color: #922B21; font-size: 0.84rem; line-height: 1.6; }

/* ═══════════════════════════════════════
   FORMULA CHIPS
═══════════════════════════════════════ */
.formula-row { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.55rem; margin-bottom: 0.3rem; }
.fchip {
    font-family: 'IBM Plex Mono', monospace;
    background: #D6EAF8; border: 1px solid #AED6F1;
    color: #1A5276; padding: 0.26rem 0.65rem;
    border-radius: 6px; font-size: 0.74rem;
    display: inline-block; white-space: nowrap;
}

/* ═══════════════════════════════════════
   REAL-WORLD INSIGHT PANEL
═══════════════════════════════════════ */
.insight-header {
    background: linear-gradient(135deg, #2E86C1 0%, #1A5276 100%);
    border-radius: 10px 10px 0 0;
    padding: 0.9rem 1.2rem;
    display: flex; align-items: center; gap: 0.7rem;
}
.insight-header h3 { margin: 0; color: #fff; font-size: 1rem; font-weight: 700; line-height: 1.3; }
.insight-header p  { margin: 0.1rem 0 0; color: #AED6F1; font-size: 0.72rem; }
.insight-body {
    background: #fff; border: 1px solid #E2E8F0;
    border-top: none; border-radius: 0 0 10px 10px;
    padding: 1rem 1.2rem;
}
.insight-body p {
    font-size: 0.86rem; color: #2D3748; line-height: 1.7;
    margin: 0 0 0.75rem; padding-bottom: 0.75rem;
    border-bottom: 1px solid #F0F4F8;
}
.insight-body ul { list-style: none; padding: 0; margin: 0 0 0.75rem; }
.insight-body li {
    font-size: 0.84rem; color: #4A5568; padding: 0.28rem 0;
    border-bottom: 1px solid #F7FAFC;
    display: flex; align-items: flex-start; gap: 0.5rem; line-height: 1.6;
}
.insight-body li:last-child { border-bottom: none; }
.insight-body li::before { content: "→"; color: #2E86C1; font-weight: 700; flex-shrink: 0; }
.insight-example {
    background: #F7F9FC; border-left: 3px solid #F39C12;
    border-radius: 6px; padding: 0.65rem 0.9rem;
    font-size: 0.83rem; color: #4A5568; line-height: 1.65; margin-top: 0.7rem;
}

/* ═══════════════════════════════════════
   SIDEBAR QUICK-REF
═══════════════════════════════════════ */
.sb-quickref {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px; padding: 0.65rem 0.9rem; margin-top: 0.3rem;
}
.sb-quickref p {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem; line-height: 1.9;
    color: #E8F4FD !important; margin: 0;
}
.sb-qr-title {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #7FB3D3 !important; margin-bottom: 0.3rem;
}

/* ═══════════════════════════════════════
   METRIC CARDS
═══════════════════════════════════════ */
div[data-testid="metric-container"] {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 10px; padding: 0.85rem 1rem 0.8rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.45rem !important; color: #1A202C !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.74rem !important; font-weight: 600 !important; color: #718096 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.73rem !important; }

/* ═══════════════════════════════════════
   PLOTLY CHARTS
═══════════════════════════════════════ */
.stPlotlyChart {
    border: 1px solid #E2E8F0; border-radius: 10px;
    overflow: hidden; background: #fff;
}

/* ═══════════════════════════════════════
   FOOTER
═══════════════════════════════════════ */
.waveiq-footer {
    text-align: center; padding: 1.1rem 0 0.3rem;
    margin-top: 1.5rem; border-top: 1px solid #E2E8F0;
    font-size: 0.72rem; color: #A0AEC0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Hide ONLY the collapse arrow button — use visibility not display:none ──
   visibility:hidden keeps the element in DOM (sidebar stays open/functional)
   but makes the button invisible so users cannot click to collapse ── */
[data-testid="collapsedControl"]       { visibility: hidden !important; width: 0 !important; }
[data-testid="stSidebarCollapseButton"]{ visibility: hidden !important; width: 0 !important; }
button[aria-label="Collapse sidebar"]  { visibility: hidden !important; width: 0 !important; }
button[aria-label="collapse sidebar"]  { visibility: hidden !important; width: 0 !important; }
</style>
"""


def inject_css() -> None:
    """Inject the WaveIQ CSS once at startup."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)