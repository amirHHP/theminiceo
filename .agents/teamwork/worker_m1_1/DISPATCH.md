## 2026-10-10T09:40:31Z

You are worker_m1_1.
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/worker_m1_1
Your parent is orchestrator_2 (ID: 1390bbb4-2296-47f7-8f97-a4b7fde0fc3d).

Objective: Implement and verify the production-grade localization audit & CI verification tool `scripts/verify_localization.py` and its test suite `scripts/test_verify_localization.py` for Milestone 1.

Files to read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (MANDATORY)
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_2/PROJECT.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m1_1/handoff.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m1_2/handoff.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m1_1/handoff.md
- /Users/sotoon/personal/theminiceo/scripts/test_localization_e2e.py (specifically T1.1, T4.1, T4.5)

File write ownership:
- scripts/verify_localization.py
- scripts/test_verify_localization.py

Detailed Requirements:
1. Pure Python standard library (no external pip dependencies).
2. Traversal & Exclusions: Traverse content/ ignoring content/pdfs/, .obsidian/, content/.obsidian/, _drafts/, and non-markdown files.
3. Language Pairing: Verify that every Persian *.md file has an exact companion *.en.md in the same directory (handling Persian Unicode slugs like decomposed combining madda accurately).
4. Robust Frontmatter Parsing: Parse YAML (---) and TOML (+++ using standard library tomllib). Handle colons in quotes, inline lists, and YAML block lists (e.g. categories:\n  - Books).
5. Validation Logic: Validate title, date (except root index/categories), description (strictly required for books and reports; for other content required when Persian counterpart has description), and non-empty content (>50 bytes).
6. CLI Flags: Support --root / --content-dir, --strict, --json, -v/--verbose, -q/--quiet, --min-file-size.
7. Exit code semantics: 0 when 100% paired and valid; 1 when any missing page or validation error is detected. Output must contain summary keywords required by E2E test T4.1 ("SUCCESS" or "100%").
8. Comprehensive Unit Tests: Write scripts/test_verify_localization.py using unittest and tempfile.TemporaryDirectory covering at least 15 edge cases (exclusions, TOML/YAML, block lists, unicode slugs, exit codes).
9. Run verification commands:
   - python3 scripts/test_verify_localization.py
   - python3 scripts/test_localization_e2e.py --tier 1
   Document all test output and results.
