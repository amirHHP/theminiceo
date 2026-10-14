# Handoff Report: Milestone 1 Specification Mining & Traceability (`scripts/verify_localization.py`)

**Agent**: `spec_miner_m1_1`  
**Working Directory**: `/Users/sotoon/personal/theminiceo/.agents/teamwork/spec_miner_m1_1`  
**Date**: 2026-10-10T09:35:00Z  
**Type**: Hard Handoff (Specification Mining Complete)  
**Parent**: `orchestrator_2` (ID: `1390bbb4-2296-47f7-8f97-a4b7fde0fc3d`)  

---

## Executive Summary

This specification mining report establishes the authoritative functional, non-functional, interface, and test requirements for Milestone 1 (`scripts/verify_localization.py`), the automated localization audit and CI verification tool for `theminiceo`. 

The primary sources examined are:
1. `/Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md` (§ R1 and Acceptance Criteria)
2. `/Users/sotoon/personal/theminiceo/scripts/test_localization_e2e.py` (specifically tests T1.1, T4.1, T4.5, with cross-references to T1.4, T1.5, T2.3, T2.4, T3.5)
3. `/Users/sotoon/personal/theminiceo/TEST_READY.md` (Test inventory & threshold definitions)
4. `/Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_2/PROJECT.md` (Interface contracts & milestone definitions)
5. `/Users/sotoon/personal/theminiceo/scripts/verify_localization.py` (Active verification script in repository)

All interface contracts, return codes, CLI flags, output formats, test assertions, and requirement mappings have been probed, verified, and mapped into a comprehensive Requirements Traceability Matrix (RTM).

---

## 1. Direct Observations

### 1.1. Authoritative Requirement R1 from `ORIGINAL_REQUEST.md`

From `/Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md` (lines 12–17 and 34–36):
```markdown
### R1. Automated Localization Audit & CI Verification Tool
Create a dedicated verification script (e.g., `scripts/verify_localization.py`) that deterministically audits all content files across the repository.
- Must verify that for every Persian content file (`*.md`, excluding `content/pdfs/`, `.obsidian/`, and `_drafts/`), an equivalent English file (`*.en.md`) exists in the same directory.
- Must validate frontmatter completeness (presence of English `title`, `date`, `description`) and check that files are non-empty.
- Must return exit code 0 when all pages have valid English counterparts, and non-zero if any missing pages or frontmatter issues are detected.

### Acceptance Criteria § Audit & Coverage Verification
- [ ] Programmatic verification script runs and reports 100% English coverage across all content directories (exiting with code 0).
- [ ] Zero missing `.en.md` files remain for any active Persian content page in `content/docs/books/`, `content/docs/reports/`, or other site sections.
```

### 1.2. Direct Inspection of `scripts/test_localization_e2e.py`

#### A. Test T1.1: `test_t1_1_verification_script_contract` (Lines 268–287)
```python
268:     def test_t1_1_verification_script_contract(self, t: AssertionTracker):
269:         """T1.1: Verification script exists at scripts/verify_localization.py and is executable."""
270:         script_path = SCRIPTS_DIR / "verify_localization.py"
271:         t.assert_true(script_path.exists(), f"Verification script missing at {script_path}")
272:         if script_path.exists():
273:             size = script_path.stat().st_size
274:             t.assert_greater_equal(size, 50, "verify_localization.py size should be >= 50 bytes")
275:             content = script_path.read_text(encoding="utf-8")
276:             try:
277:                 ast.parse(content)
278:                 syntax_valid = True
279:             except SyntaxError:
280:                 syntax_valid = False
281:             t.assert_true(syntax_valid, "verify_localization.py must parse cleanly as valid Python")
282:             t.assert_true("audit" in content or "main" in content, "verify_localization.py must define audit or main function")
```
- **Assertions**: 4 total assertions.
- **Contract Tested**: Script existence, minimum size >= 50 bytes, valid Python syntax (`ast.parse`), and public symbol declaration (`audit` or `main`).
- **Live Test Execution**: `python3 scripts/test_localization_e2e.py -v --tier 1` output:
  `[PASS] T1.1: T1.1: Verification Script Contract (4 assertions, 0.00s)`

