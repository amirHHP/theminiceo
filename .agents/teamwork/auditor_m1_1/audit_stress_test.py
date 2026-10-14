#!/usr/bin/env python3
"""
Adversarial Stress Test Suite for auditor_m1_1.
Tests verify_localization.py against hostile inputs and verifies behavior.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add project root and scripts dir
PROJECT_ROOT = Path("/Users/sotoon/personal/theminiceo")
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from verify_localization import audit, is_excluded, parse_frontmatter, main

def run_tests():
    print("=== STARTING ADVERSARIAL AUDIT CHECKS ===")
    
    # 1. Stress test: Persian in English Title
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
        (tmp / "test.en.md").write_text("---\ntitle: 'English with فارسی'\ndate: '2026-01-01'\n---\nValid body text longer than fifty bytes threshold here.", encoding="utf-8")
        res = audit(content_dir=str(tmp))
        assert not res.is_success, "Should fail when English title has Persian"
        assert any(e.issue_type == "persian_in_title" for e in res.frontmatter_errors), "Missing persian_in_title error"
        print("PASS: Persian in English title detected correctly.")

    # 2. Stress test: Undersized file (< 50 bytes)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
        (tmp / "test.en.md").write_text("---\ntitle: 'T'\n---", encoding="utf-8") # < 50 bytes
        res = audit(content_dir=str(tmp))
        assert not res.is_success, "Should fail when English file is undersized"
        assert any(e.issue_type == "undersized_file" for e in res.empty_files), "Missing undersized_file error"
        print("PASS: Undersized file (<50 bytes) detected correctly.")

    # 3. Stress test: Empty body on book
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        bdir = tmp / "docs" / "books"
        bdir.mkdir(parents=True)
        (bdir / "book1.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
        (bdir / "book1.en.md").write_text("---\ntitle: 'Book 1'\ndate: '2026-01-01'\ndescription: 'Description'\n---\n", encoding="utf-8")
        res = audit(content_dir=str(tmp))
        assert not res.is_success, "Should fail when book body is empty"
        assert any(e.issue_type == "empty_body" for e in res.empty_files), "Missing empty_body error"
        print("PASS: Empty markdown body detected correctly.")

    # 4. Stress test: Decomposed Unicode combining characters
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # Decomposed combining madda: U+0627 + U+0653
        slug = "خلق-محصولات-آینده-راهنمای-هوش-مصنوعی"
        (tmp / f"{slug}.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
        (tmp / f"{slug}.en.md").write_text("---\ntitle: 'Future Products'\ndate: '2026-01-01'\n---\nValid body text longer than fifty bytes threshold here.", encoding="utf-8")
        res = audit(content_dir=str(tmp))
        assert res.is_success, f"Should succeed with decomposed combining character slug, got {res.total_issues} issues"
        print("PASS: Decomposed Unicode combining characters paired cleanly.")

    # 5. Stress test: Clean directory produces exit code 0 and SUCCESS in stdout
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "page.md").write_text("---\ntitle: 'صفحه'\n---", encoding="utf-8")
        (tmp / "page.en.md").write_text("---\ntitle: 'Page'\ndate: '2026-01-01'\n---\nValid body text longer than fifty bytes threshold here.", encoding="utf-8")
        cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "verify_localization.py"), "--root", str(tmp)]
        p = subprocess.run(cmd, capture_output=True, text=True)
        assert p.returncode == 0, f"Clean directory should exit 0, got {p.returncode}"
        assert "SUCCESS" in p.stdout, "Clean output should contain 'SUCCESS'"
        assert "100%" in p.stdout, "Clean output should contain '100%'"
        print("PASS: Clean directory exits 0 with SUCCESS and 100% banner.")

    # 6. Stress test: Strict mode flags placeholders
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "page.md").write_text("---\ntitle: 'صفحه'\n---", encoding="utf-8")
        (tmp / "page.en.md").write_text("---\ntitle: 'Page'\ndate: '2026-01-01'\n---\nValid body text longer than fifty bytes threshold here. TODO: add more content.", encoding="utf-8")
        res = audit(content_dir=str(tmp), strict=True)
        assert not res.is_success, "Strict mode must flag TODO placeholder"
        assert any(e.issue_type == "placeholder_text" for e in res.other_errors), "Missing placeholder_text error"
        print("PASS: Strict mode flags TODO placeholder.")

    # 7. Stress test: Frontmatter YAML edge cases (quotes with colons, inline lists)
    yaml_edge = """---
title: "Product: Architecture & Strategy"
date: "2026-01-01"
categories: ["Books", "Tech"]
tags:
  - architecture
  - strategy
---
Body text here with a divider.

---

More body text after horizontal rule.
"""
    fmt, kv, raw, body = parse_frontmatter(yaml_edge)
    assert fmt == "yaml"
    assert kv.get("title") == "Product: Architecture & Strategy", f"Failed parsing quoted colon: {kv.get('title')}"
    assert kv.get("categories") == ["Books", "Tech"], f"Failed parsing inline array: {kv.get('categories')}"
    assert kv.get("tags") == ["architecture", "strategy"], f"Failed parsing block list: {kv.get('tags')}"
    assert "More body text after horizontal rule." in body, "Failed preserving body with horizontal rule"
    print("PASS: Frontmatter parser handles colons in quotes, inline lists, block lists, and horizontal rules.")

    print("=== ALL ADVERSARIAL AUDIT CHECKS PASSED ===")

if __name__ == "__main__":
    run_tests()
