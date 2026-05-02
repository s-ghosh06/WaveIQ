"""
ui/components.py
────────────────
WaveIQ UI components — fixes:
  1. Header: LEFT-aligned title, RIGHT-aligned mode pill, bigger font
  2. Section headers: bigger font size
  3. Mode-aware analysis callout: clearly different text per mode
  4. Real-world insight: mode content is always rendered and prominent
  5. All HTML uses unsafe_allow_html=True — no raw HTML leaks
"""

import streamlit as st
from core.modes import ModeContent


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE HEADER — left title, right mode pill
# ─────────────────────────────────────────────────────────────────────────────

def render_header(mode: str) -> None:
    """
    Header banner: WaveIQ title LEFT, subtitle below, mode pill RIGHT.
    Font larger than before. Maintains same gradient style.
    """
    st.markdown(f"""
    <div class="waveiq-banner">
        <div class="waveiq-banner-left">
            <p class="waveiq-banner-title">〰️ Wave<span>IQ</span></p>
            <p class="waveiq-banner-sub">Intelligent Signal Sampling &amp; Aliasing Analyzer</p>
        </div>
        <div class="waveiq-mode-tag">🎛️ &nbsp;{mode}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  METRIC CARDS ROW
# ─────────────────────────────────────────────────────────────────────────────

def render_metric_cards(
    f: float, fs: float, f_alias: float,
    rms: float, A: float, aliasing: bool,
) -> None:
    """4 KPI cards using st.metric — reactive, native."""
    nyquist_rate = 2 * f
    rms_label = (
        "High — aliased"  if rms > 0.5 * A else
        "Low — clean"     if rms < 0.1 * A else
        "Moderate"
    )
    alias_status = "⚠️ Aliasing active" if aliasing else "✅ No aliasing"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="📶  Signal Frequency",
            value=f"{f} Hz",
            delta=f"Nyquist needs ≥ {nyquist_rate} Hz",
            delta_color="off",
            help="Frequency of the original continuous sine wave.",
        )
    with c2:
        st.metric(
            label="🎚  Sampling Frequency",
            value=f"{fs} Hz",
            delta="Below Nyquist rate" if aliasing else "Above Nyquist rate",
            delta_color="inverse" if aliasing else "normal",
            help="Samples captured per second by the ADC.",
        )
    with c3:
        st.metric(
            label="👻  Alias Frequency",
            value=f"{f_alias:.2f} Hz",
            delta=alias_status,
            delta_color="inverse" if aliasing else "normal",
            help="Phantom frequency that appears when aliasing occurs.",
        )
    with c4:
        st.metric(
            label="📉  RMS Error",
            value=f"{rms:.4f}",
            delta=rms_label,
            delta_color="off",
            help="Root-mean-square difference between original and aliased signal.",
        )


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION HEADER — bigger font
# ─────────────────────────────────────────────────────────────────────────────

def section_header(icon: str, text: str) -> None:
    """Section divider — font increased to 1rem for readability."""
    st.markdown(f"""
    <div class="sec-header">
        <span class="sec-header-icon">{icon}</span>
        <span class="sec-header-text">{text}</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  NYQUIST ANALYSIS PANEL
# ─────────────────────────────────────────────────────────────────────────────

def render_nyquist_panel(
    f: float, fs: float, f_alias: float,
    nyquist_rate: float, aliasing: bool,
) -> None:
    """Alert panel + 3 metric tiles + formula chips."""
    ratio = fs / nyquist_rate
    k     = round(f / fs) if fs > 0 else 0

    if aliasing:
        st.markdown(f"""
        <div class="alert-danger">
            <h4>🔴 &nbsp;Aliasing Detected — Signal Cannot Be Reconstructed</h4>
            <p>
                Sampling frequency <b>fs = {fs} Hz</b> is below the required
                Nyquist rate of <b>{nyquist_rate:.0f} Hz</b>.
                The <b>{f} Hz</b> signal is misrepresented as a phantom
                <b>{f_alias:.2f} Hz</b> alias.
                Increase fs to at least <b>{int(nyquist_rate * 1.5)} Hz</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif f_alias < 1.0:
        st.markdown(f"""
        <div class="alert-ok">
            <h4>🟢 &nbsp;Perfectly Sampled — Maximum Fidelity</h4>
            <p>
                <b>fs = {fs} Hz</b> exceeds the Nyquist rate of
                <b>{nyquist_rate:.0f} Hz</b> by <b>{ratio:.2f}×</b>.
                Alias ≈ 0 Hz. Signal captured with zero distortion.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-ok">
            <h4>🟢 &nbsp;Nyquist Criterion Met — Signal Recoverable</h4>
            <p>
                <b>fs = {fs} Hz</b> satisfies the Nyquist criterion
                (≥ {nyquist_rate:.0f} Hz). Alias = {f_alias:.2f} Hz is within
                the representable band (below fs/2 = {fs/2:.0f} Hz).
            </p>
        </div>
        """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("fs / Nyquist Rate", f"{ratio:.3f}×",
                  delta="Need ≥ 1.0×",
                  delta_color="inverse" if ratio < 1 else "normal",
                  help="Ratio of sampling frequency to required Nyquist rate.")
    with m2:
        st.metric("Nyquist Rate", f"{nyquist_rate:.0f} Hz",
                  delta=f"= 2 × {f} Hz", delta_color="off",
                  help="Minimum fs to avoid aliasing.")
    with m3:
        st.metric("Max Representable", f"{fs/2:.0f} Hz",
                  delta="= fs / 2", delta_color="off",
                  help="Highest frequency representable at this sampling rate.")

    st.markdown(f"""
    <div class="formula-row">
        <span class="fchip">f_alias = |{f} − {k}×{fs}| = {f_alias:.2f} Hz</span>
        <span class="fchip">Nyquist = 2 × {f} = {nyquist_rate:.0f} Hz</span>
        <span class="fchip">fs / Nyquist = {ratio:.3f}×</span>
        <span class="fchip">Max freq = fs/2 = {fs/2:.0f} Hz</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  INTELLIGENT ANALYSIS CALLOUT — mode-aware
# ─────────────────────────────────────────────────────────────────────────────

def render_analysis_callout(
    f: float, fs: float, f_alias: float,
    aliasing: bool, mode: str,
) -> None:
    """
    Real-time analysis sentence — changes meaning based on active mode.
    Audio / Camera / Sensor / Basic each get distinct, relevant text.
    """
    ratio      = fs / (2 * f)
    freq_error = round(abs(100 * (f_alias - f) / f), 1) if f > 0 else 0

    # Mode-specific context phrase
    mode_context = {
        "📻 Basic":    f"sampling a {f} Hz sine wave",
        "🎵 Audio":    f"digitising a {f} Hz audio tone (e.g. a musical note)",
        "📷 Camera":   f"capturing a {f} Hz repeating visual pattern (e.g. spinning wheel)",
        "📡 Sensor":   f"reading a {f} Hz vibration signal from an industrial sensor",
    }.get(mode, f"sampling a {f} Hz signal")

    mode_consequence = {
        "📻 Basic":  "the reconstructed signal will have the wrong frequency.",
        "🎵 Audio":  "you will hear a distorted phantom tone instead of the original note.",
        "📷 Camera": "the motion will appear frozen or reversed (wagon-wheel effect).",
        "📡 Sensor": "the sensor will log a false reading — fault detection will fail.",
    }.get(mode, "the signal cannot be faithfully reconstructed.")

    if aliasing:
        msg = (
            f"**⚠️ Aliasing Active [{mode}]:** While {mode_context}, "
            f"fs = {fs} Hz is only {ratio:.2f}× the Nyquist rate. "
            f"The {f} Hz signal appears as **{f_alias:.2f} Hz** — "
            f"{mode_consequence} "
            f"Raise fs above **{2*f} Hz** to fix this."
        )
        st.warning(msg)
    elif f_alias < 1.0:
        msg = (
            f"**✅ Clean Sampling [{mode}]:** While {mode_context}, "
            f"fs = {fs} Hz is {ratio:.2f}× the Nyquist rate. "
            f"Zero aliasing. Full bandwidth up to **{fs//2} Hz** is preserved."
        )
        st.success(msg)
    else:
        msg = (
            f"**✅ Nyquist Satisfied [{mode}]:** While {mode_context}, "
            f"fs = {fs} Hz ({ratio:.2f}× Nyquist). "
            f"Alias at {f_alias:.2f} Hz is within the representable band — signal is recoverable."
        )
        st.info(msg)


# ─────────────────────────────────────────────────────────────────────────────
#  REAL-WORLD INSIGHT PANEL
# ─────────────────────────────────────────────────────────────────────────────

def render_rw_explanation(content: ModeContent, mode: str) -> None:
    """
    Mode-specific real-world insight.
    Gradient header (HTML) + body (HTML, single call, no open/close split).
    Content changes dynamically based on mode selection.
    """
    st.markdown(f"""
    <div class="insight-header">
        <span style="font-size:1.5rem;">{content.icon}</span>
        <div>
            <h3>{content.title}</h3>
            <p>Mode: {mode} &nbsp;·&nbsp; Real-World Application</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    bullets = "".join(f"<li>{pt}</li>" for pt in content.bullet_points)
    st.markdown(f"""
    <div class="insight-body">
        <p>{content.context}</p>
        <ul>{bullets}</ul>
        <div class="formula-row" style="margin-bottom:0.75rem;">
            <span class="fchip">{content.formula}</span>
        </div>
        <div class="insight-example">{content.real_example}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  AI RECOMMENDER PANEL
# ─────────────────────────────────────────────────────────────────────────────

def render_ai_recommender(rec_data: dict) -> None:
    """
    Renders the AI-based sampling rate recommendation panel.
    """
    status = rec_data.get("status", "neutral")
    rec_fs = rec_data.get("recommended_fs", 0)
    explanation = rec_data.get("explanation", "")
    confidence = rec_data.get("confidence", "Medium")

    if status == "danger":
        color = "#E74C3C"
        bg = "#FDEDEC"
        icon = "🚨"
    elif status == "warning":
        color = "#F39C12"
        bg = "#FEF9E7"
        icon = "💡"
    elif status == "success":
        color = "#27AE60"
        bg = "#EAFAF1"
        icon = "✨"
    else:
        color = "#2E86C1"
        bg = "#EBF5FB"
        icon = "🤖"

    st.markdown(f"""
    <div style="background:{bg};border-left:4px solid {color};
                border-radius:8px;padding:1rem;margin-top:1rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <span style="font-weight:700;color:{color};font-size:1rem;">
                {icon} AI Recommendation: set fs ≥ {rec_fs} Hz
            </span>
            <span style="font-size:0.75rem;padding:0.2rem 0.5rem;background:white;
                         border:1px solid {color}44;border-radius:4px;color:{color};">
                Confidence: {confidence}
            </span>
        </div>
        <div style="color:#2D3748;font-size:0.9rem;line-height:1.4;">
            {explanation}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  STRONG ALIASING ALERT
# ─────────────────────────────────────────────────────────────────────────────

def render_aliasing_alert(f: float, fs: float) -> None:
    """Strong visual alert for aliasing status."""
    ratio = fs / (2 * f) if f > 0 else 2.0
    
    if ratio < 1.0:
        color = "#FFFFFF"
        bg = "#E74C3C" # Red
        icon = "🚨"
        title = "CRITICAL: ALIASING DETECTED"
        msg = f"Sampling rate (fs={fs}Hz) is below the Nyquist limit (2f={2*f}Hz). Original signal is irreversibly distorted."
    elif ratio < 1.05:
        color = "#1A252F"
        bg = "#F1C40F" # Yellow
        icon = "⚠️"
        title = "WARNING: NYQUIST EDGE"
        msg = f"Sampling rate (fs={fs}Hz) is dangerously close to the Nyquist limit. Minimal safety margin against noise."
    else:
        color = "#FFFFFF"
        bg = "#27AE60" # Green
        icon = "✅"
        title = "SAFE: OPTIMAL SAMPLING"
        msg = f"Sampling rate (fs={fs}Hz) safely exceeds the Nyquist limit. Signal fidelity is preserved."

    st.markdown(f"""
    <div style="background:{bg}; color:{color}; text-align:center; padding:0.6rem 1rem; border-radius:8px; margin: 0.5rem 0 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h4 style="margin:0; font-size:1rem; font-weight:700; letter-spacing:0.02em; color:{color};">{icon} {title}</h4>
        <p style="margin:0.2rem 0 0; font-size:0.85rem; font-weight:500;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────

def render_footer() -> None:
    st.markdown("""
    <div class="waveiq-footer">
        WaveIQ &nbsp;·&nbsp; Intelligent Signal Sampling &amp; Aliasing Analyzer
        &nbsp;·&nbsp; Nyquist-Shannon Theorem
        &nbsp;·&nbsp; Streamlit &amp; Plotly
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SAMPLING REGIME PANEL  (Gap 1)
# ─────────────────────────────────────────────────────────────────────────────

def render_regime_panel(regime: dict) -> None:
    """
    Displays the current sampling regime clearly:
    Under-Sampling | Nyquist Sampling | Over-Sampling
    with color coding and description.
    """
    color  = regime["color"]
    bg     = regime["bg"]
    label  = regime["label"]
    ratio  = regime["ratio"]
    desc   = regime["description"]

    # Three regime cards always visible
    c1, c2, c3 = st.columns(3)
    regime_name = regime["regime"]

    for col, (name, display, clr, bkg) in zip(
        [c1, c2, c3],
        [
            ("under",   "① Under-Sampling\nfs < 2f",    "#E74C3C", "#FDEDEC"),
            ("nyquist", "② Nyquist Sampling\nfs ≈ 2f",  "#F39C12", "#FEF9E7"),
            ("over",    "③ Over-Sampling\nfs > 2f",     "#27AE60", "#EAFAF1"),
        ],
    ):
        is_active = (name == regime_name) or \
                    (name == "over" and regime_name == "over")
        border = f"3px solid {clr}" if is_active else f"1px solid {clr}44"
        opacity = "1" if is_active else "0.45"
        st.markdown(f"""
        <div style="background:{bkg};border:{border};border-radius:10px;
                    padding:0.8rem 1rem;text-align:center;opacity:{opacity};
                    transition:all 0.2s;">
            <div style="font-size:0.75rem;font-weight:700;color:{clr};
                        white-space:pre-line;line-height:1.5;">
                {display}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Active regime description
    st.markdown(f"""
    <div style="background:{bg};border-left:4px solid {color};
                border-radius:8px;padding:0.75rem 1rem;margin-top:0.6rem;">
        <span style="font-weight:700;color:{color};font-size:0.88rem;">
            {label}
        </span>
        <span style="color:#2D3748;font-size:0.84rem;margin-left:0.5rem;">
            — {desc}
        </span>
        <span style="font-family:'IBM Plex Mono',monospace;
                     font-size:0.78rem;color:{color};margin-left:0.5rem;">
            (fs/Nyquist = {ratio:.3f}×)
        </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  REGIME SUMMARY TABLE  (Gap 4)
# ─────────────────────────────────────────────────────────────────────────────

def render_regime_table(f: float, fs: float) -> None:
    """
    Clean summary table comparing all three sampling regimes
    for the current signal frequency f.
    """
    nyq = 2 * f
    rows = [
        ("Under-Sampling",   f"fs < {nyq:.0f} Hz",      "fs < 2f",  "Aliasing — info lost",       "❌", "#FDEDEC", "#E74C3C"),
        ("Nyquist Sampling", f"fs = {nyq:.0f} Hz",      "fs = 2f",  "Marginal — noise risk",      "⚠️", "#FEF9E7", "#F39C12"),
        ("Over-Sampling",    f"fs > {nyq:.0f} Hz",      "fs > 2f",  "Safe — perfect recovery",    "✅", "#EAFAF1", "#27AE60"),
    ]
    current_fs_label = f"Your fs = {fs} Hz"

    header = (
        '<div style="overflow-x:auto;margin-top:0.5rem;">'
        '<table style="width:100%;border-collapse:collapse;font-size:0.82rem;">'
        '<thead><tr style="background:#2E86C1;color:white;">'
        '<th style="padding:0.5rem 0.8rem;text-align:left;">Regime</th>'
        '<th style="padding:0.5rem 0.8rem;text-align:center;">fs Range</th>'
        '<th style="padding:0.5rem 0.8rem;text-align:center;">Condition</th>'
        '<th style="padding:0.5rem 0.8rem;text-align:center;">Result</th>'
        '<th style="padding:0.5rem 0.8rem;text-align:center;">Status</th>'
        '</tr></thead><tbody>'
    )

    body = ""
    for name, fs_range, condition, result, status, bg, clr in rows:
        # Highlight the current regime row
        is_current = (
            (name == "Under-Sampling"   and fs < nyq) or
            (name == "Nyquist Sampling" and abs(fs - nyq) / nyq < 0.05) or
            (name == "Over-Sampling"    and fs >= nyq * 1.05)
        )
        row_style = (
            f"background:{bg};font-weight:700;border-left:4px solid {clr};"
            if is_current else f"background:#fff;"
        )
        body += (
            f'<tr style="{row_style}border-bottom:1px solid #E2E8F0;">'
            f'<td style="padding:0.45rem 0.8rem;color:{clr};font-weight:600;">'
            f'  {name}'
            f'  {"← " + current_fs_label if is_current else ""}'
            f'</td>'
            f'<td style="padding:0.45rem 0.8rem;text-align:center;'
            f'font-family:IBM Plex Mono,monospace;font-size:0.78rem;">{fs_range}</td>'
            f'<td style="padding:0.45rem 0.8rem;text-align:center;'
            f'font-family:IBM Plex Mono,monospace;font-size:0.78rem;">{condition}</td>'
            f'<td style="padding:0.45rem 0.8rem;text-align:center;color:#4A5568;">{result}</td>'
            f'<td style="padding:0.45rem 0.8rem;text-align:center;font-size:1rem;">{status}</td>'
            f'</tr>'
        )

    footer = '</tbody></table></div>'
    st.markdown(header + body + footer, unsafe_allow_html=True)