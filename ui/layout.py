"""
ui/layout.py
────────────
WaveIQ page orchestrator — fixes:
  1. Real-world insight always shown (not gated by show_rw checkbox)
  2. Error signal and FFT always shown (Display Options removed from sidebar)
  3. Mode content passes through correctly to all mode-aware components
  4. Clean render order, no unclosed HTML
"""

import streamlit as st

from core.signal import compute_all
from core.modes  import get_mode_content

from ui.sidebar    import render_sidebar
from ui.components import (
    render_header,
    render_metric_cards,
    render_nyquist_panel,
    render_analysis_callout,
    render_rw_explanation,
    render_footer,
    section_header,
)
from ui.charts import (
    chart_time_domain,
    chart_aliased_signal,
    chart_difference,
    chart_fft_spectrum,
    chart_nyquist_gauge,
)
from utils.styles    import inject_css
from utils.constants import PLOTLY_CONFIG


def render_page() -> None:
    """
    Full WaveIQ page render — one call per Streamlit rerun.

    Order:
      1.  CSS
      2.  Sidebar → params
      3.  Signal computation
      4.  Header (left title / right mode pill)
      5.  KPI metric cards
      6.  Mode-aware intelligent analysis callout
      7.  Nyquist Analysis (alert + metrics + gauge)
      8.  Signal Visualization (time-domain | aliased)
      9.  Reconstruction Error
      10. Frequency Domain (FFT)
      11. Real-World Insight (mode-specific, always shown)
      12. Footer
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
    data = compute_all(f, A, fs)

    # 4. Header
    render_header(mode)

    # 5. Metric cards
    render_metric_cards(
        f=f, fs=fs, f_alias=data.f_alias,
        rms=data.rms_error, A=A, aliasing=data.aliasing,
    )

    # 6. Mode-aware intelligent callout
    render_analysis_callout(
        f=f, fs=fs, f_alias=data.f_alias,
        aliasing=data.aliasing, mode=mode,
    )

    # 7. Nyquist Analysis
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

    # 8. Signal Visualization
    section_header("📈", "Signal Visualization")
    col_orig, col_alias = st.columns(2, gap="medium")
    with col_orig:
        st.caption("⏱ Original Signal + Sample Points")
        st.plotly_chart(
            chart_time_domain(
                data.t_cont, data.x_cont,
                data.t_samp, data.x_samp, f, fs,
            ),
            use_container_width=True, config=PLOTLY_CONFIG,
        )
    with col_alias:
        st.caption("👻 Aliased Signal Reconstruction")
        st.plotly_chart(
            chart_aliased_signal(
                data.t_cont, data.x_cont,
                data.t_alias, data.x_alias, f, data.f_alias,
            ),
            use_container_width=True, config=PLOTLY_CONFIG,
        )

    # 9. Reconstruction Error
    section_header("📉", "Reconstruction Error")
    st.caption("Point-wise difference: Original − Aliased signal")
    st.plotly_chart(
        chart_difference(data.t_diff, data.x_diff, data.rms_error),
        use_container_width=True, config=PLOTLY_CONFIG,
    )

    # 10. FFT Spectrum
    section_header("🔬", "Frequency Domain Analysis")
    st.caption("FFT magnitude spectrum — Original vs Aliased · Nyquist boundary marked")
    st.plotly_chart(
        chart_fft_spectrum(
            data.freqs_orig, data.mags_orig,
            data.freqs_alias, data.mags_alias,
            f, data.f_alias, fs,
        ),
        use_container_width=True, config=PLOTLY_CONFIG,
    )

    # 11. Real-World Insight — always shown, mode-specific content
    section_header("🌍", "Real-World Insight")
    content = get_mode_content(
        mode=mode, f=f, fs=fs,
        f_alias=data.f_alias, aliasing=data.aliasing,
    )
    render_rw_explanation(content, mode)

    # 12. Footer
    render_footer()