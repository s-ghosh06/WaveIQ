"""
ui/charts.py
────────────
WaveIQ — all Plotly figure builders.
Gap fills:
  - chart_time_domain: adds Nyquist rate annotation + sampling period marker
  - chart_reconstruction: NEW — shows sinc-interpolated reconstruction
  - chart_aliased_signal: renamed title to be accurate
  - chart_regime_comparison: NEW — 3-panel under/nyquist/over comparison
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.constants import COLORS, PLOTLY_BASE_LAYOUT, PLOTLY_AXIS_DEFAULTS, CHART_HEIGHT


# ─────────────────────────────────────────────────────────────────────────────
#  LAYOUT HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _layout(**overrides) -> dict:
    base = {**PLOTLY_BASE_LAYOUT}
    base["xaxis"] = {**PLOTLY_AXIS_DEFAULTS}
    base["yaxis"] = {**PLOTLY_AXIS_DEFAULTS}
    base.update(overrides)
    return base


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 1 — TIME DOMAIN  (Gap 3: + Nyquist rate marker)
# ─────────────────────────────────────────────────────────────────────────────

def chart_time_domain(
    t_cont: np.ndarray, x_cont: np.ndarray,
    t_samp: np.ndarray, x_samp: np.ndarray,
    f: float, fs: float,
) -> go.Figure:
    """
    Time-domain: smooth continuous signal + lollipop sample markers.
    Now includes: sampling period annotation + regime label.
    """
    fig = go.Figure()

    nyquist_rate = 2 * f
    regime_color = "#E74C3C" if fs < nyquist_rate else "#27AE60"
    regime_label = "UNDER-SAMPLING" if fs < nyquist_rate else "PROPER SAMPLING"

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

    # Sampling period annotation — show Ts
    Ts_ms = 1000.0 / fs
    if len(t_samp) >= 2:
        tx0, tx1 = t_samp[0] * 1000, t_samp[1] * 1000
        fig.add_annotation(
            x=(tx0 + tx1) / 2, y=float(np.max(np.abs(x_cont))) * 1.15,
            text=f"Ts = {Ts_ms:.2f} ms",
            showarrow=False,
            font=dict(size=10, color=COLORS["sampled"], family="IBM Plex Mono"),
            bgcolor="rgba(255,255,255,0.85)",
        )

    # Regime label
    fig.add_annotation(
        xref="paper", yref="paper", x=0.01, y=0.97,
        text=f"◉ {regime_label}",
        showarrow=False,
        font=dict(size=10, color=regime_color, family="IBM Plex Mono"),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=regime_color, borderwidth=1.2, borderpad=4,
    )

    fig.update_layout(**_layout(
        title=dict(
            text=f"⏱  Time Domain — Original Signal + Discrete Samples  (fs = {fs} Hz)",
            font=dict(size=13, color="#1A202C"),
        ),
        xaxis_title="Time (ms)",
        yaxis_title="Amplitude",
        height=CHART_HEIGHT["time_domain"],
    ))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 2 — ALIASED SIGNAL  (accurately titled)
# ─────────────────────────────────────────────────────────────────────────────

def chart_aliased_signal(
    t_cont: np.ndarray, x_cont: np.ndarray,
    t_alias: np.ndarray, x_alias: np.ndarray,
    f: float, f_alias: float,
) -> go.Figure:
    """
    Aliased signal overlaid on faded original — shows the phantom frequency.
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
        name=f"Alias  {f_alias:.2f} Hz",
        line=dict(color=COLORS["aliased"], width=2.8),
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Alias</extra>",
    ))

    # Label the alias
    fig.add_annotation(
        xref="paper", yref="paper", x=0.01, y=0.97,
        text=f"👻 Alias: {f} Hz → {f_alias:.2f} Hz",
        showarrow=False,
        font=dict(size=10, color=COLORS["aliased"], family="IBM Plex Mono"),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=COLORS["aliased"], borderwidth=1.2, borderpad=4,
    )

    fig.update_layout(**_layout(
        title=dict(
            text=f"👻  Alias Signal — {f} Hz appears as {f_alias:.2f} Hz",
            font=dict(size=13, color="#1A202C"),
        ),
        xaxis_title="Time (ms)",
        yaxis_title="Amplitude",
        height=CHART_HEIGHT["aliased"],
    ))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 2b — SINC RECONSTRUCTION  (Gap 2 — new)
