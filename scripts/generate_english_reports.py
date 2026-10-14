#!/usr/bin/env python3
"""
scripts/generate_english_reports.py - Generator for English Reports in TheMiniCEO
Generates all 17 English report companion files in content/docs/reports/*.en.md
with complete metadata, specifications table, structured research takeaways,
2026 relevance, audience analysis, and working book-download shortcodes.
"""

import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "content" / "docs" / "reports"

REPORTS_DATA = [
    {
        "filename": "the-2024-state-of-product-management-report.en.md",
        "old_file": "the-2024-state-of-product-management-report.md",
        "new_file": "the-2024-state-of-product-management-report.md",
        "title": "The 2024 State of Product Management Report",
        "category": "State of Product Management",
        "publisher": "Product Management Today / Mind the Product",
        "year": "2024",
        "date": "2026-09-16",
        "size": "3.8 MB",
        "dl_url": "https://dl.theminiceo.ir/The-2024-State-of-Product-Management-Report.pdf",
        "description": "Annual industry report analyzing key priorities, team topologies, tooling stacks, and AI adoption across thousands of global product teams in 2024.",
        "overview": (
            "The 2024 State of Product Management Report provides an extensive empirical examination of how modern "
            "product organizations operate amidst rapidly shifting technological and economic realities. Based on data "
            "gathered from thousands of practicing product managers, directors, and executives worldwide, this benchmark "
            "delivers vital insights into how teams prioritize initiatives, organize cross-functional topologies, and "
            "incorporate generative artificial intelligence into everyday workflows."
        ),
        "takeaways": [
            ("Strategic Prioritization & AI Integration", "Product teams are shifting from speculative experimentation toward practical AI integration, deploying foundation models to accelerate discovery, customer research synthesis, and requirement drafting."),
            ("Product Team Topologies", "Standardized ratios between product managers, software engineers, and product designers have stabilized, accompanied by tighter operational integration across discovery and delivery squads."),
            ("Modern Tooling Ecosystem", "Comprehensive mapping of platforms dominating roadmapping, user telemetry, and customer feedback management, highlighting a flight to consolidated tool suites."),
            ("Economic Discipline & Unit Economics", "A decisive transition from growth-at-all-costs toward sustainable unit economics, operational efficiency, and measurable customer lifetime value.")
        ],
        "relevance_2026": (
            "In 2026, as enterprise AI workflows transition from experimental novelty to standard infrastructure, "
            "this benchmark provides the crucial historical baseline for understanding how high-performing teams "
            "adapted their roadmapping cadences and team ratios during the initial generative wave."
        ),
        "audience": [
            "**Product Managers & CPOs:** To benchmark team structures, resource allocations, and roadmap methodologies against global standards.",
            "**UX Researchers & Designers:** To analyze cross-functional collaboration dynamics and design-engineering integration benchmarks.",
            "**Tech Founders & Executives:** To align corporate development and compensation structures with international software industry realities."
        ]
    },
    {
        "filename": "the-state-of-product-management-annual-report-2023.en.md",
        "old_file": "the-state-of-product-management-annual-report-2023.md",
        "new_file": "the-state-of-product-management-annual-report-2023.md",
        "title": "The State of Product Management Annual Report 2023",
        "category": "State of Product Management",
        "publisher": "Product School",
        "year": "2023",
        "date": "2026-09-16",
        "size": "12.2 MB",
        "dl_url": "https://dl.theminiceo.ir/The-State-of-Product-Management-Annual-Report-2023.pdf",
        "description": "Comprehensive survey detailing product manager compensation, feature prioritization frameworks, tooling ecosystems, and team dynamics in 2023.",
        "overview": (
            "The State of Product Management Annual Report 2023 captures a definitive pulse of the international product "
            "community following major macroeconomic shifts. Synthesizing responses from over 5,000 product professionals "
            "spanning startups, scale-ups, and global enterprises, the study investigates salary bands, decision-making "
            "frameworks, remote work models, and leadership expectations."
        ),
        "takeaways": [
            ("Global Compensation Benchmarks", "Detailed salary distributions, bonus structures, and equity compensation trends mapped across geographical regions and organizational seniority levels."),
            ("Feature Prioritization Frameworks", "Empirical data detailing the prevalence of RICE, MoSCoW, Kano, and Opportunity Scoring models used to resolve stakeholder conflicts."),
            ("Hybrid & Remote Work Dynamics", "Examining organizational adaptations to distributed collaboration, asynchronous communication protocols, and return-to-office policies."),
            ("Performance Measurement Criteria", "The primary key performance indicators (KPIs) and business impact metrics utilized by executive leadership to assess product department effectiveness.")
        ],
        "relevance_2026": (
            "Serves as an essential reference point for analyzing the structural maturation of product roles and "
            "compensation dynamics following the post-pandemic market correction, providing enduring guidance for "
            "career progression and team leveling."
        ),
        "audience": [
            "**Product Practitioners & Leads:** For salary negotiations, career ladder planning, and establishing rigorous prioritization cadences.",
            "**Talent & People Leaders:** To design competitive compensation bands and career ladders tailored to high-performing product professionals.",
            "**Engineering & Design Partners:** To better understand product management decision frameworks and streamline cross-functional alignment."
        ]
    },
    {
        "filename": "the-2022-state-of-product-management-report-by-productplan.md".replace(".md", ".en.md"),
        "old_file": "the-2022-state-of-product-management-report-by-productplan.md",
        "new_file": "the-2022-state-of-product-management-report-by-productplan.md",
        "title": "The 2022 State of Product Management Report by ProductPlan",
        "category": "State of Product Management",
        "publisher": "ProductPlan",
        "year": "2022",
        "date": "2026-09-16",
        "size": "5.5 MB",
        "dl_url": "https://dl.theminiceo.ir/The-2022-State-of-Product-Management-Report-by-ProductPlan.pdf",
        "description": "ProductPlan industry benchmark examining remote product management, roadmapping strategies, and organizational alignment during 2022.",
        "overview": (
            "The 2022 State of Product Management Report by ProductPlan investigates the rapid transformation of roadmap "
            "planning, team synchronization, and executive communication during the height of global remote work adoption. "
            "The report highlights how modern product managers pivoted away from rigid annual plans toward agile, outcome-focused "
            "roadmaps built on real-time customer data."
        ),
        "takeaways": [
            ("Roadmapping Evolution", "The transition from timeline-heavy Gantt charts toward outcome-based, flexible theme roadmaps tailored for distributed team execution."),
            ("Distributed Team Synchronization", "Tactical solutions for eliminating Zoom fatigue, improving asynchronous alignment, and synchronizing engineering sprints with high-level corporate objectives."),
            ("The Executive Expectation Gap", "Quantifying the frequent disconnect between high-level executive strategic goals and daily product delivery capabilities."),
            ("Data-Driven Decision Making", "Increased reliance on quantitative product telemetry to justify feature investments and defend prioritization trade-offs.")
        ],
        "relevance_2026": (
            "Foundational roadmap principles documented in this study remain standard best practices today, "
            "illustrating how outcome-driven product management outlasts temporary project-management fads."
        ),
        "audience": [
            "**Product Leaders & Roadmappers:** To implement modern, outcome-focused roadmapping templates that maintain executive alignment.",
            "**Scrum Masters & Agile Coaches:** To eliminate friction between sprint-level backlog tracking and multi-quarter strategic product roadmaps.",
            "**Startup Executives:** To establish transparent product communication loops with boards, investors, and cross-functional teams."
        ]
    },
    {
        "filename": "wef-future-of-jobs-report-2025.en.md",
        "old_file": "wef-future-of-jobs-report-2025.md",
        "new_file": "wef-future-of-jobs-report-2025.md",
        "title": "The Future of Jobs Report 2025 – World Economic Forum (WEF)",
        "category": "Future of Work & Skills",
        "publisher": "World Economic Forum (WEF)",
        "year": "2025",
        "date": "2026-09-16",
        "size": "14.0 MB",
        "dl_url": "https://dl.theminiceo.ir/WEF_Future_of_Jobs_Report_2025.pdf",
        "description": "World Economic Forum landmark report exploring labor market transformations, AI automation, and essential competencies for leaders through 2025 and beyond.",
        "overview": (
            "The Future of Jobs Report 2025 by the World Economic Forum is the definitive global benchmark on workforce "
            "transformation, labor economics, and technical skill demand. Gathering executive perspectives from hundreds of "
            "the world's largest employers across dozens of economic sectors, the report maps the trajectory of automated work, "
            "human-AI collaboration, and emergent organizational models."
        ),
        "takeaways": [
            ("Core Cognitive & Technical Competencies", "The top 10 skills essential for technology professionals, highlighting analytical thinking, resilience, flexibility, and technological literacy."),
            ("Automation & Structural Displacement", "A balanced forecast of job roles created versus displaced by artificial intelligence, cloud infrastructure, and robotics across digital sectors."),
            ("Enterprise Upskilling & Reskilling", "Corporate blueprints for continuous talent upskilling initiatives engineered to bridge technical talent deficits."),
            ("Global Labor Market Dynamics", "Macroeconomic impacts of workforce digitization, demographic shifts, and geographically distributed labor pools.")
        ],
        "relevance_2026": (
            "Essential reading for product and engineering leaders structuring modern technical organizations that "
            "pair human ingenuity with autonomous, agentic artificial intelligence."
        ),
        "audience": [
            "**Executive Leaders & Strategists:** To anticipate macro workforce trends and structure resilient technology organizations.",
            "**Product Leaders & Engineering Managers:** To identify critical skill gaps and architect high-impact internal training curricula.",
            "**Career-Focused Tech Professionals:** To proactively acquire future-proof competencies in system architecture, AI orchestration, and strategic decision-making."
        ]
    },
    {
        "filename": "product-leadership-census-2023-v2.en.md",
        "old_file": "product-leadership-census-2023-v2.md",
        "new_file": "product-leadership-census-2023-v2.md",
        "title": "Product Leadership Census 2023",
        "category": "Product Leadership & People",
        "publisher": "Product Collective / AMerchant",
        "year": "2023",
        "date": "2026-09-16",
        "size": "7.3 MB",
        "dl_url": "https://dl.theminiceo.ir/Product%20Leadership%20Census_2023_v2.pdf",
        "description": "In-depth census of Chief Product Officers (CPOs) and VP-level leaders detailing reporting hierarchies, governance, and organizational design.",
        "overview": (
            "The Product Leadership Census 2023 presents a comprehensive survey of executive product leaders, including "
            "Chief Product Officers, VPs of Product, and Heads of Product across both high-growth startups and mature enterprise "
            "corporations. The study investigates organizational structures, reporting lines, resource allocation models, and "
            "the strategic challenges of leading product organizations."
        ),
        "takeaways": [
            ("Executive Reporting Structures", "Direct reporting configurations between CPOs, Chief Executive Officers, and corporate boards of directors."),
            ("Budget Allocation & Department ROI", "Capital allocation models, headcount budgets, and performance indicators used to measure product department business value."),
            ("Talent Retention & Senior Hiring", "Strategies for overcoming recruitment hurdles, mitigating executive burnout, and retaining high-impact product specialists."),
            ("Commercial & Revenue Alignment", "Operational bridges connecting product strategy directly with revenue operations, sales enablement, and go-to-market teams.")
        ],
        "relevance_2026": (
            "Offers proven organizational design patterns for scaling product departments in high-efficiency, "
            "capital-disciplined technology enterprises."
        ),
        "audience": [
            "**Chief Product Officers (CPOs) & VPs:** To validate departmental organizational charts, governance models, and board reporting structures.",
            "**Startup CEOs & Venture Partners:** To optimize executive leadership hires and define clear accountability between product, sales, and engineering.",
            "**Aspiring Executive Product Leaders:** To master executive presence, financial literacy, and the strategic responsibilities of C-suite product roles."
        ]
    },
    {
        "filename": "fpmr-2023-enterprise.en.md",
        "old_file": "fpmr-2023-enterprise.md",
        "new_file": "fpmr-2023-enterprise.md",
        "title": "Future of Product Management Report 2023: Enterprise Edition",
        "category": "State of Product Management",
        "publisher": "Alpha / Publicis Sapient",
        "year": "2023",
        "date": "2026-09-16",
        "size": "1.1 MB",
        "dl_url": "https://dl.theminiceo.ir/FPMR-2023_enterprise.pdf",
        "description": "Enterprise research exploring digital transformation, scaling product operating models, and legacy modernization in large-scale corporations.",
        "overview": (
            "The Future of Product Management in the Enterprise Report (FPMR 2023) focuses specifically on the challenges "
            "and structural transformations occurring within Fortune 1000 enterprises. It dissects how large traditional corporations "
            "dismantle legacy project management mentalities to establish modern, outcome-driven Product Operating Models "
            "capable of rapid innovation."
        ),
        "takeaways": [
            ("The Product Operating Model", "Structural frameworks for transforming traditional project-based IT cost centers into value-generating product organizations."),
            ("Architectural Debt & Legacy Systems", "Architectural and organizational strategies to manage deep technical debt and uncouple legacy systems without interrupting business operations."),
            ("Enterprise Data Governance & Compliance", "Establishing strict data privacy standards, regulatory compliance, and risk controls across dozens of distributed product squads."),
            ("Scaled Agile vs. Autonomous Squads", "Evaluating the operational trade-offs between heavy agile scaling frameworks (SAFe/LeSS) and autonomous, outcome-driven product squads.")
        ],
        "relevance_2026": (
            "Provides vital blueprints for enterprise technology leaders modernizing core corporate platforms "
            "and implementing high-velocity product practices within heavily regulated environments."
        ),
        "audience": [
            "**Enterprise Transformation Leaders:** To guide legacy organizations away from project-centric delivery toward enduring product operating models.",
            "**Enterprise Architects & CIOs:** To align software modernization roadmaps with measurable business outcomes and regulatory standards.",
            "**Product Operations Managers:** To orchestrate standardized discovery, governance, and delivery frameworks across hundreds of cross-functional teams."
        ]
    },
    {
        "filename": "the-future-of-product-2024.en.md",
        "old_file": "the-future-of-product-2024.md",
        "new_file": "the-future-of-product-2024.md",
        "title": "The Future of Product 2024",
        "category": "Future of Work & Skills",
        "publisher": "Product Collective",
        "year": "2024",
        "date": "2026-09-16",
        "size": "9.6 MB",
        "dl_url": "https://dl.theminiceo.ir/The_Future_of_Product_-_2024.pdf",
        "description": "Strategic insights into how generative AI models, agentic workflows, and intent-driven interfaces are redefining modern software products.",
        "overview": (
            "The Future of Product 2024 offers an authoritative roadmap for the next generation of software products. "
            "As generative foundation models and agentic computing reshape digital interactions, this report analyzes the "
            "fundamental architectural, ethical, and organizational shifts required to build enduring product experiences in the AI era."
        ),
        "takeaways": [
            ("Beyond Traditional GUIs", "Transitioning from rigid graphical user interfaces toward dynamic, conversational, and intent-driven interaction paradigms."),
            ("Real-Time Personalization via LLMs", "Harnessing large language models to construct context-aware, hyper-personalized customer journeys dynamically on the fly."),
            ("Agentic Discovery & Automated Usability", "Deploying autonomous AI agents to dramatically compress user discovery cycles, automated QA, and quantitative analytics."),
            ("Ethical AI & Algorithmic Governance", "Frameworks for ensuring algorithmic transparency, data privacy compliance, and human-in-the-loop oversight in customer-facing AI products.")
        ],
        "relevance_2026": (
            "Directly anticipates the rise of autonomous agentic applications, delivering actionable frameworks for "
            "designing intelligent products that continuously adapt to individual user intent."
        ),
        "audience": [
            "**AI Product Managers:** To design resilient architectures, human-in-the-loop validation, and intuitive prompts for intelligent agentic software.",
            "**Design Systems Engineers:** To explore adaptive design components capable of fluidly responding to non-deterministic user interactions.",
            "**Innovation & R&D Leaders:** To identify emerging product categories unlocked by multi-modal reasoning and specialized machine learning models."
        ]
    },
    {
        "filename": "amplitude-product-report-2022.en.md",
        "old_file": "amplitude-product-report-2022.md",
        "new_file": "amplitude-product-report-2022.md",
        "title": "Amplitude Product Report 2022",
        "category": "Data Analytics & User Behavior",
        "publisher": "Amplitude",
        "year": "2022",
        "date": "2026-09-16",
        "size": "2.0 MB",
        "dl_url": "https://dl.theminiceo.ir/Amplitude%20Product%20Report%202022.pdf",
        "description": "Behavioral telemetry benchmark across millions of active digital users examining engagement patterns and retention loops in top apps.",
        "overview": (
            "The Amplitude Product Report 2022 is an empirical study of digital product usage based on aggregated behavioral "
            "data from over 1.4 trillion user interactions across thousands of global digital products. It examines user retention, "
            "feature engagement, product-led growth mechanics, and the quantifiable behaviors that separate category leaders from laggards."
        ),
        "takeaways": [
            ("Empirical Retention Curves", "Longitudinal retention benchmarks across B2B SaaS, consumer apps, and fintech, identifying baseline retention thresholds required for sustainable growth."),
            ("Uncovering the 'Aha Moment'", "Statistical correlation between early user interaction milestones and long-term customer lifetime value."),
            ("Personalization Impact on LTV", "Direct quantitative evidence demonstrating how tailored user onboarding paths expand revenue expansion and retention."),
            ("Product-Led Growth (PLG) Mechanics", "Proven tactical frameworks for turning engaged active users into organic acquisition and self-serve expansion loops.")
        ],
        "relevance_2026": (
            "Fundamental telemetry and retention mechanics analyzed in this report remain the core bedrock for building "
            "sustainable, self-serve software businesses in any economic environment."
        ),
        "audience": [
            "**Growth Product Managers:** To establish empirical retention baselines, activation milestones, and self-serve expansion loops.",
            "**Data Analysts & Engineers:** To configure event tracking taxonomies that accurately measure critical user journeys and churn inflection points.",
            "**Product Marketers:** To understand user conversion triggers and optimize onboarding flows based on verified behavioral telemetry."
        ]
    },
    {
        "filename": "airtable-product-insights-report.en.md",
        "old_file": "airtable-product-insights-report.md",
        "new_file": "airtable-product-insights-report.md",
        "title": "Airtable Product Insights Report",
        "category": "Tools & Enterprise Innovation",
        "publisher": "Airtable",
        "year": "2022",
        "date": "2026-09-16",
        "size": "2.9 MB",
        "dl_url": "https://dl.theminiceo.ir/Airtable_Product-insights-report.pdf",
        "description": "Enterprise report examining how modern teams accelerate product discovery and delivery using no-code platforms and connected data.",
        "overview": (
            "The Airtable Product Insights Report examines how forward-thinking product organizations streamline cross-functional "
            "collaboration and eliminate operational silos using modern connected-data platforms and flexible no-code architectures. "
            "Featuring insights from leading digital brands, the report outlines how visual relational databases accelerate "
            "time-to-market and bridge gaps between product, engineering, and business teams."
        ),
        "takeaways": [
            ("Eliminating Cross-Departmental Silos", "Unifying product roadmaps, user research backlogs, and marketing launch schedules within a single collaborative relational data layer."),
            ("Compressing Time-to-Market", "Accelerating software delivery cycles by enabling product teams to build, test, and iterate on custom workflows without dedicated developer overhead."),
            ("Centralizing Qualitative Feedback", "Systematizing customer interview findings, feature requests, and support tickets directly into sprint prioritization boards."),
            ("Automated Product Operations (ProdOps)", "Blueprints from industry leaders on automating status reporting, asset tracking, and stakeholder notifications.")
        ],
        "relevance_2026": (
            "Demonstrates the continued value of modular, flexible relational databases in orchestrating modern "
            "product operations and reducing manual administrative friction across large product organizations."
        ),
        "audience": [
            "**Product Operations Managers:** To build streamlined operational cadences, automated reporting, and transparent cross-functional roadmaps.",
            "**Technical Product Managers:** To implement rapid internal tooling and connected discovery databases that reduce engineering dependencies.",
            "**Cross-Functional Program Leads:** To foster transparency and accountability across product, customer success, sales, and marketing teams."
        ]
    },
    {
        "filename": "heap-digital-experiences-insights-report2.en.md",
        "old_file": "heap-digital-experiences-insights-report2.md",
        "new_file": "heap-digital-experiences-insights-report2.md",
        "title": "Heap Digital Experiences Insights Report",
        "category": "Data Analytics & User Behavior",
        "publisher": "Heap",
        "year": "2022",
        "date": "2026-09-16",
        "size": "400 KB",
        "dl_url": "https://dl.theminiceo.ir/heap-digital-experiences-insights-report2.pdf",
        "description": "User experience analysis exploring customer journey friction, funnel drop-off points, and conversion optimization strategies across web and mobile.",
        "overview": (
            "The Heap Digital Experience Insights Report analyzes billions of user interactions to diagnose the exact moments "
            "of customer friction, disorientation, and abandonment across web and mobile experiences. By analyzing complete, "
            "autocaptured datasets, the report highlights the common design pitfalls that depress conversion rates and reveals "
            "high-leverage interventions for digital product optimization."
        ),
        "takeaways": [
            ("Unnoticed Funnel Drop-offs", "Pinpointing hidden UX bottlenecks across user registration, onboarding flows, and multi-step payment checkouts."),
            ("The Value of Autocapture Analytics", "How automated, retroactive event tracking surfaces unexpected navigational dead-ends that manual tracking plans overlook."),
            ("Latency & Interface Bloat Impact", "Quantifying how micro-delays, confusing navigation hierarchies, and interface clutter directly depress key feature engagement."),
            ("Conversion Funnel Optimization", "Systematic testing methodologies to eliminate checkout friction, improve form completion, and maximize revenue per visitor.")
        ],
        "relevance_2026": (
            "Pinpointing micro-friction in digital user experiences is even more vital today, as user attention spans "
            "shorten and intolerance for clunky interfaces continues to grow."
        ),
        "audience": [
            "**UX Researchers & Interaction Designers:** To pinpoint subtle usability bottlenecks and validate design enhancements through concrete telemetry.",
            "**E-commerce & Conversion Specialists:** To optimize checkout flows, eliminate friction, and maximize transaction completion rates.",
            "**Frontend Engineers:** To understand how technical performance metrics and interface responsiveness directly drive customer satisfaction and retention."
        ]
    },
    {
        "filename": "designvaluereport1.en.md",
        "old_file": "designvaluereport1.md",
        "new_file": "designvaluereport1.md",
        "title": "Design Value Benchmark Report",
        "category": "Design & Business Value",
        "publisher": "Design Management Institute (DMI)",
        "year": "2021",
        "date": "2026-09-16",
        "size": "1.3 MB",
        "dl_url": "https://dl.theminiceo.ir/DesignValueReport1.pdf",
        "description": "Empirical study measuring the Return on Investment (ROI) of design and how design-centric companies outperform broader financial markets.",
        "overview": (
            "The Design Value Benchmark Report, conducted by the Design Management Institute (DMI), provides conclusive empirical "
            "evidence of the direct relationship between strategic design investment and outsized shareholder value. Tracking a portfolio "
            "of publicly traded, design-centric corporations over a ten-year horizon, the report quantifies the commercial "
            "returns of embedding design thinking into executive leadership."
        ),
        "takeaways": [
            ("The Design Value Index (DVI)", "Empirical proof showing that design-centric public corporations outperformed the S&P 500 index by over 200% over a decade."),
            ("Translating Craft into Revenue", "Concrete mechanisms for connecting superior user experience, aesthetic polish, and intuitive interaction directly to operating margins and pricing power."),
            ("Design Maturity Framework", "A four-stage maturity model evaluating how organizations evolve from superficial aesthetic styling to strategic business design."),
            ("Durable Customer Affinity", "How emotionally resonant, cohesive product identities build lasting customer loyalty and brand defensibility against generic commoditization.")
        ],
        "relevance_2026": (
            "Proves definitively that design craft and exceptional user experience are not mere aesthetic luxuries, "
            "but fundamental strategic engines of enterprise valuation and customer retention."
        ),
        "audience": [
            "**Chief Design Officers & VP of Design:** To communicate the quantifiable business ROI of design investments persuasively to CFOs and CEOs.",
            "**Product Managers & General Managers:** To champion aesthetic quality and user-centric problem solving as core strategic market differentiators.",
            "**Investors & Corporate Strategists:** To evaluate target acquisition candidates through the lens of design maturity and product user experience."
        ]
    },
    {
        "filename": "گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md",
        "old_file": "گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md",
        "new_file": "گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md",
        "title": "Annual Report on the Payment Industry of Iran (9th Edition)",
        "category": "Iran Ecosystem & Industry Benchmarks",
        "publisher": "Way2pay / Shaparak",
        "year": "2022",
        "date": "2026-09-16",
        "size": "5.7 MB",
        "dl_url": "https://dl.theminiceo.ir/%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B5%D9%86%D8%B9%D8%AA%20%D9%BE%D8%B1%D8%AF%D8%A7%D8%AE%D8%AA%20%D8%A7%DB%8C%D8%B1%D8%A7%D9%86%20%D9%86%D8%B3%D8%AE%D9%87%20%D9%86%D9%87%D9%85.pdf",
        "description": "In-depth statistical analysis of electronic transactions, PSP market shares, payment gateways, and fintech trends across Iran.",
        "overview": (
            "The Annual Report on the Payment Industry of Iran (9th Edition) delivers a rigorous, data-driven statistical analysis "
            "of the Iranian electronic payment ecosystem. Leveraging primary telemetry from the Shaparak national payment switch and "
            "licensed Payment Service Providers (PSPs), this publication details transaction volumes, value settlements, channel dynamics, "
            "and emerging fintech trends."
        ),
        "takeaways": [
            ("Transaction Volumes & Settlement Values", "Macroeconomic analysis of electronic settlement growth, seasonal transaction surges, and online payment gateway (IPG) throughput."),
            ("PSP Market Share Rankings", "Granular market share breakdown and competitive rankings of licensed Iranian Payment Service Providers across POS, IPG, and mobile channels."),
            ("Mobile Payment Trajectories", "Shifts in consumer behavior across smartphone banking apps, USSD protocols, and emerging digital wallet platforms."),
            ("Regulatory Challenges & Horizons", "The impact of regulatory ceilings, transaction fees, and central banking compliance on domestic fintech innovation.")
        ],
        "relevance_2026": (
            "Provides an indispensable empirical baseline for analyzing high-volume electronic payment rails, "
            "consumer transaction behavior, and financial infrastructure within a distinctive emerging market economy."
        ),
        "audience": [
            "**Fintech Product Managers & Leaders:** To understand payment gateway settlement dynamics, PSP provider capabilities, and transaction success rates.",
            "**Financial Analysts & Economists:** To evaluate national electronic payment velocity and consumer purchasing patterns across digital channels.",
            "**Enterprise Founders & CTOs:** To choose optimal payment infrastructure and navigate regulatory compliance in domestic commerce."
        ]
    },
    {
        "filename": "iran-startup-ecosystem-report-techrasa-1400.en.md",
        "old_file": "1666697156021.md",
        "new_file": "iran-startup-ecosystem-report-techrasa-1400.md",
        "title": "Iran Startup Ecosystem Report – TechRasa (Spring 2021 / 1400)",
        "category": "Iran Ecosystem & Industry Benchmarks",
        "publisher": "TechRasa",
        "year": "2021",
        "date": "2026-09-16",
        "size": "1.8 MB",
        "dl_url": "https://dl.theminiceo.ir/1666697156021.pdf",
        "description": "Comprehensive field study surveying over 100 startup founders and CEOs on growth metrics, valuations, and macroeconomic headwinds.",
        "overview": (
            "The Iran Startup Ecosystem Report by TechRasa provides an empirical field survey capturing direct insights from "
            "over 100 startup founders, chief executives, and technology operators across Iran. Conducted during a critical inflection "
            "point, the study documents venture maturity stages, capitalization dynamics, talent constraints, and macroeconomic adaptations."
        ),
        "takeaways": [
            ("Founder Perspectives & Growth Sentiments", "First-hand survey data from over 100 tech CEOs and founders on operational runway, team expansion, and hiring bottlenecks."),
            ("Venture Maturity Benchmarking", "Comparative growth indicators categorizing startups across Seed, Early Stage, and Expansion phases."),
            ("Macroeconomic & Connectivity Headwinds", "Quantifying the operational impacts of domestic currency inflation, international sanctions, and internet connectivity disruptions on digital ventures."),
            ("Venture Capital & Valuation Bottlenecks", "Analyzing valuation methodologies, angel investment activity, and the scarcity of institutional growth capital.")
        ],
        "relevance_2026": (
            "Stands as a vital historical record of operational resilience, extreme capital efficiency, and adaptive "
            "business modeling in the face of acute macroeconomic and structural constraints."
        ),
        "audience": [
            "**Startup Founders & Entrepreneurs:** To benchmark growth milestones, runway planning, and capital efficiency against fellow regional ventures.",
            "**Venture Investors & Angels:** To evaluate stage-appropriate valuations and operational performance indicators in challenging markets.",
            "**Policy & Ecosystem Observers:** To assess the structural needs and economic contributions of innovation-driven tech businesses."
        ]
    },
    {
        "filename": "hbr-2022-11-12.en.md",
        "old_file": "hbr-2022-11-12.md",
        "new_file": "hbr-2022-11-12.md",
        "title": "Harvard Business Review Magazine (Nov-Dec 2022 Issue)",
        "category": "Specialized Periodicals & Journals",
        "publisher": "Harvard Business Publishing",
        "year": "2022",
        "date": "2026-09-16",
        "size": "90.4 MB",
        "dl_url": "https://dl.theminiceo.ir/HBR%202022%2011%2012.pdf",
        "description": "Full edition of Harvard Business Review examining executive leadership strategies during uncertainty, resilience, and high-stakes decision-making.",
        "overview": (
            "The November–December 2022 issue of the Harvard Business Review brings together leading management thinkers "
            "and business scholars to address executive decision-making during severe economic ambiguity. Featuring peer-reviewed "
            "essays, global case studies, and strategic playbooks, the publication tackles supply chain disruptions, pricing power "
            "during inflationary cycles, and the psychological demands of leadership."
        ),
        "takeaways": [
            ("Organizational Resilience Under Stress", "Empirical management research from Harvard Business School outlining strategies for enterprise longevity and structural durability."),
            ("Strategic Pricing in Inflationary Environments", "Dynamic value-based pricing methodologies and agile supply chain adjustments that protect gross margins."),
            ("Executive Psychology & Crisis Leadership", "Frameworks for managing executive cognitive load, mitigating organizational anxiety, and sustaining team cohesion during downturns."),
            ("Corporate Business Model Transformation", "In-depth case studies analyzing enterprise pivots toward recurring subscription models and programmatic client retention.")
        ],
        "relevance_2026": (
            "Provides enduring strategic wisdom on leading through economic uncertainty, safeguarding operating margins, "
            "and maintaining team focus during systemic market disruptions."
        ),
        "audience": [
            "**C-Suite Executives & General Managers:** To sharpen high-level strategic reasoning, crisis decision-making, and organizational leadership.",
            "**Senior Product Directors:** To align product portfolio roadmaps with broader corporate financial sustainability and margin targets.",
            "**Management Consultants & Strategists:** To leverage academic management research and case studies in client engagements."
        ]
    },
    {
        "filename": "generative-ai-the-insights-you-need-from-harvard-business-review.en.md",
        "old_file": "generative-ai-the-insights-you-need-from-harvard-business-review.md",
        "new_file": "generative-ai-the-insights-you-need-from-harvard-business-review.md",
        "title": "Generative AI: The Insights You Need from Harvard Business Review",
        "category": "Specialized Periodicals & Journals",
        "publisher": "Harvard Business Review Press",
        "year": "2023",
        "date": "2026-09-16",
        "size": "6.7 MB",
        "dl_url": "https://dl.theminiceo.ir/Generative_AI_The_Insights_You_Need_From_Harvard_Business_Review.pdf",
        "description": "Curated HBR anthology on generative AI exploring its transformative influence on enterprise strategy, knowledge work, and competitive advantage.",
        "overview": (
            "Generative AI: The Insights You Need from Harvard Business Review is a curated compendium of critical research "
            "and strategic commentary examining the generative AI revolution. Authored by industry researchers, academics, and "
            "enterprise technologists, the anthology investigates how foundation models transform knowledge productivity, software development, "
            "competitive moats, and corporate governance."
        ),
        "takeaways": [
            ("Reinventing Knowledge Work", "How foundation models augment human creativity, software development throughput, and strategic document analysis across corporate divisions."),
            ("Enterprise Risk & Governance Safeguards", "Tactical guidance for mitigating intellectual property liability, model hallucinations, and customer privacy violations."),
            ("Building Defensible Competitive Moats", "Strategic playbooks for technology startups to establish sustainable differentiation beyond simple model API wrappers."),
            ("Autonomous Customer Interaction Pipelines", "Redesigning customer service, technical support, and sales interactions using intelligent, responsive autonomous assistants.")
        ],
        "relevance_2026": (
            "Critical for separating real AI value from superficial wrappers, offering timeless business frameworks "
            "for building defensible products around foundation intelligence."
        ),
        "audience": [
            "**Technology Executives & Strategists:** To formulate high-ROI artificial intelligence roadmaps and build defensible enterprise moats.",
            "**Product Managers & Innovators:** To integrate generative capabilities thoughtfully without compromising intellectual property or data privacy.",
            "**Business Operations Leaders:** To redesign core organizational workflows and upskill teams for autonomous collaborative AI environments."
        ]
    },
    {
        "filename": "the-analytics-stack-guidebook.en.md",
        "old_file": "the-analytics-stack-guidebook.md",
        "new_file": "the-analytics-stack-guidebook.md",
        "title": "The Analytics Stack Guidebook: Selecting Modern Product Data Infrastructure",
        "category": "Tools & Enterprise Innovation",
        "publisher": "Fivetran / dbt Labs",
        "year": "2022",
        "date": "2026-09-16",
        "size": "13.5 MB",
        "dl_url": "https://dl.theminiceo.ir/the-analytics-stack-guidebook.pdf",
        "description": "Architectural comparison of modern data collection, storage, and behavioral analytics tools including Snowflake, BigQuery, Segment, and Amplitude.",
        "overview": (
            "The Analytics Stack Guidebook provides a rigorous architectural breakdown of the modern product data ecosystem. "
            "Evaluating technologies across data extraction, cloud warehousing, transformation, and behavioral analytics, "
            "the guidebook assists technology leaders in assembling a cohesive, scalable infrastructure that empowers product teams "
            "with reliable, self-serve data."
        ),
        "takeaways": [
            ("Modern Data Stack (MDS) Blueprint", "Comprehensive architectural overview spanning automated ELT connectors, cloud data warehouses, dbt modeling, and product analytics."),
            ("CDP vs. Data Warehouse Architectures", "Technical and operational trade-offs between Customer Data Platforms (such as Segment) and direct-to-warehouse analytics architectures."),
            ("Maturity-Based Tool Recommendations", "Pragmatic tooling stacks optimized for companies at various scale thresholds, from early pre-revenue teams to enterprise leaders."),
            ("Warehouse Query & Storage Cost Governance", "Proven architectural patterns to control storage costs, optimize partitioning, and govern compute spending at scale.")
        ],
        "relevance_2026": (
            "Data warehouse architecture and reliable event streaming remain essential foundations for powering "
            "modern product analytics, experimentation engines, and fine-tuned AI inference models."
        ),
        "audience": [
            "**Data Engineers & Architects:** To design scalable, modular data pipelines that reliably power both operational analytics and ML inference.",
            "**Technical Product Managers:** To establish clean tracking contracts and collaborate effectively with data infrastructure teams.",
            "**Engineering Leadership:** To maintain strict financial governance over cloud warehouse compute, storage, and ETL licensing costs."
        ]
    },
    {
        "filename": "heap-implicit-vs-explicit-guide-2022.en.md",
        "old_file": "heap-implicit-vs-explicit-guide-2022.md",
        "new_file": "heap-implicit-vs-explicit-guide-2022.md",
        "title": "Heap Guide 2022: Implicit vs. Explicit Data in Modern Product Analytics",
        "category": "Data Analytics & User Behavior",
        "publisher": "Heap",
        "year": "2022",
        "date": "2026-09-16",
        "size": "1.7 MB",
        "dl_url": "https://dl.theminiceo.ir/HEAP_Implicit-vs-Explicit_Guide_2022.pdf",
        "description": "Technical guide on automated event capture contrasting implicit telemetry with explicit tracking plans to eliminate analytical blind spots.",
        "overview": (
            "The Heap Guide on Implicit vs. Explicit Data is an authoritative technical playbook comparing two competing philosophies "
            "of digital product analytics: reactive manual event tracking (explicit data) versus proactive automatic event capture "
            "(implicit data). The guide explores how relying exclusively on manual tracking plans creates costly data blind spots and "
            "slows product iteration."
        ),
        "takeaways": [
            ("Implicit vs. Explicit Architectures", "Contrasting manual event tagging against retroactive, automatic capture architectures to understand trade-offs in completeness and precision."),
            ("Eliminating Analytical Blind Spots", "How implicit data capture surfaces unhypothesized user behaviors, dead clicks, and unexpected navigational detours automatically."),
            ("Slashing Developer Maintenance Overhead", "Dramatically reducing engineering sprint hours spent instrumenting, fixing, and maintaining brittle tracking code across releases."),
            ("Virtualizing Telemetry into Insights", "Best practices for virtualizing raw interaction events into verified, executive-level business metrics without corrupting raw event streams.")
        ],
        "relevance_2026": (
            "Balances the agility of retroactive event capture with disciplined schema governance, delivering "
            "vital strategies for designing resilient, low-maintenance telemetry systems."
        ),
        "audience": [
            "**Analytics Product Managers:** To establish flexible telemetry foundations that capture comprehensive user interactions without brittle instrumentation.",
            "**Software & Frontend Engineers:** To minimize maintenance overhead associated with manual event tagging and fragile tracking plans.",
            "**Growth & Experimentation Leads:** To analyze past user behavior retroactively without waiting weeks for newly instrumented tracking code to collect data."
        ]
    }
]