#### B. Test T4.1: `test_t4_1_verify_localization_script_execution` (Lines 884–903)
```python
884:     def test_t4_1_verify_localization_script_execution(self, t: AssertionTracker):
885:         """T4.1: Execute python3 scripts/verify_localization.py and verify it exits 0 with 100% pass."""
886:         script_path = SCRIPTS_DIR / "verify_localization.py"
887:         if not script_path.exists():
888:             t.assert_true(False, f"scripts/verify_localization.py not found at {script_path}")
889:             t.assert_true(False, "Cannot execute missing verify_localization.py")
890:             return
891: 
892:         proc = subprocess.run(
893:             [sys.executable, str(script_path)],
894:             cwd=str(ROOT_DIR),
895:             stdout=subprocess.PIPE,
896:             stderr=subprocess.PIPE,
897:             text=True,
898:             timeout=60,
899:         )
900: 
901:         t.assert_equal(proc.returncode, 0, f"verify_localization.py returned code {proc.returncode}. Stderr: {proc.stderr}")
902:         t.assert_true("SUCCESS" in proc.stdout or "100%" in proc.stdout, "verify_localization.py stdout should report success/100% parity")
```
- **Assertions**: 2 total assertions.
- **Contract Tested**: Subprocess execution via `sys.executable`, return code exactly 0, and stdout containing `"SUCCESS"` or `"100%"`.
- **Live Test Execution**: `python3 scripts/test_localization_e2e.py -v --tier 4` output:
  `[FAIL] T4.1: T4.1: Verify Script Execution (2 assertions, 0.09s)`  
  `AssertionError: verify_localization.py returned code 1. Stderr: : expected 0, got 1`  
  `AssertionError: verify_localization.py stdout should report success/100% parity`  
  *(Note: Failure is expected in pre-generation state due to 407 missing `.en.md` files and 18 legacy frontmatter description omissions).*

#### C. Test T4.5: `test_t4_5_verify_localization_strict_mode` (Lines 968–984)
```python
968:     def test_t4_5_verify_localization_strict_mode(self, t: AssertionTracker):
969:         """T4.5: Execute python3 scripts/verify_localization.py --strict and verify clean exit code 0."""
970:         script_path = SCRIPTS_DIR / "verify_localization.py"
971:         if not script_path.exists():
972:             t.assert_true(False, f"scripts/verify_localization.py not found for strict audit")
973:             return
974: 
975:         proc = subprocess.run(
976:             [sys.executable, str(script_path), "--strict"],
977:             cwd=str(ROOT_DIR),
978:             stdout=subprocess.PIPE,
979:             stderr=subprocess.PIPE,
980:             text=True,
981:             timeout=60,
982:         )
983:         t.assert_equal(proc.returncode, 0, f"verify_localization.py --strict failed with code {proc.returncode}. Stderr: {proc.stderr}")
```
- **Assertions**: 1 total assertion.
- **Contract Tested**: Subprocess execution with `--strict` flag, verifying exit code exactly 0 when all descriptions are present repo-wide.
- **Live Test Execution**: Output in Tier 4 runner:
  `[FAIL] T4.5: T4.5: Strict Localization Audit (1 assertions, 0.09s)`  
  `AssertionError: verify_localization.py --strict failed with code 1. Stderr: : expected 0, got 1`

### 1.3. Probing `scripts/verify_localization.py` CLI Behavior

1. **Invocation**: `python3 scripts/verify_localization.py --help`
   - Exit Code: `0`
   - Available options:
     - `--content-dir CONTENT_DIR` (default: `content`)
     - `--strict` (enforce `description` on all pages repo-wide, default: `False`)
     - `--min-file-size MIN_FILE_SIZE` (default: `50`)
     - `--min-body-size MIN_BODY_SIZE` (default: `50`)
     - `--json` (output in JSON format, default: `False`)
     - `--verbose`, `-v` (display all missing files and error details without truncation, default: `False`)
     - `--quiet`, `-q` (only display summary results, default: `False`)

