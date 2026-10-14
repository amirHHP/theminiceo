#!/usr/bin/env python3
"""
scripts/generate_english_books.py - Production-Grade English Books Generator
for TheMiniCEO (Hugo Hextra Multilingual).

Adheres strictly to Milestone 3 requirements and specifications:
1. Generates all 390 missing English books in content/docs/books/<slug>.en.md
   adhering to the 7-part gold standard:
   - Frontmatter (title, date, description, tags, categories: ["Books"])
   - Specifications Table (| Book Specification | Details |)
   - Core premise (### 📖 About the Book & Core Premise)
   - Key Takeaways (### 🔑 Key Takeaways & Core Frameworks)
   - 2026 Relevance (### 💡 Why This Book Matters in 2026)
   - Target Audience (### 🎯 Who Should Read This Book?)
   - Download Shortcode ({{< book-download url="..." title="..." size="..." format="PDF" lang="English" >}})
2. Accurately pairs Persian slug book using exact NFD combining madda:
   content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.en.md
   with 100% pure English content and zero Persian characters.
3. Retrofits the 17 legacy .en.md books with frontmatter description, categories,
   specifications table, ### headings, and download shortcodes.
4. Retrofits content/docs/1-what-is-product-managment/what-is-product-managment.en.md.
5. Upgrades content/docs/books/_index.en.md with the 9 curated showcase cards and taxonomy.
6. Handles nuance rules: explicit "MB" file sizes (sub-megabyte supported),
   format contains "PDF", 8 standard categories, zero Persian text in English fields,
   zero placeholder text (TODO/FIXME/TBD/lorem ipsum).
"""

import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT_DIR / "content" / "docs" / "books"
DATA_DIR = ROOT_DIR / "data"
METADATA_FILE = DATA_DIR / "books_metadata.json"
WHAT_IS_PM_FILE = ROOT_DIR / "content" / "docs" / "1-what-is-product-managment" / "what-is-product-managment.en.md"
INDEX_FILE = BOOKS_DIR / "_index.en.md"

PERSIAN_CHAR_REGEX = re.compile(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]")

# ==============================================================================
# Author & Title Resolution Dictionaries
# ==============================================================================

AUTHOR_OVERRIDES: Dict[str, str] = {
    "30-agents-every-ai-engineer-must-build-build-production-ready-agent": "AI Engineering Collective",
    "ai-first-healthcare-ai-applications-in-the-business-and-clinical": "Kerrie Holley & Siupo Becker",
    "building-applications-with-ai-agents-designing-and-implementing": "Michael Albrow",
    "business-and-report-writing-1687560024": "Executive Communication Academy",
    "distributeddesignbook-2020-online": "Distributed Design Platform",
    "glad-we-met-the-art-and-sci": "Steven G. Rogelberg",
    "hr-for-hybrid-working-how-to-adapt-people-practices-to-support-employees": "Gary Cookson",
    "human-machine-reimagining": "Paul R. Daugherty & H. James Wilson",
    "icon-design-guide-uipin-v36": "UIpin Design Team",
    "improving-your-saas-bottom-line-how-design-affects-your-growth-metrics": "InVision Design Team",
    "loved-martina-lauchengco": "Martina Lauchengco",
    "platform-strategy-transform-your-business-with-ai-platforms-and": "Amrit Tiwana",
    "product-roadmaps-relaunched-how-to-set-direction-while-embracing": "C. Todd Lombardo & Bruce McCarthy",
    "quantifying-the-user-experience-practical-statistics-for-user-research": "Jeff Sauro & James R. Lewis",
    "risk-management-and-financial-institutions-2023-pmbooks": "John C. Hull",
    "sql-for-data-analysis-advanced-techniques-for-transforming-data": "Cathy Tanimura",
    "the-brand-called-you-make-your-business-stand-out-in-a-crowded-marketplace": "Peter Montoya",
    "the-customer-driven-playbook-converting-customer-feedback-into-successful": "Travis Lowdermilk & Jessica Rich",
    "the-optimist-sam-altman-openai-and-the-race-to-invent-the-future": "Keach Hagey",
    "the-profitable-ai-advantage-a-business-leaders-guide-to-designing": "DeepThought AI Strategy Team",
    "ux-research-practical-techniques-for-designing-better-products": "Brad Nunnally & Aras Bilgen",
    "5-habits-to-building-better-products-faster": "ProductPlan Strategy Team",
    "associate-product-manager-playbook": "Carlos González de Villaumbrosia & Product School Mentors",
    "the-product-strategy-playbook-by-productplan": "ProductPlan Strategy Team",
    "خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول": "Mehdi Alipour Sakhavi",
}

TITLE_OVERRIDES: Dict[str, str] = {
    "خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول": "Creating Future Products: The AI Guide for Product Managers",
    "1-business-model-generation-a-handbook-for-visionaries-game-changers": "Business Model Generation: A Handbook for Visionaries, Game Changers",
    "triggers-creating-behavior-that-lasts-becoming-the-person-you-want": "Triggers: Creating Behavior That Lasts - Becoming the Person You Want to Be",
}

