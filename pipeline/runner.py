"""
ProSEIT Innovation-to-Implementation Pipeline runner.

Executes the 19-stage pipeline as a sequence of Claude API calls.
Returns a dict keyed by stage name with the Claude-generated content.
"""
from __future__ import annotations
from typing import Callable
from pipeline.client import call_claude

STAGES = [
    "00_intake",
    "01_policy",
    "02_concept",
    "03_editions",
    "04_architecture",
    "05_user_stories",
    "06_ux_wireframes",
    "07_data_model",
    "08_api_design",
    "09_integrations",
    "10_security",
    "11_testing",
    "12_deployment",
    "13_documentation",
    "14_budget",
    "15_business_plan",
    "16_governance",
    "17_roadmap",
    "18_package",
]

STAGE_LABELS = {
    "00_intake":       "Stage 00 · Intake & Validation",
    "01_policy":       "Stage 01 · Policy & Compliance",
    "02_concept":      "Stage 02 · Concept Development",
    "03_editions":     "Stage 03 · Edition Planning",
    "04_architecture": "Stage 04 · Technical Architecture",
    "05_user_stories": "Stage 05 · User Stories",
    "06_ux_wireframes":"Stage 06 · UIX Prototype Agent",
    "07_data_model":   "Stage 07 · Data Model",
    "08_api_design":   "Stage 08 · API Design",
    "09_integrations": "Stage 09 · Integrations",
    "10_security":     "Stage 10 · Security",
    "11_testing":      "Stage 11 · Testing Strategy",
    "12_deployment":   "Stage 12 · Deployment",
    "13_documentation":"Stage 13 · Documentation",
    "14_budget":       "Stage 14 · Budget & Cost",
    "15_business_plan":"Stage 15 · Business Plan",
    "16_governance":   "Stage 16 · Governance Routing",
    "17_roadmap":      "Stage 17 · Roadmap",
    "18_package":      "Stage 18 · Final Package",
}

# ── Agriculture sector detection ─────────────────────────────────────────────

AGRI_SECTORS = {
    "Agriculture & Agronomy",
    "AgriTech & Precision Agriculture",
    "Agroprocessing & Value Addition",
    "Agriculture Value Chains",
    "Animal Husbandry & Livestock",
    "Forestry, Bamboo & NTFPs",
    "Apiculture & Beekeeping",
}

# ── Agriculture knowledge base registry ──────────────────────────────────────────
# Each entry defines a validated source that the agent may cite.
# tier 1 = multi-crop national/regional catalogues (highest authority)
# tier 2 = crop-specific or topic-specific validated books/manuals

