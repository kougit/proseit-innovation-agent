"""ProSEIT Innovation Agent — New Innovation submission page."""
from __future__ import annotations
import io
import streamlit as st
from pipeline.runner import (
    STAGES, STAGE_LABELS, AGRI_SECTORS, AGRI_KB_REGISTRY,
    _prompt_for_stage, SYSTEM_PROMPT, run_pipeline,
)
from pipeline.client import call_claude
from pipeline.document_builder import (
    STAGE_DELIVERABLES, EXCEL_STAGES, PPTX_STAGES,
    build_word_doc, build_excel_doc, build_pptx_doc,
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

_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


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

    resume_mode: bool = st.session_state.get("innov_resume_mode", False)
    current_step = st.session_state.get("innov_step", 0)
    is_agri = st.session_state.get("innov_is_agri", False)

    if is_agri:
        step_labels = ["Idea", "Knowledge Base", "Stages", "Generate", "Results"]
        display_step = current_step
    else:
        step_labels = ["Idea", "Stages", "Generate", "Results"]
        display_map = {0: 0, 2: 1, 3: 2, 4: 3}
        display_step = display_map.get(current_step, 0)

    step_indicator(step_labels, display_step)

    if current_step == 0:
        _step_idea(api_key)
    elif current_step == 1:
        _step_kb()
    elif current_step == 2:
        _step_stages(is_agri, resume_mode)
    elif current_step == 3:
        _step_generate(api_key, resume_mode)


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
        "Select validated knowledge sources. The agent will cite these in all outputs.",
        kind="info",
    )

    tier1 = [s for s in AGRI_KB_REGISTRY if s["tier"] == 1]
    tier2 = [s for s in AGRI_KB_REGISTRY if s["tier"] == 2]

    section_bar("Tier 1 · Official Multi-Crop Catalogues")
    tier1_options = {f"{s['name']} · {', '.join(s['countries'])}": s["id"] for s in tier1}
    tier1_selected = st.multiselect(
        "Tier 1 sources", options=list(tier1_options.keys()),
        default=list(tier1_options.keys()), label_visibility="collapsed", key="kb_tier1",
    )
    tier1_ids = [tier1_options[lbl] for lbl in tier1_selected]

    st.markdown("<br>", unsafe_allow_html=True)
    section_bar("Tier 2 · Crop-Specific & Topic-Specific Sources")
    tier2_options = {
        f"{s['name']} · {', '.join(s['crops'])} · {', '.join(s['countries'])}": s["id"]
        for s in tier2
    }
    tier2_selected = st.multiselect(
        "Tier 2 sources", options=list(tier2_options.keys()),
        default=[], label_visibility="collapsed", key="kb_tier2",
    )
    tier2_ids = [tier2_options[lbl] for lbl in tier2_selected]
    all_ids = tier1_ids + tier2_ids

    if all_ids:
        with st.expander(f"📚 Citation preview — {len(all_ids)} source(s)"):
            for sid in all_ids:
                src = next((s for s in AGRI_KB_REGISTRY if s["id"] == sid), None)
                if src:
                    st.markdown(
                        f'<div style="font-size:0.8rem;padding:0.35rem 0;border-bottom:1px solid #eee">'
                        f'<strong>{src["name"]}</strong><br>'
                        f'<span style="color:#666;font-style:italic">{src["citation"]}</span></div>',
                        unsafe_allow_html=True,
                    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_bar("Upload Additional Knowledge Base Documents")
    banner(
        "📄 <strong>Have a source not listed above?</strong> Upload PDFs/TXT or paste content below.",
        kind="info",
    )
    uploaded_files = st.file_uploader(
        "Upload documents (PDF or TXT)", type=["pdf", "txt"],
        accept_multiple_files=True, key="kb_uploads",
    )
    paste_content = st.text_area(
        "Or paste content from a validated source", height=150, key="kb_paste",
        placeholder="Include source name and year at the top so the agent can cite it.",
    )

    parts: list[str] = []
    if uploaded_files:
        for f in uploaded_files:
            try:
                if f.type == "text/plain":
                    parts.append(f"=== {f.name} ===\n{f.read().decode('utf-8', errors='ignore')}")
                elif f.type == "application/pdf":
                    try:
                        import pypdf
                        reader = pypdf.PdfReader(io.BytesIO(f.read()))
                        pages = []
                        for i, page in enumerate(reader.pages, 1):
                            txt = page.extract_text() or ""
                            if txt.strip():
                                pages.append(f"[Page {i}]\n{txt}")
                        parts.append(f"=== {f.name} ===\n" + "\n\n".join(pages))
                    except ImportError:
                        parts.append(f"=== {f.name} ===\n[pypdf not installed — text extraction skipped]")
                    except Exception as e:
                        parts.append(f"=== {f.name} ===\n[PDF parse error: {e}]")
            except Exception as e:
                st.warning(f"Could not read {f.name}: {e}")
    if paste_content.strip():
        parts.append(f"=== User-Pasted Content ===\n{paste_content.strip()}")
    user_content = "\n\n".join(parts)

    if user_content:
        st.success(f"✓ {len(uploaded_files) if uploaded_files else 0} file(s) + content ready")

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_go, _ = st.columns([1, 1, 3])
    with c_back:
        if st.button("← Back"):
            st.session_state["innov_step"] = 0
            st.rerun()
    with c_go:
        btn_label = "Continue →" if all_ids or user_content else "Skip →"
        if st.button(btn_label, type="primary"):
            st.session_state["innov_kb_context"] = {
                "selected_sources": all_ids,
                "user_content": user_content,
            }
            st.session_state["innov_step"] = 2
            st.rerun()


def _step_stages(is_agri: bool = False, resume_mode: bool = False) -> None:
    step_num = "3" if is_agri else "2"
    existing_results: dict = st.session_state.get("innov_results", {})
    done_stages = set(existing_results.keys())

    if resume_mode and done_stages:
        section_bar(f"Step {step_num} · Continue Pipeline — Select Remaining Stages")
        banner(
            f"▶️ <strong>Resume mode</strong> — {len(done_stages)} stage(s) already completed. "
            "Select which remaining stages to run next.",
            kind="info",
        )

        # Show completed stages (locked)
        with st.expander(f"✅ {len(done_stages)} completed stage(s) — will not be re-run", expanded=False):
            for s in STAGES:
                if s in done_stages:
                    st.markdown(
                        f'<div style="font-size:0.8rem;color:rgba(36,54,75,0.5);padding:0.1rem 0">'  
                        f'✔️ {STAGE_LABELS.get(s, s)}</div>',
                        unsafe_allow_html=True,
                    )

        # Pending stages as checkboxes
        pending = [s for s in STAGES if s not in done_stages]
        st.markdown(
            '<div style="font-size:0.82rem;color:rgba(36,54,75,0.7);margin:0.6rem 0 0.8rem">'
            'Select stages to run next:</div>',
            unsafe_allow_html=True,
        )
        selected: list[str] = []
        for stage in pending:
            label = STAGE_LABELS.get(stage, stage)
            deliverables = STAGE_DELIVERABLES.get(stage, ["Word (.docx)"])
            c1, c2 = st.columns([3, 2])
            with c1:
                checked = st.checkbox(label, value=True, key=f"rcb_{stage}")
            with c2:
                st.markdown(
                    f'<div style="font-size:0.71rem;color:rgba(36,54,75,0.45);'
                    f'padding-top:0.42rem">{", ".join(deliverables)}</div>',
                    unsafe_allow_html=True,
                )
            if checked:
                selected.append(stage)

        if selected:
            st.markdown(
                f'<div style="font-size:0.8rem;color:rgba(36,54,75,0.55);margin-top:0.4rem">'
                f'{len(selected)} stage(s) selected to run</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Select at least one stage to continue.")

        st.markdown("<br>", unsafe_allow_html=True)
        c_back, c_go, _ = st.columns([1, 2, 2])
        with c_back:
            if st.button("← Back to Results"):
                st.session_state["innov_resume_mode"] = False
                st.switch_page("pages/results.py")
        with c_go:
            if st.button(
                f"Run {len(selected)} Stage(s) →",
                type="primary",
                disabled=(not selected),
            ):
                st.session_state["innov_selected_stages"] = selected
                st.session_state["innov_step"] = 3
                # In resume mode, keep innov_results — only reset run index
                st.session_state.pop("innov_run_idx", None)
                st.session_state.pop("innov_context", None)
                st.rerun()
        return

    # ── Normal (non-resume) stage selection ───────────────────────────────────
    section_bar(f"Step {step_num} · Select Pipeline Stages")
    banner(
        "⚡ <strong>Quick Run</strong> — 7 key stages (~3 min). "
        "<strong>Full Pipeline</strong> — all 19 stages (~15 min). "
        "<strong>Custom</strong> — choose individual stages and see their deliverables.",
        kind="info",
    )

    run_mode = st.radio(
        "Run mode",
        [
            "Quick Run (7 stages — recommended for first use)",
            "Full Pipeline (all 19 stages)",
            "Custom — choose individual stages",
        ],
        index=0,
        key="run_mode_radio",
    )

    selected_normal: list[str] = []

    if "Full Pipeline" in run_mode:
        selected_normal = list(FULL_STAGES)
        st.markdown(
            '<div style="font-size:0.8rem;color:rgba(36,54,75,0.55);margin-top:0.5rem">'
            'All 19 stages selected</div>',
            unsafe_allow_html=True,
        )
    elif "Quick Run" in run_mode:
        selected_normal = list(QUICK_STAGES)
        st.markdown(
            '<div style="font-size:0.8rem;color:rgba(36,54,75,0.55);margin-top:0.5rem">7 core stages: '
            + ", ".join(STAGE_LABELS[s].split(" · ")[1] for s in selected_normal)
            + "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="font-size:0.82rem;color:rgba(36,54,75,0.7);'
            'margin:0.6rem 0 0.8rem">Check the stages to include. '
            'Deliverables are shown for each stage.</div>',
            unsafe_allow_html=True,
        )
        default_on = set(QUICK_STAGES)
        custom: list[str] = []
        for stage in STAGES:
            label = STAGE_LABELS.get(stage, stage)
            deliverables = STAGE_DELIVERABLES.get(stage, ["Word (.docx)"])
            c1, c2 = st.columns([3, 2])
            with c1:
                checked = st.checkbox(
                    label, value=(stage in default_on), key=f"scb_{stage}",
                )
            with c2:
                st.markdown(
                    f'<div style="font-size:0.71rem;color:rgba(36,54,75,0.45);'
                    f'padding-top:0.42rem">{", ".join(deliverables)}</div>',
                    unsafe_allow_html=True,
                )
            if checked:
                custom.append(stage)
        selected_normal = custom
        if selected_normal:
            st.markdown(
                f'<div style="font-size:0.8rem;color:rgba(36,54,75,0.55);margin-top:0.4rem">'
                f'{len(selected_normal)} stage(s) selected</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("Select at least one stage to continue.")

    st.markdown("<br>", unsafe_allow_html=True)
    c_back, c_go, _ = st.columns([1, 1, 3])
    with c_back:
        if st.button("← Back"):
            st.session_state["innov_step"] = 1 if is_agri else 0
            st.rerun()
    with c_go:
        if st.button("Run Pipeline →", type="primary", disabled=(not selected_normal)):
            st.session_state["innov_selected_stages"] = selected_normal
            st.session_state["innov_step"] = 3
            # Fresh run: clear any previous run state
            for k in ["innov_run_idx", "innov_context", "innov_results"]:
                st.session_state.pop(k, None)
            st.rerun()


def _mid_dl_row(stage: str, content: str, title: str) -> None:
    lbl = STAGE_LABELS.get(stage, stage)
    ncols = 1 + (1 if stage in EXCEL_STAGES else 0) + (1 if stage in PPTX_STAGES else 0)
    cols = st.columns([3] + [1] * ncols)
    with cols[0]:
        st.markdown(
            f'<div style="font-size:0.78rem;font-weight:600;color:{NAVY};'
            f'padding:0.3rem 0">{lbl}</div>',
            unsafe_allow_html=True,
        )
    ci = 1
    slug = title[:24].replace(" ", "_")
    try:
        with cols[ci]:
            st.download_button(
                "📄",
                data=build_word_doc(stage, lbl, content, title),
                file_name=f"{stage}_{slug}.docx",
                mime=_DOCX_MIME,
                key=f"mid_w_{stage}",
                use_container_width=True,
            )
        ci += 1
    except Exception:
        pass
    if stage in EXCEL_STAGES:
        try:
            with cols[ci]:
                st.download_button(
                    "📊",
                    data=build_excel_doc(stage, lbl, content, title),
                    file_name=f"{stage}_{slug}.xlsx",
                    mime=_XLSX_MIME,
                    key=f"mid_x_{stage}",
                    use_container_width=True,
                )
            ci += 1
        except Exception:
            pass
    if stage in PPTX_STAGES:
        try:
            with cols[ci]:
                st.download_button(
                    "🎥",
                    data=build_pptx_doc(stage, lbl, content, title),
                    file_name=f"{stage}_{slug}.pptx",
                    mime=_PPTX_MIME,
                    key=f"mid_p_{stage}",
                    use_container_width=True,
                )
        except Exception:
            pass


def _step_generate(api_key: str, resume_mode: bool = False) -> None:
    is_agri = st.session_state.get("innov_is_agri", False)
    step_num = "4" if is_agri else "3"
    section_bar(f"Step {step_num} · Running the Pipeline")

    idea = st.session_state.get("innov_idea", "")
    selected: list[str] = st.session_state.get("innov_selected_stages", QUICK_STAGES)
    kb_context = st.session_state.get("innov_kb_context")
    title = st.session_state.get("innov_title", "Innovation")

    if not idea or not api_key:
        st.error("Missing idea or API key. Please start again.")
        if st.button("← Start over"):
            st.session_state["innov_step"] = 0
            st.rerun()
        return

    # Initialise per-run state on first entry.
    # In resume mode, preserve innov_results — only reset the run index.
    if "innov_run_idx" not in st.session_state:
        st.session_state["innov_run_idx"] = 0
        if not resume_mode:
            st.session_state["innov_results"] = {}
        else:
            # Seed context from already-completed stages so later stages have prior output
            existing = st.session_state.get("innov_results", {})
            st.session_state["innov_context"] = dict(existing)
        if "innov_results" not in st.session_state:
            st.session_state["innov_results"] = {}
        st.session_state["innov_context"] = dict(st.session_state.get("innov_results", {}))
        st.session_state["innov_results_title"] = title

    run_idx: int = st.session_state["innov_run_idx"]
    results: dict[str, str] = st.session_state["innov_results"]
    total = len(selected)

    st.progress(run_idx / total if total else 1.0)

    if run_idx < total:
        stage = selected[run_idx]
        slabel = STAGE_LABELS.get(stage, stage)
        st.markdown(
            f'<div style="font-size:0.82rem;color:rgba(36,54,75,0.7);margin-bottom:0.8rem">'
            f'⚙️ Running: <strong>{slabel}</strong> ({run_idx + 1} of {total})…</div>',
            unsafe_allow_html=True,
        )

        if results:
            with st.expander(
                f"✅ {len(results)} stage(s) complete — download now",
                expanded=False,
            ):
                banner(
                    "You can download completed stages while the pipeline continues running.",
                    kind="info",
                )
                for s, c in results.items():
                    _mid_dl_row(s, c, title)

        try:
            context: dict[str, str] = st.session_state.get("innov_context", {})
            prompt = _prompt_for_stage(stage, idea, context, kb_context=kb_context)
            output = call_claude(prompt, system=SYSTEM_PROMPT, api_key=api_key)
            st.session_state["innov_results"][stage] = output
            st.session_state["innov_context"][stage] = output
            st.session_state["innov_run_idx"] = run_idx + 1
            st.rerun()
        except Exception as exc:
            st.error(f"Error in {slabel}: {exc}")
            if st.button("← Back to stage selection"):
                for k in ["innov_run_idx", "innov_context"]:
                    st.session_state.pop(k, None)
                st.session_state["innov_step"] = 2
                st.rerun()
    else:
        st.progress(1.0)
        all_done = len(st.session_state.get("innov_results", {}))
        st.success(f"✓ {total} new stage(s) complete! {all_done} total stage(s) in package.")
        for k in ["innov_run_idx", "innov_context", "innov_resume_mode"]:
            st.session_state.pop(k, None)
        st.session_state["innov_results_title"] = title
        st.switch_page("pages/results.py")


render()
