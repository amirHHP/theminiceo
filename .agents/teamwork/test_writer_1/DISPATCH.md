# Dispatch for E2E Test Writer

## 2026-10-09T17:15:00Z
Task: Design and implement the comprehensive E2E test suite for theminiceo localization.

Files to read:
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md` (MANDATORY)
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_1/PROJECT.md`
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_1/TEST_INFRA.md`
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_survey_1/handoff.md`
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_survey_2/handoff.md`
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_survey_3/handoff.md`

File write ownership:
- `scripts/test_localization_e2e.py`
- `/Users/sotoon/personal/theminiceo/TEST_READY.md`

Objectives:
1. Implement `scripts/test_localization_e2e.py` covering all 4 tiers described in `TEST_INFRA.md`:
   - Tier 1: Feature Coverage (file pairing, frontmatter completeness, non-empty content)
   - Tier 2: Boundary & Corner Cases (Persian slug files, exclusions, zero placeholder text, zero untranslated Persian blocks in English pages)
   - Tier 3: Cross-Feature Interactions (valid download URLs, taxonomy category mapping, shortcode parameters)
   - Tier 4: Real-World Workloads (`scripts/verify_localization.py` execution, `hugo --renderToMemory` compilation & page count delta verification)
2. Support running all tests or specific tiers via CLI arguments (e.g. `--tier 1`, `--tier 2`, etc.).
3. Verify test runner execution.
4. Publish `TEST_READY.md` at `/Users/sotoon/personal/theminiceo/TEST_READY.md`.
5. Deliver handoff report to `/Users/sotoon/personal/theminiceo/.agents/teamwork/test_writer_1/handoff.md`.
