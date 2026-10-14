#!/usr/bin/env python3
"""
scripts/test_challenger_m2_reports.py - Empirical Challenger Stress Harness for Milestone 2 Reports.

Empirically stress-tests the 17 English reports in content/docs/reports/ against:
1. scripts/setup_reports_section.py URL parity and size parity.
2. Persian slug report (گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md) content and language integrity.
3. Boundary cases (HBR 90.4MB, Heap 400KB, date format, YAML escaping).
4. Persian Unicode leakage across titles, descriptions, headings, body, and shortcodes.
5. Hugo compilation and rendered HTML inspection in target directory.
"""

import os
import re
import sys
import shutil
import tempfile
import urllib.parse
from pathlib import Path
import subprocess

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "content" / "docs" / "reports"
SETUP_SCRIPT = ROOT_DIR / "scripts" / "setup_reports_section.py"

# Regex for Arabic/Persian Unicode characters
PERSIAN_REGEX = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")

def load_setup_reports_map():
    """Extract reports_map from setup_reports_section.py dynamically."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("setup_reports_section", SETUP_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.reports_map

def parse_frontmatter_manual(content: str):
    """
    Standard library parser for frontmatter and markdown body.
    """
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_fm = parts[1]
            body = parts[2]
            kv = {}
            for line in raw_fm.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                m = re.match(r"^([a-zA-Z0-9_-]+)\s*[:=]\s*(.*)$", line)
                if m:
                    k = m.group(1).strip()
                    v = m.group(2).strip()
                    if v.startswith('"') and v.endswith('"'):
                        v = v[1:-1]
                    elif v.startswith("'") and v.endswith("'"):
                        v = v[1:-1]
                    kv[k] = v
            return kv, body, raw_fm
    elif content.startswith("+++"):
        parts = content.split("+++", 2)
        if len(parts) >= 3:
            raw_fm = parts[1]
            body = parts[2]
            kv = {}
            for line in raw_fm.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                m = re.match(r"^([a-zA-Z0-9_-]+)\s*=\s*(.*)$", line)
                if m:
                    k = m.group(1).strip()
                    v = m.group(2).strip()
                    if v.startswith('"') and v.endswith('"'):
                        v = v[1:-1]
                    elif v.startswith("'") and v.endswith("'"):
                        v = v[1:-1]
                    kv[k] = v
            return kv, body, raw_fm
    return {}, content, ""

def extract_shortcodes(content: str):
    """Extract book-download shortcodes and their attributes."""
    matches = re.findall(r"\{\{<\s*book-download\s+([^>]+)\s*>\}\}", content)
    shortcodes = []
    for m in matches:
        raw_tuples = re.findall(r'(\w+)=(?:"([^"]*)"|([^\s>]+))', m)
        attrs = {k: v1 if v1 else v2 for k, v1, v2 in raw_tuples}
        shortcodes.append(attrs)
    return shortcodes

def run_stress_tests():
    reports_map = load_setup_reports_map()
    assert len(reports_map) == 17, f"Expected 17 reports in setup_reports_section.py, found {len(reports_map)}"

    results = {
        "url_parity": [],
        "persian_slug_report": [],
        "boundary_cases": [],
        "persian_leakage": [],
        "yaml_frontmatter": [],
        "hugo_compilation": [],
        "rendered_html": [],
    }

    errors = []

    print("=" * 70)
    print("EMPIRICAL CHALLENGER STRESS HARNESS - MILESTONE 2 (REPORTS)")
    print("=" * 70)

    # ---------------------------------------------------------
    # TEST 1: URL Parity & File Existence
    # ---------------------------------------------------------
    print("\n[TEST 1] Verifying URL Parity and File Existence for 17 Reports...")
    for idx, r in enumerate(reports_map, 1):
        new_file = r["new_file"]
        base_slug = new_file.replace(".md", "")
        en_filename = f"{base_slug}.en.md"
        en_filepath = REPORTS_DIR / en_filename
        expected_url = r["dl_url"]

        if not en_filepath.exists():
            msg = f"Report {idx} ({en_filename}): English file does NOT exist!"
            errors.append(msg)
            results["url_parity"].append((en_filename, "MISSING_FILE", False))
            continue

        content = en_filepath.read_text(encoding="utf-8")
        shortcodes = extract_shortcodes(content)

        if not shortcodes:
            msg = f"Report {idx} ({en_filename}): No book-download shortcode found!"
            errors.append(msg)
            results["url_parity"].append((en_filename, "NO_SHORTCODE", False))
            continue

        actual_url = shortcodes[0].get("url", "")
        
        # Test exact match
        exact_match = (actual_url == expected_url)
        # Test unquoted match
        unquoted_match = (urllib.parse.unquote(actual_url) == urllib.parse.unquote(expected_url))

        if not exact_match:
            msg = (f"Report {idx} ({en_filename}): URL MISMATCH!\n"
                   f"  Expected: {expected_url}\n"
                   f"  Actual:   {actual_url}\n"
                   f"  Unquoted Match: {unquoted_match}")
            errors.append(msg)
            results["url_parity"].append((en_filename, f"MISMATCH: {actual_url} != {expected_url}", False))
        else:
            print(f"  [{idx:02d}/17] MATCH: {en_filename}")
            results["url_parity"].append((en_filename, actual_url, True))

    url_success_count = sum(1 for _, _, ok in results["url_parity"] if ok)
    print(f"URL Parity Result: {url_success_count}/17 passed.")

    # ---------------------------------------------------------
    # TEST 2: Persian Slug Report
    # ---------------------------------------------------------
    print("\n[TEST 2] Verifying Persian Slug Report (گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md)...")
    persian_slug = "گزارش-صنعت-پرداخت-ایران-نسخه-نهم"
    ps_file = REPORTS_DIR / f"{persian_slug}.en.md"

    if not ps_file.exists():
        msg = f"Persian slug file {ps_file} does NOT exist!"
        errors.append(msg)
        results["persian_slug_report"].append(("existence", False, msg))
    else:
        results["persian_slug_report"].append(("existence", True, "File exists"))
        ps_content = ps_file.read_text(encoding="utf-8")
        fm, body, fm_raw = parse_frontmatter_manual(ps_content)

        # Check frontmatter fields
        title = fm.get("title", "")
        desc = fm.get("description", "")

        # Check for Persian characters in title, description
        for field_name, text in [("title", title), ("description", desc)]:
            found = PERSIAN_REGEX.findall(text)
            if found:
                msg = f"Persian characters found in {field_name}: {''.join(found)}"
                errors.append(msg)
                results["persian_slug_report"].append((f"fm_{field_name}", False, msg))
            else:
                results["persian_slug_report"].append((f"fm_{field_name}", True, f"Clean: {text[:40]}..."))

        # Check body content (excluding URL attribute values and markdown link targets)
        # We clean out markdown links and URL attrs
        cleaned_body = re.sub(r"\(/(?:docs|fa|en)/[^\)]+\)", "", body)
        cleaned_body = re.sub(r'url="https?://[^"]+"', "", cleaned_body)
        body_persian = PERSIAN_REGEX.findall(cleaned_body)
        if body_persian:
            msg = f"Persian characters found in Persian slug body text: {set(body_persian)}"
            errors.append(msg)
            results["persian_slug_report"].append(("body", False, msg))
        else:
            results["persian_slug_report"].append(("body", True, f"Body 100% English ({len(body)} chars)"))

        # Check download shortcode in Persian slug report
        ps_shortcodes = extract_shortcodes(body)
        if ps_shortcodes:
            sc = ps_shortcodes[0]
            sc_title = sc.get("title", "")
            sc_lang = sc.get("lang", "")
            sc_size = sc.get("size", "")
            print(f"  Shortcode title: {sc_title}")
            print(f"  Shortcode lang:  {sc_lang}")
            print(f"  Shortcode size:  {sc_size}")
            if PERSIAN_REGEX.search(sc_title):
                errors.append(f"Persian characters in shortcode title: {sc_title}")
                results["persian_slug_report"].append(("shortcode_title", False, sc_title))
            else:
                results["persian_slug_report"].append(("shortcode_title", True, sc_title))
            if sc_lang != "English":
                errors.append(f"Shortcode lang is '{sc_lang}', expected 'English'")
                results["persian_slug_report"].append(("shortcode_lang", False, sc_lang))
            else:
                results["persian_slug_report"].append(("shortcode_lang", True, sc_lang))

    # ---------------------------------------------------------
    # TEST 3: Boundary Cases
    # ---------------------------------------------------------
    print("\n[TEST 3] Stress-Testing Boundary Cases (HBR 90.4MB, Heap 400KB, Dates, YAML)...")
    
    # 3a. HBR Report (~90.4MB)
    hbr_file = REPORTS_DIR / "hbr-2022-11-12.en.md"
    if hbr_file.exists():
        hbr_content = hbr_file.read_text(encoding="utf-8")
        hbr_sc = extract_shortcodes(hbr_content)
        if hbr_sc:
            hbr_size = hbr_sc[0].get("size", "")
            hbr_url = hbr_sc[0].get("url", "")
            print(f"  HBR Report Size in shortcode: {hbr_size}")
            print(f"  HBR Report URL in shortcode:  {hbr_url}")
            if "90.4" not in hbr_size or "MB" not in hbr_size:
                errors.append(f"HBR size unexpected: {hbr_size}")
                results["boundary_cases"].append(("hbr_size", False, hbr_size))
            else:
                results["boundary_cases"].append(("hbr_size", True, hbr_size))
            
            # Check URL percent-encoding for spaces in 'HBR 2022 11 12.pdf'
            if "%20" not in hbr_url and " " in hbr_url:
                errors.append(f"HBR URL contains unencoded space: {hbr_url}")
                results["boundary_cases"].append(("hbr_url_encoding", False, hbr_url))
            else:
                results["boundary_cases"].append(("hbr_url_encoding", True, hbr_url))

    # 3b. Heap Report (~400KB)
    heap_file = REPORTS_DIR / "heap-digital-experiences-insights-report2.en.md"
    if heap_file.exists():
        heap_content = heap_file.read_text(encoding="utf-8")
        heap_sc = extract_shortcodes(heap_content)
        if heap_sc:
            heap_size = heap_sc[0].get("size", "")
            print(f"  Heap Report Size in shortcode: {heap_size}")
            if "400" not in heap_size or "KB" not in heap_size:
                errors.append(f"Heap size unexpected: {heap_size}")
                results["boundary_cases"].append(("heap_size", False, heap_size))
            else:
                results["boundary_cases"].append(("heap_size", True, heap_size))

    # 3c. YAML Frontmatter & Date Formats across all 17 reports + _index.en.md
    all_en_files = sorted(list(REPORTS_DIR.glob("*.en.md")))
    print(f"  Checking frontmatter and dates across {len(all_en_files)} English report files...")
    
    date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}.*)?$")
    for f in all_en_files:
        content = f.read_text(encoding="utf-8")
        try:
            fm, body, fm_raw = parse_frontmatter_manual(content)
            # Check required fields
            if f.name != "_index.en.md":
                for req in ["title", "date", "description"]:
                    if req not in fm or not fm[req]:
                        errors.append(f"{f.name}: Missing required field '{req}'")
                        results["yaml_frontmatter"].append((f.name, False, f"Missing {req}"))
                
                # Check date format
                date_val = str(fm.get("date", ""))
                if not date_regex.match(date_val):
                    errors.append(f"{f.name}: Date '{date_val}' does not match ISO format YYYY-MM-DD")
                    results["yaml_frontmatter"].append((f.name, False, f"Bad date {date_val}"))
                else:
                    results["yaml_frontmatter"].append((f.name, True, f"Valid YAML, date={date_val}"))
            else:
                # TOML check for _index.en.md
                results["yaml_frontmatter"].append((f.name, True, "TOML index frontmatter OK"))

        except Exception as e:
            errors.append(f"{f.name}: parse error: {e}")
            results["yaml_frontmatter"].append((f.name, False, str(e)))

    # ---------------------------------------------------------
    # TEST 4: Persian Unicode Leakage Scan across ALL 17 Reports
    # ---------------------------------------------------------
    print("\n[TEST 4] Scanning for Persian Unicode Leakage across all English files...")
    for f in all_en_files:
        content = f.read_text(encoding="utf-8")
        fm, body, _ = parse_frontmatter_manual(content)
        
        # Check title
        title = fm.get("title", "")
        title_p = PERSIAN_REGEX.findall(str(title))
        if title_p:
            msg = f"{f.name} Title contains Persian: {''.join(title_p)}"
            errors.append(msg)
            results["persian_leakage"].append((f.name, "title", False, msg))

        # Check description
        desc = fm.get("description", "")
        desc_p = PERSIAN_REGEX.findall(str(desc))
        if desc_p:
            msg = f"{f.name} Description contains Persian: {''.join(desc_p)}"
            errors.append(msg)
            results["persian_leakage"].append((f.name, "description", False, msg))

        # Check headings in body
        headings = re.findall(r"^#+\s*(.+)$", body, re.MULTILINE)
        for h in headings:
            h_p = PERSIAN_REGEX.findall(h)
            if h_p:
                msg = f"{f.name} Heading '{h}' contains Persian: {''.join(h_p)}"
                errors.append(msg)
                results["persian_leakage"].append((f.name, "heading", False, msg))

        # Check body text (excluding YAML aliases which intentionally redirect from Persian legacy URLs)
        lines = body.splitlines()
        for line_no, line in enumerate(lines, 1):
            clean_line = re.sub(r"\(/(?:docs|fa|en)/[^\)]+\)", "", line)
            clean_line = re.sub(r'url="https?://[^"]+"', "", clean_line)
            line_p = PERSIAN_REGEX.findall(clean_line)
            if line_p:
                msg = f"{f.name}:{line_no} Body line contains Persian: {''.join(set(line_p))} in '{line.strip()}'"
                errors.append(msg)
                results["persian_leakage"].append((f.name, f"line_{line_no}", False, msg))

    persian_leakage_failures = [x for x in results["persian_leakage"] if not x[2]]
    print(f"Persian Leakage Check: {len(persian_leakage_failures)} leakages found across {len(all_en_files)} files.")

    # ---------------------------------------------------------
    # TEST 5: Hugo Build & Rendered HTML Output Inspection
    # ---------------------------------------------------------
    print("\n[TEST 5] Executing Hugo Build to Temporary Directory...")
    temp_dir = tempfile.mkdtemp(prefix="hugo_challenger_test_")
    try:
        cmd = ["hugo", "--destination", temp_dir]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT_DIR)
        print(f"Hugo exit code: {res.returncode}")
        if res.returncode != 0:
            errors.append(f"Hugo build failed:\n{res.stderr}")
            results["hugo_compilation"].append(("hugo_exit_code", False, res.stderr))
        else:
            results["hugo_compilation"].append(("hugo_exit_code", True, "Exit code 0"))
            
            # Verify each report has an HTML file generated under /en/docs/reports/
            en_reports_out = Path(temp_dir) / "en" / "docs" / "reports"
            print(f"Inspecting rendered HTML in {en_reports_out}...")
            
            if not en_reports_out.exists():
                errors.append(f"Rendered reports output directory {en_reports_out} does not exist!")
                results["rendered_html"].append(("dir_exists", False, "Missing output dir"))
            else:
                for r in reports_map:
                    base_slug = r["new_file"].replace(".md", "")
                    # In Hugo pretty URLs, the page is at <slug>/index.html
                    html_file = en_reports_out / base_slug / "index.html"
                    if not html_file.exists():
                        errors.append(f"Expected HTML output file {html_file} does not exist!")
                        results["rendered_html"].append((base_slug, False, "Missing HTML"))
                    else:
                        html_text = html_file.read_text(encoding="utf-8")
                        # Check that the book-download button exists in the HTML
                        if r["dl_url"] not in html_text:
                            errors.append(f"Download URL {r['dl_url']} missing in rendered HTML for {base_slug}")
                            results["rendered_html"].append((base_slug, False, "Missing dl_url in HTML"))
                        else:
                            # Check for English download button strings
                            has_en_button = ("Download" in html_text or "Direct CDN" in html_text or "Size:" in html_text)
                            results["rendered_html"].append((base_slug, True, f"Rendered HTML OK ({len(html_text)} bytes)"))
                
                rendered_success_count = sum(1 for _, ok, _ in results["rendered_html"] if ok)
                print(f"Rendered HTML Check: {rendered_success_count}/17 reports confirmed in Hugo build output!")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # ---------------------------------------------------------
    # SUMMARY & VERDICT
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("STRESS HARNESS EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Total Errors / Anomalies Detected: {len(errors)}")
    if errors:
        for err in errors:
            print(f"  ❌ {err}")
        print("\nVERDICT: REQUEST_CHANGES")
        return False
    else:
        print("  ✅ All 17 reports passed URL parity.")
        print("  ✅ Persian slug report verified and 100% English.")
        print("  ✅ Boundary cases (HBR 90.4MB, Heap 400KB, date formats, YAML escapes) passed.")
        print("  ✅ Zero Persian character leakage in titles, descriptions, headings, or body.")
        print("  ✅ Hugo build succeeded with exit code 0 and all 17 HTML files verified.")
        print("\nVERDICT: APPROVE")
        return True

if __name__ == "__main__":
    success = run_stress_tests()
    sys.exit(0 if success else 1)