AGRI_KB_REGISTRY: list[dict] = [
    # ── Tier 1: Official multi-crop catalogues ────────────────────────────────────
    {
        "tier": 1,
        "id": "adcrc",
        "name": "Africa Digital Crop Variety Catalogue (ADCRC)",
        "publisher": "AGRA (Alliance for a Green Revolution in Africa)",
        "year": "2023",
        "crops": ["Maize", "Beans", "Cassava"],
        "countries": ["Uganda", "Tanzania", "Kenya", "Rwanda", "Malawi", "Ethiopia"],
        "content": (
            "Structured variety data: maturity days, yield potential, drought tolerance, "
            "CMD/CBSD resistance, recommended agro-ecological zones. "
            "Already digitised — suitable for direct RAG ingestion."
        ),
        "citation": (
            "AGRA (2023). Africa Digital Crop Variety Catalogue (ADCRC). "
            "Alliance for a Green Revolution in Africa, Nairobi."
        ),
    },
    {
        "tier": 1,
        "id": "naro_catalogue",
        "name": "NARO National Crop Variety Release Catalogue",
        "publisher": "National Agricultural Research Organisation (NARO), Uganda",
        "year": "2023",
        "crops": ["Maize", "Beans", "Bananas", "Cassava", "Pineapple", "Sorghum",
                  "Groundnuts", "Sweet Potato"],
        "countries": ["Uganda"],
        "content": (
            "Release year, breeder, yield, recommended agro-ecological zones, "
            "biotic/abiotic stress resistance. Legal authority for Uganda variety registration."
        ),
        "citation": (
            "NARO (2023). National Crop Variety Release Catalogue. "
            "National Agricultural Research Organisation, Entebbe, Uganda."
        ),
    },
    {
        "tier": 1,
        "id": "kephis_nvl",
        "name": "KEPHIS National Variety List",
        "publisher": "Kenya Plant Health Inspectorate Service (KEPHIS)",
        "year": "2024",
        "crops": ["Maize", "Beans", "Cassava", "Pineapple", "Sorghum"],
        "countries": ["Kenya"],
        "content": (
            "Officially released varieties with performance data for Kenyan "
            "agro-ecological zones. Cross-border validation reference."
        ),
        "citation": (
            "KEPHIS (2024). National Variety List. "
            "Kenya Plant Health Inspectorate Service, Nairobi."
        ),
    },
    {
        "tier": 1,
        "id": "tari_catalogue",
        "name": "TARI Crop Variety Catalogue",
        "publisher": "Tanzania Agricultural Research Institute (TARI)",
        "year": "2023",
        "crops": ["Maize", "Beans", "Cassava", "Cashew", "Sorghum"],
        "countries": ["Tanzania"],
        "content": (
            "Released varieties for Tanzania with yield, maturity, "
            "and stress tolerance data across Tanzanian agro-ecological zones."
        ),
        "citation": (
            "TARI (2023). Crop Variety Catalogue. "
            "Tanzania Agricultural Research Institute, Dodoma."
        ),
    },
    {
        "tier": 1,
        "id": "rab_catalogue",
        "name": "RAB Crop Variety Catalogue",
        "publisher": "Rwanda Agriculture and Animal Resources Development Board (RAB)",
        "year": "2023",
        "crops": ["Maize", "Beans", "Cassava", "Banana"],
        "countries": ["Rwanda"],
        "content": (
            "Released varieties for Rwanda with performance data "
            "across agro-ecological zones. Includes highland adaptations."
        ),
        "citation": (
            "RAB (2023). Crop Variety Catalogue. "
            "Rwanda Agriculture and Animal Resources Development Board, Kigali."
        ),
    },

    # ── Tier 2: Crop-specific validated books/manuals ─────────────────────────────────
    {
        "tier": 2,
        "id": "cimmyt_maize",
        "name": "CIMMYT/NARO Maize Variety Catalogue for Eastern Africa",
        "publisher": "CIMMYT & NARO",
        "year": "2022",
        "crops": ["Maize"],
        "countries": ["Uganda", "Kenya", "Tanzania", "Ethiopia", "Rwanda"],
        "content": (
            "Drought-tolerant, Striga-resistant, N-use efficient hybrids. "
            "DH, SC, OPV lines by altitude and agro-zone. "
            "Includes seed company licensing information."
        ),
        "citation": (
            "CIMMYT/NARO (2022). Maize Variety Catalogue for Eastern Africa. "
            "CIMMYT, Nairobi."
        ),
    },
    {
        "tier": 2,
        "id": "ciat_beans",
        "name": "CIAT/PABRA Bean Variety Catalogue for Eastern and Central Africa",
        "publisher": "CIAT & Pan-Africa Bean Research Alliance (PABRA)",
        "year": "2023",
        "crops": ["Beans", "Common Bean"],
        "countries": ["Uganda", "Kenya", "Tanzania", "Rwanda", "DRC", "Malawi", "Zambia"],
        "content": (
            "100+ varieties with BBMV, BCMV, anthracnose, low-fertility tolerance, "
            "cooking time, protein content, and market class (climbing, bush, runner). "
            "Agro-zone performance tables."
        ),
        "citation": (
            "CIAT/PABRA (2023). Bean Variety Catalogue for Eastern and Central Africa. "
            "CIAT, Cali, Colombia."
        ),
    },
    {
        "tier": 2,
        "id": "bioversity_banana",
        "name": "Banana Cultivars in Eastern Africa",
        "publisher": "Bioversity International / IITA",
        "year": "2021",
        "crops": ["Banana", "Plantain", "Matooke"],
        "countries": ["Uganda", "Tanzania", "Kenya", "Rwanda", "DRC"],
        "content": (
            "Matooke, cooking, dessert, and beer banana types. "
            "Nematode, weevil, BXW (Banana Xanthomonas Wilt) resistance ratings. "
            "Tissue culture variety performance by region."
        ),
        "citation": (
            "Bioversity International/IITA (2021). Banana Cultivars in Eastern Africa. "
            "Bioversity International, Rome."
        ),
    },
    {
        "tier": 2,
        "id": "iita_cassava",
        "name": "Cassava Varieties of Africa",
        "publisher": "IITA (International Institute of Tropical Agriculture)",
        "year": "2022",
        "crops": ["Cassava"],
        "countries": ["Uganda", "Tanzania", "Kenya", "Rwanda", "DRC", "Zambia", "Malawi"],
        "content": (
            "CMD1, CMD2, CBSD resistant varieties by zone. "
            "Dry matter content (DMC), yield, cyanide levels, cooking quality, "
            "starch content for processing applications."
        ),
        "citation": (
            "IITA (2022). Cassava Varieties of Africa. "
            "International Institute of Tropical Agriculture, Ibadan."
        ),
    },
    {
        "tier": 2,
        "id": "naro_pineapple",
        "name": "NARO Horticulture Crops Production Manual — Pineapple",
        "publisher": "NARO, Uganda",
        "year": "2020",
        "crops": ["Pineapple"],
        "countries": ["Uganda"],
        "content": (
            "Smooth Cayenne, MD2, Jubilee varieties. "
            "Mealybug wilt resistance, nematode tolerance, "
            "post-harvest handling, juice/fresh market specifications."
        ),
        "citation": (
            "NARO (2020). Horticulture Crops Production Manual: Pineapple. "
            "NARO, Entebbe, Uganda."
        ),
    },
    {
        "tier": 2,
        "id": "icraf_shea",
        "name": "Shea Tree (Vitellaria paradoxa) — A Monograph",
        "publisher": "ICRAF (World Agroforestry Centre)",
        "year": "2004",
        "crops": ["Shea", "Shea Butter"],
        "countries": ["Uganda", "Tanzania", "Sudan", "South Sudan", "DRC"],
        "content": (
            "Ecotypes by region, oil content (%), fruit yield, propagation methods. "
            "No formal varieties — ecotype-based classification. "
            "Value chain data: kernel to butter processing ratios."
        ),
        "citation": (
            "ICRAF (2004). Shea Tree (Vitellaria paradoxa): A Monograph. "
            "World Agroforestry Centre, Nairobi."
        ),
    },
    {
        "tier": 2,
        "id": "icraf_beekeeping",
        "name": "Beekeeping in Eastern Africa: A Practical Manual",
        "publisher": "ICRAF / NARO",
        "year": "2018",
        "crops": ["Honey", "Apiculture", "Beeswax", "Propolis"],
        "countries": ["Uganda", "Kenya", "Tanzania", "Ethiopia"],
        "content": (
            "Apis mellifera scutellata ecotypes, hive types "
            "(Langstroth, Kenya top-bar, log hive), "
            "floral calendars by region, varroa and disease management, "
            "honey quality standards, market grades."
        ),
        "citation": (
            "ICRAF/NARO (2018). Beekeeping in Eastern Africa: A Practical Manual. "
            "World Agroforestry Centre, Nairobi."
        ),
    },
    {
        "tier": 2,
        "id": "inbar_bamboo",
        "name": "Bamboo Species for Africa",
        "publisher": "INBAR (International Bamboo and Rattan Organisation)",
        "year": "2020",
        "crops": ["Bamboo"],
        "countries": ["Uganda", "Kenya", "Tanzania", "Ethiopia", "Rwanda"],
        "content": (
            "Oxytenanthera abyssinica, Bambusa vulgaris, Dendrocalamus species. "
            "Use-case table: construction, food shoots, carbon sequestration, "
            "charcoal. Site suitability and planting density data."
        ),
        "citation": (
            "INBAR (2020). Bamboo Species for Africa. "
            "International Bamboo and Rattan Organisation, Beijing."
        ),
    },
    {
        "tier": 2,
        "id": "tari_cashew",
        "name": "Cashew Variety Catalogue — Tanzania",
        "publisher": "TARI / Naliendele Agricultural Research Institute",
        "year": "2021",
        "crops": ["Cashew"],
        "countries": ["Tanzania", "Kenya", "Uganda"],
        "content": (
            "AZA 1, AZA 2, H-series hybrids. "
            "Nut yield (kg/tree), kernel outturn (%), cashew stem borer (CSB) tolerance, "
            "early bearing age, canopy architecture."
        ),
        "citation": (
            "TARI/Naliendele (2021). Cashew Variety Catalogue. "
            "Tanzania Agricultural Research Institute, Naliendele."
        ),
    },
    {
        "tier": 2,
        "id": "prota_wild_mango",
        "name": "Irvingia gabonensis (Wild/Bush Mango) — PROTA Monograph",
        "publisher": "PROTA / ICRAF",
        "year": "2008",
        "crops": ["Wild Mango", "Bush Mango", "Ogbono"],
        "countries": ["Uganda", "DRC", "Tanzania"],
        "content": (
            "Kernel fat/oil content, fruit traits, wild vs selected germplasm. "
            "No formal varieties — wild collection and plus-tree selection only. "
            "Dika nut processing and export market data."
        ),
        "citation": (
            "PROTA/ICRAF (2008). Irvingia gabonensis. "
            "In: Plant Resources of Tropical Africa 2. "
            "PROTA Foundation, Wageningen."
        ),
    },
    {
        "tier": 2,
        "id": "fao_livestock",
        "name": "FAO Livestock Production Systems in Uganda and East Africa",
        "publisher": "FAO / ILRI",
        "year": "2020",
        "crops": ["Livestock", "Cattle", "Goats", "Poultry", "Pigs", "Sheep"],
        "countries": ["Uganda", "Kenya", "Tanzania", "Ethiopia", "Rwanda"],
        "content": (
            "Breed performance by production system (pastoral, agropastoral, mixed), "
            "feed systems, disease management (CBPP, FMD, Newcastle, ASF), "
            "slaughter weights, offtake rates, value chain analysis."
        ),
        "citation": (
            "FAO/ILRI (2020). Livestock Production Systems in East Africa. "
            "Food and Agriculture Organisation, Rome."
        ),
    },
    {
        "tier": 2,
        "id": "ilri_breeds",
        "name": "ILRI Breed Catalogue for East and Central Africa",
        "publisher": "ILRI (International Livestock Research Institute)",
        "year": "2022",
        "crops": ["Cattle", "Goats", "Sheep", "Poultry", "Pigs"],
        "countries": ["Uganda", "Kenya", "Tanzania", "Ethiopia", "Rwanda",
                      "Zambia", "Malawi"],
        "content": (
            "Indigenous and improved breeds: Ankole, Boran, Zebu, KALRO dairy breeds, "
            "Kuroiler poultry, improved Large White pigs. "
            "Productivity benchmarks, disease tolerance, market traits, feed conversion ratios."
        ),
        "citation": (
            "ILRI (2022). Livestock Breed Catalogue for East and Central Africa. "
            "ILRI, Nairobi."
        ),
    },
]


