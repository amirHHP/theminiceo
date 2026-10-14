# BRIEFING — 2026-10-10T14:13:00Z

## Mission
Survey frontend architecture of Hugo static site `theminiceo` for book download delivery and paywall integration.

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: explorer, analyst
- Working directory: /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_1
- Original parent: 9ed02628-d33c-493d-a7b6-1a1e0cf0ad72
- Milestone: architecture_survey

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Do NOT modify any source code files
- Deliver detailed report in handoff.md
- Send completion message to parent orchestrator

## Current Parent
- Conversation ID: 9ed02628-d33c-493d-a7b6-1a1e0cf0ad72
- Updated: 2026-10-10T14:04:23Z

## Investigation State
- **Explored paths**:
  - `layouts/shortcodes/book-download.html` & `buy-button.html`
  - `layouts/_partials/` (`head-css.html`, `scripts.html`, `custom/head-end.html`, `baseof.html`)
  - `content/docs/books/` (420 shortcode calls inspected across markdown files)
  - `assets/css/custom.css` & `themes/hextra/assets/js/theme.js`
  - `assets/js/framework-tools.js` (vanilla JS architecture patterns)
  - `data/books_metadata.json` (book catalog mappings)
  - `hugo.toml` (site config, parameters, multilingual setup)
- **Key findings**:
  - All 420 book downloads currently link directly to `https://dl.theminiceo.ir/<filename>.pdf`.
  - Filename/key in R2 can be extracted directly via Hugo `path.Base $url` or in JS dataset.
  - Theme is Hextra; uses `.dark` class toggle on `document.documentElement` + `localStorage['color-theme']`.
  - No existing QR code library; recommend lightweight vanilla SVG QR code generator in `assets/js/`.
  - Hugo Pipes (`resources.Get` | `minify` | `fingerprint`) provides robust asset bundling without Node build step.
  - Paywall component should be an interactive card replacing the direct download button, with instant verification via `POST /api/verify-payment`.
- **Unexplored areas**: None for frontend survey.

## Key Decisions Made
- Confirmed paywall shortcode parameter compatibility (`url`, `title`, `size`, `format`, `lang`).
- Outlined API contract for `/api/verify-payment` and `/api/config`.
- Formulated QR code rendering with vector SVG and high-contrast light container for dark/light themes.

## Artifact Index
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_1/DISPATCH.md` — Incoming task dispatch
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_1/BRIEFING.md` — Situational awareness
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_1/progress.md` — Liveness heartbeat
- `/Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_1/handoff.md` — Comprehensive survey report
