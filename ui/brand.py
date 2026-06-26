"""ProSEIT brand constants and global CSS."""
from __future__ import annotations
import streamlit as st

NAVY      = "#24364B"
GOLD      = "#D4A62A"
WHITE     = "#FFFFFF"
SOFT_GREY = "#F4F6F8"
DARK_TEXT = "#1F2933"
GREEN     = "#00843D"
RED       = "#C0392B"
AMBER     = "#E67E22"
NAVY_DARK = "#1a2b3b"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
            color: {DARK_TEXT};
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {NAVY} 0%, {NAVY_DARK} 100%);
            border-right: 3px solid {GOLD};
        }}
        section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.9) !important; }}
        section[data-testid="stSidebar"] .ps-nav-lbl {{
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {GOLD} !important;
            margin: 1.2rem 0 0.3rem 0.2rem;
        }}

        .ps-card {{
            background: {WHITE};
            border: 1px solid rgba(36,54,75,0.10);
            border-radius: 10px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 1px 4px rgba(36,54,75,0.06);
        }}
        .ps-card-navy {{
            background: linear-gradient(135deg, {NAVY} 0%, {NAVY_DARK} 100%);
            border-radius: 10px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 2px 8px rgba(36,54,75,0.18);
        }}
        .ps-card-gold {{
            background: linear-gradient(135deg, {GOLD} 0%, #b8860b 100%);
            border-radius: 10px;
            padding: 1.2rem 1.4rem;
            color: {WHITE};
        }}

        .ps-hero {{
            background: linear-gradient(135deg, {NAVY} 0%, #1a3550 50%, {NAVY_DARK} 100%);
            border-radius: 14px;
            padding: 2.8rem 2.4rem 2.4rem;
            margin-bottom: 1.8rem;
            position: relative;
            overflow: hidden;
        }}
        .ps-hero::before {{
            content: '';
            position: absolute;
            top: -40px; right: -40px;
            width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(212,166,42,0.15) 0%, transparent 70%);
            border-radius: 50%;
        }}

        .ps-page-title {{
            border-left: 4px solid {GOLD};
            padding-left: 1rem;
            margin-bottom: 1.4rem;
        }}
        .ps-page-title h1 {{
            color: {NAVY};
            font-weight: 700;
            font-size: 1.6rem;
            margin: 0 0 0.2rem;
        }}
        .ps-page-title p {{
            color: rgba(36,54,75,0.6);
            font-size: 0.88rem;
            margin: 0;
        }}

        .ps-section-bar {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 1.4rem 0 0.9rem;
        }}
        .ps-section-bar span {{
            font-weight: 700;
            font-size: 0.8rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {NAVY};
        }}
        .ps-section-bar::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, rgba(36,54,75,0.15) 0%, transparent 100%);
        }}

        .ps-stat {{
            text-align: center;
            padding: 1rem 0.5rem;
        }}
        .ps-stat-value {{
            font-size: 2.2rem;
            font-weight: 800;
            color: {NAVY};
            line-height: 1;
        }}
        .ps-stat-value.gold {{ color: {GOLD}; }}
        .ps-stat-label {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: rgba(36,54,75,0.5);
            margin-top: 0.3rem;
        }}

        .ps-badge {{
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 20px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .ps-badge.navy  {{ background: {NAVY};  color: {WHITE}; }}
        .ps-badge.gold  {{ background: {GOLD};  color: {WHITE}; }}
        .ps-badge.green {{ background: {GREEN}; color: {WHITE}; }}
        .ps-badge.red   {{ background: {RED};   color: {WHITE}; }}
        .ps-badge.amber {{ background: {AMBER}; color: {WHITE}; }}
        .ps-badge.grey  {{ background: rgba(36,54,75,0.12); color: {NAVY}; }}

        .ps-steps {{
            display: flex;
            gap: 0.3rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }}
        .ps-step {{
            padding: 0.3rem 0.7rem;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
            border: 1.5px solid rgba(36,54,75,0.15);
            color: rgba(36,54,75,0.45);
            background: transparent;
        }}
        .ps-step.active {{
            background: {GOLD};
            color: {WHITE};
            border-color: {GOLD};
        }}
        .ps-step.done {{
            background: {GREEN};
            color: {WHITE};
            border-color: {GREEN};
        }}

        .ps-flag-triggered {{
            background: #fff3cd;
            border: 1px solid #f0c040;
            border-left: 4px solid #D4A62A;
            border-radius: 6px;
            padding: 0.7rem 1rem;
            margin-bottom: 0.5rem;
        }}
        .ps-flag-clear {{
            background: #f0faf4;
            border: 1px solid #b7dfca;
            border-left: 4px solid {GREEN};
            border-radius: 6px;
            padding: 0.7rem 1rem;
            margin-bottom: 0.5rem;
        }}

        .ps-banner {{
            border-radius: 8px;
            padding: 0.8rem 1.1rem;
            margin-bottom: 1rem;
            font-size: 0.85rem;
            line-height: 1.5;
        }}
        .ps-banner.info    {{ background:#e8f4fd; border-left:4px solid #2196f3; color:#1a4a6b; }}
        .ps-banner.warning {{ background:#fff8e1; border-left:4px solid {GOLD};  color:#6b4e00; }}
        .ps-banner.success {{ background:#f0faf4; border-left:4px solid {GREEN}; color:#1a4a2e; }}
        .ps-banner.error   {{ background:#fdecea; border-left:4px solid {RED};   color:#6b1a1a; }}

        .ps-dl-bar {{
            background: linear-gradient(90deg, {NAVY} 0%, #1a3550 100%);
            border-radius: 10px;
            padding: 1rem 1.4rem;
            color: {WHITE};
            margin-bottom: 0.8rem;
        }}

        .ps-footer {{
            margin-top: 3rem;
            padding-top: 1.2rem;
            border-top: 1px solid rgba(36,54,75,0.08);
            text-align: center;
            font-size: 0.72rem;
            color: rgba(36,54,75,0.35);
            letter-spacing: 0.04em;
        }}

        .ps-sb-user {{
            background: rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 0.6rem 0.8rem;
            margin: 0.5rem 0;
        }}
        .ps-sb-contact {{
            font-size: 0.7rem;
            color: rgba(255,255,255,0.45) !important;
            line-height: 1.7;
            margin-top: 0.5rem;
        }}

        div[data-testid="stMetric"] {{
            background: {WHITE};
            border: 1px solid rgba(36,54,75,0.10);
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
        }}
        div.stButton > button {{
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.82rem;
        }}
        div.stButton > button[kind="primary"] {{
            background: {GOLD};
            border-color: {GOLD};
            color: {WHITE};
        }}
        div.stButton > button[kind="primary"]:hover {{
            background: #b8860b;
            border-color: #b8860b;
        }}
        div[data-testid="stTabs"] button[role="tab"] {{
            font-weight: 600;
            font-size: 0.82rem;
        }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: {NAVY} !important;
            border-bottom-color: {GOLD} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