# ── System prompt ─────────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are the ProSEIT Innovation-to-Implementation Agent.
ProSEIT (Professional Society for Engineering, Innovation & Technology) is a
Pan-African professional body headquartered in Uganda.

Your role: convert innovation ideas into complete, implementable product packages
that follow ProSEIT's governance framework, brand values, and technical standards.

Brand values: Integrity · Collaboration · Advocacy · Respect · Excellence
Tone: confident, precise, professional, forward-thinking.
Default tech stack (unless overridden): ERPNext/Frappe backend, Angular 18 frontend.
Edition model: Community (CE) · Professional (PE) · Enterprise Cloud (E-C) · Enterprise On-Premise (E-O).
Phase tags: MVP · FULL · PHASE-2 · PHASE-3 · OPTIONAL.

Format your response with clear markdown headings. Be specific and actionable.
Do not pad with filler text. Use tables where structured data helps.
""".strip()


# ── Knowledge base section builder ─────────────────────────────────────────────

def _build_kb_section(kb_context: dict | None) -> str:
    """Build a formatted KB section to append to any stage prompt."""
    if not kb_context:
        return ""

    selected_ids: list[str] = kb_context.get("selected_sources", [])
    user_content: str = kb_context.get("user_content", "").strip()

    if not selected_ids and not user_content:
        return ""

    lines: list[str] = [
        "\n\n---",
        "## Knowledge Base & Citation Requirements",
        "",
        "> **MANDATORY CITATION RULE**: Every variety name, yield figure, agronomic practice, "
        "breed characteristic, agrochemical rate, processing ratio, or validated technical "
        "specification you include MUST be cited inline using the format: "
        "`[Source Name, Year, Section/Page if known]`. "
        "Do not assert facts from these sources without a citation. "
        "If a required fact is not found in the sources below, flag it explicitly as: "
        "`[Unverified — requires validation against local data]`.",
        "",
        "> **KNOWLEDGE BASE INTEGRATION**: For each stage output, include a "
        "**Knowledge Base Integration** subsection that explicitly states which sources "
        "informed which recommendations, and how the validated data shaped the technical "
        "or commercial design decisions.",
        "",
    ]

    if selected_ids:
        lines.append("### Pre-Validated Sources Available\n")
        for src_id in selected_ids:
            src = next((s for s in AGRI_KB_REGISTRY if s["id"] == src_id), None)
            if not src:
                continue
            lines.append(f"**{src['name']}** *(Tier {src['tier']})*")
            lines.append(f"- Publisher: {src['publisher']}, {src['year']}")
            lines.append(f"- Crops / Topics: {', '.join(src['crops'])}")
            lines.append(f"- Countries validated for: {', '.join(src['countries'])}")
            lines.append(f"- What it provides: {src['content']}")
            lines.append(f"- Cite as: `{src['citation']}`")
            lines.append("")

    if user_content:
        lines.append("### User-Provided Knowledge Base Content\n")
        lines.append(
            "The following content was provided by the user from a validated source. "
            "Treat it as authoritative. "
            "Cite as: `[User-Provided Source, Section/Page if indicated]`.\n"
        )
        trimmed = user_content[:5000]
        if len(user_content) > 5000:
            trimmed += "\n\n... [content truncated — agent should reference the full document]"
        lines.append(f"```\n{trimmed}\n```\n")

    lines += [
        "### Deployment Context",
        "- **Pilot country**: Uganda (design all recommendations Uganda-first)",
        "- **Phase 2 markets**: Kenya, Tanzania, Rwanda",
        "- **Phase 3 markets**: Sudan, South Sudan, Zambia, Malawi, and Southern Africa",
        "- All variety, breed, or practice recommendations must reference specific "
        "**agro-ecological zones** in the relevant countries",
        "- Where performance data differs by country, state this explicitly in a table",
        "- If a validated source does not cover a specific country or crop, state: "
        "`[Source not available for [Country/Crop] — user may upload validated local "
        "data via the Knowledge Base upload feature in the ProSEIT Innovation Agent]`",
        "",
    ]

    return "\n".join(lines)


# ── Prompt builder ───────────────────────────────────────────────────────────────────

def _prompt_for_stage(
    stage: str,
    idea: str,
    context: dict,
    kb_context: dict | None = None,
) -> str:
    prior = "\n\n".join(
        f"### {STAGE_LABELS.get(k, k)}\n{v}"
        for k, v in context.items()
        if v
    )
    prior_section = f"\n\n---\n## Prior Stage Outputs\n{prior}" if prior else ""

    prompts = {
        "00_intake": f"""
