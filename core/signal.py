"""
core/signal.py
──────────────
All signal generation, sampling, and aliasing math.
Pure functions — no Streamlit, no Plotly dependencies.
"""

import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
#  DATA CONTAINERS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SignalData:
    """Holds all computed signal arrays for one simulation run."""
    # Continuous original
    t_cont:   np.ndarray
    x_cont:   np.ndarray

    # Sampled points
    t_samp:   np.ndarray
    x_samp:   np.ndarray

    # Aliased reconstruction
    t_alias:  np.ndarray
    x_alias:  np.ndarray

    # Error / difference
    t_diff:   np.ndarray
    x_diff:   np.ndarray

    # Frequency spectra
    freqs_orig:  np.ndarray
    mags_orig:   np.ndarray
    freqs_alias: np.ndarray
    mags_alias:  np.ndarray

    # Derived scalars
    f_alias:      float
    nyquist_rate: float
    rms_error:    float
    aliasing:     bool


# ─────────────────────────────────────────────────────────────────────────────
#  SIGNAL GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_continuous_signal(
    f: float,
    A: float,
    duration: float,
    num_points: int = 4000,
    signal_type: str = "Sine"
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a high-resolution continuous signal for smooth plotting.

    Args:
        f:          Signal frequency in Hz.
        A:          Peak amplitude.
        duration:   Duration in seconds.
        num_points: Number of points for smooth rendering.
        signal_type: "Sine", "Square", or "Triangle".

    Returns:
        (t, x) — time array (s) and amplitude array.
    """
    t = np.linspace(0, duration, num_points)
    
    if signal_type == "Square":
        from scipy.signal import square
        x = A * square(2 * np.pi * f * t)
    elif signal_type == "Triangle":
        from scipy.signal import sawtooth
        x = A * sawtooth(2 * np.pi * f * t, width=0.5)
    else:
        x = A * np.sin(2 * np.pi * f * t)
        
    return t, x


def sample_signal(
    f: float,
    A: float,
    fs: float,
    duration: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Discretely sample the sine wave at sampling frequency fs.

    Args:
        f:        Signal frequency in Hz.
        A:        Peak amplitude.
        fs:       Sampling frequency in Hz.
        duration: Duration in seconds.

    Returns:
        (t_samples, x_samples) — discrete sample times and amplitudes.
    """
    n_samples = max(2, int(fs * duration))
    t_samples = np.linspace(0, duration, n_samples)
    x_samples = A * np.sin(2 * np.pi * f * t_samples)
    return t_samples, x_samples


# ─────────────────────────────────────────────────────────────────────────────
#  ADVANCED DSP (NOISE + FILTERING)
# ─────────────────────────────────────────────────────────────────────────────

def add_noise(x: np.ndarray, snr_db: float) -> np.ndarray:
    """Adds Additive White Gaussian Noise (AWGN) based on a target SNR."""
    if snr_db >= 100.0:
        return x
    
    signal_power = np.mean(x ** 2)
    if signal_power == 0:
        return x
        
    snr_linear = 10 ** (snr_db / 10)
    noise_power = signal_power / snr_linear
    noise = np.sqrt(noise_power) * np.random.randn(len(x))
    
    return x + noise

def apply_lowpass_filter(x: np.ndarray, cutoff: float, fs_cont: float, order: int = 4) -> np.ndarray:
    """Applies a zero-phase Butterworth lowpass filter."""
    nyq = 0.5 * fs_cont
    normal_cutoff = cutoff / nyq
    if normal_cutoff >= 1.0 or normal_cutoff <= 0:
        return x
        
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, x)


# ─────────────────────────────────────────────────────────────────────────────
#  ALIASING MATH
# ─────────────────────────────────────────────────────────────────────────────

def compute_alias_frequency(f: float, fs: float) -> float:
    """
    Compute alias frequency using the industry-correct formula.

    Formula:  f_alias = | f - round(f / fs) * fs |

    This handles all aliasing cases correctly — including cases
    where f > fs and where f is close to multiples of fs.

    Args:
        f:  Original signal frequency in Hz.
        fs: Sampling frequency in Hz.

    Returns:
        Alias frequency in Hz (always non-negative).
    """
    k = round(f / fs)
    return float(abs(f - k * fs))