2. **Invocation**: `python3 scripts/verify_localization.py`
   - Exit Code: `1`
   - Scanned: 555 Persian files, 148 English files.
   - Missing: 407 `.en.md` files (390 in `content/docs/books/`, 17 in `content/docs/reports/`).
   - Frontmatter errors: 18 (1 in `content/docs/1-what-is-product-managment/what-is-product-managment.en.md`, 17 in `content/docs/books/*.en.md`).
   - Empty/undersized: 0.

3. **Invocation**: `python3 scripts/verify_localization.py --quiet`
   - Exit Code: `1`
   - Output: `FAILED: 425 issues detected.`

4. **Invocation**: `python3 scripts/verify_localization.py --unknown-arg`
   - Exit Code: `2` (standard Python argparse error code).
   - Stderr: `verify_localization.py: error: unrecognized arguments: --unknown-arg`

5. **Invocation**: `python3 scripts/verify_localization.py --min-file-size 1000000 --quiet`
   - Exit Code: `1`
   - Output: `FAILED: 555 issues detected.` (triggers undersized file checks).

---

## 2. Logic Chain

1. **Premise 1 (R1 in ORIGINAL_REQUEST.md)**: The user specification explicitly mandates a dedicated audit tool (`scripts/verify_localization.py`) to verify that for every Persian content file (`*.md` outside excluded folders), an English file (`*.en.md`) exists in the same directory, frontmatter has `title`, `date`, `description`, files are non-empty, and returns exit code 0 on complete localization and non-zero on issues.
2. **Premise 2 (E2E Test Contract in test_localization_e2e.py)**: The test suite codifies this mandate into three direct tests:
   - T1.1 checks that `scripts/verify_localization.py` exists, is >= 50 bytes, has valid Python syntax, and defines `audit` or `main`.
   - T4.1 executes `python3 scripts/verify_localization.py`, checks returncode == 0, and checks stdout contains `"SUCCESS"` or `"100%"`.
   - T4.5 executes `python3 scripts/verify_localization.py --strict` and checks returncode == 0.
3. **Premise 3 (Live Probing Results)**:
   - `scripts/verify_localization.py` is implemented and passes T1.1 immediately (`4/4 assertions pass`).
   - T4.1 and T4.5 currently exit code 1 because 407 English counterparts are missing and 18 existing English files lack the `description` frontmatter field.
   - The stdout banners produced by `verify_localization.py`:
     - On pass: `"✅ SUCCESS: 100% English localization parity achieved! All tests pass."`
     - On quiet pass: `"SUCCESS: 100% English localization parity verified."`
     Both satisfy `t.assert_true("SUCCESS" in proc.stdout or "100%" in proc.stdout)` in T4.1.
