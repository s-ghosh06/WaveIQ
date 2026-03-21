"""
core/modes.py
─────────────
Real-world application mode content: explanations, examples, and formulas.
Completely decoupled from UI — just returns plain Python dicts.
"""

from dataclasses import dataclass


@dataclass
class ModeContent:
    """Structured content for a real-world application mode."""
    icon:         str
    title:        str
    context:      str          # HTML-safe description string
    bullet_points: list[str]   # HTML-safe bullet items
    formula:      str
    real_example: str


# ─────────────────────────────────────────────────────────────────────────────
#  MODE REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

def get_mode_content(
    mode: str,
    f: float,
    fs: float,
    f_alias: float,
    aliasing: bool,
) -> ModeContent:
    """
    Return mode-specific educational content based on current signal params.

    Args:
        mode:     One of "📻 Basic", "🎵 Audio", "📷 Camera", "📡 Sensor".
        f:        Signal frequency (Hz).
        fs:       Sampling frequency (Hz).
        f_alias:  Computed alias frequency (Hz).
        aliasing: True if fs < 2*f.

    Returns:
        ModeContent dataclass.
    """
    nyq          = fs / 2
    nyq_rate     = 2 * f
    status_text  = "⚠️ aliasing occurs" if aliasing else "✅ signal is faithfully captured"

    _modes = {
        "📻 Basic": ModeContent(
            icon="📻",
            title="Fundamentals — Nyquist-Shannon Sampling Theorem",
            context=(
                f"Sampling a <b>{f} Hz</b> sine wave at <b>{fs} Hz</b>. "
                f"The Nyquist rate = {nyq_rate:.0f} Hz. Currently, {status_text}."
            ),
            bullet_points=[
                "Shannon's theorem: a band-limited signal sampled at fs > 2·f_max can be perfectly reconstructed.",
                f"Alias formula: f_alias = |f − round(f/fs) × fs| = <b>{f_alias:.2f} Hz</b>",
                "Aliasing is <b>irreversible</b> — once sampled below Nyquist, the original information is permanently lost.",
                f"Oversampling (fs ≫ 2f) gives more reconstruction accuracy and noise margin.",
                f"Nyquist frequency = fs/2 = <b>{nyq:.0f} Hz</b> — the maximum representable frequency at this rate.",
            ],
            formula="fs > 2 × f_max   (Nyquist Criterion)",
            real_example=(
                "🔬 MRI machines sample nuclear spin signals at very high rates to reconstruct "
                "anatomical detail without aliasing artifacts (ghosting) in the image."
            ),
        ),

        "🎵 Audio": ModeContent(
            icon="🎵",
            title="Audio Sampling — PCM & Digital Audio",
            context=(
                f"In digital audio, your signal at <b>{f} Hz</b> is sampled at <b>{fs} Hz</b>. "
                f"The Nyquist theorem demands fs ≥ {nyq_rate:.0f} Hz to preserve this frequency. "
                f"Currently, {status_text}."
            ),
            bullet_points=[
                "CD audio uses 44,100 Hz — covers the human hearing range up to ~22 kHz.",
                "Studio-grade audio uses 96 kHz or 192 kHz for headroom against aliasing artifacts.",
                f"At your settings, alias appears at <b>{f_alias:.2f} Hz</b> — a phantom tone that doesn't exist in the original.",
                "This is why low-bitrate audio streams or phone calls sound 'tinny' or distorted.",
                "Anti-aliasing filters (analog low-pass) are applied <i>before</i> the ADC to band-limit the input signal.",
            ],
            formula="f_alias = |f − round(f/fs) × fs|",
            real_example=(
                "📼 Vintage telephone systems sampled at ~8 kHz — resulting in 4 kHz bandwidth, "
                "which strips high-frequency content like consonant clarity ('s', 'f', 'th' sounds)."
            ),
        ),

        "📷 Camera": ModeContent(
            icon="📷",
            title="Camera & Video — Spatial & Temporal Aliasing",
            context=(
                f"In video/imaging, your signal at <b>{f} Hz</b> represents a repeating visual pattern "
                f"(e.g., a spinning wheel or striped fabric). "
                f"The camera captures at <b>{fs} fps / lines per frame</b>. {status_text.capitalize()}."
            ),
            bullet_points=[
                "The <b>wagon-wheel effect</b>: a wheel spinning at 24 Hz captured at 24 fps appears stationary.",
                f"At {f} Hz pattern and {fs} Hz capture rate, the perceived frequency = <b>{f_alias:.2f} Hz</b>.",
                "Spatial aliasing creates <b>moiré patterns</b> in fabric, brickwork, or fine grids on digital cameras.",
                "Film cameras use depth-of-field blur and motion blur as natural optical anti-aliasing.",
                "DSLR sensors use an optical low-pass filter (OLPF) placed before the sensor to reduce spatial aliasing.",
            ],
            formula="f_apparent = f − round(f/fs) × fs",
            real_example=(
                "🎬 The helicopter rotor illusion in film: rotor blades appear frozen or reversing "
                "because the blade-pass frequency matches or aliases against the camera's frame rate."
            ),
        ),

        "📡 Sensor": ModeContent(
            icon="📡",
            title="IoT / Sensor Systems — Industrial Measurement Aliasing",
            context=(
                f"An industrial sensor measures vibration at <b>{f} Hz</b>, but the DAQ system "
                f"samples at only <b>{fs} Hz</b>. "
                f"Nyquist requires ≥ {nyq_rate:.0f} Hz. Currently, {status_text}."
            ),
            bullet_points=[
                "Undersampled vibration data can <b>miss fault signatures</b> in rotating machinery entirely.",
                f"A bearing fault at {f} Hz sampled at {fs} Hz is logged as a false <b>{f_alias:.2f} Hz</b> signal.",
                "Oil/gas pipelines use accelerometers at 10–50 kHz to catch high-frequency mechanical fault modes.",
                "Temperature sensors (1–10 Hz sampling) are fine because thermal signals change slowly.",
                "Industry rule of thumb: sample at <b>≥ 2.5×</b> the highest frequency of interest for safety margin.",
            ],
            formula="Safe fs ≥ 2.5 × f_max   (Industry Rule of Thumb)",
            real_example=(
                "⚙️ Predicting wind turbine gearbox failure: vibration signatures at 2.5 kHz must be sampled "
                "at minimum 5 kHz — real SCADA systems typically run at 10–25 kHz for reliable diagnostics."
            ),
        ),
    }

    return _modes.get(mode, _modes["📻 Basic"])


# Convenience: list of all available modes for the UI dropdown
ALL_MODES: list[str] = ["📻 Basic", "🎵 Audio", "📷 Camera", "📡 Sensor"]