# ─────────────────────────────────────────────────────────────────────────────

def chart_reconstruction(
    t_cont:  np.ndarray,
    x_cont:  np.ndarray,
    t_samp:  np.ndarray,
    x_samp:  np.ndarray,
    x_recon: np.ndarray,
    f: float,
    fs: float,
) -> go.Figure:
    """
    Sinc (Whittaker-Shannon) reconstruction vs original.
    Shows how well the signal is recovered from discrete samples.
    """
    fig = go.Figure()

    # Original
    fig.add_trace(go.Scatter(
        x=t_cont * 1000, y=x_cont,
        mode="lines",
        name=f"Original  {f} Hz",
        line=dict(color=COLORS["original"], width=2, dash="dot"),
        opacity=0.5,
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Original</extra>",
    ))

    # Sinc reconstruction
    fig.add_trace(go.Scatter(
        x=t_cont * 1000, y=x_recon,
        mode="lines",
        name="Sinc Reconstruction",
        line=dict(color="#8E44AD", width=2.5),
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Reconstructed</extra>",
    ))

    # Sample markers
    fig.add_trace(go.Scatter(
        x=t_samp * 1000, y=x_samp,
        mode="markers",
        name=f"Samples",
        marker=dict(color=COLORS["sampled"], size=7,
                    line=dict(color="white", width=1.2)),
        hovertemplate="t = %{x:.3f} ms<br>A = %{y:.4f}<extra>Sample</extra>",
    ))

    # Quality annotation
    recon_error = float(np.sqrt(np.mean((x_cont - x_recon) ** 2)))
    quality = "Perfect" if recon_error < 0.05 else "Good" if recon_error < 0.3 else "Poor"
    fig.add_annotation(
        xref="paper", yref="paper", x=0.01, y=0.97,
        text=f"Reconstruction quality: {quality}  (RMS={recon_error:.4f})",
        showarrow=False,
        font=dict(size=10, color="#8E44AD", family="IBM Plex Mono"),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#8E44AD", borderwidth=1.2, borderpad=4,
    )

    fig.update_layout(**_layout(
        title=dict(
            text="🔄  Sinc Reconstruction — Whittaker-Shannon Interpolation",
            font=dict(size=13, color="#1A202C"),
        ),
        xaxis_title="Time (ms)",
        yaxis_title="Amplitude",
        height=CHART_HEIGHT["time_domain"],
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
    """Filled error signal with RMS annotation."""
    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color="#CBD5E0", width=1.5))

    fig.add_trace(go.Scatter(
        x=t_diff * 1000, y=x_diff,
        mode="lines", name="Error",
        line=dict(color=COLORS["difference"], width=2),
        fill="tozeroy", fillcolor="rgba(142,68,173,0.08)",
        hovertemplate="t = %{x:.3f} ms<br>Err = %{y:.4f}<extra>Error</extra>",
    ))

    peak = float(np.max(np.abs(x_diff))) if len(x_diff) > 0 else 1.0
    fig.add_annotation(
        x=float(np.max(t_diff * 1000)) * 0.76, y=peak * 0.84,
        text=f"RMS Error: {rms:.4f}",
        showarrow=False,
        font=dict(size=12, color=COLORS["difference"], family="IBM Plex Mono"),
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor=COLORS["difference"], borderwidth=1.5, borderpad=7,
    )

    fig.update_layout(**_layout(
        title=dict(text="📉  Reconstruction Error  (Original − Aliased)",
                   font=dict(size=13, color="#1A202C")),
        xaxis_title="Time (ms)", yaxis_title="Error",
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
    """Dual FFT spectra with Nyquist and signal frequency markers."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=freqs_orig, y=mags_orig, mode="lines",
        name="Original spectrum",
        line=dict(color=COLORS["spectrum_orig"], width=2),
        fill="tozeroy", fillcolor="rgba(46,134,193,0.10)",
        hovertemplate="f = %{x:.1f} Hz<br>Mag = %{y:.4f}<extra>Original</extra>",
    ))

    fig.add_trace(go.Scatter(
        x=freqs_alias, y=mags_alias, mode="lines",
        name="Aliased spectrum",
        line=dict(color=COLORS["spectrum_alias"], width=2, dash="dash"),
        fill="tozeroy", fillcolor="rgba(243,156,18,0.08)",
        hovertemplate="f = %{x:.1f} Hz<br>Mag = %{y:.4f}<extra>Aliased</extra>",
    ))

    nyq = fs / 2
    fig.add_vline(x=nyq, line=dict(color=COLORS["nyquist"], width=2, dash="dot"),
                  annotation_text=f"Nyquist  {nyq:.0f} Hz",
                  annotation_position="top right",
                  annotation_font=dict(size=11, color=COLORS["nyquist"]))

    fig.add_vline(x=f, line=dict(color=COLORS["original"], width=1.5, dash="dash"),
                  annotation_text=f"f = {f} Hz",
                  annotation_position="top left",
                  annotation_font=dict(size=11, color=COLORS["original"]))

    if f_alias > 1.0 and abs(f_alias - f) > 1.0:
        fig.add_vline(x=f_alias,
                      line=dict(color=COLORS["aliased"], width=1.5, dash="dashdot"),
                      annotation_text=f"alias = {f_alias:.1f} Hz",
                      annotation_position="bottom right",
                      annotation_font=dict(size=10, color=COLORS["aliased"]))

    display_max = max(fs * 0.75, f * 2.5, 200)
    layout = _layout(
        title=dict(text="📊  Frequency Spectrum — FFT Analysis (Original vs Aliased)",
                   font=dict(size=13, color="#1A202C")),
        xaxis_title="Frequency (Hz)", yaxis_title="Magnitude",
        height=CHART_HEIGHT["fft"],
    )
    layout["xaxis"]["range"] = [0, display_max]
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 5 — NYQUIST RATIO GAUGE
# ─────────────────────────────────────────────────────────────────────────────

def chart_nyquist_gauge(f: float, fs: float) -> go.Figure:
    """Gauge showing fs / Nyquist Rate ratio with regime zones."""
    nyquist_rate = 2 * f
    ratio        = fs / nyquist_rate
    bar_color    = COLORS["success"] if ratio >= 1.0 else COLORS["danger"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(ratio, 3),
        delta={"reference": 1.0,
               "increasing": {"color": COLORS["success"]},
               "decreasing": {"color": COLORS["danger"]}},
        title={"text": "fs / Nyquist Rate", "font": {"size": 13}},
        number={"suffix": "×", "font": {"size": 22, "family": "IBM Plex Mono"}},
        gauge={
            "axis": {"range": [0, 4], "tickwidth": 1, "tickfont": {"size": 10}},
            "bar":  {"color": bar_color, "thickness": 0.28},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "#E2E8F0",
            "steps": [
                {"range": [0, 1],   "color": "rgba(231,76,60,0.15)"},
                {"range": [1, 1.1], "color": "rgba(243,156,18,0.25)"},
                {"range": [1.1, 2], "color": "rgba(243,156,18,0.10)"},
                {"range": [2, 4],   "color": "rgba(39,174,96,0.10)"},
            ],
            "threshold": {
                "line": {"color": COLORS["nyquist"], "width": 3},
                "thickness": 0.8, "value": 2,
            },
        },
    ))

    fig.update_layout(
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#1A202C"),
        margin=dict(l=20, r=20, t=40, b=20),
        height=CHART_HEIGHT["gauge"],
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CHART 6 — REGIME COMPARISON  (Gap 4 — new)
# ─────────────────────────────────────────────────────────────────────────────

def chart_regime_comparison(f: float, A: float, fs: float) -> go.Figure:
    """
    Three-panel subplot comparing under-sampling, Nyquist sampling,
    and over-sampling for the same signal frequency.
    Shows continuous signal + samples for each regime side by side.
    """
    duration = max(0.02, 3.0 / f)
    t_cont   = np.linspace(0, duration, 2000)
    x_cont   = A * np.sin(2 * np.pi * f * t_cont)

    regimes = [
        {"label": "Under-Sampling",  "fs": f * 1.2,  "color": "#E74C3C"},
        {"label": "Nyquist Sampling","fs": f * 2.0,  "color": "#F39C12"},
        {"label": "Over-Sampling",   "fs": f * 5.0,  "color": "#27AE60"},
    ]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[
            f"<b>① Under-Sampling</b><br>fs = {f*1.2:.0f} Hz (0.6× Nyquist)",
            f"<b>② Nyquist Sampling</b><br>fs = {f*2.0:.0f} Hz (1.0× Nyquist)",
            f"<b>③ Over-Sampling</b><br>fs = {f*5.0:.0f} Hz (2.5× Nyquist)",
        ],
        horizontal_spacing=0.06,
    )

    for col_idx, regime in enumerate(regimes, start=1):
        fs_r = regime["fs"]
        n_s  = max(2, int(fs_r * duration))
        t_s  = np.linspace(0, duration, n_s)
        x_s  = A * np.sin(2 * np.pi * f * t_s)

        # Continuous reference
        fig.add_trace(go.Scatter(
            x=t_cont * 1000, y=x_cont,
            mode="lines", name="Original" if col_idx == 1 else None,
            showlegend=(col_idx == 1),
            line=dict(color=COLORS["original"], width=2),
            opacity=0.4,
        ), row=1, col=col_idx)

        # Samples + stems
        fig.add_trace(go.Scatter(
            x=t_s * 1000, y=x_s,
            mode="markers",
            name=f"Samples" if col_idx == 1 else None,
            showlegend=(col_idx == 1),
            marker=dict(color=regime["color"], size=7,
                        line=dict(color="white", width=1.2)),
        ), row=1, col=col_idx)

        for tx, sx in zip(t_s * 1000, x_s):
            fig.add_shape(type="line", x0=tx, x1=tx, y0=0, y1=sx,
                          line=dict(color=regime["color"], width=1, dash="dot"),
                          row=1, col=col_idx)

        # Regime annotation
        fig.add_annotation(
            xref=f"x{'' if col_idx==1 else col_idx} domain",
            yref=f"y{'' if col_idx==1 else col_idx} domain",
            x=0.5, y=0.05,
            text=regime["label"],
            showarrow=False,
            font=dict(size=10, color=regime["color"], family="IBM Plex Mono"),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=regime["color"], borderwidth=1, borderpad=3,
        )

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="#F8FAFB",
        font=dict(family="Inter, sans-serif", size=11, color="#1A202C"),
        margin=dict(l=40, r=20, t=80, b=40),
        height=300,
        title=dict(
            text="📊  Sampling Regime Comparison — Under / Nyquist / Over",
            font=dict(size=13, color="#1A202C"),
        ),
        showlegend=False,
    )
    fig.update_xaxes(title_text="Time (ms)", tickfont=dict(size=9),
                     gridcolor="#ECF0F1")
    fig.update_yaxes(title_text="Amplitude", tickfont=dict(size=9),
                     gridcolor="#ECF0F1")
    return fig