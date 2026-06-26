"""
ProSEIT Innovation Agent — Document Builder

Converts Claude-generated markdown stage outputs into branded:
  • Word documents (.docx)     — all stages
  • Excel workbooks (.xlsx)    — data/table-heavy stages
  • PowerPoint slides (.pptx)  — key presentation stages
  • ZIP archive                — bundling all formats
"""
from __future__ import annotations
import io
import re
import zipfile
from datetime import date as _date

from docx import Document
from docx.shared import Inches, Pt, RGBColor as WRGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from openpyxl import Workbook
from openpyxl.styles import (
    Font as XLFont, PatternFill as XLFill,
    Alignment as XLAlign, Border as XLBorder, Side as XLSide,
)
from openpyxl.utils import get_column_letter

from pptx import Presentation
from pptx.util import Inches as PIn, Pt as PPt
from pptx.dml.color import RGBColor as PRGBColor
from pptx.enum.text import PP_ALIGN

# ── Brand colours ───────────────────────────────────────────────────
_WN = WRGBColor(0x24, 0x36, 0x4B)    # Navy
_WG = WRGBColor(0xD4, 0xA6, 0x2A)    # Gold
_WW = WRGBColor(0xFF, 0xFF, 0xFF)    # White
_WGR = WRGBColor(0xF4, 0xF6, 0xF8)  # Soft grey
_WDT = WRGBColor(0x1F, 0x29, 0x33)  # Dark text

_PN = PRGBColor(0x24, 0x36, 0x4B)
_PG = PRGBColor(0xD4, 0xA6, 0x2A)
_PW = PRGBColor(0xFF, 0xFF, 0xFF)
_PDT = PRGBColor(0x1F, 0x29, 0x33)
_PGR = PRGBColor(0x88, 0x88, 0x88)

PROSEIT_CONTACT = (
    "ProSEIT · Professional Society for Engineering, Innovation & Technology"
    "  |  www.proseit.org  |  info@proseit.org  |  Kampala, Uganda, East Africa"
)
_TODAY = _date.today().strftime("%d %B %Y")

# ── Stage routing ─────────────────────────────────────────────────
EXCEL_STAGES = frozenset({
    "03_editions", "05_user_stories", "07_data_model",
    "08_api_design", "09_integrations", "11_testing",
    "14_budget", "17_roadmap", "18_package",
})
PPTX_STAGES = frozenset({
    "00_intake", "02_concept", "15_business_plan",
    "17_roadmap", "18_package",
})
STAGE_DELIVERABLES: dict[str, list[str]] = {
    "00_intake":        ["Word (.docx)", "PowerPoint (.pptx)"],
    "01_policy":        ["Word (.docx)"],
    "02_concept":       ["Word (.docx)", "PowerPoint (.pptx)"],
    "03_editions":      ["Word (.docx)", "Excel (.xlsx)"],
    "04_architecture":  ["Word (.docx)"],
    "05_user_stories":  ["Word (.docx)", "Excel (.xlsx)"],
    "06_ux_wireframes": ["Word (.docx)"],
    "07_data_model":    ["Word (.docx)", "Excel (.xlsx)"],
    "08_api_design":    ["Word (.docx)", "Excel (.xlsx)"],
    "09_integrations":  ["Word (.docx)", "Excel (.xlsx)"],
    "10_security":      ["Word (.docx)"],
    "11_testing":       ["Word (.docx)", "Excel (.xlsx)"],
    "12_deployment":    ["Word (.docx)"],
    "13_documentation": ["Word (.docx)"],
    "14_budget":        ["Word (.docx)", "Excel Budget (.xlsx)"],
    "15_business_plan": ["Word (.docx)", "PowerPoint (.pptx)"],
    "16_governance":    ["Word (.docx)"],
    "17_roadmap":       ["Word (.docx)", "Excel (.xlsx)", "PowerPoint (.pptx)"],
    "18_package":       ["Word (.docx)", "PowerPoint (.pptx)", "Excel (.xlsx)"],
}


