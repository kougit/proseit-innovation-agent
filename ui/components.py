"""Shared UI components for ProSEIT Innovation Agent."""
from __future__ import annotations
import streamlit as st
from ui.brand import NAVY, GOLD, WHITE, GREEN, RED, AMBER, DARK_TEXT


def page_title(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="ps-page-title">
            <h1>{title}</h1>
            {"<p>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_bar(label: str, hint: str = "") -> None:
    st.markdown(
        f"""
        <div class="ps-section-bar">
            <span>{label}</span>
            {"<span style='font-size:0.75rem;color:rgba(36,54,75,0.45);font-weight:400'>" + hint + "</span>" if hint else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_footer() -> None:
    st.markdown(
        """
        <div class="ps-footer">
            ProSEIT Innovation-to-Implementation Agent &nbsp;&middot;&nbsp;
            Powered by Claude AI &nbsp;&middot;&nbsp;
            <a href="https://proseit.org" style="color:inherit">proseit.org</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def banner(text: str, kind: str = "info") -> None:
    st.markdown(
        f'<div class="ps-banner {kind}">{text}</div>',
        unsafe_allow_html=True,
    )


def badge(text: str, colour: str = "navy") -> str:
    return f'<span class="ps-badge {colour}">{text}</span>'


def stat_card(value: str, label: str, gold: bool = False) -> None:
    cls = "gold" if gold else ""
    st.markdown(
        f"""
        <div class="ps-card ps-stat">
            <div class="ps-stat-value {cls}">{value}</div>
            <div class="ps-stat-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(api_key_provided: bool = False) -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center;padding:1.2rem 0 1rem">
                <div style="font-size:1.6rem;font-weight:800;color:{WHITE};
                            letter-spacing:-0.01em;line-height:1">ProSEIT</div>
                <div style="font-size:0.62rem;color:{GOLD};font-weight:700;
                            letter-spacing:0.18em;text-transform:uppercase;
                            margin-top:0.2rem">Innovation Agent</div>
                <div style="height:2px;background:linear-gradient(90deg,transparent,{GOLD},transparent);
                            margin:0.8rem auto 0;width:60%"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="ps-nav-lbl">Navigation</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ps-sb-contact">
                <div style="color:{GOLD} !important;font-weight:700;
                            font-size:0.68rem;letter-spacing:0.1em;
                            text-transform:uppercase;margin-bottom:0.3rem">About</div>
                Converts innovation ideas into full<br>
                implementation-ready product packages<br>
                using Claude AI and the ProSEIT<br>
                19-stage pipeline.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="ps-sb-contact" style="margin-top:1rem">
                <div style="color:{GOLD} !important;font-weight:700;
                            font-size:0.68rem;letter-spacing:0.1em;
                            text-transform:uppercase;margin-bottom:0.3rem">Contact</div>
                ProSEIT Secretariat<br>
                info@proseit.org
            </div>
            """,
            unsafe_allow_html=True,
        )
        if api_key_provided:
            st.markdown(
                f'<div style="margin-top:1rem">{badge("API Key Active", "green")}</div>',
                unsafe_allow_html=True,
            )


def step_indicator(steps: list[str], current: int) -> None:
    parts = []
    for i, s in enumerate(steps):
        cls = "done" if i < current else ("active" if i == current else "")
        parts.append(f'<span class="ps-step {cls}">{s}</span>')
    st.markdown(
        f'<div class="ps-steps">{" ".join(parts)}</div>',
        unsafe_allow_html=True,
    )
