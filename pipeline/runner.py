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
    "06_ux_wireframes":"Stage 06 · UIX Prototype",
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

# ── Agriculture sector detection ─────────────────────────────────────────────────────

AGRI_SECTORS = {
    "Agriculture & Agronomy",
    "AgriTech & Precision Agriculture",
    "Agroprocessing & Value Addition",
    "Agriculture Value Chains",
    "Animal Husbandry & Livestock",
    "Forestry, Bamboo & NTFPs",
    "Apiculture & Beekeeping",
}

# ── Agriculture knowledge base registry ──────────────────────────────────────────────
AGRI_KB_REGISTRY: list[dict] = [
    {"tier": 1, "id": "adcrc", "name": "Africa Digital Crop Variety Catalogue (ADCRC)", "publisher": "AGRA", "year": "2023", "crops": ["Maize", "Beans", "Cassava"], "countries": ["Uganda", "Tanzania", "Kenya", "Rwanda", "Malawi", "Ethiopia"], "content": "Structured variety data: maturity days, yield potential, drought tolerance, CMD/CBSD resistance, recommended agro-ecological zones.", "citation": "AGRA (2023). Africa Digital Crop Variety Catalogue (ADCRC). Alliance for a Green Revolution in Africa, Nairobi."},
    {"tier": 1, "id": "naro_catalogue", "name": "NARO National Crop Variety Release Catalogue", "publisher": "National Agricultural Research Organisation (NARO), Uganda", "year": "2023", "crops": ["Maize", "Beans", "Bananas", "Cassava", "Pineapple", "Sorghum", "Groundnuts", "Sweet Potato"], "countries": ["Uganda"], "content": "Release year, breeder, yield, recommended agro-ecological zones, biotic/abiotic stress resistance. Legal authority for Uganda variety registration.", "citation": "NARO (2023). National Crop Variety Release Catalogue. National Agricultural Research Organisation, Entebbe, Uganda."},
    {"tier": 1, "id": "kephis_nvl", "name": "KEPHIS National Variety List", "publisher": "Kenya Plant Health Inspectorate Service (KEPHIS)", "year": "2024", "crops": ["Maize", "Beans", "Cassava", "Pineapple", "Sorghum"], "countries": ["Kenya"], "content": "Officially released varieties with performance data for Kenyan agro-ecological zones.", "citation": "KEPHIS (2024). National Variety List. Kenya Plant Health Inspectorate Service, Nairobi."},
    {"tier": 1, "id": "tari_catalogue", "name": "TARI Crop Variety Catalogue", "publisher": "Tanzania Agricultural Research Institute (TARI)", "year": "2023", "crops": ["Maize", "Beans", "Cassava", "Cashew", "Sorghum"], "countries": ["Tanzania"], "content": "Released varieties for Tanzania with yield, maturity, and stress tolerance data.", "citation": "TARI (2023). Crop Variety Catalogue. Tanzania Agricultural Research Institute, Dodoma."},
    {"tier": 1, "id": "rab_catalogue", "name": "RAB Crop Variety Catalogue", "publisher": "Rwanda Agriculture and Animal Resources Development Board (RAB)", "year": "2023", "crops": ["Maize", "Beans", "Cassava", "Banana"], "countries": ["Rwanda"], "content": "Released varieties for Rwanda with performance data across agro-ecological zones.", "citation": "RAB (2023). Crop Variety Catalogue. Rwanda Agriculture and Animal Resources Development Board, Kigali."},
    {"tier": 2, "id": "cimmyt_maize", "name": "CIMMYT/NARO Maize Variety Catalogue for Eastern Africa", "publisher": "CIMMYT & NARO", "year": "2022", "crops": ["Maize"], "countries": ["Uganda", "Kenya", "Tanzania", "Ethiopia", "Rwanda"], "content": "Drought-tolerant, Striga-resistant, N-use efficient hybrids. DH, SC, OPV lines by altitude and agro-zone.", "citation": "CIMMYT/NARO (2022). Maize Variety Catalogue for Eastern Africa. CIMMYT, Nairobi."},
    {"tier": 2, "id": "ciat_beans", "name": "CIAT/PABRA Bean Variety Catalogue for Eastern and Central Africa", "publisher": "CIAT & Pan-Africa Bean Research Alliance (PABRA)", "year": "2023", "crops": ["Beans", "Common Bean"], "countries": ["Uganda", "Kenya", "Tanzania", "Rwanda", "DRC", "Malawi", "Zambia"], "content": "100+ varieties with BBMV, BCMV, anthracnose, low-fertility tolerance, cooking time, protein content.", "citation": "CIAT/PABRA (2023). Bean Variety Catalogue for Eastern and Central Africa. CIAT, Cali, Colombia."},
    {"tier": 2, "id": "bioversity_banana", "name": "Banana Cultivars in Eastern Africa", "publisher": "Bioversity International / IITA", "year": "2021", "crops": ["Banana", "Plantain", "Matooke"], "countries": ["Uganda", "Tanzania", "Kenya", "Rwanda", "DRC"], "content": "Matooke, cooking, dessert, and beer banana types. Nematode, weevil, BXW resistance ratings.", "citation": "Bioversity International/IITA (2021). Banana Cultivars in Eastern Africa. Bioversity International, Rome."},
    {"tier": 2, "id": "iita_cassava", "name": "Cassava Varieties of Africa", "publisher": "IITA", "year": "2022", "crops": ["Cassava"], "countries": ["Uganda", "Tanzania", "Kenya", "Rwanda", "DRC", "Zambia", "Malawi"], "content": "CMD1, CMD2, CBSD resistant varieties by zone. Dry matter content, yield, cyanide levels.", "citation": "IITA (2022). Cassava Varieties of Africa. International Institute of Tropical Agriculture, Ibadan."},
    {"tier": 2, "id": "fao_livestock", "name": "FAO Livestock Production Systems in Uganda and East Africa", "publisher": "FAO / ILRI", "year": "2020", "crops": ["Livestock", "Cattle", "Goats", "Poultry", "Pigs", "Sheep"], "countries": ["Uganda", "Kenya", "Tanzania", "Ethiopia", "Rwanda"], "content": "Breed performance by production system, feed systems, disease management, slaughter weights, offtake rates.", "citation": "FAO/ILRI (2020). Livestock Production Systems in East Africa. Food and Agriculture Organisation, Rome."},
]