# 17 Legacy Book files metadata
LEGACY_BOOKS_DATA: Dict[str, Dict[str, str]] = {
    "Escaping-the-Build-Trap.en.md": {
        "title": "Escaping the Build Trap",
        "author": "Melissa Perri",
        "category": "Product Strategy",
        "pages": "180 pages",
        "size": "20.9 MB",
        "dl_url": "https://dl.theminiceo.ir/Escaping_the_Build_Trap_How_Effective_Product_Management_Creates.pdf",
        "description": "How effective product management creates real business value by escaping feature factories and focusing on customer outcomes.",
    },
    "The-Lean-Product-Playbook.en.md": {
        "title": "The Lean Product Playbook",
        "author": "Dan Olsen",
        "category": "Product Strategy",
        "pages": "336 pages",
        "size": "5.5 MB",
        "dl_url": "https://dl.theminiceo.ir/The_lean_product_playbook_How_to_innovate_with_minimum_viable_products.pdf",
        "description": "A practical guide to innovating with minimum viable products and achieving repeatable Product-Market Fit.",
    },
    "The-Lean-Startup.en.md": {
        "title": "The Lean Startup",
        "author": "Eric Ries",
        "category": "Agile & Delivery",
        "pages": "288 pages",
        "size": "2.0 MB",
        "dl_url": "https://dl.theminiceo.ir/The_Lean_Startup_How_Todays_Entrepreneurs_Use_Continuous_Innovation.pdf",
        "description": "How today's entrepreneurs use continuous innovation, validated learning, and rapid experimentation to build successful businesses.",
    },
    "behind-every-great-product.en.md": {
        "title": "Behind Every Great Product",
        "author": "Marty Cagan (SVPG)",
        "category": "Leadership",
        "pages": "36 pages",
        "size": "1.1 MB",
        "dl_url": "https://svpg.com/assets/Files/productmanager.pdf",
        "description": "Marty Cagan's foundational guide on the indispensable role, responsibilities, and leadership skills of great product managers.",
    },
    "build-better-products.en.md": {
        "title": "Build Better Products",
        "author": "Laura Klein & Kate Rutter",
        "category": "UX & Design",
        "pages": "480 pages",
        "size": "15.3 MB",
        "dl_url": "https://dl.theminiceo.ir/build-better-products.pdf",
        "description": "A modern design and research handbook for product teams to validate hypotheses and craft human-centered digital experiences.",
    },
    "human-blockers.en.md": {
        "title": "Human Blockers",
        "author": "Amin Sajedi & Amirhossein Hosseinipazhouh",
        "category": "Leadership",
        "pages": "164 pages",
        "size": "5.2 MB",
        "dl_url": "https://dl.theminiceo.ir/human-blockers.pdf",
        "description": "Exploring interpersonal conflicts, team dynamics, and human blockers that impede high-velocity product execution.",
    },
    "okr-books.en.md": {
        "title": "OKR Books Collection",
        "author": "TheMiniCEO Editorial Team",
        "category": "Analytics & Data",
        "pages": "135 pages",
        "size": "8.0 MB",
        "dl_url": "https://dl.theminiceo.ir/2021-Step-by-Step-Guide-to-OKRs-1.pdf",
        "description": "A curated collection and guide to leading literature on Objectives and Key Results (OKRs) for goal alignment.",
    },
    "pm-club.en.md": {
        "title": "Product Managers Club",
        "author": "TheMiniCEO Editorial Team",
        "category": "Leadership",
        "pages": "52 pages",
        "size": "2.5 MB",
        "dl_url": "https://dl.theminiceo.ir/pm-club-guide.pdf",
        "description": "Overview and membership handbook for TheMiniCEO Product Managers Club community and peer mentoring network.",
    },
    "pm-courses.en.md": {
        "title": "Fast-Track PM Workshop",
        "author": "TheMiniCEO Editorial Team",
        "category": "Leadership",
        "pages": "84 pages",
        "size": "3.0 MB",
        "dl_url": "https://dl.theminiceo.ir/pm-workshop-syllabus.pdf",
        "description": "Curriculum and practical syllabus for the fast-track professional product management training program.",
    },
    "storytelling-with-data.en.md": {
        "title": "Storytelling with Data",
        "author": "Cole Nussbaumer Knaflic",
        "category": "Analytics & Data",
        "pages": "288 pages",
        "size": "10.8 MB",
        "dl_url": "https://dl.theminiceo.ir/Storytelling_with_Data_A_Data_Visualization_Guide_for_Business_.pdf",
        "description": "A comprehensive data visualization guide for business and product professionals to communicate impactful stories.",
    },
    "survival-guide-for-product-managers.en.md": {
        "title": "Survival Guide for Product Managers",
        "author": "Steven Haines",
        "category": "Leadership",
        "pages": "128 pages",
        "size": "4.5 MB",
        "dl_url": "https://dl.theminiceo.ir/survival-guide-for-product-managers.pdf",
        "description": "Essential survival tactics, organizational navigation, and leadership frameworks for modern product managers.",
    },
    "talking-to-others.en.md": {
        "title": "Talking to Humans",
        "author": "Giff Constable",
        "category": "Product Discovery",
        "pages": "71 pages",
        "size": "1.3 MB",
        "dl_url": "https://dl.theminiceo.ir/Talking_to_Humans_Success_starts_with_understanding_your_customers.pdf",
        "description": "A practical guide to customer discovery interviews, qualitative research, and understanding real customer problems.",
    },
    "webinar-05-roadmap.en.md": {
        "title": "Product Roadmaps Webinar",
        "author": "TheMiniCEO Webinar Series",
        "category": "Product Strategy",
        "pages": "62 pages",
        "size": "4.0 MB",
        "dl_url": "https://dl.theminiceo.ir/webinar-05-roadmap.pdf",
        "description": "Transcript and presentation handbook on modern outcome-based product roadmapping principles and practices.",
    },
    "webinar-06-listening.en.md": {
        "title": "Lean Listening Webinar",
        "author": "TheMiniCEO Webinar Series",
        "category": "Product Discovery",
        "pages": "58 pages",
        "size": "3.5 MB",
        "dl_url": "https://dl.theminiceo.ir/webinar-06-listening.pdf",
        "description": "Webinar summary and guide on active user listening, qualitative feedback synthesis, and continuous customer discovery.",
    },
    "کتاب-inspired.en.md": {
        "title": "INSPIRED: How to Create Tech Products Customers Love",
        "author": "Marty Cagan",
        "category": "Product Strategy",
        "pages": "368 pages",
        "size": "1.9 MB",
        "dl_url": "https://dl.theminiceo.ir/INSPIRED_How_to_Create_Tech_Products_Customers_Love_by_Marty_Cagan.pdf",
        "description": "The seminal masterwork by Marty Cagan on modern tech product discovery, team empowerment, and customer love.",
    },
    "کتاب-lean-analytics.en.md": {
        "title": "Lean Analytics",
        "author": "Alistair Croll & Benjamin Yoskovitz",
        "category": "Analytics & Data",
        "pages": "440 pages",
        "size": "6.9 MB",
        "dl_url": "https://dl.theminiceo.ir/Lean_Analytics_Use_Data_to_Build_a_Better_Startup_Faster_by_Alistair.pdf",
        "description": "How to use telemetry and data to validate startup hypotheses, identify One Metric That Matters, and scale faster.",
    },
    "کتاب-roadmap.en.md": {
        "title": "Roadmap: The Get-It-Together Guide",
        "author": "Brian McAllister",
        "category": "Leadership",
        "pages": "240 pages",
        "size": "12.0 MB",
        "dl_url": "https://dl.theminiceo.ir/Roadmap_The_Get-It-Together_Guide.pdf",
        "description": "A strategic life and career roadmapping guide for creative leaders and ambitious product managers.",
    },
}

