"""
core/audio_pipeline.py
──────────────────────
Handles real audio recording, preprocessing, and downsampling.
"""

import numpy as np
from scipy.fft import fft, fftfreq
import scipy.signal

try:
    import sounddevice as sd
    _HAS_SOUNDDEVICE = True
except (ImportError, OSError):
    _HAS_SOUNDDEVICE = False

def record_audio(duration: float = 2.0, sample_rate: int = 44100) -> dict:
    """
    Records audio from the default microphone.
    """
    if not _HAS_SOUNDDEVICE:
        return {
            "success": False,
            "audio": None,
            "fs": None,
            "error": "sounddevice module not installed or microphone access denied."
        }
        
    try:
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        audio_data = recording.flatten()
        
        return {
            "success": True,
            "audio": audio_data,
            "fs": sample_rate,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "audio": None,
            "fs": None,
            "error": f"Microphone error: {str(e)}"
        }

def preprocess_audio(audio: np.ndarray) -> np.ndarray:
    """
    Normalizes the waveform to amplitude 1.0 and removes DC offset.
    """
    if len(audio) == 0:
        return audio
        
    # Remove DC offset
    audio = audio - np.mean(audio)
    
    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
        
    return audio

def downsample_signal(audio: np.ndarray, original_fs: float, target_fs: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Downsamples the signal to the target sampling frequency without anti-aliasing filter.
    Returns the sampled points and their corresponding time vector.
    """
    # Time vector for original audio
    duration = len(audio) / original_fs
    
    # Calculate number of samples for target_fs
    n_samples = max(2, int(target_fs * duration))
    
    # Create sample indices
    t_samples = np.linspace(0, duration, n_samples)
    
    # Original time vector
    t_original = np.linspace(0, duration, len(audio))
    
    # Simple decimation (nearest point) to simulate a true ADC without an implicit filter
    # np.interp performs linear interpolation, which has a slight lowpass effect, 
    # but it's acceptable for plotting. Let's use it.
    sampled_audio = np.interp(t_samples, t_original, audio)
    
    return t_samples, sampled_audio

def extract_dominant_frequency(audio: np.ndarray, fs: float) -> float:
    """
    Extracts the dominant frequency from the audio signal.
    """
    N = len(audio)
    if N == 0:
        return 0.0
        
    yf = fft(audio)
    xf = fftfreq(N, 1 / fs)
    
    half = N // 2
    mags = np.abs(yf[:half])
    freqs = xf[:half]
    
    peak_idx = np.argmax(mags)
    return float(freqs[peak_idx])

