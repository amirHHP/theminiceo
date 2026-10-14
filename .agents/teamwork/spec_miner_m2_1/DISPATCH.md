## 2026-10-10T14:03:48Z

You are spec_miner_m2_1.
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m2_1
Your parent is orchestrator_2 (ID: 1390bbb4-2296-47f7-8f97-a4b7fde0fc3d).

Objective: Mine authoritative requirements, interface contracts, and E2E assertions for Milestone 2 (Reports localization & Shortcode i18n).

Files to read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (MANDATORY) § R3, R4
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_2/PROJECT.md
- /Users/sotoon/personal/theminiceo/scripts/test_localization_e2e.py (tests T1.2, T1.4, T1.5, T2.2, T2.4, T2.5, T2.6, T3.1, T3.2, T3.4)
- /Users/sotoon/personal/theminiceo/TEST_READY.md

Tasks:
1. Extract all functional requirements for the 17 English reports: frontmatter fields (title, date, description, tags, categories: ["Reports"]), body structure, key research takeaways, download shortcode parameters.
2. Document all E2E assertions touching reports:
   - T1.2: 17 reports + _index.en.md exist
   - T1.4: Frontmatter completeness on all 17 reports
   - T1.5: Body non-empty (>100 chars, ### headings)
   - T2.2: Persian slug report exists and valid
   - T2.4: Zero Persian characters in English reports
   - T2.5: Zero dummy placeholder text
   - T2.6: Boundary file sizes (HBR ~90.4MB, Heap ~400KB)
   - T3.1: Download URLs cross-referenced against setup_reports_section.py
   - T3.2: Category is ["Reports"]
   - T3.4: Shortcode template multilingual support
3. Build a precise Requirements Traceability Matrix for Milestone 2.

Constraints:
- Read-only. Do NOT modify source code files.
- Deliver your report to:
  /Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m2_1/handoff.md
- Send a completion message to parent when done.