# ── System prompt ──────────────────────────────────────────────────────────────────────────

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


# ── Knowledge base section builder ───────────────────────────────────────────────────

def _build_kb_section(kb_context: dict | None) -> str:
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
        trimmed = user_content[:5000]
        if len(user_content) > 5000:
            trimmed += "\n\n... [content truncated]"
        lines.append(f"```\n{trimmed}\n```\n")
    lines += [
        "### Deployment Context",
        "- **Pilot country**: Uganda (design all recommendations Uganda-first)",
        "- **Phase 2 markets**: Kenya, Tanzania, Rwanda",
        "- **Phase 3 markets**: Sudan, South Sudan, Zambia, Malawi, and Southern Africa",
        "",
    ]
    return "\n".join(lines)


# ── Prompt builder ──────────────────────────────────────────────────────────────────────

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
## Stage 06 · UIX Prototype Generator

You are generating a complete, browsable Angular UIX prototype for the innovation described below.{prior_section}

**Innovation Idea:**
{idea}

---

### OUTPUT FORMAT — CRITICAL

Output EVERY file using this exact delimiter format. Do NOT use markdown code fences. Use ONLY the delimiters:

===UIX_FILE: [filename] ===
[complete file content]
===UIX_END===

Generate ALL of the following files in order:

1. `a/s.css` — Master stylesheet
2. `a/j.js` — Master JavaScript
3. `i.html` — Dashboard / Home screen
4. `p1.html` — Primary feature screen 1
5. `p2.html` — Primary feature screen 2
6. `p3.html` — Primary feature screen 3
7. `p4.html` — Primary feature screen 4
8. `p5.html` — Primary feature screen 5
9. `p6.html` — Secondary feature / list screen
10. `p7.html` — Detail / form screen
11. `p8.html` — Reports / analytics screen
12. `g.html` — Global settings / configuration
13. `s.html` — Superadmin / system admin panel
14. `readme.md` — Developer handover notes