## Stage 00 · Intake & Validation

Analyse the following innovation idea submitted to ProSEIT.

**Innovation Idea:**
{idea}

Produce:
1. **Innovation ID** — suggest a slug (lowercase, hyphens, e.g. `smart-cpd-tracker`)
2. **Title** — concise product name (≤8 words)
3. **Problem Statement** — what pain point does this solve?
4. **Target Users** — primary and secondary personas
5. **ProSEIT Strategic Fit** — how does this align with ProSEIT's mandate?
6. **Feasibility Assessment** — technical, financial, operational (High / Medium / Low each)
7. **Recommended Scope** — MVP scope in ≤5 bullet points
8. **Next-Stage Flags** — which later stages need special attention?
""",

        "01_policy": f"""
## Stage 01 · Policy & Compliance

Based on the innovation below, identify all relevant policy and compliance requirements.{prior_section}

Produce:
1. **Applicable Regulations** — data protection, professional licensing, sector-specific laws (focus on Uganda / East Africa / Pan-Africa)
2. **ProSEIT Governance Committees Required** — list from:
   - Professional Training and Certification Committee
   - Legal, Arbitration and Communication Committee
   - Professional Standards and Ethics Committee
   - Investment Advisory Committee
   - Innovations, Patents and Intellectual Property Committee
3. **IP & Patent Considerations**
4. **Data Residency Requirements**
5. **Compliance Checklist** — table with Item | Requirement | Status
""",

        "02_concept": f"""
## Stage 02 · Concept Development

Develop the full product concept for the innovation.{prior_section}

Produce:
1. **Product Vision Statement** (one sentence)
2. **Key Features** — grouped by edition (CE / PE / E-C / E-O) and phase tag (MVP / FULL / PHASE-2)
3. **Unique Value Proposition**
4. **Competitive Landscape** — 3-5 comparable solutions, gap analysis
5. **Success Metrics** — KPIs with targets
6. **Assumptions & Risks** — table with Risk | Likelihood | Impact | Mitigation
7. **Knowledge Base Integration** — how validated sources from the knowledge base inform the concept and differentiate it from unvalidated alternatives
""",

        "03_editions": f"""
## Stage 03 · Edition Planning

Define the edition and licensing model.{prior_section}

Produce a table for each of the four editions:

| Feature | CE | PE | E-C | E-O |
|---|---|---|---|---|

Then provide:
1. **Licensing Model** — open-source vs. proprietary per edition
2. **Pricing Rationale** — narrative (exact figures are Stage 14)
3. **Upgrade Path** — how users move between editions
4. **Support Tiers** per edition
""",

        "04_architecture": f"""
## Stage 04 · Technical Architecture

Design the technical architecture.{prior_section}

