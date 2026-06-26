"""
ProSEIT Innovation-to-Implementation Pipeline runner.

Executes the 19-stage pipeline as a sequence of Claude API calls.
Returns a dict keyed by stage name with the Claude-generated content.
"""
from __future__ import annotations
from typing import Callable
from pipeline.client import call_claude

STAGES = [
    "00_intake", "01_policy", "02_concept", "03_editions",
    "04_architecture", "05_user_stories", "06_ux_wireframes",
    "07_data_model", "08_api_design", "09_integrations", "10_security",
    "11_testing", "12_deployment", "13_documentation", "14_budget",
    "15_business_plan", "16_governance", "17_roadmap", "18_package",
]

STAGE_LABELS = {
    "00_intake":        "Stage 00 · Intake & Validation",
    "01_policy":        "Stage 01 · Policy & Compliance",
    "02_concept":       "Stage 02 · Concept Development",
    "03_editions":      "Stage 03 · Edition Planning",
    "04_architecture":  "Stage 04 · Technical Architecture",
    "05_user_stories":  "Stage 05 · User Stories",
    "06_ux_wireframes": "Stage 06 · UX & Wireframes",
    "07_data_model":    "Stage 07 · Data Model",
    "08_api_design":    "Stage 08 · API Design",
    "09_integrations":  "Stage 09 · Integrations",
    "10_security":      "Stage 10 · Security",
    "11_testing":       "Stage 11 · Testing Strategy",
    "12_deployment":    "Stage 12 · Deployment",
    "13_documentation": "Stage 13 · Documentation",
    "14_budget":        "Stage 14 · Budget & Cost",
    "15_business_plan": "Stage 15 · Business Plan",
    "16_governance":    "Stage 16 · Governance Routing",
    "17_roadmap":       "Stage 17 · Roadmap",
    "18_package":       "Stage 18 · Final Package",
}

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


