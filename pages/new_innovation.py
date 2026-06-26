"""ProSEIT Innovation Agent — New Innovation submission page."""
from __future__ import annotations
import io
import streamlit as st
from pipeline.runner import (
    STAGES, STAGE_LABELS, AGRI_SECTORS, AGRI_KB_REGISTRY, run_pipeline,
)
from ui.brand import NAVY, GOLD, WHITE
from ui.components import page_title, section_bar, banner, page_footer, step_indicator

QUICK_STAGES = [
    "00_intake", "02_concept", "14_budget", "15_business_plan",
    "16_governance", "17_roadmap", "18_package",
]
FULL_STAGES = STAGES

SECTOR_OPTIONS = [
    "Engineering & Technology",
    "Professional Development & CPD",
    "Legal & Compliance",
    "Finance & Investment",
    "Healthcare Technology",
    "Education Technology",
    "Agriculture & Agronomy",
    "AgriTech & Precision Agriculture",
    "Agroprocessing & Value Addition",
    "Agriculture Value Chains",
    "Animal Husbandry & Livestock",
    "Forestry, Bamboo & NTFPs",
    "Apiculture & Beekeeping",
    "Smart Infrastructure",
    "Other",
]


def _get_api_key() -> str:
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        return st.session_state.get("api_key_input", "")


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
                "Anthropic API Key",
                type="password",
                key="api_key_input",
                label_visibility="collapsed",
                placeholder="sk-ant-…",
            )
            api_key = api_key_input

    current_step = st.session_state.get("innov_step", 0)
    is_agri = st.session_state.get("innov_is_agri", False)

    if is_agri:
        step_labels = ["Idea", "Knowledge Base", "Stages", "Generate", "Results"]
        display_step = current_step
    else:
        step_labels = ["Idea", "Stages", "Generate", "Results"]
        display_map = {0: 0, 2: 1, 3: 2}
        display_step = display_map.get(current_step, 0)

    step_indicator(step_labels, display_step)

    if current_step == 0:
        _step_idea(api_key)
    elif current_step == 1:
        _step_kb()
    elif current_step == 2:
        _step_stages(is_agri)
    elif current_step == 3:
        _step_generate(api_key)


def _step_idea(api_key: str) -> None:
    section_bar("Step 1 · Describe Your Innovation")

    banner(
        "💡 <strong>Tip:</strong> Describe your innovation in as much detail as possible. "
        "Include the problem it solves, who will use it, and why ProSEIT should build it.",
        kind="info",
    )

    with st.form("idea_form"):
        title = st.text_input(
            "Innovation Title *",
            placeholder="e.g. Smart CPD Tracker for Engineering Professionals",
        )
        idea = st.text_area(
            "Innovation Description *",
            placeholder=(
                "Describe the innovation idea in detail. Include:\n"
                "• What problem does it solve?\n"
                "• Who are the target users?\n"
                "• What makes it unique?\n"
                "• Any technical requirements or constraints?\n"
                "• How does it align with ProSEIT's mandate?"
            ),
            height=240,
        )
        sector = st.selectbox("Primary Sector", SECTOR_OPTIONS)
        submitted = st.form_submit_button("Continue →", type="primary")

    if submitted:
        if not title.strip() or not idea.strip():
            st.error("Title and description are required.")
            return
        if not api_key:
            st.error("Please enter your Anthropic API key in the sidebar.")
            return

        is_agri = sector in AGRI_SECTORS
        st.session_state["innov_title"] = title.strip()
        st.session_state["innov_idea"] = (
            f"**Title:** {title.strip()}\n\n"
            f"**Sector:** {sector}\n\n"
            f"**Description:**\n{idea.strip()}"
        )
        st.session_state["innov_sector"] = sector
        st.session_state["innov_is_agri"] = is_agri
        st.session_state["innov_step"] = 1 if is_agri else 2
        st.rerun()