Produce:
1. **Architecture Diagram Description** — describe components and interactions in prose (ASCII diagram if helpful)
2. **Tech Stack** — layer by layer (frontend, backend, database, infrastructure)
3. **ERPNext/Frappe Modules Used** — list doctypes and custom apps
4. **Angular 18 Modules** — list key Angular modules and routing
5. **Integration Points** — external systems
6. **Scalability Considerations** — for CE vs. Enterprise
7. **Non-Functional Requirements** — performance, availability, disaster recovery
8. **Knowledge Base Integration** — how validated agronomic/livestock data from the knowledge base is stored, queried, and surfaced within the architecture
""",

        "05_user_stories": f"""
## Stage 05 · User Stories

Write comprehensive user stories.{prior_section}

Format each as:
> As a [persona], I want to [action] so that [benefit].

Group by:
- **MVP Stories** (must ship in v1.0)
- **FULL Stories** (complete the feature set)
- **PHASE-2 Stories** (future enhancement)

Include acceptance criteria for each MVP story.
""",

        "06_ux_wireframes": f"""
## Stage 06 · ProSEIT Innovation-Specific Angular UIX Prototype Pack Generator

You are a multidisciplinary senior agent acting simultaneously as:
- UIX Prototyping Engineer (HTML/CSS/JS, Angular Material simulation)
- Angular 18 Architect (component architecture, routing, state)
- ERPNext/Frappe Integration Analyst (DocTypes, hooks, REST APIs)
- Business Analyst (epics, user stories, screen flows)
- QA Architect (acceptance criteria, test coverage mapping)

Your mission: Generate a COMPLETE, INNOVATION-SPECIFIC Angular UIX prototype pack for the innovation described below. Every screen, component name, DocType reference, and data field must be SPECIFIC to this innovation — not generic. A reviewer must immediately identify which product a screen belongs to without reading the page title.

**Innovation Idea:**
{idea}
{prior_section}

---

## PHASE 1 — INTERNAL ANALYSIS

Before generating files, work through these analysis steps:

### Step 1: Innovation Context Profile
Extract from the idea and prior stages:
- Innovation short code (3–5 uppercase letters, e.g. SMART, AGRI, CPDT)
- Core domain and sub-domain
- Primary personas
- MVP feature set
- Technology stack (ERPNext/Frappe + Angular 18 confirmed)

### Step 2: User Story & Role Analysis
Map every MVP user story (from Stage 05 or derived from idea) to:
- Actor / persona
- Screen that fulfils it
- DocType(s) required
- Acceptance criteria

### Step 3: Architecture Module Analysis
From Stage 04 (or derive), identify:
- Angular feature modules and shared module
- Frappe custom app name
- Key DocTypes (custom + standard ERPNext)
- Critical API endpoints

### Step 4: Epic & Screen Plan
Name each of the 8 feature screens (p1–p8) using innovation-specific names:
- Screen name (e.g. "Crop Yield Monitor" not "Feature Screen 1")
- Angular component selector using the innovation short code (e.g. `app-crop-yield-card`)
- Primary DocType(s)
- Primary user story(ies) satisfied

### Step 5: Anti-Generic Validation
For EACH planned screen, verify:
☑ Screen name references the innovation domain
☑ Angular component selector contains innovation-specific terminology
☑ Sample data uses domain-realistic values (not "Sample Item 1", "User Name")
☑ DocType names are innovation-specific
☑ Layout serves the innovation's workflow, not a generic CRUD form

---

## PHASE 2 — FILE GENERATION

Generate ALL files using ONLY this delimiter format. No markdown code fences:

===UIX_FILE: [filename] ===
[complete file content]
===UIX_END===

### FILES TO GENERATE (in order):

1. `a/s.css` — Master stylesheet
2. `a/j.js` — Master JavaScript
3. `i.html` — Dashboard / Home (innovation-specific KPIs and charts)
4. `p1.html` — [Innovation-specific screen from Step 4]
5. `p2.html` — [Innovation-specific screen from Step 4]
6. `p3.html` — [Innovation-specific screen from Step 4]
7. `p4.html` — [Innovation-specific screen from Step 4]
8. `p5.html` — [Innovation-specific screen from Step 4]
9. `p6.html` — [Innovation-specific list/search screen]
10. `p7.html` — [Innovation-specific detail/form screen]
11. `p8.html` — [Innovation-specific reports/analytics screen]
12. `g.html` — System Settings (innovation-specific config options)
13. `s.html` — Superadmin / System Administration
14. `readme.md` — Developer Handover Document
15. `ng/cmp.md` — Angular Component Specification
16. `ng/svc.md` — Angular Service & State Specification
17. `xl_map.md` — UIX Mapping Workbook Source Data (13 sections, see spec below)

---

### DESIGN REQUIREMENTS

#### Brand & Colours
- Primary Navy: `#24364B`
- Gold Accent: `#D4A62A`
- White: `#FFFFFF`
- Soft Grey: `#F4F6F8`
- Dark Text: `#1F2933`
- Sidebar: Navy bg, White text, Gold active item
- Buttons: primary = Navy + White; accent = Gold + Dark text

#### Layout (ALL pages)
- Fixed left sidebar (240px) with links to ALL pages
- Top navbar: ProSEIT wordmark, innovation name, page title, user avatar, notification bell
- Main content: 24px padding
- Footer: `ProSEIT · Plot 5 Blue Heights Plaza, Nkrumah Road, Kampala, Uganda  |  Tel: +256 790 334 653  |  www.proseit.org  |  info@proseit.org`
- Responsive: sidebar collapses to hamburger at <768px

#### Anti-Generic Rule — MANDATORY
Every screen MUST:
- Use innovation's domain terminology in headings, labels, column names
- Show domain-realistic sample data (Uganda/East Africa context, UGX currency)
- Have an innovation-specific `<title>` and `<h1>`
- Name Angular components with innovation short code in the selector
- Reference real innovation-specific DocType names