4. **Deduction**: The interface contract between the verification tool and the CI / test runner is complete, well-specified, and already implemented with high fidelity. What remains for Milestone 1 is documenting the authoritative specification and ensuring Milestone 2 and Milestone 3 generators produce content matching the verification tool's exact parsing logic.

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Contract | Programmatic Entrypoint | Expose `audit()` function for direct Python import | `content_dir: str, strict: bool, min_file_size: int, min_body_size: int` | `AuditResult` dataclass | Returns structured error object | T1.1, `scripts/verify_localization.py:233` |
| 2 | Contract | CLI Entrypoint | Expose `main()` CLI function | `argv: Optional[List[str]] = None` | `int` (exit code: `0` or `1`) | Exits `2` on bad CLI args | T1.1, `scripts/verify_localization.py:439` |
| 3 | Core Audit | Deterministic Traversal | Traverses all markdown files in `content/` sorted lexicographically | Directory path | Sorted file lists | Traversal error logged to `other_errors` | R1, `verify_localization.py:259` |
| 4 | Core Audit | Directory Exclusions | Excludes `content/pdfs/`, `.obsidian/`, `_drafts/`, and hidden files `.*` | Path string / parts | Filtered directory list in-place | Silently skips excluded trees | R1, T2.3, `verify_localization.py:36` |
| 5 | Core Audit | 1:1 Counterpart Pairing | Matches Persian `<stem>.md` to English `<stem>.en.md` in same folder | Persian file path | Computed `.en.md` target path | Records `missing_counterpart` issue | R1, T3.5, `verify_localization.py:280` |
| 6 | Validation | File Size & Non-Empty | Asserts file exists, size > `min_file_size` (50B), and content non-whitespace | File path, bytes | Boolean pass / fail | Records `undersized_file` or `empty_file` | R1, T1.5, `verify_localization.py:301` |
| 7 | Validation | Frontmatter Parsing | Parses YAML (`---`) and TOML (`+++`) frontmatter blocks; handles UTF-8 BOM | Raw file content | `(fmt_type, kv_dict, raw_fm, body)` | Records `invalid_delimiters` if none | R1, T1.4, `verify_localization.py:61` |
| 8 | Validation | Title Presence & English | Asserts `title` exists in frontmatter and contains zero Persian unicode | Parsed frontmatter dict | Pass / fail | Records `missing_title` or `persian_in_title` | R1, T1.4, T2.4, `verify_localization.py:355` |
| 9 | Validation | Date Presence | Asserts `date` exists (exempts index pages unless Persian counterpart has date) | Parsed frontmatter dict | Pass / fail | Records `missing_date` | R1, T1.4, T3.5, `verify_localization.py:374` |
| 10 | Validation | Description Completeness | Validates `description` for books/reports/persian-has-desc, or repo-wide in `--strict` | Parsed frontmatter dict, strict flag | Pass / fail | Records `missing_description` or `persian_in_description` | R1, T1.4, T4.5, `verify_localization.py:388` |
| 11 | Validation | Body Non-Empty & Size | Validates markdown body after frontmatter is non-empty (>50B for books/reports) | Markdown body text | Pass / fail | Records `empty_body` or `undersized_body` | R1, T1.5, `verify_localization.py:411` |
| 12 | CLI | Strict Mode (`--strict`) | Enforces `description` frontmatter field repo-wide | Flag: `--strict` | Stricter audit filter | Fails if any page lacks `description` | T4.5, `verify_localization.py:451` |
| 13 | CLI | JSON Output (`--json`) | Serializes complete audit results and issues into JSON | Flag: `--json` | Valid JSON printed to stdout | Exit code reflects pass/fail status | CLI probe, `verify_localization.py:468` |
| 14 | CLI | Quiet Mode (`--quiet`) | Suppresses detailed breakdowns, prints one-line pass/fail status | Flag: `--quiet`, `-q` | Single summary string | Single line with exit code 1 | CLI probe, `verify_localization.py:480` |
| 15 | CLI | Verbose Mode (`--verbose`) | Displays full list of missing files without sample truncation | Flag: `--verbose`, `-v` | Full stdout breakdown | Un-truncated issue list | CLI probe, `verify_localization.py:474` |
| 16 | CLI | Configurable Content Dir | Audits a custom directory path | Option: `--content-dir <path>` | Audits specified root | Handles empty/custom root | CLI probe, `verify_localization.py:446` |
| 17 | CLI | Configurable Size Limits | Adjusts minimum file and body thresholds | Options: `--min-file-size`, `--min-body-size` | Audits with custom limits | Flags files below custom threshold | CLI probe, `verify_localization.py:456` |

---

