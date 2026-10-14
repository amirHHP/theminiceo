## 2026-10-10T14:47:12Z
You are worker_m3_1.
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/worker_m3_1
Your parent is orchestrator_2 (ID: 1390bbb4-2296-47f7-8f97-a4b7fde0fc3d).

Objective: Implement Milestone 3: Create `scripts/generate_english_books.py`, generate all 390 English books in `content/docs/books/*.en.md`, retrofit the 17 legacy .en.md books, retrofit what-is-product-managment.en.md, and upgrade `content/docs/books/_index.en.md`.

Files to read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (MANDATORY) § R2
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_2/PROJECT.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m3_1/handoff.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m3_2/handoff.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m3_1/handoff.md
- /Users/sotoon/personal/theminiceo/data/books_metadata.json
- /Users/sotoon/personal/theminiceo/scripts/curated_books_data.py
- /Users/sotoon/personal/theminiceo/scripts/test_localization_e2e.py

File write ownership:
- scripts/generate_english_books.py
- content/docs/books/*.en.md (390 generated + 17 retrofitted + _index.en.md)
- content/docs/1-what-is-product-managment/what-is-product-managment.en.md

Detailed Requirements:
1. Implement `scripts/generate_english_books.py` based on the architectural blueprints and data models in `explorer_m3_2/handoff.md` and specifications in `spec_miner_m3_1/handoff.md`.
2. Generate all 390 missing English books (`content/docs/books/<slug>.en.md`) with 100% adherence to the 7-part gold standard:
   - Frontmatter: `title`, `date`, `description`, `tags`, `categories: ["Books"]`.
   - Specifications table: `| Book Specification | Details |` (Author, Category, Pages, Format: "PDF", File Size, Target Audience).
   - Core premise: `### 📖 About the Book & Core Premise`.
   - Takeaways: `### 🔑 Key Takeaways & Core Frameworks` (4-5 bullet points).
   - 2026 relevance: `### 💡 Why This Book Matters in 2026`.
   - Target audience: `### 🎯 Who Should Read This Book?`.
   - Download shortcode: `{{< book-download url="..." title="..." size="..." format="PDF" lang="English" >}}` with valid CDN URL from `data/books_metadata.json`.
3. Persian slug book: Pair `content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md` with `content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.en.md` using the exact NFD decomposed combining madda. Content must be 100% English.
4. Retrofit the 17 legacy `.en.md` book files: Add `description:`, `categories: ["Books"]`, specifications table, `###` headings, and download shortcode.
5. Retrofit `content/docs/1-what-is-product-managment/what-is-product-managment.en.md`: Add missing `description:` frontmatter field so `verify_localization.py --strict` passes with 0 issues repo-wide.
6. Upgrade `content/docs/books/_index.en.md`: Populate body with the 9 curated showcase cards and category breakdown matching `_index.md`.
7. Nuance checks:
   - For `triggers-creating-behavior-that-lasts...`, ensure "PDF" appears in the specs table/content for T3.3 assertion pass.
   - For sub-megabyte file sizes, ensure explicit "MB" representation (e.g., `0.8 MB`).
   - Map all 390 books to the 8 standard categories (Leadership, Product Strategy, Product Discovery, Analytics & Data, UX & Design, Engineering & Tech, Agile & Delivery, Growth & Marketing).
   - Zero Persian text in English fields (`title`, `description`, headings, body).
   - Zero placeholder tokens (`TODO`, `FIXME`, `TBD`, `lorem ipsum`).
8. Verification commands:
   - `python3 scripts/generate_english_books.py`
   - `python3 scripts/verify_localization.py --strict`
   - `python3 scripts/test_localization_e2e.py -v --tier 1`
   - `python3 scripts/test_localization_e2e.py -v --tier 2`
   - `python3 scripts/test_localization_e2e.py -v --tier 3`
   - `python3 scripts/test_localization_e2e.py -v --tier 4`
   - `hugo --renderToMemory`
   Document all outputs in your handoff report.
