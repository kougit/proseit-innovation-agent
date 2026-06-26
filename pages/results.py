"""ProSEIT Innovation Agent — Results viewer page."""
from __future__ import annotations
import io
import zipfile
import streamlit as st
from pipeline.runner import STAGE_LABELS
from ui.brand import NAVY, GOLD, WHITE, GREEN
from ui.components import page_title, section_bar, banner, page_footer, badge


def _build_zip(results: dict[str, str], title: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for stage, content in results.items():
            label = STAGE_LABELS.get(stage, stage).replace(" · ", "_").replace(" ", "_")
            zf.writestr(f"{label}.md", content)
        index_lines = [f"# {title} — Innovation Package\n"] + [
            f"- {STAGE_LABELS.get(s, s)}" for s in results
        ]
        zf.writestr("INDEX.md", "\n".join(index_lines))
    return buf.getvalue()


def render() -> None:
    results: dict[str, str] = st.session_state.get("innov_results", {})
    title = st.session_state.get("innov_results_title", "Innovation Package")

    if not results:
        page_title("Results", "No results loaded.")
        banner("No pipeline results found. Run the pipeline on the New Innovation page first.", kind="warning")
        if st.button("➕ Start New Innovation", type="primary"):
            st.switch_page("pages/new_innovation.py")
        page_footer()
        return

    page_title(f"Results: {title}", f"{len(results)} stage(s) completed")

    st.markdown(
        f'<div class="ps-dl-bar"><div>'
        f'<div style="color:{GOLD};font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase">Innovation Package Ready</div>'
        f'<div style="color:{WHITE};font-weight:600;font-size:0.95rem;margin-top:0.15rem">{title}</div>'
        f'<div style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin-top:0.1rem">{len(results)} stage outputs</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.download_button(
        "⬇️ Download Full Package (ZIP)",
        data=_build_zip(results, title),
        file_name=f"{title.lower().replace(' ', '_')}_innovation_package.zip",
        mime="application/zip",
        type="primary",
    )
    st.markdown("---")

    stage_keys = list(results.keys())
    tab_defs = [
        ("📋 Overview",    [s for s in stage_keys if s in ("00_intake", "01_policy", "02_concept")]),
        ("⚙️ Technical",   [s for s in stage_keys if s in ("04_architecture", "05_user_stories", "06_ux_wireframes", "07_data_model", "08_api_design", "09_integrations", "10_security", "11_testing", "12_deployment")]),
        ("📦 Editions",    [s for s in stage_keys if s in ("03_editions",)]),
        ("💼 Business",    [s for s in stage_keys if s in ("13_documentation", "14_budget", "15_business_plan")]),
        ("🏛️ Governance", [s for s in stage_keys if s in ("16_governance",)]),
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
                section_bar("Download Individual Stages")
                for stage, content in results.items():
                    lbl2 = STAGE_LABELS.get(stage, stage)
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f'<div style="font-size:0.85rem;font-weight:600;color:{NAVY};padding:0.4rem 0">{lbl2}</div>', unsafe_allow_html=True)
                    with c2:
                        st.download_button("⬇️ .md", data=content, file_name=f"{stage}.md", mime="text/markdown", key=f"dl_i_{stage}", use_container_width=True)
                continue
            if not sts:
                st.info("No stages in this category were run.")
                continue
            for stage in sts:
                content = results.get(stage, "")
                stage_label = STAGE_LABELS.get(stage, stage)
                with st.expander(stage_label, expanded=(stage == sts[0])):
                    st.markdown(content)
                    st.download_button(
                        f"⬇️ Download {stage_label.split(' · ')[1]}",
                        data=content,
                        file_name=f"{stage}_{title.lower().replace(' ', '_')}.md",
                        mime="text/markdown",
                        key=f"dl_s_{stage}",
                    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Start Another Innovation"):
        for k in ["innov_results", "innov_results_title", "innov_idea", "innov_title", "innov_selected_stages", "innov_step"]:
            st.session_state.pop(k, None)
        st.switch_page("pages/new_innovation.py")

    page_footer()


render()