# ═══════════════════════════════════════════════════════════════════════════
# Shared markdown parser
# ═══════════════════════════════════════════════════════════════════════════

def _parse_md(text: str) -> list[tuple[str, str]]:
    """Tokenise markdown into (type, content) pairs."""
    items: list[tuple[str, str]] = []
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line:
            items.append(("blank", ""))
        elif line.startswith("#### "):
            items.append(("h4", line[5:]))
        elif line.startswith("### "):
            items.append(("h3", line[4:]))
        elif line.startswith("## "):
            items.append(("h2", line[3:]))
        elif line.startswith("# "):
            items.append(("h1", line[2:]))
        elif line.startswith("|") and "|" in line[1:]:
            items.append(("table_row", line))
        elif re.match(r"^\s*[-*]\s", line):
            items.append(("bullet", re.sub(r"^\s*[-*]\s", "", line)))
        elif line.startswith("> "):
            items.append(("quote", line[2:]))
        elif re.match(r"^[-=]{3,}$", line.strip()):
            items.append(("hr", ""))
        else:
            items.append(("para", line))
    return items


def _plain(text: str) -> str:
    """Strip markdown inline formatting to plain text."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    return text.strip()


def _extract_tables(text: str) -> list[list[list[str]]]:
    """Extract markdown tables as list[table] where table = list[row] where row = list[cell]."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for t, content in _parse_md(text):
        if t == "table_row":
            cells = [c.strip() for c in content.strip("|").split("|")]
            if all(re.match(r"^[-: ]+$", c) for c in cells if c):
                continue  # separator row
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


# ═══════════════════════════════════════════════════════════════════════════
# Word document builder
# ═══════════════════════════════════════════════════════════════════════════

def _cell_bg(cell, hex6: str) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex6)
    tcPr.append(shd)


def _add_cover(doc: Document, innov_title: str, stage_label: str) -> None:
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.cell(0, 0)
    _cell_bg(cell, "24364B")

    def _cp(text: str, size: int, color: WRGBColor,
            bold: bool = False, italic: bool = False) -> None:
        p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.name = "Calibri"

    # Use the initial empty paragraph as top padding
    p0 = cell.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.add_run(" ").font.size = Pt(6)

    _cp("PROSEIT", 42, _WG, bold=True)
    _cp("Professional Society for Engineering, Innovation & Technology", 11, _WW)
    _cp("─" * 40, 10, _WG)
    _cp(" ", 6, _WW)
    _cp("INNOVATION PIPELINE REPORT", 12, _WG, bold=True)
    _cp(" ", 4, _WW)
    _cp(innov_title, 22, _WW, bold=True)
    _cp(" ", 4, _WW)
    _cp(stage_label, 14, _WG)
    _cp(" ", 6, _WW)
    _cp(_TODAY, 10, _WW)
    _cp(" ", 6, _WW)
    _cp("CONFIDENTIAL — ProSEIT Internal Document", 9, _WG, italic=True)
    _cp(" ", 6, _WW)

    tbl.rows[0].height = Cm(20)
    doc.add_page_break()


def _setup_hf(doc: Document, stage_label: str, innov_title: str) -> None:
    section = doc.sections[0]
    section.header_distance = Cm(1.0)
    section.footer_distance = Cm(0.8)

    hdr = section.header
    hdr.paragraphs[0].clear()
    p = hdr.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r1 = p.add_run("ProSEIT  |  ")
    r1.bold = True
    r1.font.color.rgb = _WN
    r1.font.size = Pt(9)
    r2 = p.add_run(stage_label)
    r2.font.color.rgb = _WG
    r2.font.size = Pt(9)
    r3 = p.add_run(f"  —  {innov_title}")
    r3.font.color.rgb = _WN
    r3.font.size = Pt(8)

    ftr = section.footer
    ftr.paragraphs[0].clear()
    pf = ftr.paragraphs[0]
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf = pf.add_run(PROSEIT_CONTACT)
    rf.font.size = Pt(7.5)
    rf.font.color.rgb = _WN


