## 2026-10-10T14:35:35Z
You are spec_miner_m3_1.
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m3_1
Your parent is orchestrator_2 (ID: 1390bbb4-2296-47f7-8f97-a4b7fde0fc3d).

Objective: Mine authoritative requirements, interface contracts, and E2E assertions for Milestone 3 (Books English Localization).

Files to read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (MANDATORY) § R2
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_2/PROJECT.md
- /Users/sotoon/personal/theminiceo/scripts/test_localization_e2e.py (tests T1.3, T1.4, T1.5, T2.1, T2.4, T2.5, T2.6, T3.1, T3.2, T3.3, T3.5)
- /Users/sotoon/personal/theminiceo/TEST_READY.md
- /Users/sotoon/personal/theminiceo/scripts/verify_localization.py

Tasks:
1. Extract all functional requirements for the 390 English books, 17 retrofitted books, and _index.en.md.
2. Document all E2E assertions touching books:
   - T1.3: 408 English book files exist in content/docs/books/ (390 generated + 17 legacy + _index.en.md), data/books_metadata.json parity, sample categories coverage.
   - T1.4: Frontmatter completeness (title, date, description, categories) on all 407 books.
   - T1.5: Body non-empty (>100 chars, ### headings) on all books and _index.en.md.
   - T2.1: Persian slug book exists with English title, description, body, and download shortcode.
   - T2.4: Zero Persian characters in English fields.
   - T2.5: Zero dummy placeholder text.
   - T3.1: Download URLs cross-referenced against books_metadata.json.
   - T3.2: Category is ["Books"].
   - T3.3: Specifications table integrity on all books.
3. Build a precise Requirements Traceability Matrix for Milestone 3.
4. Deliver handoff report to:
   /Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m3_1/handoff.md
5. Send completion message to parent when done.
