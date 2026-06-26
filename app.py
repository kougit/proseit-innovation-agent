"""
ProSEIT Innovation-to-Implementation Agent — application entry point.

Run with:
    streamlit run app.py
"""
from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="ProSEIT — Innovation Agent",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.brand import inject_css
inject_css()

_pages = [
    st.Page("pages/home.py",            title="Home",           icon="🏠", default=True),
    st.Page("pages/new_innovation.py",  title="New Innovation", icon="💡"),
    st.Page("pages/results.py",         title="Results",        icon="📊"),
]

_nav = st.navigation(_pages, position="sidebar")

from ui.components import render_sidebar
render_sidebar()

_nav.run()
