"""
ui/sidebar.py — WaveIQ sidebar, all issues fixed at once:
  1. Display Options checkboxes RESTORED and return dict uses their values
  2. Slider ↔ number_input two-way sync via session_state + on_change
  3. Min/max always visible as plain st.markdown text
  4. No scrolling — compact layout
  5. Return dict correctly passes show_diff, show_fft, show_rw from checkboxes
"""

import streamlit as st
from core.modes import ALL_MODES
from utils.constants import SLIDER
from core.audio_pipeline import record_audio, preprocess_audio, extract_dominant_frequency


def _control(key: str, min_val: float, max_val: float,
             step: float, default: float, label: str) -> float:
    """
    Slider + number_input, truly two-way synced via session_state.
    - Slider key = session_state key → Streamlit writes to it automatically
    - number_input on_change callback writes to same session_state key
    - Min/max shown as permanent plain text (not CSS-dependent)
    """
    if key not in st.session_state:
        st.session_state[key] = default

    ni_key = f"__ni_{key}"

    def fmt(v: float) -> str:
        return str(int(v)) if v == int(v) else str(round(v, 2))

    def on_number_change():
        raw = st.session_state.get(ni_key)
        if raw is not None:
            st.session_state[key] = max(min_val, min(max_val, float(raw)))

    # Slider — label contains range so it's always readable
    st.slider(
        f"{label}  [{fmt(min_val)} – {fmt(max_val)}]",
        min_value=min_val,
        max_value=max_val,
        step=step,
        key=key,
    )

    # Min / max as permanent plain text in two columns
    col_lo, col_hi = st.columns(2)
    with col_lo:
        st.markdown(
            f'<p style="margin:0;font-size:0.68rem;color:#7FB3D3;">{fmt(min_val)}</p>',
            unsafe_allow_html=True,
        )
    with col_hi:
        st.markdown(
            f'<p style="margin:0;font-size:0.68rem;color:#7FB3D3;text-align:right;">'
            f'{fmt(max_val)}</p>',
            unsafe_allow_html=True,
        )

    # Caption above the number input (not inside it)
    st.markdown(
        '<p style="margin:0.3rem 0 0.1rem;font-size:0.68rem;'
        'color:#7FB3D3;letter-spacing:0.04em;">✏️ Type exact value &amp; press Enter</p>',
        unsafe_allow_html=True,
    )
    # Number input — label hidden (shown as caption above), value centred via CSS
    st.number_input(
        label="value",
        min_value=min_val,
        max_value=max_val,
        value=float(st.session_state[key]),
        step=step,
        format="%g",
        key=ni_key,
        on_change=on_number_change,
        label_visibility="collapsed",
    )

    return float(st.session_state[key])