---

### DESIGN REQUIREMENTS

#### Brand & Colours
- Primary Navy: `#24364B`
- Gold Accent: `#D4A62A`
- White: `#FFFFFF`
- Soft Grey: `#F4F6F8`
- Dark Text: `#1F2933`
- Sidebar background: `#24364B`, sidebar text: `#FFFFFF`, active item: `#D4A62A`
- Top bar: Navy with Gold accent strip
- All buttons: primary = Navy bg + White text; accent = Gold bg + Dark text

#### Layout (all pages)
- Fixed left sidebar (240px wide) with navigation links to ALL pages (i.html, p1–p8, g.html, s.html)
- Top navbar with: ProSEIT logo text, page title, user avatar chip, notification bell
- Main content area with padding 24px
- Footer bar: `ProSEIT · Plot 5 Blue Heights Plaza, Nkrumah Road, Kampala, Uganda | Tel: +256 790 334 653 | www.proseit.org | info@proseit.org`
- Fully responsive: sidebar collapses to hamburger on mobile (<768px)

#### Angular Material Simulation
- Use plain HTML + CSS to simulate Angular Material components:
  - `mat-card`: white card, 2px border-left gold, box-shadow 0 2px 8px rgba(0,0,0,0.08)
  - `mat-table`: striped rows, navy header, gold sort arrows
  - `mat-button`: rounded 4px, ripple effect via CSS :active
  - `mat-chip`: small pill badges for status (Active=green, Pending=gold, Inactive=grey)
  - `mat-form-field`: underline-style inputs with gold focus ring
  - `mat-toolbar`: top bar component
  - `mat-sidenav`: sidebar component
  - `mat-dialog`: modal overlay (trigger via JS)
  - `mat-snackbar`: toast notification at bottom
  - `mat-progress-bar`: gold/navy gradient progress bar
  - `mat-tab`: tab strip with gold underline on active tab

#### ERPNext/Frappe Backend Mapping
On each feature page (p1–p8), include a **Developer Handover Panel** — a collapsible `<details>` element at the bottom of the page styled in soft grey with navy border, containing:
- **DocType(s)**: which Frappe DocTypes this screen maps to
- **API Endpoints**: `frappe.call` method names or REST paths (GET/POST)
- **Key Fields**: field names and types from the DocType
- **Permissions**: which Frappe roles can access this screen
- **Custom App**: which custom Frappe app this module belongs to
- **Angular Component**: component name (e.g. `FeatureListComponent`), selector, module
- **Routing**: Angular route path (e.g. `/app/feature/list`)
- **Data Binding**: key `@Input()` and `@Output()` bindings

#### Dashboard (i.html) Requirements
- 4 KPI stat cards at top (use realistic numbers for this innovation domain)
- 2 charts simulated with CSS bars or SVG (bar chart + line/donut)
- Recent activity feed (5 items)
- Quick action buttons panel
- Alerts/notifications section

#### Realistic Sample Data
- Populate ALL tables, lists, and forms with 5–8 rows of realistic, domain-specific sample data relevant to this innovation
- Use Uganda/East Africa context for names, locations, currencies (UGX), dates

#### Screen-Specific Naming
Name each p1–p8 screen based on the MVP user stories from Stage 05 and the architecture from Stage 04. If prior stages are not available, derive screen names from the innovation idea.

#### Settings (g.html)
- System settings: organisation name, logo upload placeholder, currency, timezone, language
- Notification settings: email/SMS toggles
- Integration settings: API key fields (masked)
- Edition badge showing current edition (CE/PE/E-C/E-O)