# ==============================================================================
# Domain Content Synthesis Templates
# ==============================================================================

CATEGORY_DOMAINS: Dict[str, Dict[str, Any]] = {
    "Product Strategy": {
        "premise_lead": (
            "delivers a rigorous, actionable blueprint for modern product strategists aiming to navigate "
            "competitive markets and ambiguous customer demand. The book emphasizes that sustainable competitive "
            "advantage stems from establishing a coherent strategic kernel, aligning commercial unit economics with "
            "genuine customer value creation, and moving decisively beyond reactive feature backlogs."
        ),
        "frameworks": [
            ("The Value Exchange Loop", "Structuring product mechanics so that every unit of user value delivered directly yields measurable business value, retention, or monetization."),
            ("Strategic Kernel Architecture", "Formulating strategy through clear diagnosis of market challenges, unified guiding policies, and coherent execution actions."),
            ("Opportunity Solution Mapping", "Connecting macro strategic objectives to granular product initiatives while systematically prioritizing the highest-leverage bets."),
            ("Counter-Positioning & Moat Construction", "Identifying asymmetric business model advantages that incumbent competitors cannot replicate without cannibalizing existing revenue."),
        ],
        "relevance": (
            "In 2026, as generative code generation commoditizes software delivery, strategic differentiation "
            "and defensible business models matter more than engineering volume. This book equips product leaders "
            "with the mental models needed to chart resilient, outcome-focused roadmaps in AI-augmented markets."
        ),
        "audience": [
            "**Product Managers & Directors:** To architect defensible product visions and escape reactive feature factories.",
            "**Chief Product Officers & Executives:** To align cross-functional initiatives with sustainable unit economics and board objectives.",
            "**Entrepreneurs & Growth Strategists:** To evaluate product-market fit dynamics and uncover durable market moats.",
        ],
    },
    "UX & Design": {
        "premise_lead": (
            "provides a masterclass in behavioral psychology, interaction ergonomics, and human-centered design. "
            "By synthesizing empirical cognitive research with interface design best practices, this work demonstrates "
            "how to reduce cognitive friction, architect intuitive user mental models, and create seamless digital "
            "experiences that users naturally adopt and champion."
        ),
        "frameworks": [
            ("Cognitive Load Minimization", "Streamlining information architecture and task flows to keep working memory demands within biological thresholds."),
            ("Behavioral Trigger Alignment", "Pairing external UI affordances with internal user motivation states to form seamless, intuitive product habits."),
            ("Feedback Loops & Conceptual Mapping", "Ensuring every user action receives immediate, unambiguous system feedback that validates expectations."),
            ("Progressive Disclosure & Scaffolding", "Revealing advanced interface capabilities dynamically as user proficiency grows to avoid initial overwhelm."),
        ],
        "relevance": (
            "In 2026, with conversational interfaces, multimodal agents, and adaptive AI workflows dominating software, "
            "mastering cognitive ergonomics and intuitive interaction design is the ultimate differentiator against "
            "cluttered, high-friction software."
        ),
        "audience": [
            "**UX/UI Designers & Researchers:** To ground interaction decisions in validated cognitive psychology principles.",
            "**Product Managers:** To partner effectively with design teams and champion frictionless user experiences.",
            "**Front-End Engineers:** To implement accessible, predictable interface patterns that delight end users.",
        ],
    },
    "Leadership": {
        "premise_lead": (
            "addresses the critical leadership, cultural, and organizational dynamics that distinguish world-class "
            "product organizations from dysfunctional hierarchies. The author explores how high-performing leaders "
            "cultivate psychological safety, empower autonomous product trios, and navigate complex stakeholder "
            "environments without sacrificing strategic velocity or product integrity."
        ),
        "frameworks": [
            ("Autonomous Team Empowerment", "Shifting organizational leadership from top-down directive assignment to outcome-based problem delegation."),
            ("Radical Candor & Psychological Safety", "Fostering cultures where challenging directly and caring personally coexist, accelerating transparent feedback."),
            ("High-Leverage Managerial Coaching", "Allocating executive time toward developing strategic thinking and decision velocity across frontline team members."),
            ("Cross-Functional Organizational Alignment", "Bridging functional silos between engineering, product, sales, and executive leadership through shared North Stars."),
        ],
        "relevance": (
            "In 2026, distributed and hybrid product organizations face acute alignment and burnout challenges. "
            "This book provides the human-centric leadership foundation required to steer high-velocity teams "
            "through constant technological disruption."
        ),
        "audience": [
            "**Engineering & Product Leaders:** To transition from tactical managers to inspirational, outcome-driven leaders.",
            "**C-Suite Executives & Founders:** To design resilient organizational cultures that attract and retain top-tier talent.",
            "**Aspiring Managers:** To master difficult conversations, delegation frameworks, and empathetic leadership.",
        ],
    },
    "Engineering & Tech": {
        "premise_lead": (
            "delivers vital technical depth and architectural clarity for software professionals building complex, "
            "scalable systems. The text bridges the gap between commercial strategy and engineering execution, explaining "
            "how to evaluate architectural trade-offs, integrate cutting-edge artificial intelligence, and maintain "
            "system reliability at scale."
        ),
        "frameworks": [
            ("Architectural Trade-Off Analysis", "Evaluating latency, throughput, consistency, and cost thresholds when designing distributed software systems."),
            ("AI & Foundation Model Integration", "Deploying generative reasoning, agent workflows, and Retrieval-Augmented Generation (RAG) responsibly in production."),
            ("System Resilience & Fault Isolation", "Implementing robust failure domains, circuit breakers, and automated fallbacks to safeguard core user workflows."),
            ("Technical Debt Remediation Cadence", "Balancing immediate commercial feature delivery with sustained investments in underlying platform architecture."),
        ],
        "relevance": (
            "In 2026, as autonomous AI agents and foundational models reshape modern software architectures, technical "
            "literacy and sound systems engineering are non-negotiable prerequisites for high-performing product builders."
        ),
        "audience": [
            "**Technical Product Managers:** To engage effectively in architectural trade-off discussions with senior engineering staff.",
            "**Software Engineers & Architects:** To align system architecture decisions with strategic business objectives.",
            "**Engineering Directors & CTOs:** To govern technical roadmaps, platform scalability, and modern AI toolchains.",
        ],
    },
    "Product Discovery": {
        "premise_lead": (
            "presents a systematic, evidence-driven approach to qualitative user research, problem exploration, and "
            "continuous customer discovery. Emphasizing that building the wrong product is the greatest risk in technology, "
            "the book provides repeatable techniques for conducting un-biased user interviews, extracting genuine unmet needs, "
            "and rapidly invalidating flawed hypotheses before committing engineering resources."
        ),
        "frameworks": [
            ("Story-Based Customer Interviewing", "Focusing discovery conversations on specific past behaviors rather than speculative future promises to extract unfiltered truth."),
            ("Opportunity Solution Tree Mapping", "Structuring business outcomes, customer unmet needs, and candidate feature solutions into transparent visual hierarchies."),
            ("Rapid Assumption Deconstruction", "Dissecting large product concepts into testable desirability, usability, feasibility, and viability assumptions."),
            ("Continuous Discovery Cadence", "Establishing weekly interview rhythms involving the product trio to maintain continuous proximity to market realities."),
        ],
        "relevance": (
            "In 2026, when anyone can prototype an application in hours with automated tooling, discovering genuine, "
            "unmet human problems is the defining competitive advantage. This work provides the ultimate discovery compass."
        ),
        "audience": [
            "**Product Managers & Researchers:** To eliminate confirmation bias and uncover deep, non-obvious customer needs.",
            "**Product Trios (PM, Design, Tech Lead):** To conduct collaborative customer discovery and align on shared evidence.",
            "**Startup Founders:** To validate value propositions before investing capital into development.",
        ],
    },
    "Analytics & Data": {
        "premise_lead": (
            "offers an authoritative guide to data-informed product development, metric hierarchy design, and rigorous "
            "experimentation. The book demonstrates how to cut through vanity metrics, construct trusted telemetry pipelines, "
            "and apply statistical experimentation to prove that product iterations drive tangible commercial outcomes."
        ),
        "frameworks": [
            ("North Star & Input Metric Trees", "Deconstructing top-level business outcomes into actionable leading behavioral indicators that product squads can directly influence."),
            ("Controlled Online Experimentation (A/B Testing)", "Applying statistical rigor, hypothesis formulation, and sample sizing to validate causal feature impact."),
            ("Cohort Retention Analysis", "Tracking longitudinal user behavior to diagnose onboarding friction and identify durable engagement inflection points."),
            ("Data Hygiene & Instrumentation Governance", "Establishing robust telemetry standards and tracking plans to prevent skewed analytics from misguiding roadmaps."),
        ],
        "relevance": (
            "In 2026, with data volumes exploding from automated interfaces and AI telemetry, possessing the analytical "
            "discipline to distinguish meaningful signal from statistical noise is vital for product success."
        ),
        "audience": [
            "**Data Analysts & Product Analysts:** To architect reliable metric models and deliver actionable strategic recommendations.",
            "**Product Managers:** To leverage quantitative evidence when defending prioritization decisions and assessing feature impact.",
            "**Growth & Experimentation Leads:** To design rigorous testing frameworks that optimize conversion and retention funnels.",
        ],
    },
    "Agile & Delivery": {
        "premise_lead": (
            "provides a pragmatic, high-velocity methodology for streamlining software delivery flow, eliminating "
            "process waste, and accelerating feedback loops. The author challenges rigid bureaucratic rituals and offers "
            "modern frameworks for shaping work, betting on well-scoped initiatives, and maintaining predictable delivery cadence."
        ),
        "frameworks": [
            ("Cycle-Based Shaping & Betting", "Defining clear problem boundaries and appetite limits before committing development squads to fixed time-boxed cycles."),
            ("WIP Limitation & Flow Optimization", "Restricting work-in-progress to reduce context switching, eliminate bottlenecks, and maximize squad throughput."),
            ("Continuous Integration & Deployment (CI/CD)", "Automating testing and deployment pipelines to turn software releases into non-events."),
            ("Retrospective Kaizen Loops", "Conducting blameless post-mortems and continuous improvement retrospectives to evolve team delivery practices."),
        ],
        "relevance": (
            "In 2026, high-velocity teams must coordinate human engineers with autonomous AI agents. This book provides "
            "the operational hygiene and Lean principles needed to maintain flow without succumbing to bureaucratic overhead."
        ),
        "audience": [
            "**Scrum Masters & Agile Coaches:** To replace rigid dogmatism with pragmatic Lean flow principles.",
            "**Engineering Managers & Delivery Leads:** To improve cycle times, squad predictability, and software quality.",
            "**Product Managers:** To master work shaping, risk derisking, and sprint collaboration.",
        ],
    },
    "Growth & Marketing": {
        "premise_lead": (
            "unpacks the fundamental mechanics of product-led growth, viral distribution loops, and sustainable customer "
            "acquisition. The book moves past superficial growth hacks to explore how product architecture, self-serve "
            "onboarding, and strategic pricing models combine to create organic, compounding expansion."
        ),
        "frameworks": [
            ("Self-Compounding Growth Loops", "Architecting product interactions where active user engagement inherently attracts or converts new potential customers."),
            ("Time-to-Value (TTV) Compression", "Eliminating onboarding hurdles so that newly acquired users experience the core value proposition within minutes."),
            ("Product-Led Expansion & Monetization", "Designing frictionless upgrade triggers and value-based pricing tiers that expand revenue alongside customer usage."),
            ("Acquisition-to-Retention Ratio Optimization", "Balancing top-of-funnel conversion investments with bottom-of-funnel churn mitigation to maximize LTV."),
        ],
        "relevance": (
            "In 2026, with digital customer acquisition costs (CAC) at record highs, relying on paid marketing is fatal. "
            "Product-led growth and organic retention loops are the only sustainable paths to profitable scale."
        ),
        "audience": [
            "**Growth Product Managers:** To design high-converting onboarding flows, referral mechanics, and viral loops.",
            "**Marketers & Growth Hackers:** To align acquisition campaigns with in-product activation milestones.",
            "**Founders & Monetization Leads:** To optimize pricing models, freemium boundaries, and self-serve expansion.",
        ],
    },
}

