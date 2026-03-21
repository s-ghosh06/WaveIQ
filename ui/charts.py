"""
ui/charts.py
────────────
WaveIQ — all Plotly figure builders.
Each function takes pure numpy data and returns a go.Figure.
No Streamlit calls here — all rendering happens in ui/layout.py.
"""

import numpy as np
import plotly.graph_objects as go

from utils.constants import COLORS, PLOTLY_BASE_LAYOUT, PLOTLY_AXIS_DEFAULTS, CHART_HEIGHT


# ─────────────────────────────────────────────────────────────────────────────
#  LAYOUT HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _layout(**overrides) -> dict:
    """Merge shared Plotly layout with per-chart overrides."""
    base = {**PLOTLY_BASE_LAYOUT}
    base["xaxis"] = {**PLOTLY_AXIS_DEFAULTS}
    base["yaxis"] = {**PLOTLY_AXIS_DEFAULTS}
    base.update(overrides)
    return base


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 1 — TIME DOMAIN  (original + sampled)
# ─────────────────────────────────────────────────────────────────────────────

def chart_time_domain(
    t_cont: np.ndarray, x_cont: np.ndarray,
    t_samp: np.ndarray, x_samp: np.ndarray,
    f: float, fs: float,
) -> go.Figure:
    """
    Time-domain: smooth continuous signal + lollipop sample markers.
    """
    fig = go.Figure()

    # Continuous original
    fig.add_trace(go.Scatter(
        x=t_cont * 1000, y=x_cont,
        mode="lines",
        name=f"Original  {f} Hz",
        line=dict(color=COLORS["original"], width=2.5),
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Original</extra>",
    ))

    # Sample markers
    fig.add_trace(go.Scatter(
        x=t_samp * 1000, y=x_samp,
        mode="markers",
        name=f"Samples  fs = {fs} Hz",
        marker=dict(
            color=COLORS["sampled"], size=8, symbol="circle",
            line=dict(color="white", width=1.5),
        ),
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Sample</extra>",
    ))

    # Stems (lollipop lines)
    for tx, sx in zip(t_samp * 1000, x_samp):
        fig.add_shape(
            type="line", x0=tx, x1=tx, y0=0, y1=sx,
            line=dict(color=COLORS["sampled"], width=1, dash="dot"),
        )

    fig.update_layout(**_layout(
        title=dict(text="⏱  Time Domain — Original Signal + Sample Points",
                   font=dict(size=13, color="#1A202C")),
        xaxis_title="Time (ms)",
        yaxis_title="Amplitude",
        height=CHART_HEIGHT["time_domain"],
    ))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 2 — ALIASED SIGNAL
# ─────────────────────────────────────────────────────────────────────────────

def chart_aliased_signal(
    t_cont: np.ndarray, x_cont: np.ndarray,
    t_alias: np.ndarray, x_alias: np.ndarray,
    f: float, f_alias: float,
) -> go.Figure:
    """
    Aliased reconstruction overlaid on faded original reference.
    """
    fig = go.Figure()

    # Original — faded reference
    fig.add_trace(go.Scatter(
        x=t_cont * 1000, y=x_cont,
        mode="lines",
        name=f"Original  {f} Hz  (ref)",
        line=dict(color=COLORS["original"], width=1.5, dash="dot"),
        opacity=0.30,
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Original (ref)</extra>",
    ))

    # Aliased signal
    fig.add_trace(go.Scatter(
        x=t_alias * 1000, y=x_alias,
        mode="lines",
        name=f"Aliased  {f_alias:.2f} Hz",
        line=dict(color=COLORS["aliased"], width=2.8),
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Aliased</extra>",
    ))

    fig.update_layout(**_layout(
        title=dict(text="👻  Aliased Signal Reconstruction",
                   font=dict(size=13, color="#1A202C")),
        xaxis_title="Time (ms)",
        yaxis_title="Amplitude",
        height=CHART_HEIGHT["aliased"],
    ))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 3 — RECONSTRUCTION ERROR
# ─────────────────────────────────────────────────────────────────────────────