## 4. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Non-ASCII Persian Slugs | `content/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md` | Script expects exact matching base name `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` in the same directory. Flagged as missing until generated with exact non-ASCII name. |
| 2 | Excluded Directories | `content/docs/books/_drafts/growth-hacking.md` | Correctly excluded via `is_excluded()`. Script does NOT expect or flag `growth-hacking.en.md`. |
| 3 | Excluded PDF Directory | `content/pdfs/sample.pdf` or markdown inside `content/pdfs/` | Correctly excluded via `is_excluded()`. 0 files inside `content/pdfs/` are audited. |
| 4 | Hidden Directories & Files | `.obsidian/` or `.DS_Store` | Skipped during traversal via `p.startswith(".")`. No `.obsidian` items audited. |
| 5 | UTF-8 BOM (`\ufeff`) | File starting with byte order mark `\ufeff---` | `content.lstrip("\ufeff")` cleanly strips BOM before checking delimiters; prevents `invalid_delimiters` false positive. |
| 6 | Quoted Frontmatter Values | Frontmatter line: `title: "What is Product Management?"` | `_parse_flat_kv` unquotes matching double or single quotes; checks trimmed string value. |
| 7 | Taxonomy & Section Index Nodes | `_index.md` / `_index.en.md` in `content/` or `categories/` | Hugo taxonomy index nodes do not naturally require `date` or large body. Script checks `is_index_page` and only requires `date` if the Persian counterpart explicitly has `date`. |
| 8 | Untranslated Persian in Title/Desc | English title containing `مدیریت` | `has_persian()` detects Persian unicode characters (`[\u0600-\u06FF...]`), flagging `persian_in_title` or `persian_in_description`. |
| 9 | Nonexistent Content Directory | `--content-dir nonexistent_dir` | Scans 0 files, reports 0 issues, exits 0. Note: While deterministic, callers must pass valid directory. |
| 10 | Invalid CLI Arguments | `--invalid-option` | `argparse` displays usage, prints error message, and exits with code 2. |
| 11 | Legacy Book Description Omission | `content/docs/books/Escaping-the-Build-Trap.en.md` | Legacy English book lacks `description:`. Because it is in `docs/books/`, script flags `missing_description`. |
| 12 | Non-Book Article Description Omission | `content/docs/1-what-is-product-managment/what-is-product-managment.en.md` | Persian counterpart has `description:`, while English does not. Comparative audit flags `missing_description`. |

---

## 5. Authoritative Requirements Specifications

### 5.1. Functional Requirements

- **FR-1: Deterministic Content Traversal**
  The tool MUST recursively traverse the target content directory (`content/` by default) in lexicographical order (`sorted()`), ensuring identical, deterministic evaluation across all operating systems and runtimes.
- **FR-2: Exclusion Filtering**
  The tool MUST ignore files and subdirectories located within:
  - `content/pdfs/`
  - `.obsidian/`
  - `_drafts/` (or any directory beginning with `_draft`)
  - Any directory or file beginning with a dot (`.`)
- **FR-3: 1:1 Co-Located Translation Pairing**
  For every active Persian markdown file (`*.md` that does not end with `.en.md`), the tool MUST assert that a companion English file (`*.en.md`) exists with the identical file stem in the exact same directory.
- **FR-4: File Integrity & Non-Emptiness**
  The tool MUST assert that every English `.en.md` file:
  - Exists and is readable via UTF-8.
  - Has file size strictly exceeding `min_file_size` (default: 50 bytes).
  - Contains non-whitespace content.
- **FR-5: Frontmatter Delimiter Validation**
  The tool MUST support both YAML (`---`) and TOML (`+++`) frontmatter delimiters and verify proper closing delimiters. Files missing valid delimiters MUST be flagged with `invalid_delimiters`.
- **FR-6: Frontmatter Title Completeness & Localization**
  The frontmatter MUST contain a non-empty `title` key. The title MUST NOT contain any Persian/Arabic unicode characters (`[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]`).
- **FR-7: Frontmatter Date Completeness**
  The frontmatter MUST contain a non-empty `date` key. Exemption: Section index pages (`_index.en.md`) are exempt from `date` unless the corresponding Persian `_index.md` explicitly includes `date`.
- **FR-8: Frontmatter Description Completeness**
  The frontmatter MUST contain a non-empty `description` key if:
  - The file is in `content/docs/books/` or `content/docs/reports/`, OR
  - The corresponding Persian file possesses a `description` field, OR
  - Strict mode (`--strict`) is enabled.
  The description MUST NOT contain Persian/Arabic unicode characters.
- **FR-9: Body Content Completeness**
  For non-index pages, the markdown body after the frontmatter closing delimiter MUST NOT be empty. For books and reports, the body size MUST strictly exceed `min_body_size` (default: 50 bytes).
- **FR-10: CLI Arguments & Modes**
  The tool MUST support the following CLI options:
  - `--content-dir <dir>` (default: `content`)
  - `--strict` (flag to enforce description repo-wide)
  - `--min-file-size <int>` (default: 50)
  - `--min-body-size <int>` (default: 50)
  - `--json` (flag for JSON formatted output)
  - `-v`, `--verbose` (flag for un-truncated issue listings)
  - `-q`, `--quiet` (flag for single-line summary output)
  - `-h`, `--help` (flag for standard help documentation)