def render_sidebar() -> dict:
    """Render WaveIQ sidebar. Returns: mode, f, A, fs, show_diff, show_fft, show_rw"""
    with st.sidebar:

        # ── Application Mode ──────────────────────────────────────────────
        st.caption("🎛️  APPLICATION MODE")
        mode = st.radio(
            label="mode",
            options=ALL_MODES,
            index=0,
            label_visibility="collapsed",
        )

        st.divider()

        # ── Real-Time Audio Input ─────────────────────────────────────────
        st.caption("🎤  REAL-TIME AUDIO")
        use_mic = st.toggle("🎙️ Use Audio Input", value=False)
        if use_mic:
            if st.button("🔴 Record Audio (5s)", use_container_width=True):
                with st.spinner("Recording..."):
                    res = record_audio(duration=5.0)
                    if res["success"]:
                        # Preprocess audio
                        audio_data = preprocess_audio(res["audio"])
                        audio_fs = res["fs"]
                        
                        # Extract and clamp frequency
                        freq = extract_dominant_frequency(audio_data, audio_fs)
                        f_min = float(SLIDER["f"]["min"])
                        f_max = float(SLIDER["f"]["max"])
                        freq_clamped = max(f_min, min(f_max, freq))
                        
                        # Save to session state
                        st.session_state["audio_data"] = audio_data
                        st.session_state["audio_fs"] = audio_fs
                        st.session_state["f_val"] = freq_clamped
                        st.session_state[f"__ni_f_val"] = freq_clamped
                        
                        st.success(f"Recorded successfully! Dominant f: {freq:.1f} Hz")
                    else:
                        st.error(res["error"])
                        
            if st.session_state.get("audio_data") is not None:
                st.info("Using recorded audio buffer.")
            else:
                st.warning("No audio recorded yet. Please click Record.")
        else:
            # Clear audio state if toggle is off
            if "audio_data" in st.session_state:
                st.session_state.pop("audio_data")
                st.session_state.pop("audio_fs")
                
        st.divider()

        # ── Preset Demo Scenarios ─────────────────────────────────────────
        st.caption("🎬  PRESET DEMOS")
        col1, col2, col3 = st.columns([1, 1.2, 1], gap="small")
        if col1.button("Clean", use_container_width=True, help="f=100, fs=800"):
            st.session_state["f_val"] = 100
            st.session_state["__ni_f_val"] = 100
            st.session_state["fs_val"] = 800
            st.session_state["__ni_fs_val"] = 800
            st.rerun()
        if col2.button("Nyquist", use_container_width=True, help="f=200, fs=400"):
            st.session_state["f_val"] = 200
            st.session_state["__ni_f_val"] = 200
            st.session_state["fs_val"] = 400
            st.session_state["__ni_fs_val"] = 400
            st.rerun()
        if col3.button("Alias", use_container_width=True, help="f=200, fs=150"):
            st.session_state["f_val"] = 200
            st.session_state["__ni_f_val"] = 200
            st.session_state["fs_val"] = 150
            st.session_state["__ni_fs_val"] = 150
            st.rerun()
            
        st.divider()

        # ── Signal Type ───────────────────────────────────────────────────
        st.caption("〰️  SIGNAL SHAPE")
        signal_type = st.selectbox(
            "signal_type",
            options=["Sine", "Square", "Triangle"],
            index=0,
            disabled=use_mic,
            label_visibility="collapsed"
        )

        st.divider()

        # ── Signal Frequency ──────────────────────────────────────────────
        f = _control(
            key="f_val",
            min_val=float(SLIDER["f"]["min"]),
            max_val=float(SLIDER["f"]["max"]),
            step=float(SLIDER["f"]["step"]),
            default=float(SLIDER["f"]["default"]),
            label="📶 Signal Frequency — f (Hz)",
        )

        st.divider()

        # ── Amplitude ─────────────────────────────────────────────────────
        A = _control(
            key="A_val",
            min_val=float(SLIDER["A"]["min"]),
            max_val=float(SLIDER["A"]["max"]),
            step=float(SLIDER["A"]["step"]),
            default=float(SLIDER["A"]["default"]),
            label="🔊 Amplitude — A",
        )

        st.divider()

        # ── Sampling Frequency ────────────────────────────────────────────
        fs = _control(
            key="fs_val",
            min_val=float(SLIDER["fs"]["min"]),
            max_val=float(SLIDER["fs"]["max"]),
            step=float(SLIDER["fs"]["step"]),
            default=float(SLIDER["fs"]["default"]),
            label="🎚 Sampling Frequency — fs (Hz)",
        )

        st.divider()

        # ── Display Options (restored, values used in return dict) ────────
        st.caption("📐  DISPLAY OPTIONS")
        show_diff = st.checkbox("Show Error Signal",       value=True)
        show_fft  = st.checkbox("Show FFT Spectrum",       value=True)
        show_rw   = st.checkbox("Show Real-World Insight", value=True)

        st.divider()

        # ── Advanced DSP ──────────────────────────────────────────────────
        st.caption("🎛️  ADVANCED DSP")
        snr_db = st.slider(
            "Signal-to-Noise Ratio (SNR dB)",
            min_value=10, max_value=100, value=100, step=5,
            help="100 dB = No Noise. Lower values add more Gaussian noise."
        )
        apply_filter = st.checkbox(
            "Apply Anti-Aliasing Filter", value=False,
            help="Applies a low-pass filter at the Nyquist frequency before sampling."
        )

        st.divider()

        # ── Live Nyquist status ───────────────────────────────────────────
        nyq_rate = 2 * f
        aliasing = fs < nyq_rate
        ratio    = fs / nyq_rate

        if aliasing:
            st.error(f"⚠️ Aliasing!\nfs = {int(fs)} Hz  <  2f = {int(nyq_rate)} Hz")
        else:
            st.success(f"✅ Nyquist OK\nfs = {int(fs)} Hz  ≥  2f = {int(nyq_rate)} Hz")

        st.markdown(f"""
        <div class="sb-quickref">
            <div class="sb-qr-title">Live Reference</div>
            <p>
                f &nbsp;&nbsp;&nbsp;= {int(f)} Hz<br>
                fs &nbsp;&nbsp;= {int(fs)} Hz<br>
                2f &nbsp;&nbsp;= {int(nyq_rate)} Hz<br>
                fs/2f = {ratio:.3f}×
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Return actual checkbox values (NOT hardcoded True) ────────────────
    return dict(
        mode=mode,
        f=int(f),
        A=float(A),
        fs=int(fs),
        show_diff=show_diff,
        show_fft=show_fft,
        show_rw=show_rw,
        snr_db=float(snr_db),
        apply_filter=apply_filter,
        audio_data=st.session_state.get("audio_data") if use_mic else None,
        audio_fs=st.session_state.get("audio_fs") if use_mic else None,
        signal_type=signal_type,
    )