def chart_difference(
    t_diff: np.ndarray,
    x_diff: np.ndarray,
    rms:    float,
) -> go.Figure:
    """
    Filled error signal with RMS annotation box.
    """
    fig = go.Figure()

    fig.add_hline(y=0, line=dict(color="#CBD5E0", width=1.5))

    fig.add_trace(go.Scatter(
        x=t_diff * 1000, y=x_diff,
        mode="lines",
        name="Error",
        line=dict(color=COLORS["difference"], width=2),
        fill="tozeroy",
        fillcolor="rgba(142,68,173,0.08)",
        hovertemplate="t = %{x:.3f} ms<br>Err = %{y:.4f}<extra>Error</extra>",
    ))

    peak = float(np.max(np.abs(x_diff))) if len(x_diff) > 0 else 1.0
    fig.add_annotation(
        x=float(np.max(t_diff * 1000)) * 0.76,
        y=peak * 0.84,
        text=f"RMS Error: {rms:.4f}",
        showarrow=False,
        font=dict(size=12, color=COLORS["difference"], family="IBM Plex Mono"),
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor=COLORS["difference"],
        borderwidth=1.5,
        borderpad=7,
    )

    fig.update_layout(**_layout(
        title=dict(text="📉  Reconstruction Error  (Original − Aliased)",
                   font=dict(size=13, color="#1A202C")),
        xaxis_title="Time (ms)",
        yaxis_title="Error",
        height=CHART_HEIGHT["difference"],
    ))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 4 — FFT SPECTRUM
# ─────────────────────────────────────────────────────────────────────────────

def chart_fft_spectrum(
    freqs_orig: np.ndarray, mags_orig: np.ndarray,
    freqs_alias: np.ndarray, mags_alias: np.ndarray,
    f: float, f_alias: float, fs: float,
) -> go.Figure:
    """
    Dual FFT spectra with Nyquist frequency and signal frequency markers.
    """
    fig = go.Figure()

    # Original spectrum
    fig.add_trace(go.Scatter(
        x=freqs_orig, y=mags_orig,
        mode="lines",
        name="Original spectrum",
        line=dict(color=COLORS["spectrum_orig"], width=2),
        fill="tozeroy",
        fillcolor="rgba(46,134,193,0.10)",
        hovertemplate="f = %{x:.1f} Hz<br>Mag = %{y:.4f}<extra>Original</extra>",
    ))

    # Aliased spectrum
    fig.add_trace(go.Scatter(
        x=freqs_alias, y=mags_alias,
        mode="lines",
        name="Aliased spectrum",
        line=dict(color=COLORS["spectrum_alias"], width=2, dash="dash"),
        fill="tozeroy",
        fillcolor="rgba(243,156,18,0.08)",
        hovertemplate="f = %{x:.1f} Hz<br>Mag = %{y:.4f}<extra>Aliased</extra>",
    ))

    # Nyquist frequency line
    nyq = fs / 2
    fig.add_vline(
        x=nyq,
        line=dict(color=COLORS["nyquist"], width=2, dash="dot"),
        annotation_text=f"Nyquist  {nyq:.0f} Hz",
        annotation_position="top right",
        annotation_font=dict(size=11, color=COLORS["nyquist"]),
    )

    # Signal frequency marker
    fig.add_vline(
        x=f,
        line=dict(color=COLORS["original"], width=1.5, dash="dash"),
        annotation_text=f"f = {f} Hz",
        annotation_position="top left",
        annotation_font=dict(size=11, color=COLORS["original"]),
    )

    display_max = max(fs * 0.75, f * 2.5, 200)
    layout = _layout(
        title=dict(text="📊  Frequency Spectrum — FFT Analysis",
                   font=dict(size=13, color="#1A202C")),
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        height=CHART_HEIGHT["fft"],
    )
    layout["xaxis"]["range"] = [0, display_max]
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 5 — NYQUIST RATIO GAUGE
# ─────────────────────────────────────────────────────────────────────────────

def chart_nyquist_gauge(f: float, fs: float) -> go.Figure:
    """
    Gauge showing fs / Nyquist Rate ratio.
    Red zone < 1×, yellow 1–2×, green 2–4×.
    """
    nyquist_rate = 2 * f
    ratio        = fs / nyquist_rate
    bar_color    = COLORS["success"] if ratio >= 1.0 else COLORS["danger"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(ratio, 3),
        delta={
            "reference": 1.0,
            "increasing": {"color": COLORS["success"]},
            "decreasing": {"color": COLORS["danger"]},
        },
        title={"text": "fs / Nyquist Rate", "font": {"size": 13}},
        number={"suffix": "×", "font": {"size": 22, "family": "IBM Plex Mono"}},
        gauge={
            "axis": {"range": [0, 4], "tickwidth": 1, "tickfont": {"size": 10}},
            "bar":  {"color": bar_color, "thickness": 0.28},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "#E2E8F0",
            "steps": [
                {"range": [0, 1], "color": "rgba(231,76,60,0.15)"},
                {"range": [1, 2], "color": "rgba(243,156,18,0.12)"},
                {"range": [2, 4], "color": "rgba(39,174,96,0.10)"},
            ],
            "threshold": {
                "line": {"color": COLORS["nyquist"], "width": 3},
                "thickness": 0.8,
                "value": 2,
            },
        },
    ))

    fig.update_layout(
        paper_bgcolor="white",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#1A202C"),
        margin=dict(l=20, r=20, t=40, b=20),
        height=CHART_HEIGHT["gauge"],
    )
    return fig