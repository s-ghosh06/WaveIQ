"""
core/recommender.py
───────────────────
AI-based sampling rate recommender.
Rule-based logic to suggest the optimal sampling rate
based on the signal frequency and application mode.
"""

def get_recommendation(f: float, fs: float, f_alias: float, mode: str, aliasing: bool) -> dict:
    """
    Generates a recommended sampling rate and explanation.
    
    Args:
        f: Signal frequency
        fs: Current sampling frequency
        f_alias: Alias frequency
        mode: Application mode
        aliasing: Whether aliasing is currently occurring
        
    Returns:
        dict containing recommendation details
    """
    if f <= 0:
        return {
            "recommended_fs": int(fs),
            "explanation": "Please provide a valid, positive frequency to get a recommendation.",
            "confidence": "Low",
            "status": "neutral"
        }

    # Determine recommended sampling multiplier based on mode
    if mode == "🎵 Audio":
        multiplier = 4.0
        explanation = (
            "Audio signals require significant oversampling (often > 4x or industry standards like 44.1kHz) "
            "to prevent audible distortion and allow for gradual anti-aliasing filters."
        )
    elif mode == "📡 Sensor":
        multiplier = 2.5
        explanation = (
            "Industrial standards recommend sampling at ≥ 2.5x the highest frequency of interest "
            "to safely capture transient fault signatures and avoid missed alerts."
        )
    elif mode == "📷 Camera":
        multiplier = 2.5
        explanation = (
            "To avoid spatial moiré or temporal wagon-wheel effects, sampling at > 2x is required. "
            "A factor of 2.5x gives a reliable safety margin."
        )
    else: # Basic
        multiplier = 2.5
        explanation = (
            "While the Nyquist limit is exactly 2x, practical systems use 2.5x to 3x "
            "to ensure perfect reconstruction using standard sinc-interpolation filters."
        )

    rec_fs = int(f * multiplier)

    # Determine status (color coding)
    if aliasing:
        status = "danger"
        confidence = "High"
        prefix = "Critical: Aliasing detected! "
    elif fs < rec_fs:
        status = "warning"
        confidence = "Medium"
        prefix = "Sub-optimal: "
    else:
        status = "success"
        confidence = "High"
        prefix = "Optimal: "

    return {
        "recommended_fs": rec_fs,
        "explanation": prefix + explanation,
        "confidence": confidence,
        "status": status
    }