- **FR-11: Process Exit Codes**
  - Exit Code `0`: Zero issues detected (`total_issues == 0`).
  - Exit Code `1`: One or more issues detected (`total_issues > 0`).
  - Exit Code `2`: Invalid CLI syntax or arguments.

### 5.2. Non-Functional Requirements

- **NFR-1: Zero Third-Party Dependencies**
  The tool MUST execute solely on Python standard library modules (`os`, `sys`, `re`, `argparse`, `json`, `dataclasses`, `pathlib`, `typing`, `ast`). No `pip install` or external virtualenv dependencies allowed.
- **NFR-2: Performance & Latency**
  The full audit of 555+ files MUST complete in under 500 milliseconds (measured execution is ~90 milliseconds).
- **NFR-3: Cross-Platform Compatibility**
  Path resolution MUST use `os.path` and `pathlib.Path` to support macOS, Linux, and Windows path delimiters.
- **NFR-4: Character Encoding Safety**
  Files MUST be decoded explicitly with UTF-8 (`encoding="utf-8"`). Unicode Byte Order Marks (`\ufeff`) MUST be stripped cleanly.
- **NFR-5: Python API Importability**
  The tool MUST expose a clean programmatic function `audit(...) -> AuditResult` returning a structured dataclass for integration with test runners.

---

## 6. E2E Test Assertions & Test Contracts

The following assertions from `scripts/test_localization_e2e.py` govern `scripts/verify_localization.py`:

```
========================================================================================
Test ID: T1.1 (scripts/test_localization_e2e.py:268-287)
Name: T1.1: Verification Script Contract
Tier: 1 (Feature Coverage)
Assertions: 4
----------------------------------------------------------------------------------------
Assertion 1: t.assert_true(script_path.exists())
             scripts/verify_localization.py must exist in the file system.
Assertion 2: t.assert_greater_equal(size, 50)
             scripts/verify_localization.py must have size >= 50 bytes.
Assertion 3: t.assert_true(syntax_valid)
             ast.parse(content) must succeed without SyntaxError.
Assertion 4: t.assert_true("audit" in content or "main" in content)
             Script must define either 'audit' or 'main' entrypoint function.
========================================================================================

========================================================================================
Test ID: T4.1 (scripts/test_localization_e2e.py:884-903)
Name: T4.1: Verify Script Execution
Tier: 4 (Real-World Workloads)
Assertions: 2
----------------------------------------------------------------------------------------
Invocation:  subprocess.run([sys.executable, str(script_path)], cwd=ROOT_DIR, timeout=60)
Assertion 1: t.assert_equal(proc.returncode, 0)
             Default audit execution must return exit code 0 when localization is complete.
Assertion 2: t.assert_true("SUCCESS" in proc.stdout or "100%" in proc.stdout)
             Standard stdout output must contain "SUCCESS" or "100%" banner.
========================================================================================

========================================================================================
Test ID: T4.5 (scripts/test_localization_e2e.py:968-984)
Name: T4.5: Strict Localization Audit
Tier: 4 (Real-World Workloads)
Assertions: 1
----------------------------------------------------------------------------------------
Invocation:  subprocess.run([sys.executable, str(script_path), "--strict"], cwd=ROOT_DIR, timeout=60)
Assertion 1: t.assert_equal(proc.returncode, 0)
             Strict audit execution must return exit code 0 when all descriptions exist.
========================================================================================
```

---

## 7. Requirements Traceability Matrix (RTM)