def generate_aliased_signal(
    f_alias: float,
    A: float,
    duration: float,
    num_points: int = 4000,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate the reconstructed aliased signal at f_alias.

    Args:
        f_alias:    Computed alias frequency in Hz.
        A:          Amplitude (same as original).
        duration:   Duration in seconds.
        num_points: Points for smooth rendering.

    Returns:
        (t, x_alias) — time array and aliased amplitude array.
    """
    t = np.linspace(0, duration, num_points)
    x = A * np.sin(2 * np.pi * f_alias * t)
    return t, x


# ─────────────────────────────────────────────────────────────────────────────
#  ERROR METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_error_signal(
    x_cont: np.ndarray,
    x_alias: np.ndarray,
) -> np.ndarray:
    """
    Compute the point-wise reconstruction error.
    Both signals must share the same time vector (same num_points).

    Returns:
        diff array (original − aliased).
    """
    return x_cont - x_alias


def rms_error(diff: np.ndarray) -> float:
    """Root-mean-square reconstruction error."""
    return float(np.sqrt(np.mean(diff ** 2)))


# ─────────────────────────────────────────────────────────────────────────────
#  FREQUENCY ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def compute_fft(
    t: np.ndarray,
    x: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute single-sided FFT magnitude spectrum.

    Args:
        t: Time array (uniform spacing).
        x: Signal amplitude array.

    Returns:
        (frequencies, magnitudes) — positive frequencies only.
    """
    N  = len(x)
    dt = t[1] - t[0]
    yf = fft(x)
    xf = fftfreq(N, dt)
    half  = N // 2
    freqs = xf[:half]
    mags  = (2.0 / N) * np.abs(yf[:half])
    return freqs, mags


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN COMPUTE PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def compute_all(f: float, A: float, fs: float, snr_db: float = 100.0, apply_filter: bool = False, audio_data: np.ndarray = None, audio_fs: float = None, signal_type: str = "Sine") -> SignalData:
    """
    Full computation pipeline — call this once per UI interaction.

    Args:
        f:  Signal frequency (Hz) (Fundamental or dominant).
        A:  Amplitude.
        fs: Sampling frequency (Hz).
        snr_db: Signal-to-Noise Ratio in dB.
        apply_filter: Whether to apply anti-aliasing lowpass filter.
        audio_data: Optional real audio array to use as the source signal.
        audio_fs: Sampling rate of the real audio array.

    Returns:
        SignalData dataclass with all arrays and derived scalars.
    """
    if audio_data is not None and audio_fs is not None:
        duration = len(audio_data) / audio_fs
        t_cont = np.linspace(0, duration, len(audio_data))
        x_cont = audio_data
        A = float(np.max(np.abs(x_cont))) if len(x_cont) > 0 else 1.0
    else:
        # Show at least 5 complete cycles
        duration = max(0.05, 5.0 / f)
        # Generate synthetic signal
        t_cont, x_cont = generate_continuous_signal(f, A, duration, signal_type=signal_type)
    
    # 1. Apply Advanced DSP to Continuous Signal
    if snr_db < 100.0:
        x_cont = add_noise(x_cont, snr_db)
        
    fs_cont = audio_fs if audio_data is not None else (len(t_cont) / duration)
    
    if apply_filter:
        # Anti-aliasing filter at Nyquist frequency of the sampling rate
        x_cont = apply_lowpass_filter(x_cont, cutoff=fs/2.0, fs_cont=fs_cont)

    # 2. Sample the Enhanced Signal
    if audio_data is not None:
        from core.audio_pipeline import downsample_signal
        t_samp, x_samp = downsample_signal(x_cont, fs_cont, fs)
    elif snr_db < 100.0 or apply_filter:
        t_samp, _ = sample_signal(f, A, fs, duration)
        x_samp = np.interp(t_samp, t_cont, x_cont)
    else:
        t_samp, x_samp = sample_signal(f, A, fs, duration)
        
    f_alias = compute_alias_frequency(f, fs)
    
    # 3. Generate Alias/Reconstructed Signal
    if audio_data is not None:
        # Reconstruct the complex aliased signal using sinc interpolation
        x_alias = sinc_reconstruct(t_samp, x_samp, t_cont, fs)
        t_alias = t_cont
    else:
        t_alias, x_alias = generate_aliased_signal(f_alias, A, duration)
        # If filtered and f is above Nyquist, the alias amplitude should also be suppressed
        if apply_filter and f > fs / 2.0:
            x_alias = apply_lowpass_filter(x_alias, cutoff=fs/2.0, fs_cont=len(t_alias)/duration)
        # Add noise to alias signal to keep it consistent
        if snr_db < 100.0:
            x_alias = add_noise(x_alias, snr_db)

    # Error
    diff = compute_error_signal(x_cont, x_alias)
    rms  = rms_error(diff)

    # FFT
    freqs_o, mags_o = compute_fft(t_cont, x_cont)
    freqs_a, mags_a = compute_fft(t_alias, x_alias)

    return SignalData(
        t_cont=t_cont, x_cont=x_cont,
        t_samp=t_samp, x_samp=x_samp,
        t_alias=t_alias, x_alias=x_alias,
        t_diff=t_cont, x_diff=diff,
        freqs_orig=freqs_o, mags_orig=mags_o,
        freqs_alias=freqs_a, mags_alias=mags_a,
        f_alias=f_alias,
        nyquist_rate=2.0 * f,
        rms_error=rms,
        aliasing=(fs < 2.0 * f),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SINC RECONSTRUCTION  (Gap 2)
# ─────────────────────────────────────────────────────────────────────────────

def sinc_reconstruct(
    t_samp: np.ndarray,
    x_samp: np.ndarray,
    t_cont: np.ndarray,
    fs: float,
) -> np.ndarray:
    """
    Reconstruct the signal from discrete samples using sinc interpolation.
    This is the mathematically correct Whittaker–Shannon reconstruction:
        x_r(t) = Σ x[n] · sinc(fs · (t − n/fs))

    Args:
        t_samp: Sample time points (s).
        x_samp: Sample amplitudes.
        t_cont: Dense time array for output (s).
        fs:     Sampling frequency (Hz).

    Returns:
        Reconstructed signal array, same shape as t_cont.
    """
    Ts = 1.0 / fs
    x_reconstructed = np.zeros_like(t_cont, dtype=float)
    for n, (tn, xn) in enumerate(zip(t_samp, x_samp)):
        x_reconstructed += xn * np.sinc((t_cont - tn) / Ts)
    return x_reconstructed


# ─────────────────────────────────────────────────────────────────────────────
#  SAMPLING REGIME CLASSIFIER  (Gap 1)
# ─────────────────────────────────────────────────────────────────────────────

def classify_sampling_regime(f: float, fs: float) -> dict:
    """
    Classify the current sampling scenario into one of three regimes.

    Returns a dict with:
        regime:      "under" | "nyquist" | "over"
        label:       Human-readable regime name
        ratio:       fs / (2*f)
        description: One-line explanation
        color:       CSS colour for the regime badge
    """
    ratio = fs / (2.0 * f)

    if ratio < 1.0:
        return dict(
            regime="under",
            label="Under-Sampling",
            ratio=ratio,
            description=(
                f"fs = {fs} Hz < 2f = {2*f:.0f} Hz. "
                "Aliasing occurs — information is permanently lost."
            ),
            color="#E74C3C",
            bg="#FDEDEC",
        )
    elif abs(ratio - 1.0) < 0.05:          # within 5% of Nyquist boundary
        return dict(
            regime="nyquist",
            label="Nyquist Sampling",
            ratio=ratio,
            description=(
                f"fs ≈ 2f = {2*f:.0f} Hz. "
                "At the critical Nyquist boundary — marginal, any noise causes aliasing."
            ),
            color="#F39C12",
            bg="#FEF9E7",
        )
    elif ratio < 2.0:
        return dict(
            regime="over",
            label="Adequate Sampling",
            ratio=ratio,
            description=(
                f"fs = {fs} Hz > 2f = {2*f:.0f} Hz. "
                "Nyquist satisfied — signal can be reconstructed faithfully."
            ),
            color="#27AE60",
            bg="#EAFAF1",
        )
    else:
        return dict(
            regime="over",
            label="Over-Sampling",
            ratio=ratio,
            description=(
                f"fs = {fs} Hz is {ratio:.1f}× the Nyquist rate. "
                "Excellent — large safety margin, near-perfect reconstruction."
            ),
            color="#1A5276",
            bg="#D6EAF8",
        )