# BRIEFING — 2026-10-09T17:15:00Z

## Mission
Implement the automated localization audit & CI verification tool `scripts/verify_localization.py` adhering strictly to Requirement R1.

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa, specialist
- Working directory: /Users/sotoon/personal/theminiceo/.agents/teamwork/worker_m1
- Original parent: f1f0915a-12eb-40f5-b776-04e4551636d5
- Milestone: M1

## 🔒 Key Constraints
- Pure Python (standard library only, zero pip dependencies).
- Excludes content/pdfs/, .obsidian/, and _drafts/.
- Verifies 1-to-1 pairing of Persian (*.md) with English (*.en.md) in the same directory.
- Validates frontmatter completeness (presence of English title, date, description) and checks non-empty body (>50 bytes).
- Returns exit code 0 when all pages have valid English counterparts, and exit code 1 if any issues are detected.
- Integrity mandate: DO NOT cheat, fake, hardcode outputs, or create dummy implementations. Genuine logic only.

## Current Parent
- Conversation ID: f1f0915a-12eb-40f5-b776-04e4551636d5
- Updated: 2026-10-09T17:15:00Z

## Task Summary
- **What to build**: `scripts/verify_localization.py`
- **Success criteria**: Audits all content files deterministically, verifies 1:1 pairing, validates frontmatter (`title`, `date`, `description`), checks non-empty content (>50 bytes), outputs detailed summary, returns 0 on 100% parity and 1 on issues.
- **Interface contracts**: `/Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_1/PROJECT.md`
- **Code layout**: `scripts/verify_localization.py`

## Key Decisions Made
- [TBD - Investigating existing frontmatter structure and CLI options]

## Artifact Index
- `scripts/verify_localization.py` — Verification & audit tool
- `.agents/teamwork/worker_m1/handoff.md` — Final handoff report

## Change Tracker
- **Files modified**: None yet
- **Build status**: Pending implementation
- **Pending issues**: None

## Quality Status
- **Build/test result**: Not yet executed
- **Lint status**: Not yet executed
- **Tests added/modified**: Pending unit test suite for verify_localization.py

## Loaded Skills
- None