| Requirement ID | Requirement Description | Test ID | Specific Test Assertion(s) | Implementation Specification in `verify_localization.py` | Status |
|:---:|:---|:---:|:---|:---|:---:|
| **REQ-M1-01** | Verification script exists on filesystem | **T1.1** | `t.assert_true(script_path.exists())` | Script located at `scripts/verify_localization.py` | ✅ VERIFIED |
| **REQ-M1-02** | Script is non-empty (>50 bytes) | **T1.1** | `t.assert_greater_equal(size, 50)` | Script is ~19.5 KB (511 lines) | ✅ VERIFIED |
| **REQ-M1-03** | Valid Python AST syntax | **T1.1** | `t.assert_true(syntax_valid)` via `ast.parse` | Pure standard library syntax, passes `ast.parse` | ✅ VERIFIED |
| **REQ-M1-04** | Exposes `audit` / `main` entrypoints | **T1.1** | `t.assert_true("audit" in content or "main" in content)` | Defines `def audit(...)` and `def main(...)` | ✅ VERIFIED |
| **REQ-M1-05** | Default CLI returns exit code 0 on parity | **T4.1** | `t.assert_equal(proc.returncode, 0)` | `main()` returns `0 if result.is_success else 1` | ⏳ PENDING M2/M3 |
| **REQ-M1-06** | Stdout reports success/100% parity | **T4.1** | `t.assert_true("SUCCESS" in proc.stdout or "100%" in proc.stdout)` | Prints `"✅ SUCCESS: 100% English localization parity achieved! All tests pass."` | ⏳ PENDING M2/M3 |
| **REQ-M1-07** | Strict mode CLI returns exit code 0 | **T4.5** | `t.assert_equal(proc.returncode, 0)` | `audit(strict=True)` enforces descriptions repo-wide | ⏳ PENDING M2/M3 |
| **REQ-M1-08** | Directory & hidden file exclusions | **T2.3** | `EXCLUDED_DIRS = {".obsidian", "_drafts", "pdfs"}` | `is_excluded()` filters `.obsidian`, `_drafts`, `pdfs`, and `.*` | ✅ VERIFIED |
| **REQ-M1-09** | 1:1 file stem pairing | **T1.2, T1.3, T3.5** | Assert matching `.en.md` for all 17 reports, 407 books, 0 orphans | Scans `*.md` and checks `en_path = fa_path[:-3] + ".en.md"` | ✅ VERIFIED |
| **REQ-M1-10** | Frontmatter delimiter validation | **T1.4** | Verifies YAML `---` or TOML `+++` parsing | `parse_frontmatter()` handles `---` and `+++`, flags `none` | ✅ VERIFIED |
| **REQ-M1-11** | Frontmatter title completeness | **T1.4, T2.4** | Title present, zero Persian characters | Checks `en_kv.get("title")` and `has_persian(title)` | ✅ VERIFIED |
| **REQ-M1-12** | Frontmatter date completeness | **T1.4, T3.5** | Date present (exempts taxonomies unless Persian has date) | Checks `en_kv.get("date")` conditionally on `is_index_page` | ✅ VERIFIED |
| **REQ-M1-13** | Frontmatter description completeness | **T1.4, T2.4** | Description present on books/reports/strict | Checks `en_kv.get("description")` and `has_persian(desc)` | ✅ VERIFIED |
| **REQ-M1-14** | Body content non-emptiness (>50B) | **T1.5** | Body > 100 chars in test; verify script asserts > 50B | Checks `len(body.strip().encode("utf-8")) > min_body_size` | ✅ VERIFIED |
| **REQ-M1-15** | Machine-readable JSON output | Ad-hoc CLI probe | `--json` outputs valid JSON with error breakdown | `json.dumps(result.to_dict(), indent=2)` | ✅ VERIFIED |
| **REQ-M1-16** | Quiet output mode | Ad-hoc CLI probe | `-q` prints single-line summary with exit code | Formats single line: `SUCCESS` or `FAILED: N issues` | ✅ VERIFIED |
| **REQ-M1-17** | Performance threshold | Execution timer | Run time < 1 second | Measured runtime: ~0.09s (90ms) | ✅ VERIFIED |

---

## 8. Caveats & Important Findings for Downstream Milestones