def _add_runs(para, text: str, base_pt: int = 11) -> None:
    parts = re.split(r"(\*\*.*?\*\*|\*[^*]+\*|`[^`]+`)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            r = para.add_run(_plain(part))
            r.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = para.add_run(part[1:-1])
            r.italic = True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = para.add_run(part[1:-1])
            r.font.name = "Courier New"
            r.font.size = Pt(base_pt - 1)
        elif part:
            para.add_run(part)


def _render_to_docx(doc: Document, tokens: list[tuple[str, str]]) -> None:
    i = 0
    while i < len(tokens):
        t, content = tokens[i]

        if t == "h1":
            p = doc.add_heading(level=1)
            p.clear()
            r = p.add_run(_plain(content))
            r.font.color.rgb = _WN
            r.bold = True
        elif t == "h2":
            p = doc.add_heading(level=2)
            p.clear()
            r = p.add_run(_plain(content))
            r.font.color.rgb = _WN
        elif t == "h3":
            p = doc.add_heading(level=3)
            p.clear()
            r = p.add_run(_plain(content))
            r.font.color.rgb = _WG
            r.bold = True
        elif t == "h4":
            p = doc.add_heading(level=4)
            p.clear()
            r = p.add_run(_plain(content))
            r.font.color.rgb = _WDT
        elif t == "bullet":
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Cm(0.5)
            _add_runs(p, content)
        elif t == "quote":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1.0)
            r = p.add_run(content)
            r.italic = True
            r.font.color.rgb = WRGBColor(0x55, 0x66, 0x77)
        elif t == "table_row":
            # Collect all consecutive table rows
            rows: list[list[str]] = []
            j = i
            while j < len(tokens) and tokens[j][0] == "table_row":
                cells = [c.strip() for c in tokens[j][1].strip("|").split("|")]
                if not all(re.match(r"^[-: ]+$", c) for c in cells if c):
                    rows.append(cells)
                j += 1
            i = j
            if rows:
                ncols = max(len(r) for r in rows)
                padded = [r + [""] * (ncols - len(r)) for r in rows]
                tbl = doc.add_table(rows=len(padded), cols=ncols)
                tbl.style = "Table Grid"
                for ri, row in enumerate(padded):
                    for ci, val in enumerate(row):
                        cell = tbl.cell(ri, ci)
                        cell.paragraphs[0].clear()
                        if ri == 0:
                            _cell_bg(cell, "24364B")
                            r = cell.paragraphs[0].add_run(_plain(val))
                            r.bold = True
                            r.font.color.rgb = _WW
                            r.font.size = Pt(9)
                        else:
                            if ri % 2 == 0:
                                _cell_bg(cell, "F4F6F8")
                            pr = cell.paragraphs[0].add_run(_plain(val))
                            pr.font.size = Pt(9)
                doc.add_paragraph()
            continue
        elif t == "hr":
            p = doc.add_paragraph("_" * 60)
            p.paragraph_format.space_after = Pt(4)
        elif t == "para" and content.strip():
            p = doc.add_paragraph()
            _add_runs(p, content)
            p.paragraph_format.space_after = Pt(4)

        i += 1


def build_word_doc(
    stage: str, stage_label: str, content: str, innov_title: str
) -> bytes:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
    _add_cover(doc, innov_title, stage_label)
    _setup_hf(doc, stage_label, innov_title)
    _render_to_docx(doc, _parse_md(content))
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# Excel workbook builder
# ═══════════════════════════════════════════════════════════════════════════

_XL_HDR = {
    "font": XLFont(bold=True, color="FFFFFF", name="Calibri", size=10),
    "fill": XLFill(fill_type="solid", fgColor="24364B"),
    "alignment": XLAlign(horizontal="center", vertical="center", wrap_text=True),
    "border": XLBorder(
        left=XLSide(style="thin"), right=XLSide(style="thin"),
        top=XLSide(style="thin"), bottom=XLSide(style="thin"),
    ),
}


