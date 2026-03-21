"""
╔══════════════════════════════════════════════════════════════╗
║  WaveIQ — Intelligent Signal Sampling & Aliasing Analyzer   ║
║  Run:  streamlit run app.py                                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from ui.layout import render_page

# Must be the VERY FIRST Streamlit call in the script
st.set_page_config(
    page_title="WaveIQ – Signal Sampling Analyzer",
    page_icon="〰️",
    layout="wide",
    initial_sidebar_state="expanded",   # Always start expanded
)

render_page()