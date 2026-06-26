"""ProSEIT Innovation Agent — Home / Dashboard page."""
from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st
from ui.brand import NAVY, GOLD, WHITE, GREEN, SOFT_GREY
from ui.components import page_footer, section_bar, banner


def _logo_b64() -> str:
    svg_path = Path(__file__).parent.parent / "static" / "proseit_logo.svg"
    return base64.b64encode(svg_path.read_bytes()).decode()


def render() -> None:
    logo = _logo_b64()
    st.markdown(
        f"""
        <div class="ps-hero" style="position:relative;overflow:hidden">
            <img src="data:image/svg+xml;base64,{logo}"
                 style="position:absolute;top:50%;right:-10px;
                        transform:translateY(-50%);
                        height:160px;width:auto;
                        opacity:0.45;pointer-events:none;
                        filter:brightness(10)"
                 aria-hidden="true" />
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

    # ── Stats row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""<div class="ps-card ps-stat">
                <div class="ps-stat-value gold">19</div>
                <div class="ps-stat-label">Pipeline Stages</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="ps-card ps-stat">
                <div class="ps-stat-value">4</div>
                <div class="ps-stat-label">Edition Tiers</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="ps-card ps-stat">
                <div class="ps-stat-value">5</div>
                <div class="ps-stat-label">Governance Committees</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""<div class="ps-card ps-stat">
                <div class="ps-stat-value gold">∞</div>
                <div class="ps-stat-label">Innovation Ideas</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Pipeline overview ──────────────────────────────────────────────────────
    section_bar("The 19-Stage Pipeline")

    stages_info = [
        ("00", "Intake & Validation", "Validate the idea and assess strategic fit with ProSEIT's mandate."),
        ("01", "Policy & Compliance", "Identify regulatory requirements, IP considerations, and applicable laws."),
        ("02", "Concept Development", "Develop the full product concept with features, KPIs, and risk analysis."),
        ("03", "Edition Planning", "Define CE / PE / Enterprise feature sets and licensing model."),
        ("04", "Technical Architecture", "Design the ERPNext/Frappe + Angular 18 architecture."),
        ("05", "User Stories", "Write acceptance-criteria-backed user stories grouped by phase."),
        ("06", "UX & Wireframes", "Describe key screens, user flows, and accessibility requirements."),
        ("07", "Data Model", "Define doctypes, relationships, and data migration plan."),
        ("08", "API Design", "Specify REST endpoints, authentication, and rate limits."),
        ("09", "Integrations", "Map all external system integrations with protocols and SLAs."),
        ("10", "Security", "Threat model, OWASP controls, and data protection measures."),
        ("11", "Testing Strategy", "Unit, integration, UAT, and performance testing plans."),
        ("12", "Deployment", "CI/CD pipeline, infrastructure-as-code, and rollback strategy."),
        ("13", "Documentation", "Technical docs, user guides, and API reference plan."),
        ("14", "Budget & Cost", "Development costs, infrastructure, TCO, and break-even analysis."),
        ("15", "Business Plan", "Market opportunity, revenue model, go-to-market, and projections."),
        ("16", "Governance Routing", "Committee routing with required approvals and priority sequencing."),
        ("17", "Roadmap", "Phased delivery plan with milestones, sprints, and resource requirements."),
        ("18", "Final Package", "Executive summary, readiness score, and top action items."),
    ]

    cols = st.columns(3)
    for i, (num, title, desc) in enumerate(stages_info):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="ps-card" style="margin-bottom:0.6rem;min-height:110px">
                    <div style="display:flex;align-items:center;gap:0.5rem;
                                margin-bottom:0.4rem">
                        <span style="background:{GOLD};color:{WHITE};
                                     border-radius:50%;width:24px;height:24px;
                                     display:flex;align-items:center;
                                     justify-content:center;font-size:0.65rem;
                                     font-weight:700;flex-shrink:0">{num}</span>
                        <span style="font-weight:700;color:{NAVY};
                                     font-size:0.82rem">{title}</span>
                    </div>
                    <div style="font-size:0.75rem;color:rgba(36,54,75,0.6);
                                line-height:1.4">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── How it works ──────────────────────────────────────────────────────────
    section_bar("How It Works")
    banner(
        "📌 <strong>Demo mode:</strong> This is a public testing instance. "
        "Add your Anthropic API key in the sidebar to run the full pipeline. "
        "All outputs are generated fresh — nothing is stored on our servers.",
        kind="info",
    )

    c_a, c_b, c_c = st.columns(3)
    steps = [
        ("1", "Describe Your Idea", "Enter your innovation concept on the New Innovation page. The more detail you provide, the richer the output."),
        ("2", "Select Stages", "Choose which of the 19 pipeline stages to run. Run all for a complete package, or select key stages for a quick assessment."),
        ("3", "Download Your Package", "Claude generates each stage output. Download the full package as a ZIP or copy individual sections."),
    ]
    for col, (num, title, desc) in zip([c_a, c_b, c_c], steps):
        with col:
            st.markdown(
                f"""
                <div class="ps-card-navy" style="text-align:center;padding:1.4rem">
                    <div style="font-size:2rem;font-weight:800;color:{GOLD};
                                line-height:1;margin-bottom:0.5rem">{num}</div>
                    <div style="font-weight:700;color:{WHITE};font-size:0.9rem;
                                margin-bottom:0.5rem">{title}</div>
                    <div style="font-size:0.78rem;color:rgba(255,255,255,0.65);
                                line-height:1.5">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start New Innovation", type="primary", use_container_width=False):
        st.switch_page("pages/new_innovation.py")

    page_footer()


render()