def _xl_row_style(ri: int) -> dict:
    bg = "F4F6F8" if ri % 2 == 0 else "FFFFFF"
    return {
        "font": XLFont(name="Calibri", size=10),
        "fill": XLFill(fill_type="solid", fgColor=bg),
        "alignment": XLAlign(horizontal="left", vertical="top", wrap_text=True),
        "border": XLBorder(
            left=XLSide(style="thin"), right=XLSide(style="thin"),
            top=XLSide(style="thin"), bottom=XLSide(style="thin"),
        ),
    }


def _xl_write_row(ws, row_num: int, cells: list[str], style: dict) -> None:
    for ci, val in enumerate(cells, 1):
        c = ws.cell(row=row_num, column=ci, value=_plain(val))
        for attr, v in style.items():
            setattr(c, attr, v)


def build_excel_doc(
    stage: str, stage_label: str, content: str, innov_title: str
) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)
    tables = _extract_tables(content)
    tokens = _parse_md(content)

    def _title_rows(ws) -> None:
        ws["A1"] = innov_title
        ws["A1"].font = XLFont(bold=True, size=13, color="24364B", name="Calibri")
        ws["A2"] = stage_label
        ws["A2"].font = XLFont(size=10, color="D4A62A", name="Calibri")
        ws["A3"] = PROSEIT_CONTACT
        ws["A3"].font = XLFont(size=8, color="888888", name="Calibri")
        ws.row_dimensions[1].height = 18

    if not tables:
        ws = wb.create_sheet("Content")
        _title_rows(ws)
        row = 5
        for t, text in tokens:
            if t in ("h1", "h2", "h3", "h4"):
                c = ws.cell(row=row, column=1, value=_plain(text))
                c.font = XLFont(bold=True, size=11, name="Calibri")
            elif t in ("para", "bullet", "quote") and text.strip():
                c = ws.cell(row=row, column=1, value=_plain(text))
                c.font = XLFont(size=10, name="Calibri")
            else:
                row += 1
                continue
            row += 1
        ws.column_dimensions["A"].width = 100
    else:
        table_idx = 0
        i = 0
        seen_table_starts = set()
        while i < len(tokens) and table_idx < len(tables):
            t, line = tokens[i]
            if t == "table_row" and i not in seen_table_starts:
                # Find heading before this table
                heading = f"Table {table_idx + 1}"
                for back in range(i - 1, max(i - 8, -1), -1):
                    bt, bc = tokens[back]
                    if bt in ("h1", "h2", "h3", "h4"):
                        heading = _plain(bc)[:28]
                        break

                sheet_name = f"{table_idx + 1}. {heading}"[:31]
                ws = wb.create_sheet(sheet_name)
                _title_rows(ws)
                ws["A2"] = f"{stage_label}  —  {heading}"
                ws["A2"].font = XLFont(size=10, color="D4A62A", name="Calibri")

                tbl_rows = tables[table_idx]
                ncols = max(len(r) for r in tbl_rows)
                for ri, row_data in enumerate(tbl_rows):
                    row_data = row_data + [""] * (ncols - len(row_data))
                    xl_row = ri + 5
                    style = _XL_HDR if ri == 0 else _xl_row_style(ri)
                    _xl_write_row(ws, xl_row, row_data, style)
                    ws.row_dimensions[xl_row].height = 20 if ri == 0 else 15

                for ci in range(1, ncols + 1):
                    col = get_column_letter(ci)
                    max_w = max(
                        len(_plain(r[ci - 1]) if ci - 1 < len(r) else "")
                        for r in tbl_rows
                    )
                    ws.column_dimensions[col].width = min(max(max_w + 2, 12), 48)
                ws.freeze_panes = "A6"

                # Skip over all rows of this table
                seen_table_starts.add(i)
                while i < len(tokens) and tokens[i][0] == "table_row":
                    i += 1
                table_idx += 1
                continue
            i += 1

    ws_info = wb.create_sheet("ProSEIT")
    ws_info["A1"] = "ProSEIT · Professional Society for Engineering, Innovation & Technology"
    ws_info["A1"].font = XLFont(bold=True, size=13, color="24364B", name="Calibri")
    for i, row_val in enumerate([
        "Website: www.proseit.org",
        "Email: info@proseit.org",
        "Address: Kampala, Uganda, East Africa",
        f"Generated: {_TODAY}",
        f"Innovation: {innov_title}",
        f"Stage: {stage_label}",
    ], start=2):
        ws_info.cell(row=i, column=1, value=row_val).font = XLFont(size=10, name="Calibri")
    ws_info.column_dimensions["A"].width = 70

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# PowerPoint builder
# ═══════════════════════════════════════════════════════════════════════════

