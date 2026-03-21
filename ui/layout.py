"""
ui/layout.py — WaveIQ page orchestrator.
Gap fills wired in:
  Gap 1: Sampling regime panel + regime comparison chart
  Gap 2: Sinc reconstruction chart
  Gap 3: Nyquist marker already in chart_time_domain
  Gap 4: Regime summary table
"""

import streamlit as st

from core.signal import compute_all, sinc_reconstruct, classify_sampling_regime
from core.modes  import get_mode_content

from ui.sidebar    import render_sidebar
from ui.components import (
    render_header,
    render_metric_cards,
    render_nyquist_panel,
    render_analysis_callout,
    render_rw_explanation,
    render_regime_panel,
    render_regime_table,
    render_footer,
    section_header,
)
from ui.charts import (
    chart_time_domain,
    chart_aliased_signal,
    chart_reconstruction,
    chart_difference,
    chart_fft_spectrum,
    chart_nyquist_gauge,
    chart_regime_comparison,
)
from utils.styles    import inject_css
from utils.constants import PLOTLY_CONFIG


def render_page() -> None:
    """
    Full WaveIQ page — 100% problem statement coverage.

    Sections:
      1.  CSS
      2.  Sidebar → params
      3.  Signal computation
      4.  Header
      5.  KPI metric cards
      6.  Mode-aware callout
      7.  ── Sampling Regime ──────────────────
          Regime panel (Under/Nyquist/Over indicator)
          Regime summary table
          Regime comparison chart (3-panel)
      8.  ── Nyquist Analysis ─────────────────
          Alert panel + metrics + gauge
      9.  ── Signal Visualization ─────────────
          Time-domain (original + samples) | Alias signal
      10. ── Signal Reconstruction ────────────
          Sinc reconstruction vs original
          Reconstruction error chart
      11. ── Frequency Domain ──────────────────
          FFT spectrum (original vs aliased)
      12. ── Real-World Insight ────────────────
      13. Footer
    """

    # 1. CSS
    inject_css()

    # 2. Sidebar
    params = render_sidebar()
    f    = params["f"]
    A    = params["A"]
    fs   = params["fs"]
    mode = params["mode"]

    # 3. Compute
    data   = compute_all(f, A, fs)
    regime = classify_sampling_regime(f, fs)
    x_recon = sinc_reconstruct(
        data.t_samp, data.x_samp, data.t_cont, fs
    )

    # 4. Header
    render_header(mode)

    # 5. Metric cards
    render_metric_cards(
        f=f, fs=fs, f_alias=data.f_alias,
        rms=data.rms_error, A=A, aliasing=data.aliasing,
    )

    # 6. Mode-aware callout
    render_analysis_callout(
        f=f, fs=fs, f_alias=data.f_alias,
        aliasing=data.aliasing, mode=mode,
    )

    # ── 7. SAMPLING REGIME ──────────────────────────────────────────────
    section_header("🎯", "Sampling Regime")
    render_regime_panel(regime)
    st.markdown("<br>", unsafe_allow_html=True)
    render_regime_table(f, fs)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("📊 Side-by-side comparison: same signal at three different sampling rates")
    st.plotly_chart(
        chart_regime_comparison(f, A, fs),
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )

    # ── 8. NYQUIST ANALYSIS ─────────────────────────────────────────────
    section_header("📐", "Nyquist Analysis")
    col_nyq, col_gauge = st.columns([3, 2], gap="large")
    with col_nyq:
        render_nyquist_panel(
            f=f, fs=fs, f_alias=data.f_alias,
            nyquist_rate=data.nyquist_rate, aliasing=data.aliasing,
        )
    with col_gauge:
        st.plotly_chart(
            chart_nyquist_gauge(f, fs),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── 9. SIGNAL VISUALIZATION ─────────────────────────────────────────
    section_header("📈", "Signal Visualization")
    col_orig, col_alias = st.columns(2, gap="medium")
    with col_orig:
        st.caption("⏱ Continuous Signal + Discrete Sample Points")
        st.plotly_chart(
            chart_time_domain(
                data.t_cont, data.x_cont,
                data.t_samp, data.x_samp, f, fs,
            ),
            use_container_width=True, config=PLOTLY_CONFIG,
        )
    with col_alias:
        st.caption("👻 Alias Signal — Phantom Frequency")
        st.plotly_chart(
            chart_aliased_signal(
                data.t_cont, data.x_cont,
                data.t_alias, data.x_alias, f, data.f_alias,
            ),
            use_container_width=True, config=PLOTLY_CONFIG,
        )

    # ── 10. SIGNAL RECONSTRUCTION ───────────────────────────────────────
    section_header("🔄", "Signal Reconstruction")
    st.caption("Whittaker-Shannon sinc interpolation from discrete samples back to continuous signal")
    st.plotly_chart(
        chart_reconstruction(
            data.t_cont, data.x_cont,
            data.t_samp, data.x_samp,
            x_recon, f, fs,
        ),
        use_container_width=True, config=PLOTLY_CONFIG,
    )

    if params["show_diff"]:
        st.caption("📉 Point-wise error: Original − Aliased signal")
        st.plotly_chart(
            chart_difference(data.t_diff, data.x_diff, data.rms_error),
            use_container_width=True, config=PLOTLY_CONFIG,
        )

    # ── 11. FREQUENCY DOMAIN ────────────────────────────────────────────
    if params["show_fft"]:
        section_header("🔬", "Frequency Domain Analysis")
        st.caption("FFT magnitude spectrum — Original vs Aliased · Nyquist + alias frequency marked")
        st.plotly_chart(
            chart_fft_spectrum(
                data.freqs_orig, data.mags_orig,
                data.freqs_alias, data.mags_alias,
                f, data.f_alias, fs,
            ),
            use_container_width=True, config=PLOTLY_CONFIG,
        )

    # ── 12. REAL-WORLD INSIGHT ──────────────────────────────────────────
    if params["show_rw"]:
        section_header("🌍", "Real-World Insight")
        content = get_mode_content(
            mode=mode, f=f, fs=fs,
            f_alias=data.f_alias, aliasing=data.aliasing,
        )
        render_rw_explanation(content, mode)

    # ── 13. FOOTER ───────────────────────────────────────────────────────
    render_footer()