#### Superadmin (s.html)
- User management table with roles
- Tenant/organisation list (for E-C edition)
- System health dashboard (CPU, memory, DB size — simulated)
- Audit log table
- Licence key management

#### JavaScript (a/j.js)
- Sidebar toggle for mobile
- Tab switching logic
- Modal open/close
- Toast notification function `showToast(message, type)`
- Simple search/filter for tables
- Chart rendering using inline SVG or canvas (no external chart library)
- Form validation helpers
- All JS must be vanilla (no jQuery, no frameworks)

#### CSS (a/s.css)
- Full reset + box-sizing
- CSS custom properties (variables) for all brand colours
- Sidebar, navbar, main content layout using CSS Grid
- All Angular Material component simulations
- Responsive breakpoints at 768px and 480px
- Print styles hiding sidebar and navbar
- Smooth transitions on sidebar collapse and modal

#### readme.md
Produce a developer handover document with:
1. **Project Overview** — product name, innovation ID, tech stack
2. **File Structure** — annotated list of all files
3. **Navigation Map** — table: File | Screen Name | Angular Component | Route
4. **DocType Map** — table: Screen | DocType(s) | Custom App
5. **Edition Feature Matrix** — which screens/features are CE vs PE vs Enterprise
6. **Getting Started** — steps to integrate into Frappe/Angular app
7. **Design Tokens** — list all CSS variables with their values
8. **Known Limitations** — what this prototype does not include
9. **Next Steps** — 5 concrete development actions

---

Generate complete, production-quality HTML/CSS/JS. Every file must be fully self-contained (linking to `a/s.css` and `a/j.js`). Do not truncate any file. Output all 14 files in order.
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
3. **Standard Frappe Doctypes Used** — list existing Frappe/ERPNext doctypes leveraged
4. **Data Validation Rules** — key constraints, regex patterns, range checks
5. **Indexing Strategy** — which fields need database indexes and why
6. **Data Migration Plan** — if migrating from existing systems
7. **Data Retention & Archival Policy** — per entity
8. **Multi-tenancy Considerations** — how data is isolated between organisations
""",

        "08_api_design": f"""
## Stage 08 · API Design

Design the complete API for the innovation.{prior_section}

Produce:
1. **API Architecture** — REST vs. Frappe RPC vs. custom; versioning strategy
2. **Endpoint Inventory** — table for all endpoints:

   | Method | Endpoint | Description | Auth Required | Request Body | Response |
   |---|---|---|---|---|---|

3. **Authentication & Authorisation** — Frappe session tokens, API keys, OAuth2 flows
4. **Request / Response Schemas** — JSON schema for key endpoints
5. **Error Codes** — table: HTTP Code | Error Type | Message | Resolution
6. **Rate Limiting** — limits per tier, headers returned
7. **Pagination** — strategy, default page size, max page size
8. **Frappe Hooks Used** — list relevant `hooks.py` entries
""",

        "09_integrations": f"""
## Stage 09 · Integrations

Define all integration requirements.{prior_section}

Produce:
1. **Integration Inventory** — table: System | Type | Direction | Protocol | Auth | Priority | Edition
2. **ERPNext Native Integrations** — which Frappe integrations apply out-of-the-box
3. **Custom Integration Specs** — for each custom integration: endpoint, payload schema, error handling, frequency
4. **Webhook Events** — table: Event Name | Trigger | Payload Fields | Consumers
5. **Third-Party Services** — table: Service | Purpose | Free Tier | Paid Tier | Data Shared
6. **Integration Testing Plan** — how each integration will be tested
7. **Fallback Behaviour** — what happens when each integration is unavailable
""",

        "10_security": f"""
## Stage 10 · Security

Produce a comprehensive security design for the innovation.{prior_section}