def _pptx_run(tf, text: str, size: int, color: PRGBColor,
             bold: bool = False, italic: bool = False,
             align: PP_ALIGN = PP_ALIGN.LEFT) -> None:
    para = tf.add_paragraph()
    para.alignment = align
    run = para.add_run()
    run.text = _plain(text)
    run.font.size = PPt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = "Calibri"


def _pptx_rect(slide, left, top, width, height, fill_color: PRGBColor):
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def build_pptx_doc(
    stage: str, stage_label: str, content: str, innov_title: str
) -> bytes:
    prs = Presentation()
    prs.slide_width = PIn(13.33)
    prs.slide_height = PIn(7.5)
    blank = prs.slide_layouts[6]

    # ── Cover slide ──────────────────────────────────────────────────
    sl = prs.slides.add_slide(blank)
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = _PN

    _pptx_rect(sl, PIn(0), PIn(0), PIn(13.33), PIn(0.12), _PG)  # gold top bar
    _pptx_rect(sl, PIn(0), PIn(7.38), PIn(13.33), PIn(0.12), _PG)  # gold bottom bar

    def _tb(left, top, width, height):
        txb = sl.shapes.add_textbox(PIn(left), PIn(top), PIn(width), PIn(height))
        txb.text_frame.word_wrap = True
        return txb.text_frame

    tf = _tb(1, 1.3, 11.33, 1.2)
    _pptx_run(tf, "PROSEIT", 54, _PG, bold=True, align=PP_ALIGN.CENTER)

    tf2 = _tb(1, 2.65, 11.33, 0.5)
    _pptx_run(tf2, "Professional Society for Engineering, Innovation & Technology", 13, _PW, align=PP_ALIGN.CENTER)

    tf3 = _tb(1, 3.25, 11.33, 0.3)
    _pptx_run(tf3, "─" * 60, 9, _PG, align=PP_ALIGN.CENTER)

    tf4 = _tb(1, 3.65, 11.33, 1.0)
    _pptx_run(tf4, innov_title, 26, _PW, bold=True, align=PP_ALIGN.CENTER)

    tf5 = _tb(1, 4.8, 11.33, 0.55)
    _pptx_run(tf5, stage_label, 16, _PG, align=PP_ALIGN.CENTER)

    tf6 = _tb(1, 5.5, 11.33, 0.4)
    _pptx_run(tf6, _TODAY, 11, _PW, align=PP_ALIGN.CENTER)

    tf7 = _tb(1, 6.85, 11.33, 0.35)
    _pptx_run(tf7, PROSEIT_CONTACT, 8, _PGR, align=PP_ALIGN.CENTER)

    # ── Content slides ─────────────────────────────────────────────
    tokens = _parse_md(content)
    cur_heading = ""
    cur_bullets: list[str] = []
    cur_paras: list[str] = []

    def _flush(heading: str, bullets: list[str], paras: list[str]) -> None:
        if not heading and not bullets and not paras:
            return
        s = prs.slides.add_slide(blank)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = _PW

        _pptx_rect(s, PIn(0), PIn(0), PIn(13.33), PIn(1.2), _PN)
        _pptx_rect(s, PIn(0), PIn(1.2), PIn(13.33), PIn(0.04), _PG)
        _pptx_rect(s, PIn(0), PIn(7.15), PIn(13.33), PIn(0.04), _PG)

        txh = s.shapes.add_textbox(PIn(0.4), PIn(0.18), PIn(12.5), PIn(0.85))
        txh.text_frame.word_wrap = True
        _pptx_run(txh.text_frame, heading or stage_label, 20, _PW, bold=True)

        all_items = [("p", t) for t in paras] + [("b", t) for t in bullets]
        if not all_items:
            return

        txc = s.shapes.add_textbox(PIn(0.5), PIn(1.4), PIn(12.3), PIn(5.6))
        tfc = txc.text_frame
        tfc.word_wrap = True
        fsize = 12 if len(all_items) <= 5 else 10 if len(all_items) <= 9 else 9

        for kind, item in all_items[:14]:
            para = tfc.add_paragraph()
            run = para.add_run()
            run.text = ("•  " if kind == "b" else "") + _plain(item)
            run.font.size = PPt(fsize)
            run.font.color.rgb = _PDT
            run.font.name = "Calibri"
            para.space_before = PPt(5)

        txf = s.shapes.add_textbox(PIn(0.3), PIn(7.18), PIn(12.7), PIn(0.28))
        _pptx_run(txf.text_frame, PROSEIT_CONTACT, 7, _PGR)

    for t, cnt in tokens:
        if t in ("h1", "h2", "h3"):
            _flush(cur_heading, cur_bullets, cur_paras)
            cur_heading = _plain(cnt)
            cur_bullets = []
            cur_paras = []
        elif t == "bullet":
            cur_bullets.append(cnt)
        elif t in ("para", "quote", "h4") and cnt.strip():
            cur_paras.append(cnt)

    _flush(cur_heading, cur_bullets, cur_paras)

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# ZIP builders
# ═══════════════════════════════════════════════════════════════════════════

