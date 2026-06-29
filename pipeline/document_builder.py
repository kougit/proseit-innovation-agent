"""
ProSEIT Innovation Agent — Document Builder

Converts Claude-generated markdown stage outputs into branded:
  • Word documents (.docx)     — all stages
  • Excel workbooks (.xlsx)    — data/table-heavy stages
  • PowerPoint slides (.pptx)  — key presentation stages
  • UIX prototype ZIP          — Stage 06 UIX Prototype
  • ZIP archive                — bundling all formats
"""
from __future__ import annotations
import io
import re
import zipfile
from datetime import date as _date

# ── Lazy imports (deferred to first use to speed up Streamlit cold start) ────
def _docx_imports():
    global Document, Inches, Pt, WRGBColor, Cm, WD_ALIGN_PARAGRAPH, qn, OxmlElement
    global NAVY, _WN, _WG, _WW, _WGR, _WDT
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor as WRGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    NAVY = WRGBColor(0x24, 0x36, 0x4B)
    _WN = NAVY
    _WG = WRGBColor(0xD4, 0xA6, 0x2A)
    _WW = WRGBColor(0xFF, 0xFF, 0xFF)
    _WGR = WRGBColor(0xF4, 0xF6, 0xF8)
    _WDT = WRGBColor(0x1F, 0x29, 0x33)

def _xl_imports():
    global Workbook, XLFont, XLFill, XLAlign, XLBorder, XLSide, get_column_letter
    from openpyxl import Workbook
    from openpyxl.styles import (
        Font as XLFont, PatternFill as XLFill,
        Alignment as XLAlign, Border as XLBorder, Side as XLSide,
    )
    from openpyxl.utils import get_column_letter

def _pptx_imports():
    global Presentation, PIn, PPt, PRGBColor, PP_ALIGN
    global _PN, _PG, _PW, _PDT, _PGR
    from pptx import Presentation
    from pptx.util import Inches as PIn, Pt as PPt
    from pptx.dml.color import RGBColor as PRGBColor
    from pptx.enum.text import PP_ALIGN
    _PN = PRGBColor(0x24, 0x36, 0x4B)
    _PG = PRGBColor(0xD4, 0xA6, 0x2A)
    _PW = PRGBColor(0xFF, 0xFF, 0xFF)
    _PDT = PRGBColor(0x1F, 0x29, 0x33)
    _PGR = PRGBColor(0x88, 0x88, 0x88)

def _cairo_imports():
    global _cairosvg, _HAS_CAIRO
    try:
        import cairosvg as _cairosvg
        _HAS_CAIRO = True
    except Exception:
        _HAS_CAIRO = False

# Module-level sentinels so references before first call don't NameError
Document = Inches = Pt = WRGBColor = Cm = WD_ALIGN_PARAGRAPH = qn = OxmlElement = None
NAVY = _WN = _WG = _WW = _WGR = _WDT = None
Workbook = XLFont = XLFill = XLAlign = XLBorder = XLSide = get_column_letter = None
Presentation = PIn = PPt = PRGBColor = PP_ALIGN = None
_PN = _PG = _PW = _PDT = _PGR = None
_cairosvg = None
_HAS_CAIRO = False

PROSEIT_CONTACT = (
    "ProSEIT · Plot 5 Blue Heights Plaza, Nkrumah Road, Kampala, Uganda"
    "  |  Tel: +256 790 334 653  |  www.proseit.org  |  info@proseit.org"
)
_TODAY = _date.today().strftime("%d %B %Y")