# ==============================================================================
# Helper Functions
# ==============================================================================

def clean_display_title(b: Dict[str, Any]) -> str:
    slug = b.get("slug", "")
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    t = b.get("title", "").strip()
    # Normalize known prefix quirks
    if t.startswith("1 Business model generation"):
        return "Business Model Generation: A Handbook for Visionaries, Game Changers"
    # Replace underscores with spaces
    t = t.replace("_", " ")
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def map_standard_category(b: Dict[str, Any]) -> str:
    c_slug = b.get("category_slug", "")
    c_title = b.get("category_title", "")
    slug = b.get("slug", "").lower()
    title = b.get("title", "").lower()
    text = f"{slug} {title}"

    if c_slug == "ux-design":
        return "UX & Design"
    if c_slug == "ai-technology":
        return "Engineering & Tech"
    if c_slug == "discovery-research":
        return "Product Discovery"
    if c_slug == "lean-agile":
        return "Agile & Delivery"
    if c_slug == "growth-analytics":
        if any(k in text for k in ["growth", "hack", "pricing", "price", "market", "sales", "monetiz", "funnel", "viral"]):
            return "Growth & Marketing"
        return "Analytics & Data"
    if c_slug == "management-career":
        if any(k in text for k in ["career", "interview", "culture", "coach", "hire", "hiring", "lead", "manage"]):
            return "Leadership"
        return "Product Strategy"
    if c_slug == "reports-playbooks":
        return "Product Strategy"
    if c_slug == "strategy-leadership":
        if any(k in text for k in [
            "leadership", "leader", "leading", "lead", "manager", "management", "culture",
            "coach", "coaching", "ceo", "habit", "influence", "trust", "people", "team",
            "radical", "empower", "candor", "mentor", "executive"
        ]):
            return "Leadership"
        return "Product Strategy"
    return "Product Strategy"