Produce:
1. **Threat Model** — table: Threat | Attack Vector | Likelihood | Impact | Control
2. **OWASP Top 10 Mitigations** — specific control per OWASP item
3. **Authentication & Session Management** — password policy, MFA, session timeout, token rotation
4. **Authorisation Model** — Frappe roles and permissions matrix
5. **Data Protection** — encryption at rest and in transit
6. **Input Validation & Sanitisation** — key validation rules, XSS/SQLi prevention
7. **Audit Logging** — what events are logged, format, retention period
8. **Vulnerability Management** — dependency scanning, patching cadence
9. **Compliance Mapping** — GDPR / Uganda DPA / ISO 27001
10. **Security Testing Plan** — SAST, DAST, manual review checkpoints
""",

        "11_testing": f"""
## Stage 11 · Testing Strategy

Define the complete testing strategy for the innovation.{prior_section}

Produce:
1. **Testing Pyramid** — balance of unit / integration / E2E tests
2. **Unit Tests** — table: Module | Function/Method | Test Cases | Edge Cases
3. **Integration Tests** — table: Component A | Component B | Test Scenario | Expected Outcome
4. **API Tests** — table: Endpoint | Method | Input | Expected Status | Expected Body
5. **End-to-End (E2E) Tests** — key user journeys (Playwright or Cypress):

   | Journey | Steps | Pass Criteria |
   |---|---|---|

6. **Performance Tests** — load targets, tools (Locust / k6), scenarios
7. **UAT Plan** — user acceptance test scenarios, tester personas, sign-off criteria
8. **Test Data Strategy** — how test data is created, anonymised, and seeded
9. **CI/CD Test Gates** — which suites must pass before merge / deploy to staging / production
10. **Defect Management** — severity definitions, SLA for fix
""",

        "12_deployment": f"""
## Stage 12 · Deployment

Design the deployment architecture and CI/CD pipeline.{prior_section}

Produce:
1. **Environment Strategy** — table: Environment | Purpose | Branch | Auto-deploy? | Data
2. **Infrastructure Design** — for each environment: cloud provider, compute, database, storage, CDN
3. **Frappe Bench Setup** — bench commands, app installation sequence, site creation
4. **CI/CD Pipeline** — pipeline stages (GitHub Actions):

   | Stage | Trigger | Steps | Failure Action |
   |---|---|---|---|

5. **Docker / Container Strategy** — Dockerfile structure, docker-compose for local dev
6. **Zero-Downtime Deployment** — blue-green or rolling strategy
7. **Rollback Plan** — how to revert a bad deployment within 15 minutes
8. **Backup & Disaster Recovery** — backup frequency, RTO, RPO, restore procedure
9. **Monitoring & Alerting** — tools, key metrics, alert thresholds
""",

        "13_documentation": f"""
## Stage 13 · Documentation

Define the complete documentation plan for the innovation.{prior_section}

Produce:
1. **Documentation Inventory** — table: Document | Audience | Format | Owner | Review Cycle
2. **Technical Documentation** — outline: ADRs, Developer Setup Guide, API Reference, DB Schema
3. **User Documentation** — outline: User Manual, Quick Start Guide, FAQ (10 questions), Video topics
4. **Administrator Documentation** — outline: Installation Guide, Enterprise Deployment, Backup Runbook
5. **ProSEIT Governance Documentation** — Governance Submission Pack, Change Control Procedure
6. **Documentation Toolchain** — recommended tools, hosting
7. **Localisation Plan** — languages (include Luganda, Swahili), translation workflow
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
6. **Recommended Next Steps** — three concrete steps the ProSEIT team should take this week
7. **Sign-off Block** — placeholders for Prepared By / Approved By / Date
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
    kb_section = _build_kb_section(kb_context)
    if kb_section:
        prompt = prompt + kb_section
    return prompt


# ── Pipeline runner ─────────────────────────────────────────────────────────────────────

def run_pipeline(
    idea: str,
    api_key: str,
    stages: list[str] | None = None,
    progress_cb: Callable[[str, float], None] | None = None,
    kb_context: dict | None = None,
) -> dict[str, str]:
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