def _step_kb() -> None:
    section_bar("Step 2 · Knowledge Base")

    sector = st.session_state.get("innov_sector", "")

    banner(
        f"🌾 <strong>Agriculture Innovation Detected</strong> — Sector: <em>{sector}</em>. "
        "Select the validated knowledge sources below. "
        "The agent will cite these in all outputs and include a "
        "<strong>Knowledge Base Integration</strong> section in each stage "
        "explaining how the sources informed its recommendations. "
        "Upload any additional documents you have access to.",
        kind="info",
    )

    tier1 = [s for s in AGRI_KB_REGISTRY if s["tier"] == 1]
    tier2 = [s for s in AGRI_KB_REGISTRY if s["tier"] == 2]

    section_bar("Tier 1 · Official Multi-Crop Catalogues (Recommended)")
    st.markdown(
        '<div style="font-size:0.8rem;color:rgba(36,54,75,0.6);margin-bottom:0.8rem">'
        'Government-validated national and regional catalogues. '
        'All pre-selected — deselect any that are not relevant.</div>',
        unsafe_allow_html=True,
    )

    tier1_options = {
        f"{s['name']} · {', '.join(s['countries'])}": s["id"] for s in tier1
    }
    tier1_selected = st.multiselect(
        "Tier 1 sources",
        options=list(tier1_options.keys()),
        default=list(tier1_options.keys()),
        label_visibility="collapsed",
        key="kb_tier1",
    )
    tier1_ids = [tier1_options[lbl] for lbl in tier1_selected]

    st.markdown("<br>", unsafe_allow_html=True)
    section_bar("Tier 2 · Crop-Specific & Topic-Specific Sources")
    st.markdown(
        '<div style="font-size:0.8rem;color:rgba(36,54,75,0.6);margin-bottom:0.8rem">'
        'Select the sources relevant to your specific crops, livestock, or topic.</div>',
        unsafe_allow_html=True,
    )

    tier2_options = {
        f"{s['name']} · {', '.join(s['crops'])} · {', '.join(s['countries'])}": s["id"]
        for s in tier2
    }
    tier2_selected = st.multiselect(
        "Tier 2 sources",
        options=list(tier2_options.keys()),
        default=[],
        label_visibility="collapsed",
        key="kb_tier2",
    )
    tier2_ids = [tier2_options[lbl] for lbl in tier2_selected]

    all_selected_ids = tier1_ids + tier2_ids

    if all_selected_ids:
        with st.expander(f"📚 Citation preview — {len(all_selected_ids)} source(s) selected"):
            for src_id in all_selected_ids:
                src = next((s for s in AGRI_KB_REGISTRY if s["id"] == src_id), None)
                if src:
                    st.markdown(
                        f'<div style="font-size:0.8rem;padding:0.35rem 0;'
                        f'border-bottom:1px solid #eee">'
                        f'<strong>{src["name"]}</strong><br>'
                        f'<span style="color:#666;font-style:italic">{src["citation"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_bar("Upload Additional Knowledge Base Documents")

    banner(
        "📄 <strong>Source not in the list above?</strong> "
        "Upload PDFs or TXT files, or paste content directly below. "
        "Use this for local extension manuals, NBS data, ministry crop reports, "
        "district agronomy data, or any other validated source you have access to.",
        kind="info",
    )

    uploaded_files = st.file_uploader(
        "Upload documents (PDF or TXT, multiple allowed)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key="kb_uploads",
    )

    paste_content = st.text_area(
        "Or paste content directly from a validated source",
        height=180,
        placeholder=(
            "Include the source name and year at the top so the agent can cite it.\n\n"
            "Example:\n"
            "Source: Uganda Banana Production Manual, NARO, 2019\n\n"
            "Content: ...\n"
        ),
        key="kb_paste",
    )

    user_content_parts: list[str] = []

    if uploaded_files:
        for f in uploaded_files:
            try:
                if f.type == "text/plain":
                    text = f.read().decode("utf-8", errors="ignore")
                    user_content_parts.append(f"=== {f.name} ===\n{text}")
                elif f.type == "application/pdf":
                    try:
                        import pypdf
                        reader = pypdf.PdfReader(io.BytesIO(f.read()))
                        pages: list[str] = []
                        for i, page in enumerate(reader.pages, 1):
                            extracted = page.extract_text() or ""
                            if extracted.strip():
                                pages.append(f"[Page {i}]\n{extracted}")
                        user_content_parts.append(f"=== {f.name} ===\n" + "\n\n".join(pages))
                    except ImportError:
                        user_content_parts.append(
                            f"=== {f.name} ===\n"
                            "[PDF uploaded — pypdf not installed, text extraction skipped. "
                            "Agent will reference by filename.]"
                        )
                    except Exception as e:
                        user_content_parts.append(
                            f"=== {f.name} ===\n"
                            f"[PDF parse error: {e}. Consider converting to TXT.]"
                        )
            except Exception as e:
                st.warning(f"Could not read {f.name}: {e}")

    if paste_content.strip():
        user_content_parts.append(f"=== User-Pasted Content ===\n{paste_content.strip()}")

    user_content = "\n\n".join(user_content_parts)

    if user_content:
        file_count = len(uploaded_files) if uploaded_files else 0
        msg = f"✓ {file_count} file(s) ready" if file_count else "✓ Pasted content ready"
        if file_count and paste_content.strip():
            msg = f"✓ {file_count} file(s) + pasted content ready"
        st.success(msg)

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_go, _ = st.columns([1, 1, 3])
    with c_back:
        if st.button("← Back"):
            st.session_state["innov_step"] = 0
            st.rerun()
    with c_go:
        btn_label = "Continue →" if all_selected_ids or user_content else "Skip →"
        if st.button(btn_label, type="primary"):
            st.session_state["innov_kb_context"] = {
                "selected_sources": all_selected_ids,
                "user_content": user_content,
            }
            st.session_state["innov_step"] = 2
            st.rerun()


def _step_stages(is_agri: bool = False) -> None:
    step_num = "3" if is_agri else "2"
    section_bar(f"Step {step_num} · Select Pipeline Stages")

    banner(
        "⚡ <strong>Quick Run</strong> executes 7 key stages in ~3 minutes. "
        "<strong>Full Pipeline</strong> runs all 19 stages in ~15 minutes.",
        kind="info",
    )

    run_mode = st.radio(
        "Run mode",
        ["Quick Run (7 stages — recommended for first use)", "Full Pipeline (all 19 stages)"],
        index=0,
    )

    if "Full Pipeline" in run_mode:
        selected = FULL_STAGES
        st.markdown(
            '<div style="font-size:0.8rem;color:rgba(36,54,75,0.55);'
            'margin-top:0.5rem">All 19 stages selected</div>',
            unsafe_allow_html=True,
        )
    else:
        selected = QUICK_STAGES
        st.markdown(
            '<div style="font-size:0.8rem;color:rgba(36,54,75,0.55);'
            'margin-top:0.5rem">7 core stages selected: '
            + ", ".join(STAGE_LABELS[s].split(" · ")[1] for s in selected)
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_go, _ = st.columns([1, 1, 3])
    with c_back:
        if st.button("← Back"):
            st.session_state["innov_step"] = 1 if is_agri else 0
            st.rerun()
    with c_go:
        if st.button("Run Pipeline →", type="primary"):
            st.session_state["innov_selected_stages"] = selected
            st.session_state["innov_step"] = 3
            st.rerun()


def _step_generate(api_key: str) -> None:
    is_agri = st.session_state.get("innov_is_agri", False)
    step_num = "4" if is_agri else "3"
    section_bar(f"Step {step_num} · Running the Pipeline")

    if "innov_results" in st.session_state:
        st.success("Pipeline complete! Redirecting to results…")
        st.session_state["innov_step"] = 0
        st.switch_page("pages/results.py")
        return

    idea = st.session_state.get("innov_idea", "")
    selected = st.session_state.get("innov_selected_stages", QUICK_STAGES)
    kb_context = st.session_state.get("innov_kb_context")

    if not idea or not api_key:
        st.error("Missing idea or API key. Please start again.")
        if st.button("← Start over"):
            st.session_state["innov_step"] = 0
            st.rerun()
        return

    if kb_context:
        src_count = len(kb_context.get("selected_sources", []))
        has_upload = bool(kb_context.get("user_content", "").strip())
        kb_note = f"{src_count} validated KB source(s)"
        if has_upload:
            kb_note += " + user-provided content"
        banner(
            f"📚 <strong>Knowledge Base active</strong> — {kb_note}. "
            "All stage outputs will include inline citations and a "
            "Knowledge Base Integration section.",
            kind="info",
        )

    banner(
        f"Running <strong>{len(selected)}</strong> pipeline stages for: "
        f"<em>{st.session_state.get('innov_title', 'your innovation')}</em>. "
        "This may take several minutes. Please keep this tab open.",
        kind="warning",
    )

    progress_bar = st.progress(0.0)
    status_text = st.empty()

    def on_progress(label: str, frac: float) -> None:
        progress_bar.progress(min(frac, 1.0))
        status_text.markdown(
            f'<div style="font-size:0.82rem;color:rgba(36,54,75,0.7)">'
            f'⚙️ {label}…</div>',
            unsafe_allow_html=True,
        )

    try:
        results = run_pipeline(
            idea=idea,
            api_key=api_key,
            stages=selected,
            progress_cb=on_progress,
            kb_context=kb_context,
        )
        progress_bar.progress(1.0)
        status_text.markdown(
            '<div style="color:#00843D;font-weight:700">✓ Pipeline complete!</div>',
            unsafe_allow_html=True,
        )
        st.session_state["innov_results"] = results
        st.session_state["innov_results_title"] = st.session_state.get("innov_title", "Innovation")
        st.success("All stages complete. Loading results…")
        st.switch_page("pages/results.py")
    except Exception as exc:
        st.error(f"Pipeline error: {exc}")
        if st.button("← Back to stage selection"):
            st.session_state["innov_step"] = 2
            st.rerun()


render()
