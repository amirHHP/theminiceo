# Dispatch for Worker M1 (Verification Tool Implementer)

## 2026-10-09T17:15:00Z
Task: Implement the automated localization audit & CI verification tool `scripts/verify_localization.py` adhering strictly to Requirement R1.

Files to read:
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md` (MANDATORY)
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_1/PROJECT.md`
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_survey_3/handoff.md`

File write ownership:
- `scripts/verify_localization.py`

Requirements:
- Pure Python (standard library only).
- Deterministically audits all content files across the repository.
- Verifies that for every Persian content file (`*.md`, excluding `content/pdfs/`, `.obsidian/`, and `_drafts/`), an equivalent English file (`*.en.md`) exists in the same directory.
- Validates frontmatter completeness (presence of English `title`, `date`, `description`) and checks that files are non-empty (>50 bytes).
- Returns exit code 0 when all pages have valid English counterparts, and non-zero (exit code 1) if any missing pages or frontmatter issues are detected.
- Outputs detailed summary: total checked, missing, invalid frontmatter, empty files.
- Test run `python3 scripts/verify_localization.py` and document output.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Deliver handoff report to:
`/Users/sotoon/personal/theminiceo/.agents/teamwork/worker_m1/handoff.md`
