"""Shared setup for the Privacy policy and Terms pages.

Fill in the values below before launch. While any value still starts with "[",
the legal pages show a warning so an unfinished page cannot go live unnoticed.
"""
from pathlib import Path

import streamlit as st

OPERATOR = "Sanket Suri"
CONTACT_EMAIL = "sanketsuri99@gmail.com"
JURISDICTION = "India"
HOSTING = "Streamlit Community Cloud"
RETENTION = "a limited time, until we delete them or the server restarts"
LAST_UPDATED = "7 October 2026"

FAVICON = Path("assets/favicon.png")


def page_setup(title: str):
    """Must be the first Streamlit call on the page."""
    st.set_page_config(
        page_title=f"{title} | EmergeRoute",
        page_icon=str(FAVICON) if FAVICON.exists() else None,
        layout="centered",
        initial_sidebar_state="collapsed",
    )


def apply_theme():
    from background import render_background
    from smooth import render_smooth_scroll
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@300;400;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
    :root { --ground:#0c0b09; --surface:#15130f; --line:#2a261d; --text:#ece7dc; --muted:#9a9283; --accent:#d6a24a;
            --sans:"Red Hat Display", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
    html, body, .stApp { font-family: var(--sans); }
    /* Keep Streamlit's icon font: icon spans must not get the text font, or their names print as words */
    [class*="st-"]:not([data-testid="stIconMaterial"]):not([class*="material"]):not([class*="Material"]) { font-family: var(--sans); }
    .stApp { background-color: var(--ground); color: var(--text); font-weight: 300; }
    .block-container { padding-top: 1.5rem; max-width: 760px; }
    #MainMenu, footer, .stDeployButton, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
    header[data-testid="stHeader"] { background: transparent; }
    h1, h2, h3 { font-weight: 300; letter-spacing: -0.01em; color: var(--text); }
    h1 { font-size: clamp(1.9rem, 3.6vw, 2.6rem); }
    h2 { font-size: 1.35rem; font-weight: 600; padding-top: 1.6rem; }
    p, li, label { color: var(--text); line-height: 1.7; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    a { color: var(--accent); text-underline-offset: 3px; }
    a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
    /* No sidebar: hide it and its open/close arrows */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"] { display: none !important; }
    .appbar { border-bottom: 1px solid var(--line); padding-bottom: 0.9rem; margin-bottom: 1.6rem; }
    .appbar a { color: var(--text); font-weight: 600; letter-spacing: 0.06em; text-decoration: none; }
    .site-footer { border-top: 1px solid var(--line); margin-top: 3rem; padding-top: 1.2rem; color: var(--muted); font-size: 0.9rem; }
    .site-footer a { color: var(--muted); text-decoration: none; margin-right: 1.5rem; }
    .site-footer a:hover { color: var(--text); }
</style>
""", unsafe_allow_html=True)

    render_background()
    render_smooth_scroll()


def render_header():
    st.markdown('<div class="appbar"><a href="/" target="_self">EmergeRoute</a></div>', unsafe_allow_html=True)


def placeholder_warning():
    values = [OPERATOR, CONTACT_EMAIL, JURISDICTION, HOSTING, RETENTION, LAST_UPDATED]
    if any(v.startswith("[") for v in values):
        st.warning("Values in square brackets must be filled in (see legal_common.py) and this page reviewed by a qualified person before launch.")


def render_footer():
    st.markdown(
        '<div class="site-footer"><a href="/" target="_self">Back to dashboard</a>'
        '<a href="privacy" target="_self">Privacy policy</a>'
        '<a href="terms" target="_self">Terms and conditions</a></div>',
        unsafe_allow_html=True,
    )
