"""ProSEIT Innovation Agent — Results viewer page."""
from __future__ import annotations
import io
import json
import streamlit as st
from pipeline.runner import STAGE_LABELS
from pipeline.document_builder import (
    STAGE_DELIVERABLES, EXCEL_STAGES, PPTX_STAGES, UIX_STAGES,
    build_word_doc, build_excel_doc, build_pptx_doc,
    build_stage_zip, build_full_zip, build_uix_zip, parse_uix_files,
)
from ui.brand import NAVY, GOLD, WHITE
from ui.components import page_title, section_bar, banner, page_footer

_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def _save_json(results: dict, title: str, idea: str) -> bytes:
    return json.dumps(
        {"innov_title": title, "innov_idea": idea, "innov_results": results},
        ensure_ascii=False, indent=2,
    ).encode("utf-8")


def _stage_dl_row(stage: str, content: str, title: str, key_prefix: str) -> None:
    lbl = STAGE_LABELS.get(stage, stage)
    deliverables = STAGE_DELIVERABLES.get(stage, ["Word (.docx)"])
    st.markdown(
        f'<div style="font-size:0.85rem;font-weight:700;color:{NAVY};'
        f'padding:0.5rem 0 0.15rem">{lbl}</div>'
        f'<div style="font-size:0.72rem;color:rgba(36,54,75,0.5);'
        f'margin-bottom:0.35rem">{", ".join(deliverables)}</div>',
        unsafe_allow_html=True,
    )

    # UIX stage gets a prominent prototype pack button first
    if stage in UIX_STAGES:
        files = parse_uix_files(content)
        file_count = len(files)
        uix_label = f"🌐 UIX Prototype Pack ({file_count} files)" if file_count else "🌐 UIX Prototype Pack"
        try:
            slug = title[:28].replace(" ", "_")
            c1, c2 = st.columns([3, 4])
            with c1:
                st.download_button(
                    uix_label,
                    data=build_uix_zip(stage, lbl, content, title),
                    file_name=f"{stage}_{slug}_uix_prototype.zip",
                    mime="application/zip",
                    key=f"{key_prefix}_uix_{stage}",
                    use_container_width=True,
                    type="primary",
                )
        except Exception as e:
            st.error(f"UIX ZIP error: {e}")
        st.markdown(
            '<div style="font-size:0.72rem;color:rgba(36,54,75,0.5);'
            'margin-bottom:0.4rem">Extract ZIP and open <code>launch.html</code> in browser</div>',
            unsafe_allow_html=True,
        )

    ncols = 1 + (1 if stage in EXCEL_STAGES else 0) + (1 if stage in PPTX_STAGES else 0) + 1
    cols = st.columns([1] * ncols + [2])  # trailing spacer
    ci = 0
    slug = title[:28].replace(" ", "_")
    try:
        with cols[ci]:
            st.download_button(
                "📄 Word",
                data=build_word_doc(stage, lbl, content, title),
                file_name=f"{stage}_{slug}.docx",
                mime=_DOCX_MIME,
                key=f"{key_prefix}_w_{stage}",
                use_container_width=True,
            )
        ci += 1
    except Exception:
        pass
    if stage in EXCEL_STAGES:
        try:
            with cols[ci]:
                st.download_button(
                    "📊 Excel",
                    data=build_excel_doc(stage, lbl, content, title),
                    file_name=f"{stage}_{slug}.xlsx",
                    mime=_XLSX_MIME,
                    key=f"{key_prefix}_x_{stage}",
                    use_container_width=True,
                )
            ci += 1
        except Exception:
            pass
    if stage in PPTX_STAGES:
        try:
            with cols[ci]:
                st.download_button(
                    "🎥 PowerPoint",
                    data=build_pptx_doc(stage, lbl, content, title),
                    file_name=f"{stage}_{slug}.pptx",
                    mime=_PPTX_MIME,
                    key=f"{key_prefix}_p_{stage}",
                    use_container_width=True,
                )
            ci += 1
        except Exception:
            pass
    try:
        with cols[ci]:
            st.download_button(
                "🗂️ ZIP",
                data=build_stage_zip(stage, lbl, content, title),
                file_name=f"{stage}.zip",
                mime="application/zip",
                key=f"{key_prefix}_z_{stage}",
                use_container_width=True,
            )
    except Exception:
        pass
    st.markdown('<hr style="margin:0.4rem 0;opacity:0.15">', unsafe_allow_html=True)