#### Angular Material Simulation (plain HTML/CSS)
- `mat-card`: white card, 2px left gold border, box-shadow 0 2px 8px rgba(0,0,0,0.08)
- `mat-table`: striped rows, navy header, gold sort arrows
- `mat-button`: rounded 4px, CSS :active ripple
- `mat-chip`: pill badges — Active=green, Pending=gold, Inactive=grey
- `mat-form-field`: underline inputs, gold focus ring
- `mat-toolbar`, `mat-sidenav`, `mat-dialog`, `mat-snackbar`, `mat-progress-bar`, `mat-tab`

#### Developer Handover Panel (p1–p8 only)
Collapsible `<details>` at bottom (soft grey bg, navy border):
- DocType(s), API Endpoints, Key Fields, Permissions, Custom App
- Angular Component (innovation-specific selector), Module, Route
- Data Binding: `@Input()` / `@Output()`

#### Dashboard (i.html)
- 4 innovation-domain KPI cards with realistic UGX/count values
- 2 CSS/SVG charts (bar + donut)
- 5-item recent activity feed (domain-specific events)
- Quick actions panel (innovation-specific actions)
- Alerts section

#### JavaScript (a/j.js)
Vanilla JS only (no jQuery): sidebar toggle, tab switching, modal open/close,
`showToast(message, type)`, table search/filter, SVG/canvas charts, form validation.

#### CSS (a/s.css)
CSS custom properties, CSS Grid layout, all Angular Material simulations,
breakpoints at 768px and 480px, print styles, smooth transitions.

---

### ng/cmp.md — Angular Component Specification

1. **Component Tree** — hierarchical list
2. **Component Catalogue** table:

| Component Class | Selector | Module | Inputs | Outputs | Screen(s) | DocType(s) |
|---|---|---|---|---|---|---|

Minimum 15 innovation-specific components. Use innovation short code in all selectors.

3. **Routing Table**: Route Path | Component | Guard | Module | Screen File
4. **State Management** — NgRx slices or service state per module
5. **Shared Components** — reusable component API

---

### ng/svc.md — Angular Service & State Specification

1. **Service Inventory** table:

| Service Class | Injected In | Frappe Endpoint(s) | State Managed | Methods |
|---|---|---|---|---|

2. HTTP Interceptors (auth token, error handling, loading spinner)
3. Frappe API Wrapper — `FrappeService` base class description
4. Innovation-Specific Services — each feature service with method signatures
5. Error Handling Strategy

---

### xl_map.md — UIX Mapping Workbook Source Data

This file is parsed into 13 Excel sheets. Use EXACTLY these 13 `## ` headings in this order, each followed by a markdown table:

## UI Catalog
| Screen File | Screen Name | Angular Component | Route | DocType(s) | Edition | Phase |

## Story Coverage
| Story ID | Story Text | Screen(s) | Component(s) | Status |

## Epic Coverage
| Epic | Stories | Screens | Complete % | Notes |

## Angular Components
| Component | Selector | Module | Inputs | Outputs | Screen(s) | DocType(s) |

## Backend Mapping
| Screen | DocType | API Method | HTTP Method | Auth Role | Custom App |

## ERPNext Reuse
| Standard DocType | Used As / Extended For | Customisation Needed | Screen(s) |

## Frappe DocTypes APIs
| DocType | Custom? | Parent DocType | Key Fields | API Endpoint | Permissions |

## QA Acceptance
| Story ID | Screen | Test Scenario | Input | Expected Output | Pass Criteria |

## Reports
| Report Name | Type | DocType | Filters | Columns | Screen |

## Mobile Screens
| Screen File | Mobile Layout | Breakpoint | Touch Targets | Collapsed Nav |

## Image Use
| File | Image Description | Alt Text | Dimensions | Purpose |

## Project Structure
| Path | Type | Description | Angular Module | Frappe App |

## Intern Resources
| Resource | Type | URL / Reference | Skill Level | Covers |

(Include 8–10 learning resources relevant to the tech stack and innovation domain)

---

Generate ALL 17 files completely. Every screen must be immediately identifiable as belonging to this specific innovation.
""",

        "07_data_model": f"""
## Stage 07 · Data Model

Define the complete data model for the innovation.{prior_section}

Produce:
1. **Entity Relationship Overview** — prose description of main entities and relationships
2. **Frappe DocType Definitions** — for each DocType:

   | DocType | Fields | Field Types | Mandatory | Linked To |
   |---|---|---|---|---|

   Include all custom doctypes required. Note which are child tables.
3. **Standard Frappe Doctypes Used** — list existing Frappe/ERPNext doctypes leveraged (Customer, User, etc.)
4. **Data Validation Rules** — key constraints, regex patterns, range checks
5. **Indexing Strategy** — which fields need database indexes and why
6. **Data Migration Plan** — if migrating from existing systems, describe the migration approach
7. **Data Retention & Archival Policy** — per entity, how long data is kept and archival rules
8. **Multi-tenancy Considerations** — how data is isolated between organisations (CE vs. E-C)
9. **Knowledge Base Integration** — how validated variety/breed/practice data from the knowledge base is modelled (e.g. a KnowledgeBase DocType, variety lookup tables, citation fields)
""",

        "08_api_design": f"""
## Stage 08 · API Design

Design the complete API for the innovation.{prior_section}

Produce:
1. **API Architecture** — REST vs. Frappe RPC vs. custom; versioning strategy
2. **Endpoint Inventory** — table for all endpoints:

   | Method | Endpoint | Description | Auth Required | Request Body | Response |
   |---|---|---|---|---|---|

   Group by resource (e.g. /api/v1/innovations/, /api/v1/users/)
