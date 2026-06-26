"""ProSEIT Innovation Agent — Home / Dashboard page."""
from __future__ import annotations
import streamlit as st
from ui.brand import NAVY, GOLD, WHITE, GREEN, SOFT_GREY
from ui.components import page_footer, section_bar, banner


def render() -> None:
    st.markdown(
        f"""
        <div class="ps-hero">
            <div style="color:{GOLD};font-size:0.72rem;font-weight:700;
                        letter-spacing:0.18em;text-transform:uppercase;
                        margin-bottom:0.6rem">
                ProSEIT · Innovation-to-Implementation Agent
            </div>
            <div style="color:{WHITE};font-size:2rem;font-weight:800;
                        line-height:1.15;margin-bottom:0.8rem">
                Turn Ideas Into<br>
                <span style="color:{GOLD}">Implementation-Ready</span><br>
                Product Packages
            </div>
            <div style="color:rgba(255,255,255,0.72);font-size:0.92rem;
                        max-width:520px;line-height:1.6">
                The ProSEIT 19-stage pipeline converts your innovation concept
                into a complete product package — architecture, user stories,
                budget, business plan, governance routing, and a delivery roadmap
                — powered by Claude AI.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl, gold in [
        (c1, "19", "Pipeline Stages", True),
        (c2, "4",  "Edition Tiers",   False),
        (c3, "5",  "Governance Committees", False),
        (c4, "∞",  "Innovation Ideas", True),
    ]:
        with col:
            st.markdown(
                f'<div class="ps-card ps-stat">'
                f'<div class="ps-stat-value{" gold" if gold else ""}">{val}</div>'
                f'<div class="ps-stat-label">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

    section_bar("The 19-Stage Pipeline")

    stages_info = [
        ("00", "Intake & Validation",    "Validate the idea and assess strategic fit."),
        ("01", "Policy & Compliance",    "Regulatory requirements, IP, and applicable laws."),
        ("02", "Concept Development",    "Full product concept with features, KPIs, and risks."),
        ("03", "Edition Planning",       "CE / PE / Enterprise feature sets and licensing."),
        ("04", "Technical Architecture", "ERPNext/Frappe + Angular 18 architecture."),
        ("05", "User Stories",           "Acceptance-criteria-backed stories by phase."),
        ("06", "UX & Wireframes",        "Key screens, user flows, and accessibility."),
        ("07", "Data Model",             "Doctypes, relationships, and migration plan."),
        ("08", "API Design",             "REST endpoints, authentication, and rate limits."),
        ("09", "Integrations",           "External system integrations with protocols and SLAs."),
        ("10", "Security",               "Threat model, OWASP controls, and data protection."),
        ("11", "Testing Strategy",       "Unit, integration, UAT, and performance plans."),
        ("12", "Deployment",             "CI/CD pipeline, IaC, and rollback strategy."),
        ("13", "Documentation",          "Technical docs, user guides, and API reference."),
        ("14", "Budget & Cost",          "Development costs, infrastructure, and TCO."),
        ("15", "Business Plan",          "Market opportunity, revenue model, and projections."),
        ("16", "Governance Routing",     "Committee routing with approvals and sequencing."),
        ("17", "Roadmap",                "Phased delivery with milestones and resources."),
        ("18", "Final Package",          "Executive summary, readiness score, action items."),
    ]

    cols = st.columns(3)
    for i, (num, title, desc) in enumerate(stages_info):
        with cols[i % 3]:
            st.markdown(
                f'<div class="ps-card" style="margin-bottom:0.6rem;min-height:100px">'
                f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.35rem">'
                f'<span style="background:{GOLD};color:{WHITE};border-radius:50%;width:22px;height:22px;'
                f'display:flex;align-items:center;justify-content:center;font-size:0.6rem;font-weight:700;flex-shrink:0">{num}</span>'
                f'<span style="font-weight:700;color:{NAVY};font-size:0.8rem">{title}</span></div>'
                f'<div style="font-size:0.74rem;color:rgba(36,54,75,0.6);line-height:1.4">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    section_bar("How It Works")
    banner(
        "📌 <strong>Demo mode:</strong> This is a public testing instance. "
        "Add your Anthropic API key in the sidebar to run the full pipeline.",
        kind="info",
    )

    c_a, c_b, c_c = st.columns(3)
    for col, num, title, desc in [
        (c_a, "1", "Describe Your Idea",    "Enter your innovation concept. The more detail you provide, the richer the output."),
        (c_b, "2", "Select Stages",         "Quick Run (7 stages, ~3 min) or Full Pipeline (all 19, ~15 min)."),
        (c_c, "3", "Download Your Package", "Download the full package as a ZIP or copy individual stage outputs."),
    ]:
        with col:
            st.markdown(
                f'<div class="ps-card-navy" style="text-align:center;padding:1.4rem">'
                f'<div style="font-size:2rem;font-weight:800;color:{GOLD};line-height:1;margin-bottom:0.5rem">{num}</div>'
                f'<div style="font-weight:700;color:{WHITE};font-size:0.9rem;margin-bottom:0.5rem">{title}</div>'
                f'<div style="font-size:0.78rem;color:rgba(255,255,255,0.65);line-height:1.5">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start New Innovation", type="primary"):
        st.switch_page("pages/new_innovation.py")

    page_footer()


render()