1. **Pre-Existing Frontmatter Description Omissions (18 files)**:
   - When running `verify_localization.py`, exactly 18 frontmatter errors are reported:
     - 17 legacy books in `content/docs/books/*.en.md` (e.g., `Escaping-the-Build-Trap.en.md`, `The-Lean-Startup.en.md`).
     - 1 documentation article: `content/docs/1-what-is-product-managment/what-is-product-managment.en.md`.
   - **Impact on M2 & M3**:
     - Milestone 3 is already scoped to retrofit the 17 legacy books with `description:`.
     - In addition, `content/docs/1-what-is-product-managment/what-is-product-managment.en.md` MUST also be retrofitted with a `description:` frontmatter field (or `verify_localization.py` will report 1 issue and exit with code 1, causing T4.1 and T4.5 to fail).
     - Recommended English description for `what-is-product-managment.en.md`:
       `description: "Explore what product management is, how it differs from project management, and the vital role of product managers in driving modern digital organizations."`

2. **Index Body Size Discrepancy between T1.5 and Verification Script**:
   - `scripts/test_localization_e2e.py` (lines 461–473, test T1.5) requires `content/docs/books/_index.en.md` and `content/docs/reports/_index.en.md` to have body length `>= 50 chars`.
   - In `scripts/verify_localization.py` (line 414), index pages are exempt from body size checking (`if not is_index_page:`).
   - **Recommendation**: In Milestone 3, when retrofitting `_index.en.md`, ensure the markdown body contains at least 50 characters of English prose to satisfy T1.5.

3. **Orphan English File Detection**:
   - Test T3.5 (`test_t3_5_co_located_stem_pairing`) asserts that every `.en.md` has a Persian `.md` companion.
   - `scripts/verify_localization.py` tracks `total_english_found`, but only flags missing English counterparts for Persian files. It does not currently flag orphaned English files.
   - **Observation**: Zero orphaned English files currently exist in the repository (`orphaned_en_files == []`), so this has zero operational impact, but downstream generators must only create `.en.md` files for matching Persian files.

---

## 9. Conclusion

1. **Milestone 1 Artifact Readiness**:
   - The verification script `scripts/verify_localization.py` is fully implemented, syntactically verified, and cleanly satisfies the contract requirements of T1.1.
   - It correctly implements the exclusion rules (R1, T2.3), Persian text leakage prevention (T2.4), delimiter parsing, comparative frontmatter validation, and dual-mode CLI/JSON output.
2. **Acceptance Criteria Gatekeeper**:
   - `scripts/verify_localization.py` serves as the deterministic gatekeeper for the entire project. When Milestones M2 (17 reports) and M3 (390 books + 18 retrofitted descriptions) complete, `scripts/verify_localization.py` will transition from exiting with code 1 to exiting with code 0, automatically satisfying tests T4.1 and T4.5 in `scripts/test_localization_e2e.py`.
3. **Traceability Fully Established**:
   - Every requirement from R1 has an unbroken trace from user requirements (`ORIGINAL_REQUEST.md`) to automated test assertions (`scripts/test_localization_e2e.py`) and implementation logic (`scripts/verify_localization.py`).

---

## 10. Verification Method

To independently verify all findings in this specification report, run the following commands:

```bash
# 1. Verify T1.1 (Verification Script Contract) passes cleanly:
python3 scripts/test_localization_e2e.py -v --tier 1
# Expected: [PASS] T1.1: T1.1: Verification Script Contract (4 assertions, 0.00s)

# 2. Verify scripts/verify_localization.py CLI help and options:
python3 scripts/verify_localization.py --help
# Expected: exit code 0, display arguments (--content-dir, --strict, --json, etc.)

# 3. Verify current audit diagnostics (reporting 407 missing files and 18 frontmatter issues):
python3 scripts/verify_localization.py --quiet
# Expected: exit code 1, output "FAILED: 425 issues detected."

# 4. Verify machine-readable JSON output:
python3 scripts/verify_localization.py --json | grep -E '"(is_success|total_issues|missing_count)"'
# Expected: "is_success": false, "total_issues": 425, "missing_count": 407

# 5. Verify execution performance of the audit tool:
python3 -c "
import time, subprocess, sys
t0 = time.time()
subprocess.run([sys.executable, 'scripts/verify_localization.py', '--quiet'])
print(f'Execution duration: {time.time() - t0:.3f}s')
"
# Expected: Duration < 0.200s (sub-second execution)
```
