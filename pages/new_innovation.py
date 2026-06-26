"""ProSEIT Innovation Agent — New Innovation submission page."""
from __future__ import annotations
import streamlit as st
from pipeline.runner import STAGES, STAGE_LABELS, run_pipeline
from ui.brand import NAVY, GOLD, WHITE
from ui.components import page_title, section_bar, banner, page_footer, step_indicator

QUICK_STAGES = [
    "00_intake", "02_concept", "14_budget", "15_business_plan",
    "16_governance", "17_roadmap", "18_package",
]
FULL_STAGES = STAGES


def render() -> None:
    page_title("New Innovation", "Submit your innovation idea and run the ProSEIT pipeline.")

    api_key = ""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass

    if not api_key:
        with st.sidebar:
            st.markdown(
                f'<div style="color:{GOLD};font-size:0.72rem;font-weight:700;'
                f'letter-spacing:0.1em;text-transform:uppercase;margin-top:1rem;'
                f'margin-bottom:0.3rem">API Key</div>',
                unsafe_allow_html=True,
            )
            api_key_input = st.text_input(
                "Anthropic API Key", type="password", key="api_key_input",
                label_visibility="collapsed", placeholder="sk-ant-…",
            )
            api_key = api_key_input

    step_labels = ["Idea", "Stages", "Generate", "Results"]
    current_step = st.session_state.get("innov_step", 0)
    step_indicator(step_labels, current_step)

    if current_step == 0:
        _step_idea(api_key)
    elif current_step == 1:
        _step_stages()
    elif current_step == 2:
        _step_generate(api_key)


def _step_idea(api_key: str) -> None:
    section_bar("Step 1 · Describe Your Innovation")
    banner(
        "💡 <strong>Tip:</strong> Describe your innovation in as much detail as possible. "
        "Include the problem it solves, who will use it, and why ProSEIT should build it.",
        kind="info",
    )
    with st.form("idea_form"):
        title = st.text_input("Innovation Title *", placeholder="e.g. Smart CPD Tracker for Engineering Professionals")
        idea = st.text_area(
            "Innovation Description *",
            placeholder="Describe the innovation in detail.\n• What problem does it solve?\n• Who are the target users?\n• What makes it unique?\n• Technical requirements?\n• ProSEIT alignment?",
            height=240,
        )
        sector = st.selectbox("Primary Sector", [
            "Engineering & Technology", "Professional Development & CPD",
            "Legal & Compliance", "Finance & Investment", "Healthcare Technology",
            "Education Technology", "Agriculture Technology", "Smart Infrastructure", "Other",
        ])
        submitted = st.form_submit_button("Continue →", type="primary")

    if submitted:
        if not title.strip() or not idea.strip():
            st.error("Title and description are required.")
            return
        if not api_key:
            st.error("Please enter your Anthropic API key in the sidebar.")
            return
        st.session_state["innov_title"] = title.strip()
        st.session_state["innov_idea"] = f"**Title:** {title.strip()}\n\n**Sector:** {sector}\n\n**Description:**\n{idea.strip()}"
        st.session_state["innov_step"] = 1
        st.rerun()


def _step_stages() -> None:
    section_bar("Step 2 · Select Pipeline Stages")
    banner(
        "⚡ <strong>Quick Run</strong> executes 7 key stages (~3 min). "
        "<strong>Full Pipeline</strong> runs all 19 stages (~15 min).",
        kind="info",
    )
    run_mode = st.radio("Run mode", [
        "Quick Run (7 stages — recommended for first use)",
        "Full Pipeline (all 19 stages)",
    ], index=0)
    selected = FULL_STAGES if "Full Pipeline" in run_mode else QUICK_STAGES
    st.markdown(
        f'<div style="font-size:0.8rem;color:rgba(36,54,75,0.55);margin-top:0.5rem">'
        + ("All 19 stages selected" if "Full Pipeline" in run_mode
           else "7 core stages: " + ", ".join(STAGE_LABELS[s].split(" · ")[1] for s in selected))
        + "</div>", unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_go, _ = st.columns([1, 1, 3])
    with c_back:
        if st.button("← Back"):
            st.session_state["innov_step"] = 0
            st.rerun()
    with c_go:
        if st.button("Run Pipeline →", type="primary"):
            st.session_state["innov_selected_stages"] = selected
            st.session_state["innov_step"] = 2
            st.rerun()


def _step_generate(api_key: str) -> None:
    section_bar("Step 3 · Running the Pipeline")
    if "innov_results" in st.session_state:
        st.session_state["innov_step"] = 0
        st.switch_page("pages/results.py")
        return
    idea = st.session_state.get("innov_idea", "")
    selected = st.session_state.get("innov_selected_stages", QUICK_STAGES)
    if not idea or not api_key:
        st.error("Missing idea or API key. Please start again.")
        if st.button("← Start over"):
            st.session_state["innov_step"] = 0
            st.rerun()
        return
    banner(
        f"Running <strong>{len(selected)}</strong> stages for "
        f"<em>{st.session_state.get('innov_title', 'your innovation')}</em>. "
        "Keep this tab open.",
        kind="warning",
    )
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    def on_progress(label: str, frac: float) -> None:
        progress_bar.progress(min(frac, 1.0))
        status_text.markdown(
            f'<div style="font-size:0.82rem;color:rgba(36,54,75,0.7)">⚙️ {label}…</div>',
            unsafe_allow_html=True,
        )

    try:
        results = run_pipeline(idea=idea, api_key=api_key, stages=selected, progress_cb=on_progress)
        progress_bar.progress(1.0)
        status_text.markdown('<div style="color:#00843D;font-weight:700">✓ Pipeline complete!</div>', unsafe_allow_html=True)
        st.session_state["innov_results"] = results
        st.session_state["innov_results_title"] = st.session_state.get("innov_title", "Innovation")
        st.switch_page("pages/results.py")
    except Exception as exc:
        st.error(f"Pipeline error: {exc}")
        if st.button("← Back to stage selection"):
            st.session_state["innov_step"] = 1
            st.rerun()


render()