def build_stage_zip(
    stage: str, stage_label: str, content: str, innov_title: str
) -> bytes:
    slug = stage_label.replace(" · ", "_").replace(" ", "_").replace("/", "-")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{slug}.docx", build_word_doc(stage, stage_label, content, innov_title))
        if stage in EXCEL_STAGES:
            zf.writestr(f"{slug}.xlsx", build_excel_doc(stage, stage_label, content, innov_title))
        if stage in PPTX_STAGES:
            zf.writestr(f"{slug}.pptx", build_pptx_doc(stage, stage_label, content, innov_title))
    return buf.getvalue()


def build_full_zip(
    results: dict[str, str],
    stage_labels: dict[str, str],
    innov_title: str,
) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for stage, content in results.items():
            label = stage_labels.get(stage, stage)
            slug = label.replace(" · ", "_").replace(" ", "_").replace("/", "-")
            folder = f"{slug}/"
            zf.writestr(folder + f"{slug}.docx",
                        build_word_doc(stage, label, content, innov_title))
            if stage in EXCEL_STAGES:
                zf.writestr(folder + f"{slug}.xlsx",
                            build_excel_doc(stage, label, content, innov_title))
            if stage in PPTX_STAGES:
                zf.writestr(folder + f"{slug}.pptx",
                            build_pptx_doc(stage, label, content, innov_title))
        index = [
            f"# {innov_title} — ProSEIT Innovation Package",
            f"Generated: {_TODAY}",
            "",
            f"Contact: {PROSEIT_CONTACT}",
            "",
            "## Contents",
        ]
        for stage, label in stage_labels.items():
            if stage in results:
                deliverables = STAGE_DELIVERABLES.get(stage, ["Word (.docx)"])
                index.append(f"- **{label}** — {', '.join(deliverables)}")
        zf.writestr("INDEX.md", "\n".join(index))
    return buf.getvalue()