def _prompt_for_stage(stage: str, idea: str, context: dict) -> str:
    prior = "\n\n".join(
        f"### {STAGE_LABELS.get(k, k)}\n{v}" for k, v in context.items() if v
    )
    prior_section = f"\n\n---\n## Prior Stage Outputs\n{prior}" if prior else ""

    prompts = {
        "00_intake": f"""## Stage 00 · Intake & Validation\n\nAnalyse the following innovation idea submitted to ProSEIT.\n\n**Innovation Idea:**\n{idea}\n\nProduce:\n1. **Innovation ID** — suggest a slug (lowercase, hyphens, e.g. `smart-cpd-tracker`)\n2. **Title** — concise product name (≤8 words)\n3. **Problem Statement** — what pain point does this solve?\n4. **Target Users** — primary and secondary personas\n5. **ProSEIT Strategic Fit** — how does this align with ProSEIT's mandate?\n6. **Feasibility Assessment** — technical, financial, operational (High / Medium / Low each)\n7. **Recommended Scope** — MVP scope in ≤5 bullet points\n8. **Next-Stage Flags** — which later stages need special attention?""",

        "01_policy": f"""## Stage 01 · Policy & Compliance\n\nBased on the innovation below, identify all relevant policy and compliance requirements.{prior_section}\n\nProduce:\n1. **Applicable Regulations** — data protection, professional licensing, sector-specific laws (Uganda / East Africa / Pan-Africa)\n2. **ProSEIT Governance Committees Required** — list from the five committees\n3. **IP & Patent Considerations**\n4. **Data Residency Requirements**\n5. **Compliance Checklist** — table: Item | Requirement | Status""",

        "02_concept": f"""## Stage 02 · Concept Development\n\nDevelop the full product concept.{prior_section}\n\nProduce:\n1. **Product Vision Statement** (one sentence)\n2. **Key Features** — by edition (CE/PE/E-C/E-O) and phase (MVP/FULL/PHASE-2)\n3. **Unique Value Proposition**\n4. **Competitive Landscape** — 3-5 comparable solutions, gap analysis\n5. **Success Metrics** — KPIs with targets\n6. **Assumptions & Risks** — table: Risk | Likelihood | Impact | Mitigation""",

        "03_editions": f"""## Stage 03 · Edition Planning\n\nDefine the edition and licensing model.{prior_section}\n\nProduce a feature comparison table:\n\n| Feature | CE | PE | E-C | E-O |\n|---|---|---|---|---|\n\nThen:\n1. **Licensing Model** per edition\n2. **Pricing Rationale** (exact figures in Stage 14)\n3. **Upgrade Path** between editions\n4. **Support Tiers** per edition""",

        "04_architecture": f"""## Stage 04 · Technical Architecture\n\nDesign the technical architecture.{prior_section}\n\nProduce:\n1. **Architecture Description** with components and interactions\n2. **Tech Stack** layer by layer\n3. **ERPNext/Frappe Modules** — doctypes and custom apps\n4. **Angular 18 Modules** — key modules and routing\n5. **Integration Points** — external systems\n6. **Scalability** — CE vs. Enterprise\n7. **Non-Functional Requirements**""",

        "05_user_stories": f"""## Stage 05 · User Stories\n\nWrite comprehensive user stories.{prior_section}\n\nFormat: > As a [persona], I want to [action] so that [benefit].\n\nGroup by: MVP Stories | FULL Stories | PHASE-2 Stories\n\nInclude acceptance criteria for each MVP story.""",

        "09_integrations": f"""## Stage 09 · Integrations\n\nDefine all integration requirements.{prior_section}\n\nProduce:\n1. **Integration Inventory** — table: System | Type | Direction | Protocol | Auth | Priority\n2. **ERPNext Native Integrations**\n3. **Custom Integration Specs**\n4. **Webhook Events**\n5. **API Rate Limits & SLAs**\n6. **Integration Testing Plan**""",

        "14_budget": f"""## Stage 14 · Budget & Cost Model\n\nProduce a comprehensive budget.{prior_section}\n\n1. **Development Cost Estimate** — table: Item | CE | PE | Enterprise | Notes\n2. **Infrastructure Cost** (monthly)\n3. **Licensing & Third-Party Costs**\n4. **Human Resources** — roles, person-months, cost range (USD)\n5. **Total Cost of Ownership** — Year 1, 2, 3\n6. **Break-Even Analysis**\n7. **Funding Recommendations**""",

        "15_business_plan": f"""## Stage 15 · Business Plan\n\nProduce an executive-ready business plan.{prior_section}\n\n1. **Executive Summary** (≤150 words)\n2. **Market Opportunity** — TAM/SAM/SOM\n3. **Revenue Model** — streams, pricing, projections (Year 1-3)\n4. **Go-to-Market Strategy**\n5. **Competitive Advantages**\n6. **Financial Projections** (table)\n7. **Key Risks & Mitigations**\n8. **Investment Ask** (if applicable)""",

        "16_governance": f"""## Stage 16 · Governance Routing\n\nProduce the full governance routing recommendation.{prior_section}\n\nFor each committee state: Triggered (Yes/No) | Reason | Required Actions | Priority\n\nCommittees:\n1. Professional Training and Certification Committee\n2. Legal, Arbitration and Communication Committee\n3. Professional Standards and Ethics Committee\n4. Investment Advisory Committee\n5. Innovations, Patents and Intellectual Property Committee\n\nEnd with a Governance Summary Table and recommended review sequence.""",

        "17_roadmap": f"""## Stage 17 · Roadmap\n\nProduce a phased delivery roadmap.{prior_section}\n\n1. **Milestone Timeline** — table: Milestone | Phase | Target Quarter | Deliverables | Owner Role\n2. **Sprint Zero** tasks\n3. **MVP Release Plan**\n4. **Post-MVP Phases** timelines\n5. **Dependencies & Critical Path**\n6. **Resource Plan** by phase""",

        "18_package": f"""## Stage 18 · Final Implementation Package\n\nProduce the complete implementation package.{prior_section}\n\n1. **Innovation Profile Card** — title, ID, vision, editions, primary committee\n2. **Executive Summary** (≤200 words)\n3. **Implementation Readiness Score** (1-5 per dimension)\n4. **Top 10 Action Items** — table: Action | Owner Role | Due | Priority\n5. **Document Index**\n6. **Recommended Next Steps** (three for this week)\n7. **Sign-off Block**""",
    }

    default_prompt = f"""## {STAGE_LABELS.get(stage, stage)}\n\nContinue the innovation pipeline.{prior_section}\n\n**Innovation Idea:**\n{idea}\n\nProduce a thorough, actionable output following ProSEIT standards."""
    return prompts.get(stage, default_prompt).strip()


def run_pipeline(
    idea: str,
    api_key: str,
    stages: list[str] | None = None,
    progress_cb: Callable[[str, float], None] | None = None,
) -> dict[str, str]:
    """Run selected pipeline stages and return results dict."""
    selected = stages or STAGES
    results: dict[str, str] = {}
    context: dict[str, str] = {}

    for i, stage in enumerate(selected):
        if progress_cb:
            progress_cb(STAGE_LABELS.get(stage, stage), i / len(selected))
        prompt = _prompt_for_stage(stage, idea, context)
        output = call_claude(prompt, system=SYSTEM_PROMPT, api_key=api_key)
        results[stage] = output
        context[stage] = output

    if progress_cb:
        progress_cb("Complete", 1.0)
    return results