3. **Authentication & Authorisation** — Frappe session tokens, API keys, OAuth2 flows
4. **Request / Response Schemas** — JSON schema for key endpoints (create, read, update)
5. **Error Codes** — table: HTTP Code | Error Type | Message | Resolution
6. **Rate Limiting** — limits per tier (CE / PE / Enterprise), headers returned
7. **Pagination** — strategy (cursor vs. offset), default page size, max page size
8. **API Versioning** — how breaking changes will be managed
9. **Frappe Hooks Used** — list relevant `hooks.py` entries (doc_events, override_whitelisted_methods, etc.)
""",

        "09_integrations": f"""
## Stage 09 · Integrations

Define all integration requirements.{prior_section}

Produce:
1. **Integration Inventory** — table: System | Type | Direction | Protocol | Auth | Priority | Edition
2. **ERPNext Native Integrations** — which Frappe integrations apply out-of-the-box (e.g. Email, SMS, Payment Gateways)
3. **Custom Integration Specs** — for each custom integration:
   - Endpoint URL pattern
   - Payload schema (request + response)
   - Error handling and retry logic
   - Frequency / trigger
4. **Webhook Events** — table: Event Name | Trigger | Payload Fields | Consumers
5. **Third-Party Services** — table: Service | Purpose | Free Tier | Paid Tier | Data Shared
6. **API Rate Limits & SLAs** — per integration, what limits apply
7. **Integration Testing Plan** — how each integration will be tested (mocks, sandbox, live)
8. **Fallback Behaviour** — what happens when each integration is unavailable
""",

        "10_security": f"""
## Stage 10 · Security

Produce a comprehensive security design for the innovation.{prior_section}

Produce:
1. **Threat Model** — table: Threat | Attack Vector | Likelihood | Impact | Control
   Cover: authentication bypass, data exfiltration, injection, privilege escalation, DoS
2. **OWASP Top 10 Mitigations** — for each OWASP item, state the specific control implemented
3. **Authentication & Session Management** — password policy, MFA requirements, session timeout, token rotation
4. **Authorisation Model** — Frappe roles and permissions matrix:

   | Role | DocType | Read | Write | Create | Delete | Submit |
   |---|---|---|---|---|---|---|

5. **Data Protection** — encryption at rest (fields, backups), encryption in transit (TLS config)
6. **Input Validation & Sanitisation** — key validation rules, XSS/SQLi prevention approach
7. **Audit Logging** — what events are logged, log format, retention period
8. **Vulnerability Management** — dependency scanning, patching cadence, penetration testing schedule
9. **Compliance Mapping** — how controls map to GDPR / Uganda DPA / ISO 27001 (where applicable)
10. **Security Testing Plan** — SAST, DAST, manual review checkpoints
""",

        "11_testing": f"""
## Stage 11 · Testing Strategy

Define the complete testing strategy for the innovation.{prior_section}

Produce:
1. **Testing Pyramid** — describe the balance of unit / integration / E2E tests for this product
2. **Unit Tests** — table: Module | Function/Method | Test Cases | Edge Cases
3. **Integration Tests** — table: Component A | Component B | Test Scenario | Expected Outcome
4. **API Tests** — table: Endpoint | Method | Input | Expected Status | Expected Body
5. **End-to-End (E2E) Tests** — key user journeys to automate (use Playwright or Cypress):

   | Journey | Steps | Pass Criteria |
   |---|---|---|

6. **Performance Tests** — load targets, tools (Locust / k6), scenarios (normal load, spike, soak)
7. **UAT Plan** — user acceptance test scenarios, tester personas, sign-off criteria
8. **Test Data Strategy** — how test data is created, anonymised, and seeded
9. **CI/CD Test Gates** — which test suites must pass before merge, before deploy to staging, before production
10. **Defect Management** — severity definitions, SLA for fix, tracking tool
""",

        "12_deployment": f"""
## Stage 12 · Deployment

Design the deployment architecture and CI/CD pipeline.{prior_section}

Produce:
1. **Environment Strategy** — table: Environment | Purpose | Branch | Auto-deploy? | Data
   (Development, Staging, UAT, Production — for CE and Enterprise separately where different)
2. **Infrastructure Design** — for each environment describe:
   - Cloud provider / hosting (recommend AWS / GCP / on-premise for Uganda context)
   - Compute: VMs, containers, or Kubernetes
   - Database: managed or self-hosted MariaDB
   - Storage: file attachments, backups
   - CDN / load balancer
3. **Frappe Bench Setup** — bench commands, app installation sequence, site creation
4. **CI/CD Pipeline** — describe the pipeline stages (GitHub Actions recommended):

   | Stage | Trigger | Steps | Failure Action |
   |---|---|---|---|

5. **Docker / Container Strategy** — Dockerfile structure, docker-compose for local dev
6. **Infrastructure as Code** — tools (Terraform / Ansible), key resources defined
7. **Zero-Downtime Deployment** — blue-green or rolling strategy for production updates
8. **Rollback Plan** — how to revert a bad deployment within 15 minutes
9. **Backup & Disaster Recovery** — backup frequency, RTO, RPO, restore procedure
10. **Monitoring & Alerting** — tools (Prometheus/Grafana, Sentry), key metrics and alert thresholds
""",

        "13_documentation": f"""
## Stage 13 · Documentation

Define the complete documentation plan for the innovation.{prior_section}

Produce:
1. **Documentation Inventory** — table: Document | Audience | Format | Owner | Review Cycle

2. **Technical Documentation** — outline the structure of:
   - Architecture Decision Records (ADRs) — list the 5 most important decisions to record
   - Developer Setup Guide — key sections
   - API Reference — how it will be generated (auto from docstrings / OpenAPI spec)
   - Database Schema Reference

