"""
core/audio_input.py
───────────────────
Handles microphone audio capture and dominant frequency extraction.
Provides safe fallbacks if the microphone is unavailable.
"""

import numpy as np
from scipy.fft import fft, fftfreq
try:
    import sounddevice as sd
    _HAS_SOUNDDEVICE = True
except (ImportError, OSError):
    _HAS_SOUNDDEVICE = False


def capture_dominant_frequency(duration: float = 1.0, sample_rate: int = 44100) -> dict:
    """
    Captures audio from the default microphone and returns the dominant frequency.
    
    Args:
        duration: Capture duration in seconds.
        sample_rate: Sampling rate for capture.
        
    Returns:
        dict: {
            "success": bool,
            "frequency": float or None,
            "error": str or None
        }
    """
    if not _HAS_SOUNDDEVICE:
        return {
            "success": False,
            "frequency": None,
            "error": "sounddevice module not installed or microphone access denied."
        }
        
    try:
        # Record audio
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait() # Block until recording is finished
        
        # Flatten the array
        audio_data = recording.flatten()
        
        # Extract dominant frequency using FFT
        N = len(audio_data)
        yf = fft(audio_data)
        xf = fftfreq(N, 1 / sample_rate)
        
        # Get positive frequencies only
        half = N // 2
        mags = np.abs(yf[:half])
        freqs = xf[:half]
        
        # Find peak
        peak_idx = np.argmax(mags)
        dom_freq = freqs[peak_idx]
        
        return {
            "success": True,
            "frequency": float(dom_freq),
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "frequency": None,
            "error": f"Microphone error: {str(e)}"
        }
