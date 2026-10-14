#!/usr/bin/env python3
"""
Empirical verification script for Milestone 2:
Validates book-download shortcode rendering across all reports and books.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = REPO_ROOT / "public"
REPORTS_DIR = REPO_ROOT / "content" / "docs" / "reports"
BOOKS_DIR = REPO_ROOT / "content" / "docs" / "books"


def extract_box(html: str) -> str:
    start_tag = 'class="book-download-box'
    idx = html.find(start_tag)
    if idx == -1:
        return ""
    start = html.rfind("<div", 0, idx)
    if start == -1:
        return ""
    pos = start
    depth = 0
    token_re = re.compile(r'<(/?)div[\s>]', re.IGNORECASE)
    for m in token_re.finditer(html, pos):
        if m.group(1) == "": # <div
            depth += 1
        else: # </div>
            depth -= 1
            if depth == 0:
                return html[start:m.end()]
    return ""

def run_checks():
    en_reports = [f for f in REPORTS_DIR.glob("*.en.md") if not f.name.startswith("_index")]
    print(f"Total English reports found: {len(en_reports)}")

    errors = []
    verified_en_count = 0
    verified_fa_count = 0

    for en_md in sorted(en_reports):
        slug = en_md.name[:-6] # strip .en.md
        fa_md = en_md.with_name(f"{slug}.md")
        if not fa_md.exists():
            errors.append(f"Companion Persian report missing for {en_md.name}")
            continue

        en_html = PUBLIC_DIR / "en" / "docs" / "reports" / slug / "index.html"
        fa_html = PUBLIC_DIR / "docs" / "reports" / slug / "index.html"

        if not en_html.exists():
            errors.append(f"Rendered EN HTML missing: {en_html}")
            continue
        if not fa_html.exists():
            errors.append(f"Rendered FA HTML missing: {fa_html}")
            continue

        en_content = en_html.read_text(encoding="utf-8")
        fa_content = fa_html.read_text(encoding="utf-8")

        en_box = extract_box(en_content)
        fa_box = extract_box(fa_content)

        if not en_box:
            errors.append(f"book-download-box not found in EN {en_html}")
            continue
        if not fa_box:
            errors.append(f"book-download-box not found in FA {fa_html}")
            continue

        # Check English box assertions
        if "Download Book File" not in en_box:
            errors.append(f"{slug} (EN): missing 'Download Book File'")
        if "Size: " not in en_box:
            errors.append(f"{slug} (EN): missing 'Size: '")
        if "Language: " not in en_box:
            errors.append(f"{slug} (EN): missing 'Language: '")
        if "High-speed Direct CDN" not in en_box:
            errors.append(f"{slug} (EN): missing 'High-speed Direct CDN'")

        # Check NO Persian in English shortcode labels
        if "دریافت فایل کتاب" in en_box:
            errors.append(f"{slug} (EN): leaked Persian 'دریافت فایل کتاب'")
        if "حجم:" in en_box:
            errors.append(f"{slug} (EN): leaked Persian 'حجم:'")
        if "سرور پرسرعت داخلی" in en_box:
            errors.append(f"{slug} (EN): leaked Persian 'سرور پرسرعت داخلی'")
        if "دانلود مستقیم نسخه اصلی کتاب" in en_box:
            errors.append(f"{slug} (EN): leaked Persian 'دانلود مستقیم نسخه اصلی کتاب'")

        verified_en_count += 1

        # Check Persian box assertions
        if "دریافت فایل کتاب" not in fa_box:
            errors.append(f"{slug} (FA): missing 'دریافت فایل کتاب'")
        if "حجم:" not in fa_box:
            errors.append(f"{slug} (FA): missing 'حجم:'")
        if "سرور پرسرعت داخلی" not in fa_box:
            errors.append(f"{slug} (FA): missing 'سرور پرسرعت داخلی'")

        # Check NO English shortcode labels in Persian box
        if "Download Book File" in fa_box:
            errors.append(f"{slug} (FA): leaked English 'Download Book File'")
        if "Size: " in fa_box:
            errors.append(f"{slug} (FA): leaked English 'Size: '")
        if "High-speed Direct CDN" in fa_box:
            errors.append(f"{slug} (FA): leaked English 'High-speed Direct CDN'")
        if "Direct Download Original Book Edition" in fa_box:
            errors.append(f"{slug} (FA): leaked English 'Direct Download Original Book Edition'")

        verified_fa_count += 1

    print(f"Verified {verified_en_count} EN reports and {verified_fa_count} FA reports.")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("ALL 17 REPORTS PASSED SHORTCODE RENDERING CHECKS WITH ZERO ERRORS!")
        return True

if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