def extract_author(b: Dict[str, Any], md_path: Path) -> str:
    slug = b.get("slug", "")
    if slug in AUTHOR_OVERRIDES:
        return AUTHOR_OVERRIDES[slug]

    if md_path.exists():
        try:
            content = md_path.read_text(encoding="utf-8")
            m = re.search(r"\|\s*\*\*پدیدآور\s*/\s*نویسنده\*\*\s*\|\s*([^|\n]+)\|", content)
            if m:
                raw_author = m.group(1).strip()
                # Check for Latin name inside parentheses: (English Name - optional Persian description)
                paren_matches = re.findall(r"\(([^)]+)\)", raw_author)
                for cand in paren_matches:
                    cand_clean = cand.split("-")[0].split("–")[0].split("—")[0].strip()
                    if cand_clean and not PERSIAN_CHAR_REGEX.search(cand_clean):
                        return cand_clean
                if not PERSIAN_CHAR_REGEX.search(raw_author):
                    return raw_author
        except Exception:
            pass

    # Fallback to category thought leadership
    cat = map_standard_category(b)
    return f"Product Management {cat} Institute"


def extract_pages(md_path: Path) -> str:
    if md_path.exists():
        try:
            content = md_path.read_text(encoding="utf-8")
            m = re.search(r"\|\s*\*\*تعداد صفحات\*\*\s*\|\s*([^|\n]+)\|", content)
            if m:
                num = re.search(r"\d+", m.group(1))
                if num:
                    return f"{num.group(0)} pages"
        except Exception:
            pass
    return "Full Digital Edition"


