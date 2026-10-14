## 2026-10-10T14:13:54Z
You are worker_m2_1.
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/worker_m2_1
Your parent is orchestrator_2 (ID: 1390bbb4-2296-47f7-8f97-a4b7fde0fc3d).

Objective: Implement Milestone 2: Update layouts/shortcodes/book-download.html for multilingual support and generate all 17 English reports in content/docs/reports/*.en.md.

Files to read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (MANDATORY) § R3, R4
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_2/PROJECT.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m2_1/handoff.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m2_2/handoff.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m2_1/handoff.md
- /Users/sotoon/personal/theminiceo/scripts/setup_reports_section.py
- /Users/sotoon/personal/theminiceo/layouts/shortcodes/book-download.html

File write ownership:
- layouts/shortcodes/book-download.html
- scripts/generate_english_reports.py
- content/docs/reports/*.en.md (all 17 report files + _index.en.md)

Detailed Requirements:
1. Shortcode i18n: Update `layouts/shortcodes/book-download.html` using the template patch from `explorer_m2_2/handoff.md`. When `.Page.Language.Lang == "en"`, render English labels ("Download Book File", "Size: ", "Language: ", "High-speed Direct CDN"). For Persian, render the existing Persian labels.
2. English Reports Generation:
   - Create and run `scripts/generate_english_reports.py` using canonical metadata from `scripts/setup_reports_section.py` and `content/docs/reports/*.md`.
   - Generate all 17 `.en.md` files in `content/docs/reports/`.
   - Special attention to non-ASCII slug: `content/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md`.
   - Each report must contain:
     * YAML frontmatter: `title`, `date`, `description`, `tags`, `categories: ["Reports"]`.
     * Specifications table: `| Report Specification | Details |`.
     * Executive Overview / Core Premise.
     * 4 structured Key Takeaways / Research Findings.
     * Industry & Market Relevance in 2026.
     * Target Audience.
     * Working `{{< book-download url="..." title="..." size="..." format="PDF" lang="English" >}}` shortcode with exact CDN URL matching setup_reports_section.py.
   - Zero Persian text in English files (`title`, `description`, headings, body).
   - Zero placeholder text (`TODO`, `FIXME`, `TBD`, `lorem ipsum`).
3. Upgrade `content/docs/reports/_index.en.md`: Add curated showcase cards, thematic pillars, and valid English links.
4. Verification:
   - Run: `python3 scripts/test_localization_e2e.py -v --tier 3` (test_t3_4 passes).
   - Run: `python3 scripts/test_localization_e2e.py -v --tier 1` (test_t1_2 passes).
   - Run: `python3 scripts/test_localization_e2e.py -v --tier 2` (test_t2_2, test_t2_4, test_t2_5, test_t2_6 pass).
   - Run: `python3 scripts/verify_localization.py` and verify all 17 reports are valid.
   Document all command outputs.