def render() -> None:
    results: dict[str, str] = st.session_state.get("innov_results", {})
    title: str = st.session_state.get("innov_results_title", "Innovation Package")
    idea: str = st.session_state.get("innov_idea", "")

    if not results:
        page_title("Results", "No results loaded.")
        banner(
            "No pipeline results found. Run the pipeline on the New Innovation page, "
            "or upload a saved progress file below.",
            kind="warning",
        )
        section_bar("Resume from Saved Progress")
        uploaded = st.file_uploader(
            "Upload a saved progress file (.json)",
            type=["json"],
            key="resume_upload",
        )
        if uploaded:
            try:
                saved = json.loads(uploaded.read().decode("utf-8"))
                st.session_state["innov_results"] = saved.get("innov_results", {})
                st.session_state["innov_results_title"] = saved.get("innov_title", "Innovation")
                st.session_state["innov_idea"] = saved.get("innov_idea", "")
                n = len(st.session_state["innov_results"])
                st.success(f"Loaded {n} completed stage(s). Reloading…")
                st.rerun()
            except Exception as e:
                st.error(f"Could not load file: {e}")
        if st.button("➕ Start New Innovation", type="primary"):
            st.switch_page("pages/new_innovation.py")
        page_footer()
        return

    page_title(f"Results: {title}", f"{len(results)} stage(s) completed")

    st.markdown(
        f'<div class="ps-dl-bar"><div>'
        f'<div style="color:{GOLD};font-size:0.68rem;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase">Innovation Package Ready</div>'
        f'<div style="color:{WHITE};font-weight:600;font-size:0.95rem;margin-top:0.15rem">'
        f'{title}</div>'
        f'<div style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin-top:0.1rem">'
        f'{len(results)} stage(s) · Word, Excel & PowerPoint formats</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    c_dl, c_save, _ = st.columns([2, 2, 3])
    with c_dl:
        try:
            st.download_button(
                "⬇️ Download Full Package (ZIP)",
                data=build_full_zip(results, STAGE_LABELS, title),
                file_name=f"{title.lower().replace(' ', '_')}_proseit_package.zip",
                mime="application/zip",
                type="primary",
            )
        except Exception as e:
            st.error(f"ZIP error: {e}")
    with c_save:
        st.download_button(
            "💾 Save Progress (.json)",
            data=_save_json(results, title, idea),
            file_name=f"{title.lower().replace(' ', '_')}_progress.json",
            mime="application/json",
        )

    st.markdown("---")

    stage_keys = list(results.keys())
    tab_defs = [
        ("📋 Overview",    [s for s in stage_keys if s in ("00_intake", "01_policy", "02_concept")]),
        ("⚙️ Technical",   [s for s in stage_keys if s in (
            "04_architecture", "05_user_stories", "06_ux_wireframes",
            "07_data_model", "08_api_design", "09_integrations",
            "10_security", "11_testing", "12_deployment")]),
        ("📦 Editions",    [s for s in stage_keys if s in ("03_editions",)]),
        ("💰 Business",    [s for s in stage_keys if s in (
            "13_documentation", "14_budget", "15_business_plan")]),
        ("🏗️ Governance", [s for s in stage_keys if s in ("16_governance",)]),
        ("🗺️ Roadmap",    [s for s in stage_keys if s in ("17_roadmap", "18_package")]),
        ("⬇️ Downloads",  []),
    ]
    active_tabs = [(lbl, sts) for lbl, sts in tab_defs if sts or lbl == "⬇️ Downloads"]
    if not active_tabs:
        active_tabs = [("All Stages", stage_keys), ("⬇️ Downloads", [])]

    tabs = st.tabs([lbl for lbl, _ in active_tabs])
    for tab, (label, sts) in zip(tabs, active_tabs):
        with tab:
            if label == "⬇️ Downloads":
                section_bar("Download Individual Stage Deliverables")
                banner(
                    "Each stage is available as a branded <strong>Word document</strong>. "
                    "Data-heavy stages also include <strong>Excel</strong>. "
                    "Key stages include <strong>PowerPoint</strong>. "
                    "Stage 06 includes a browsable <strong>Angular UIX Prototype</strong>. "
                    "Download a single format or the per-stage ZIP.",
                    kind="info",
                )
                for stage, content in results.items():
                    _stage_dl_row(stage, content, title, "dl")
                continue

            if not sts:
                st.info("No stages in this category were run.")
                continue

            for stage in sts:
                content = results.get(stage, "")
                slabel = STAGE_LABELS.get(stage, stage)
                with st.expander(slabel, expanded=(stage == sts[0])):
                    if stage in UIX_STAGES:
                        files = parse_uix_files(content)
                        if files:
                            st.markdown(
                                f"**UIX Prototype contains {len(files)} files:**  \n"
                                + "  \n".join(f"- `{fn}`" for fn in sorted(files.keys()))
                            )
                            st.markdown(
                                f'<div style="margin-top:0.5rem;padding:0.6rem 0.8rem;'
                                f'background:#f4f6f8;border-left:3px solid #D4A62A;'
                                f'border-radius:4px;font-size:0.8rem;color:#1F2933">'
                                f'💡 Download the <strong>UIX Prototype Pack</strong> below '
                                f'and open <code>launch.html</code> in your browser to browse '
                                f'the interactive prototype.</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(content)
                    else:
                        st.markdown(content)
                    st.markdown("<br>", unsafe_allow_html=True)
                    _stage_dl_row(stage, content, title, f"exp_{stage}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Start Another Innovation"):
        for k in [
            "innov_results", "innov_results_title", "innov_idea", "innov_title",
            "innov_selected_stages", "innov_step", "innov_kb_context",
            "innov_is_agri", "innov_sector", "innov_run_idx", "innov_context",
        ]:
            st.session_state.pop(k, None)
        st.switch_page("pages/new_innovation.py")

    page_footer()


render()
