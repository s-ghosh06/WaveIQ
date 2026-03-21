"""
core/signal.py
──────────────
All signal generation, sampling, and aliasing math.
Pure functions — no Streamlit, no Plotly dependencies.
"""

import numpy as np
from scipy.fft import fft, fftfreq
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
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a high-resolution continuous sine wave for smooth plotting.

    Args:
        f:          Signal frequency in Hz.
        A:          Peak amplitude.
        duration:   Duration in seconds.
        num_points: Number of points for smooth rendering.

    Returns:
        (t, x) — time array (s) and amplitude array.
    """
    t = np.linspace(0, duration, num_points)
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

def compute_all(f: float, A: float, fs: float) -> SignalData:
    """
    Full computation pipeline — call this once per UI interaction.

    Args:
        f:  Signal frequency (Hz).
        A:  Amplitude.
        fs: Sampling frequency (Hz).

    Returns:
        SignalData dataclass with all arrays and derived scalars.
    """
    # Show at least 5 complete cycles
    duration = max(0.05, 5.0 / f)

    # Generate signals
    t_cont, x_cont   = generate_continuous_signal(f, A, duration)
    t_samp, x_samp   = sample_signal(f, A, fs, duration)
    f_alias           = compute_alias_frequency(f, fs)
    t_alias, x_alias  = generate_aliased_signal(f_alias, A, duration)

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