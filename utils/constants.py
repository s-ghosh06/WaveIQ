"""
utils/constants.py
──────────────────
Global color palette, Plotly layout defaults, and app-wide constants.
Import from here — never hardcode colors or sizes elsewhere.
"""

# ─────────────────────────────────────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    # Signal traces
    "original":       "#2E86C1",   # Blue    — continuous source signal
    "sampled":        "#E74C3C",   # Red     — discrete sample markers
    "aliased":        "#F39C12",   # Orange  — aliased reconstruction
    "difference":     "#8E44AD",   # Purple  — error / difference signal
    "nyquist":        "#27AE60",   # Green   — Nyquist frequency marker

    # Spectrum
    "spectrum_orig":  "#2E86C1",
    "spectrum_alias": "#F39C12",

    # UI accents
    "primary":        "#2E86C1",
    "accent":         "#F39C12",
    "success":        "#27AE60",
    "danger":         "#E74C3C",
    "muted":          "#5D6D7E",
    "border":         "#D5DBDB",
    "grid":           "#ECF0F1",
    "bg":             "#F4F6F9",
    "card":           "#FFFFFF",
    "text":           "#1A252F",
}

# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY SHARED LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

PLOTLY_BASE_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="#F8FAFB",
    font=dict(family="Inter, sans-serif", size=12, color=COLORS["text"]),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="IBM Plex Mono"),
    margin=dict(l=55, r=20, t=48, b=45),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right",  x=1,
        font=dict(size=11),
    ),
)

PLOTLY_AXIS_DEFAULTS = dict(
    showgrid=True,
    gridcolor=COLORS["grid"],
    gridwidth=1,
    zeroline=True,
    zerolinecolor="#BDC3C7",
    zerolinewidth=1.5,
    tickfont=dict(size=10),
)

# ─────────────────────────────────────────────────────────────────────────────
#  SLIDER RANGES
# ─────────────────────────────────────────────────────────────────────────────

SLIDER = {
    "f":    dict(min=10,  max=2000, default=150,  step=5),
    "A":    dict(min=0.1, max=5.0,  default=1.0,  step=0.1),
    "fs":   dict(min=20,  max=8000, default=120,  step=10),
}

# ─────────────────────────────────────────────────────────────────────────────
#  CHART HEIGHTS
# ─────────────────────────────────────────────────────────────────────────────

CHART_HEIGHT = {
    "time_domain": 340,
    "aliased":     340,
    "difference":  260,
    "fft":         310,
    "gauge":       220,
}

# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY CONFIG (toolbar settings)
# ─────────────────────────────────────────────────────────────────────────────

PLOTLY_CONFIG = dict(
    displayModeBar=True,
    displaylogo=False,
    modeBarButtonsToRemove=["select2d", "lasso2d"],
)