3. **User Documentation** — outline the structure of:
   - User Manual (by role/persona)
   - Quick Start Guide
   - FAQ (list the 10 most likely user questions)
   - Video tutorial topics (list 5 key tutorials)

4. **Administrator Documentation** — outline:
   - Installation & Configuration Guide (CE edition)
   - Enterprise Deployment Guide
   - Backup & Recovery Runbook
   - User Management Guide

5. **ProSEIT Governance Documentation** — outline:
   - Governance Submission Pack (for committee review)
   - Change Control Procedure

6. **Knowledge Base Documentation** — outline:
   - Knowledge Base Source Registry (list of all validated sources, access method, citation format)
   - Knowledge Base Update Procedure (how to add new validated sources)
   - Citation Standards Guide (for all outputs referencing KB sources)

7. **Documentation Toolchain** — recommended tools (MkDocs, Docusaurus, Sphinx), hosting (GitHub Pages / ReadTheDocs)
8. **Localisation Plan** — languages to support (include Luganda, Swahili for East Africa), translation workflow
""",

        "14_budget": f"""
## Stage 14 · Budget & Cost Model

Produce a comprehensive budget.{prior_section}

Sections:
1. **Development Cost Estimate** — table: Item | CE | PE | Enterprise | Notes
2. **Infrastructure Cost** (monthly) — cloud, hosting, CDN, backups
3. **Licensing & Third-Party Costs**
4. **Human Resources** — roles, effort in person-months, cost range (USD)
5. **Total Cost of Ownership** — Year 1, Year 2, Year 3
6. **Break-Even Analysis** — assumptions and timeline
7. **Funding Recommendations** — grants, sponsorship, revenue share
""",

        "15_business_plan": f"""
## Stage 15 · Business Plan

Produce an executive-ready business plan.{prior_section}

Sections:
1. **Executive Summary** (≤150 words)
2. **Market Opportunity** — TAM / SAM / SOM for the target geography
3. **Revenue Model** — streams, pricing tiers, projections (Year 1–3)
4. **Go-to-Market Strategy** — channels, partnerships, launch plan
5. **Competitive Advantages**
6. **Financial Projections** — revenue, costs, EBITDA (table)
7. **Key Risks & Mitigations**
8. **Investment Ask** (if applicable)
""",

        "16_governance": f"""
## Stage 16 · Governance Routing

Produce the full governance routing recommendation.{prior_section}

For each of the five ProSEIT committees, state:
- **Triggered**: Yes / No
- **Reason**: why this innovation requires (or does not require) this committee's review
- **Required Actions**: specific decisions or approvals needed
- **Priority**: High / Medium / Low

Committees:
1. Professional Training and Certification Committee
2. Legal, Arbitration and Communication Committee
3. Professional Standards and Ethics Committee
4. Investment Advisory Committee
5. Innovations, Patents and Intellectual Property Committee

End with a **Governance Summary Table** and recommended sequence of committee reviews.
""",

        "17_roadmap": f"""
## Stage 17 · Roadmap

Produce a phased delivery roadmap.{prior_section}

Format:
1. **Milestone Timeline** — table: Milestone | Phase | Target Quarter | Deliverables | Owner Role
2. **Sprint Zero** — pre-development setup tasks
3. **MVP Release Plan** — features, acceptance criteria, launch checklist
4. **Post-MVP Phases** — FULL, PHASE-2, PHASE-3 with estimated timelines
5. **Dependencies & Critical Path**
6. **Resource Plan** — team composition by phase
""",

        "18_package": f"""
## Stage 18 · Final Implementation Package

Produce the complete implementation package summary.{prior_section}

Sections:
1. **Innovation Profile Card** — title, ID, vision, editions, primary committee
2. **Executive Summary** (≤200 words, suitable for ProSEIT board)
3. **Implementation Readiness Score** — rate each dimension 1-5:
   - Technical Feasibility
   - Market Readiness
   - Resource Availability
   - Governance Clearance
   - Financial Viability
4. **Top 10 Action Items** — table: Action | Owner Role | Due | Priority
5. **Document Index** — list all artefacts produced in this pipeline run
6. **Knowledge Base Sources Cited** — table: Source | Citation | Stages Used In
7. **Recommended Next Steps** — three concrete steps the ProSEIT team should take this week
8. **Sign-off Block** — placeholders for Prepared By / Approved By / Date
""",
    }

    default_prompt = f"""
## {STAGE_LABELS.get(stage, stage)}

Continue the innovation pipeline for the product below.{prior_section}

**Innovation Idea:**
{idea}

Produce a thorough, actionable output for this stage following ProSEIT standards.
"""

    prompt = prompts.get(stage, default_prompt).strip()

    # Append KB section for all stages when agriculture context is present
    kb_section = _build_kb_section(kb_context)
    if kb_section:
        prompt = prompt + kb_section

    return prompt


# ── Pipeline runner ───────────────────────────────────────────────────────────────────

def run_pipeline(
    idea: str,
    api_key: str,
    stages: list[str] | None = None,
    progress_cb: Callable[[str, float], None] | None = None,
    kb_context: dict | None = None,
) -> dict[str, str]:
    """Run selected pipeline stages and return results dict."""
    selected = stages or STAGES
    results: dict[str, str] = {}
    context: dict[str, str] = {}

    for i, stage in enumerate(selected):
        if progress_cb:
            progress_cb(STAGE_LABELS.get(stage, stage), i / len(selected))

        prompt = _prompt_for_stage(stage, idea, context, kb_context=kb_context)
        output = call_claude(prompt, system=SYSTEM_PROMPT, api_key=api_key)
        results[stage] = output
        context[stage] = output

    if progress_cb:
        progress_cb("Complete", 1.0)

    return results