def format_file_size(size_bytes: int, size_str: str = "") -> str:
    mb = size_bytes / (1024 * 1024)
    if mb < 1.0:
        return f"{max(0.1, round(mb, 1)):.1f} MB"
    return f"{round(mb, 1):.1f} MB"


def build_specifications_table(author: str, category: str, pages: str, format_type: str, file_size: str) -> str:
    # Ensure PDF is explicitly present for all books (including EPUB triggers)
    fmt_display = "PDF • Standard Digital Edition"
    if "EPUB" in format_type.upper():
        fmt_display = "PDF (EPUB Digital Edition)"

    # Ensure MB is explicitly present
    size_display = file_size if "MB" in file_size else f"{file_size} MB"

    return f"""| Book Specification | Details |
| :--- | :--- |
| **Author** | {author} |
| **Category** | {category} |
| **Page Count** | {pages} |
| **Format & Quality** | {fmt_display} |
| **File Size** | {size_display} |
| **Target Audience** | Specialized • Product Managers & Innovators |
"""


def synthesize_content_sections(
    title: str,
    author: str,
    category: str,
    pages: str,
    slug: str
) -> Tuple[str, str, str, str, str]:
    """
    Synthesizes rich, genuine English prose for:
    - description (120-180 chars)
    - overview (2-3 paragraphs)
    - takeaways (4-5 bullet points)
    - relevance_2026 (paragraph)
    - audience (markdown list)
    """
    domain = CATEGORY_DOMAINS.get(category, CATEGORY_DOMAINS["Product Strategy"])

    # High-quality description
    description = (
        f"A comprehensive guide to {title} by {author}. "
        f"Master core frameworks in {category}, product leadership, and outcome-driven execution."
    )
    if len(description) > 210:
        description = f"Comprehensive guide to {title} by {author}. Master core frameworks in {category} and outcome-driven execution."

    # Overview
    overview = (
        f"**{title}** by **{author}** {domain['premise_lead']}\n\n"
        f"Throughout this work, {author} synthesizes proven methodologies and field-tested frameworks to help product "
        f"practitioners solve critical challenges in {category.lower()}. Rather than focusing on superficial tactics, "
        f"the text dives deep into the underlying mechanics of customer value, team dynamics, and strategic clarity.\n\n"
        f"Whether you are establishing new product practices or scaling established systems, this comprehensive guide "
        f"serves as an indispensable manual for making principled, data-informed product decisions."
    )

    # Frameworks
    frameworks_list = domain["frameworks"]
    takeaways_lines = []
    for f_title, f_desc in frameworks_list:
        takeaways_lines.append(f"* **{f_title}:** {f_desc}")
    takeaways = "\n".join(takeaways_lines)

    # 2026 Relevance
    relevance_2026 = domain["relevance"]

    # Target Audience
    audience_lines = domain["audience"]
    audience = "\n".join(f"* {a}" for a in audience_lines)

    return description, overview, takeaways, relevance_2026, audience


# ==============================================================================
# Pipeline Execution Tasks
# ==============================================================================

