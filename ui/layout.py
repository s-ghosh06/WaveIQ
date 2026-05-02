"""
ui/layout.py — WaveIQ page orchestrator.
Gap fills wired in:
  Gap 1: Sampling regime panel + regime comparison chart
  Gap 2: Sinc reconstruction chart
  Gap 3: Nyquist marker already in chart_time_domain
  Gap 4: Regime summary table
"""

import streamlit as st
import numpy as np

from core.signal import compute_all, sinc_reconstruct, classify_sampling_regime
from core.modes  import get_mode_content
from core.recommender import get_recommendation

from ui.sidebar    import render_sidebar
from ui.components import (
    render_header,
    render_metric_cards,
    render_aliasing_alert,
    render_nyquist_panel,
    render_ai_recommender,
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
    snr_db = params.get("snr_db", 100.0)
    apply_filter = params.get("apply_filter", False)
    audio_data = params.get("audio_data")
    audio_fs = params.get("audio_fs")
    signal_type = params.get("signal_type", "Sine")

    # 3. Compute
    data   = compute_all(
        f=f, A=A, fs=fs, 
        snr_db=snr_db, apply_filter=apply_filter,
        audio_data=audio_data, audio_fs=audio_fs,
        signal_type=signal_type
    )
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
    
    # 5.5 Strong Aliasing Alert
    render_aliasing_alert(f, fs)

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
        
    # AI Recommendation Panel
    rec_data = get_recommendation(f, fs, data.f_alias, mode, data.aliasing)
    render_ai_recommender(rec_data)

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

    # ── 9.5 AUDIO PLAYBACK ──────────────────────────────────────────────
    section_header("🔊", "Audio Playback")
    col_play1, col_play2 = st.columns(2, gap="medium")
    
    # Calculate continuous sampling rate used for original signal
    if audio_data is not None and audio_fs is not None:
        duration = len(audio_data) / audio_fs
    else:
        duration = max(0.05, 5.0 / f)
    fs_cont = len(data.x_cont) / duration

    with col_play1:
        st.caption("▶ Play Original Signal")
        if len(data.x_cont) > 0:
            sig_orig = data.x_cont / np.max(np.abs(data.x_cont)) if np.max(np.abs(data.x_cont)) > 0 else data.x_cont
            st.audio(sig_orig.astype(np.float32), sample_rate=int(fs_cont))
        else:
            st.warning("Signal empty")
            
    with col_play2:
        st.caption("▶ Play Reconstructed (Sampled) Signal")
        if len(data.x_alias) > 0:
            sig_alias = data.x_alias / np.max(np.abs(data.x_alias)) if np.max(np.abs(data.x_alias)) > 0 else data.x_alias
            st.audio(sig_alias.astype(np.float32), sample_rate=int(fs_cont))
        else:
            st.warning("Signal empty")

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