def format_report_markdown(r):
    old_slug = r["old_file"].replace(".md", "")
    new_slug = r["new_file"].replace(".md", "")
    
    aliases = [f"/docs/books/{old_slug}/"]
    if old_slug != new_slug:
        aliases.append(f"/docs/reports/{old_slug}/")
        aliases.append(f"/en/docs/reports/{old_slug}/")
        aliases.append(f"/en/docs/books/{old_slug}/")
    aliases_lines = "\n".join([f"  - {a}" for a in aliases])

    takeaways_md = "\n".join([
        f"* **{title}:** {desc}" for title, desc in r["takeaways"]
    ])

    audience_md = "\n".join([f"* {item}" for item in r["audience"]])

    md = f"""---
title: "{r['title']}"
date: {r['date']}
description: "{r['description']}"
tags: ["Reports", "{r['category']}", "Product Management", "Market Analysis"]
categories: ["Reports"]
aliases:
{aliases_lines}
---

| Report Specification | Details |
| :--- | :--- |
| **Publisher / Source** | {r['publisher']} |
| **Category** | {r['category']} |
| **Publication Year** | {r['year']} |
| **Format** | PDF |
| **File Size** | {r['size']} |
| **Language** | English |

### 📊 Executive Overview & Core Premise

{r['overview']}

### 🔑 Key Takeaways & Research Findings

{takeaways_md}

### 💡 Industry & Market Relevance in 2026

{r['relevance_2026']}

### 🎯 Target Audience

{audience_md}

---

### 📥 Download Full Report

{{{{< book-download url="{r['dl_url']}" title="Download {r['title']}" size="{r['size']}" format="PDF" lang="English" >}}}}
"""
    return md

def main():
    print(f"Generating {len(REPORTS_DATA)} English report files in {REPORTS_DIR}...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    created_count = 0
    for r in REPORTS_DATA:
        out_path = REPORTS_DIR / r["filename"]
        content = format_report_markdown(r)
        out_path.write_text(content, encoding="utf-8")
        created_count += 1
        print(f"[{created_count}/17] Created: {out_path.name} ({len(content)} bytes)")

    print(f"\nSuccessfully generated all {created_count} English report files.")

if __name__ == "__main__":
    main()