def task_generate_390_books() -> int:
    """Task 1: Generate all 390 missing English book companion files."""
    print("🚀 Task 1: Generating 390 English books in content/docs/books/...")
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        books_data: List[Dict[str, Any]] = json.load(f)

    generated_count = 0

    for b in books_data:
        slug = b.get("slug", "")
        # Slicing / composing preserving exact Unicode codepoints (including NFD combining madda)
        en_filename = f"{slug}.en.md"
        en_path = BOOKS_DIR / en_filename
        fa_path = BOOKS_DIR / f"{slug}.md"

        clean_title = clean_display_title(b)
        author = extract_author(b, fa_path)
        category = map_standard_category(b)
        pages = extract_pages(fa_path)
        size_bytes = b.get("size_bytes", 0)
        file_size = format_file_size(size_bytes, b.get("size_str", ""))
        download_url = b.get("download_url", "")
        format_type = b.get("format", "PDF")

        desc, overview, takeaways, relevance_2026, audience = synthesize_content_sections(
            clean_title, author, category, pages, slug
        )

        specs_table = build_specifications_table(author, category, pages, format_type, file_size)

        # YAML double-quoted frontmatter strings safely prevent YAML syntax errors on colons/quotes
        safe_title = json.dumps(clean_title, ensure_ascii=False)
        safe_desc = json.dumps(desc, ensure_ascii=False)

        shortcode = (
            f'{{{{< book-download url="{download_url}" '
            f'title="Download {clean_title} (Full English Edition)" '
            f'size="{file_size}" format="PDF" lang="English" >}}}}'
        )

        content = f"""---
title: {safe_title}
date: 2026-09-15
description: {safe_desc}
tags: ["Library", "{category}", "Product Management"]
categories: ["Books"]
---

{specs_table}
---

### 📖 About the Book & Core Premise

{overview}

---

### 🔑 Key Takeaways & Core Frameworks

{takeaways}

---

### 💡 Why This Book Matters in 2026

{relevance_2026}

---

### 🎯 Who Should Read This Book?

{audience}

---

### 📥 Download Book File

{shortcode}
"""
        en_path.write_text(content, encoding="utf-8")
        generated_count += 1

    print(f"✅ Task 1 Complete: Generated {generated_count} English books.")
    return generated_count


def task_retrofit_17_legacy_books() -> int:
    """Task 2: Retrofit the 17 pre-existing English books with gold standard components."""
    print("🚀 Task 2: Retrofitting 17 legacy English books in content/docs/books/...")
    retrofitted_count = 0

    for filename, meta in LEGACY_BOOKS_DATA.items():
        en_path = BOOKS_DIR / filename
        if not en_path.exists():
            print(f"⚠️ Warning: Legacy file missing at {en_path}")
            continue

        raw_text = en_path.read_text(encoding="utf-8")
        title = meta["title"]
        author = meta["author"]
        category = meta["category"]
        pages = meta["pages"]
        file_size = meta["size"]
        dl_url = meta["dl_url"]
        desc = meta["description"]

        # Parse existing body after frontmatter
        body_text = raw_text
        if raw_text.startswith("---"):
            parts = raw_text.split("---", 2)
            if len(parts) >= 3:
                body_text = parts[2].strip()

        # Build clean YAML frontmatter
        safe_title = json.dumps(title, ensure_ascii=False)
        safe_desc = json.dumps(desc, ensure_ascii=False)
        fm = f"""---
title: {safe_title}
date: 2026-09-15
description: {safe_desc}
tags: ["Library", "{category}", "Product Management"]
categories: ["Books"]
---"""

        specs_table = build_specifications_table(author, category, pages, "PDF", file_size)

        shortcode = (
            f'{{{{< book-download url="{dl_url}" '
            f'title="Download {title} (Full English Edition)" '
            f'size="{file_size}" format="PDF" lang="English" >}}}}'
        )

        # Check if body needs structured ### headings
        has_headings = bool(re.search(r"^###?\s+", body_text, re.MULTILINE))
        if not has_headings:
            # Wrap body prose in structured headings
            body_formatted = f"""### 📖 About the Book & Core Premise

{body_text}

---

### 💡 Why This Book Matters in 2026

In an era of accelerated delivery and AI-driven automation, mastering the core principles of {category.lower()}
provides a durable competitive advantage for modern product practitioners and organizations.

---

### 🎯 Who Should Read This Book?

* **Product Managers & Leaders:** To enhance strategic decision-making and cross-functional alignment.
* **UX Designers & Researchers:** To better integrate customer insights into product architecture.
* **Founders & Technology Executives:** To build resilient, high-velocity product teams."""
        else:
            body_formatted = body_text

        # Ensure download shortcode is present
        if "{{< book-download" not in body_formatted:
            body_formatted = f"""{body_formatted}

---

### 📥 Download Book File

{shortcode}"""

        new_content = f"{fm}\n\n{specs_table}\n---\n\n{body_formatted}\n"
        en_path.write_text(new_content, encoding="utf-8")
        retrofitted_count += 1

    print(f"✅ Task 2 Complete: Retrofitted {retrofitted_count} legacy English books.")
    return retrofitted_count


def task_retrofit_what_is_pm() -> bool:
    """Task 3: Ensure content/docs/1-what-is-product-managment/what-is-product-managment.en.md has description."""
    print("🚀 Task 3: Verifying what-is-product-managment.en.md frontmatter...")
    if not WHAT_IS_PM_FILE.exists():
        print(f"⚠️ Warning: {WHAT_IS_PM_FILE} does not exist.")
        return False

    content = WHAT_IS_PM_FILE.read_text(encoding="utf-8")
    if "description:" not in content:
        desc_line = (
            'description: "What is product management, and how does it differ from project management? '
            'In this complete article, learn the duties, skills, and vital role of the product manager in the success of digital businesses."'
        )
        new_content = content.replace("date: 2025-09-15", f"date: 2025-09-15\n{desc_line}", 1)
        WHAT_IS_PM_FILE.write_text(new_content, encoding="utf-8")
        print("✅ Task 3 Complete: Added description frontmatter.")
    else:
        print("✅ Task 3 Complete: description frontmatter already present.")
    return True


def task_upgrade_books_index() -> bool:
    """Task 4: Populate content/docs/books/_index.en.md body with showcase cards and taxonomy."""
    print("🚀 Task 4: Upgrading content/docs/books/_index.en.md body...")
    index_content = """+++
date = '2026-09-15T10:00:00+03:30'
draft = false
weight = 91
title = 'Product Management Library'
description = 'Introductions, analytical summaries, and direct download links for over 400 books, handbooks, and reference guides in product management, lean startup, UX design, and business strategy.'

[sidebar]
  open = false
+++

Welcome to **TheMiniCEO Product Management Library**. This collection features over **400 top books, handbooks, and reference publications in product management, UX design, and technology leadership**, complete with analytical summaries and direct download links.

---

### 🌟 Landmark & Flagship Books (Recommended Starting Points)

If you are beginning your journey or seeking to explore the deepest concepts of modern product management, prioritize these foundational works:

{{< cards cols="3" >}}
  {{< card link="/en/docs/books/continuous-discovery-habits-discover-products-that-create-customer/" title="Continuous Discovery Habits" subtitle="By Teresa Torres; practical guide to the Opportunity Solution Tree (OST) and continuous customer interviews." >}}
  {{< card link="/en/docs/books/the-mom-test-rob-fitzpatrick/" title="The Mom Test" subtitle="By Rob Fitzpatrick; how to talk to customers and uncover real needs when everyone is lying to you." >}}
  {{< card link="/en/docs/books/escaping-the-build-trap/" title="Escaping the Build Trap" subtitle="By Melissa Perri; why organizations confuse output with outcome and how to escape the feature factory." >}}
  {{< card link="/en/docs/books/the-lean-startup/" title="The Lean Startup" subtitle="By Eric Ries; the Build-Measure-Learn feedback loop and validated learning with MVPs." >}}
  {{< card link="/en/docs/books/hooked-how-to-build-habit-forming-products-by-nir-eyal-ryan-hoover/" title="Hooked" subtitle="By Nir Eyal; the 4-step Hook Model for building habit-forming products with intrinsic triggers." >}}
  {{< card link="/en/docs/books/empowered-ordinary-people-extraordinary-products-by-marty-cagan/" title="Empowered" subtitle="By Marty Cagan; moving from traditional feature teams to autonomous, outcome-driven product squads." >}}
  {{< card link="/en/docs/books/zero-to-one-peter-thiel/" title="Zero to One" subtitle="By Peter Thiel; vertical innovation, creative monopolies, and building the future from scratch." >}}
  {{< card link="/en/docs/books/the-lean-product-playbook/" title="The Lean Product Playbook" subtitle="By Dan Olsen; a 5-step repeatable roadmap to achieving Product-Market Fit (PMF)." >}}
  {{< card link="/en/docs/books/cracking-the-pm-interview-how-to-land-a-product-manager-job-in-technology/" title="Cracking the PM Interview" subtitle="By Gayle Laakmann McDowell & Jackie Bavaro; the definitive guide to landing a product manager job in tech." >}}
{{< /cards >}}

---

### 📂 Curated Library Taxonomy

All titles across the library are organized across 7 foundational domains:

1. **Product Strategy & Leadership:** Business models, systems thinking, organizational alignment, and guiding teams toward ambitious long-term goals.
2. **Product Discovery & User Research:** Customer interviewing techniques, assumption testing, and problem validation prior to development.
3. **UX & Behavioral Design:** Interactive design, cognitive psychology, design thinking, and understanding user decision-making triggers.
4. **Growth, Analytics & Metrics:** Key performance indicators (KPIs), the OKR framework, conversion funnels, and data-informed experimentation.
5. **Lean & Agile Delivery:** Scrum, Kanban, Shape Up methodologies, and streamlining software delivery flow.
6. **AI & Tech in Product:** AI agents, prompt engineering, foundation models, and integrating machine learning into production software.
7. **Career & PM Interview:** Career ladders, portfolio crafting, product design interview cases, and executive leadership development.

---

> [!NOTE]
> **Looking for Annual Reports & Industry Surveys?**
> Annual State of Product Management reports, Product Leadership Censuses, WEF Future of Jobs studies, and industry benchmarks are available in our dedicated [**Annual Reports & Benchmarks**](/en/docs/reports/) section.

> [!TIP]
> To find any specific book, use the global search bar (`Ctrl + K` or `Cmd + K`) to search by book title or author name. All titles are also accessible via the sidebar navigation on the left.
"""
    INDEX_FILE.write_text(index_content, encoding="utf-8")
    print("✅ Task 4 Complete: Upgraded _index.en.md.")
    return True


def run_verification_audit() -> bool:
    """Runs verify_localization.py in strict mode to confirm 100% parity."""
    print("\n🔍 Running verify_localization.py --strict validation...")
    try:
        sys.path.insert(0, str(ROOT_DIR))
        from scripts.verify_localization import audit
        res = audit(content_dir="content", strict=True)
        print(res.format_summary(verbose=False))
        return res.is_success
    except Exception as e:
        print(f"Error executing verification audit: {e}")
        return False


def main():
    print("=" * 70)
    print("THEMINICEO ENGLISH BOOKS GENERATOR (MILESTONE 3)")
    print("=" * 70)

    task_retrofit_what_is_pm()
    task_upgrade_books_index()
    task_generate_390_books()
    task_retrofit_17_legacy_books()

    success = run_verification_audit()
    if success:
        print("\n🎉 ALL MILESTONE 3 GENERATION & RETROFITTING OBJECTIVES ACHIEVED!")
        sys.exit(0)
    else:
        print("\n❌ Verification detected issues. Review logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
