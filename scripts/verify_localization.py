#!/usr/bin/env python3
"""
scripts/verify_localization.py - Production-Grade Localization Audit & CI Verification Tool
for TheMiniCEO (Hugo Hextra Multilingual).

Adheres strictly to Requirement R1:
- Pure Python standard library only (zero third-party dependencies).
- Deterministically audits all content files across the repository.
- Excludes content/pdfs/, .obsidian/, content/.obsidian/, and _drafts/ (and hidden files).
- Verifies 1-to-1 pairing of Persian (*.md) with English (*.en.md) in the same directory,
  accurately handling Persian Unicode slugs (including decomposed combining characters).
- Robust frontmatter parser supporting YAML (---) and TOML (+++ using tomllib with fallback).
  Handles colons in quotes, inline lists, and YAML block lists.
- Validates frontmatter completeness: title, date (except root index/categories),
  description (strictly required for books and reports; for other content required when
  Persian counterpart has description), and non-empty content (>50 bytes).
- Supports CLI flags: --root / --content-dir, --strict, --json, -v/--verbose, -q/--quiet,
  --min-file-size, --min-body-size.
- Returns exit code 0 when 100% paired and valid; 1 when any missing page or error is detected.
- Outputs summary containing keywords required by E2E test T4.1 ("SUCCESS" or "100%").
"""

import argparse
from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import tomllib  # Python 3.11+
except ImportError:
    tomllib = None  # type: ignore


# ==============================================================================
# Constants & Configurations
# ==============================================================================

EXCLUDED_PARTS: Set[str] = {".obsidian", "_drafts", "pdfs"}
PERSIAN_CHAR_REGEX = re.compile(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]")
PLACEHOLDER_REGEX = re.compile(r"(?:\bTODO\b|\bFIXME\b|\bTBD\b|(?i:lorem\s+ipsum)|(?i:\[placeholder\]))")


def is_excluded(path_str: str) -> bool:
    """
    Determines whether a directory or file path is excluded from the audit.
    Excludes:
      - content/pdfs/
      - .obsidian/ (root or inside content)
      - _drafts/ (or any directory starting with '_draft')
      - Hidden directories and files starting with '.'
    """
    parts = Path(path_str).parts
    for p in parts:
        if p in EXCLUDED_PARTS or p.startswith(".") or p.startswith("_draft"):
            return True
    return False


def has_persian(text: str) -> bool:
    """Returns True if the text contains any Persian/Arabic Unicode characters."""
    return bool(PERSIAN_CHAR_REGEX.search(text))


def get_field_str(data: Dict[str, Any], key: str) -> str:
    """Safely extracts a string representation of a frontmatter field."""
    val = data.get(key)
    if val is None:
        return ""
    if hasattr(val, "isoformat"):
        return val.isoformat()
    if isinstance(val, list):
        return ", ".join(str(x) for x in val)
    return str(val).strip()


# ==============================================================================
# Robust Frontmatter Parsing (Pure Python Standard Library)
# ==============================================================================

def parse_frontmatter(content: str) -> Tuple[str, Dict[str, Any], str, str]:
    """
    Extracts frontmatter delimiters, parsed metadata dictionary, raw frontmatter, and body.
    Supports both YAML ('---') and TOML ('+++') using pure Python standard library.

    Returns:
        (fmt_type, metadata_dict, raw_fm_text, body_text)
        fmt_type: 'yaml' | 'toml' | 'none'
    """
    content = content.lstrip("\ufeff")  # Strip UTF-8 BOM if present
    lines = content.splitlines(keepends=True)
    if not lines:
        return "none", {}, "", content

    first = lines[0].strip()
    if first not in ("---", "+++"):
        return "none", {}, "", content

    delim = first
    fmt_type = "yaml" if delim == "---" else "toml"

    close_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == delim:
            close_idx = i
            break

    if close_idx == -1:
        return "none", {}, "", content

    raw_fm = "".join(lines[1:close_idx])
    body = "".join(lines[close_idx + 1:])

    # TOML parsing via standard library tomllib if available
    if fmt_type == "toml":
        if tomllib is not None:
            try:
                return "toml", tomllib.loads(raw_fm), raw_fm, body
            except Exception:
                pass
        return "toml", _parse_toml_fallback(raw_fm), raw_fm, body

    # YAML parsing via lightweight standard library parser
    return "yaml", _parse_yaml(raw_fm), raw_fm, body


def _parse_toml_scalar(raw_val: str) -> Any:
    """Parses a scalar value from a TOML key-value pair."""
    # Quoted string: '...' or "..."
    if (raw_val.startswith('"') and raw_val.endswith('"')) or (
        raw_val.startswith("'") and raw_val.endswith("'")
    ):
        return raw_val[1:-1]
    # Boolean
    if raw_val.lower() == "true":
        return True
    if raw_val.lower() == "false":
        return False
    # Integer
    if re.match(r"^-?\d+$", raw_val):
        return int(raw_val)
    # Float
    if re.match(r"^-?\d+\.\d+$", raw_val):
        return float(raw_val)
    # Array: [...]
    if raw_val.startswith("[") and raw_val.endswith("]"):
        try:
            return json.loads(raw_val)
        except Exception:
            return [x.strip().strip("\"'") for x in raw_val[1:-1].split(",") if x.strip()]
    return raw_val


def _parse_toml_fallback(raw_fm: str) -> Dict[str, Any]:
    """
    Standard library fallback parser for TOML frontmatter when tomllib is unavailable.
    Supports tables ([table]), strings, booleans, integers, datetimes, and inline arrays.
    """
    kv: Dict[str, Any] = {}
    current_section: Optional[str] = None

    for line in raw_fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Table header: [section]
        table_m = re.match(r"^\[([a-zA-Z0-9_.-]+)\]$", line)
        if table_m:
            current_section = table_m.group(1).strip()
            if current_section not in kv or not isinstance(kv[current_section], dict):
                kv[current_section] = {}
            continue

        # Key-value pair: key = value
        m = re.match(r"^([a-zA-Z0-9_-]+)\s*=\s*(.*)$", line)
        if m:
            key = m.group(1).strip()
            raw_val = m.group(2).strip()
            val = _parse_toml_scalar(raw_val)
            if current_section:
                if not isinstance(kv.get(current_section), dict):
                    kv[current_section] = {}
                kv[current_section][key] = val
            else:
                kv[key] = val

    return kv


def _parse_yaml(raw_fm: str) -> Dict[str, Any]:
    """
    Pure Python standard library parser for Hugo YAML frontmatter.
    Supports key-value pairs, quotes, colons in strings, inline JSON arrays,
    block sequences (- item), booleans, numbers, and nested sub-keys.
    """
    kv: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_list: Optional[List[Any]] = None

    for line in raw_fm.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Handle block sequence item: '- item'
        if stripped.startswith("- "):
            val = stripped[2:].strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            if current_list is not None:
                current_list.append(val)
            elif current_key is not None:
                if not isinstance(kv.get(current_key), list):
                    kv[current_key] = []
                kv[current_key].append(val)
                current_list = kv[current_key]
            continue

        # Handle top-level 'key: value'
        m = re.match(r"^([a-zA-Z0-9_-]+)\s*[:=]\s*(.*)$", line)
        if m:
            key = m.group(1).strip()
            raw_val = m.group(2).strip()
            current_key = key
            current_list = None

            if not raw_val:
                kv[key] = ""
            elif raw_val.startswith("[") and raw_val.endswith("]"):
                try:
                    kv[key] = json.loads(raw_val)
                except Exception:
                    kv[key] = [x.strip().strip("\"'") for x in raw_val[1:-1].split(",") if x.strip()]
            elif (raw_val.startswith('"') and raw_val.endswith('"')) or (
                raw_val.startswith("'") and raw_val.endswith("'")
            ):
                kv[key] = raw_val[1:-1]
            elif raw_val.lower() == "true":
                kv[key] = True
            elif raw_val.lower() == "false":
                kv[key] = False
            elif re.match(r"^-?\d+$", raw_val):
                kv[key] = int(raw_val)
            elif re.match(r"^-?\d+\.\d+$", raw_val):
                kv[key] = float(raw_val)
            else:
                kv[key] = raw_val
        else:
            # Handle nested key (e.g. '  exclude: true')
            sub_m = re.match(r"^\s+([a-zA-Z0-9_-]+)\s*[:=]\s*(.*)$", line)
            if sub_m and current_key:
                sub_k = sub_m.group(1).strip()
                sub_v = sub_m.group(2).strip()
                if (sub_v.startswith('"') and sub_v.endswith('"')) or (
                    sub_v.startswith("'") and sub_v.endswith("'")
                ):
                    sub_v = sub_v[1:-1]
                elif sub_v.lower() == "true":
                    sub_v = True
                elif sub_v.lower() == "false":
                    sub_v = False
                elif re.match(r"^-?\d+$", sub_v):
                    sub_v = int(sub_v)
                if not isinstance(kv.get(current_key), dict):
                    kv[current_key] = {}
                kv[current_key][sub_k] = sub_v

    return kv


# ==============================================================================
# Audit Data Models
# ==============================================================================

@dataclass
class FileIssue:
    file_path: str
    issue_type: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "file_path": self.file_path,
            "issue_type": self.issue_type,
            "message": self.message,
        }


@dataclass
class AuditResult:
    root_dir: str
    total_persian_scanned: int = 0
    total_english_found: int = 0
    missing_files: List[FileIssue] = field(default_factory=list)
    empty_files: List[FileIssue] = field(default_factory=list)
    frontmatter_errors: List[FileIssue] = field(default_factory=list)
    other_errors: List[FileIssue] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return (
            len(self.missing_files)
            + len(self.empty_files)
            + len(self.frontmatter_errors)
            + len(self.other_errors)
        )

    @property
    def is_success(self) -> bool:
        return self.total_issues == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_dir": self.root_dir,
            "is_success": self.is_success,
            "total_issues": self.total_issues,
            "total_persian_scanned": self.total_persian_scanned,
            "total_english_found": self.total_english_found,
            "missing_count": len(self.missing_files),
            "empty_count": len(self.empty_files),
            "frontmatter_error_count": len(self.frontmatter_errors),
            "other_error_count": len(self.other_errors),
            "missing_files": [i.to_dict() for i in self.missing_files],
            "empty_files": [i.to_dict() for i in self.empty_files],
            "frontmatter_errors": [i.to_dict() for i in self.frontmatter_errors],
            "other_errors": [i.to_dict() for i in self.other_errors],
        }

    def format_summary(self, verbose: bool = False, max_sample: int = 15) -> str:
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("THEMINICEO LOCALIZATION VERIFICATION AUDIT")
        lines.append("=" * 70)
        lines.append(f"Audit Root Directory:        {self.root_dir}")
        lines.append(f"Total Persian files scanned: {self.total_persian_scanned}")
        lines.append(f"Total English files found:   {self.total_english_found}")
        lines.append(f"Missing .en.md files:        {len(self.missing_files)}")
        lines.append(f"Empty/undersized files:      {len(self.empty_files)}")
        lines.append(f"Frontmatter error count:     {len(self.frontmatter_errors)}")
        lines.append(f"Other syntax/system errors:  {len(self.other_errors)}")
        lines.append(f"Total issues detected:       {self.total_issues}")
        lines.append("-" * 70)

        # Missing files breakdown
        if self.missing_files:
            lines.append(f"\n❌ MISSING ENGLISH COUNTERPARTS ({len(self.missing_files)} total):")
            by_dir: Dict[str, int] = {}
            for issue in self.missing_files:
                d = os.path.dirname(issue.file_path)
                by_dir[d] = by_dir.get(d, 0) + 1
            for d, count in sorted(by_dir.items()):
                lines.append(f"  - {d}: {count} missing")

            sample_limit = len(self.missing_files) if verbose else min(max_sample, len(self.missing_files))
            lines.append(f"\n  Sample missing files ({sample_limit} of {len(self.missing_files)}):")
            for issue in self.missing_files[:sample_limit]:
                lines.append(f"    • {issue.file_path}")
            if not verbose and len(self.missing_files) > sample_limit:
                lines.append(f"    ... and {len(self.missing_files) - sample_limit} more (use --verbose to view all)")

        # Empty or undersized files breakdown
        if self.empty_files:
            lines.append(f"\n❌ EMPTY OR UNDERSIZED FILES ({len(self.empty_files)} total):")
            for issue in self.empty_files[:max_sample if not verbose else len(self.empty_files)]:
                lines.append(f"  - {issue.file_path}: {issue.message}")
            if not verbose and len(self.empty_files) > max_sample:
                lines.append(f"  ... and {len(self.empty_files) - max_sample} more")

        # Frontmatter issues breakdown
        if self.frontmatter_errors:
            lines.append(f"\n❌ FRONTMATTER ISSUES ({len(self.frontmatter_errors)} total):")
            for issue in self.frontmatter_errors[:max_sample if not verbose else len(self.frontmatter_errors)]:
                lines.append(f"  - {issue.file_path}: {issue.message}")
            if not verbose and len(self.frontmatter_errors) > max_sample:
                lines.append(f"  ... and {len(self.frontmatter_errors) - max_sample} more")

        # Other errors
        if self.other_errors:
            lines.append(f"\n❌ OTHER ERRORS ({len(self.other_errors)} total):")
            for issue in self.other_errors:
                lines.append(f"  - {issue.file_path}: {issue.message}")

        lines.append("")
        if self.is_success:
            lines.append("✅ SUCCESS: 100% English localization parity achieved! All tests pass.")
        else:
            lines.append(f"❌ FAILED: Localization coverage incomplete or errors detected ({self.total_issues} issues).")

        return "\n".join(lines)


# ==============================================================================
# Audit Core Implementation
# ==============================================================================

def audit(
    content_dir: str = "content",
    strict: bool = False,
    min_file_size: int = 50,
    min_body_size: int = 50,
) -> AuditResult:
    """
    Performs a deterministic audit of the content directory.

    Args:
        content_dir: Path to Hugo content directory (default: 'content').
        strict: If True, enforces strict checks (date ISO format, body length >=100,
                categories taxonomy, book-download shortcodes, placeholder text).
        min_file_size: Minimum required total file size in bytes (default: 50).
        min_body_size: Minimum required markdown body size for books & reports (default: 50).

    Returns:
        AuditResult object containing detailed counts and issues.
    """
    result = AuditResult(root_dir=content_dir)

    if not os.path.exists(content_dir):
        result.other_errors.append(
            FileIssue(
                file_path=content_dir,
                issue_type="dir_not_found",
                message=f"Content directory does not exist: '{content_dir}'",
            )
        )
        return result

    persian_files: List[str] = []
    english_files: Set[str] = set()

    # Traverse content directory deterministically
    for root, dirs, files in os.walk(content_dir):
        # In-place directory filtering to prevent descending into excluded trees
        dirs[:] = sorted([d for d in dirs if not is_excluded(d)])
        if is_excluded(root):
            continue

        for f in sorted(files):
            p = os.path.join(root, f)
            if is_excluded(p) or not f.endswith(".md"):
                continue

            if f.endswith(".en.md"):
                english_files.add(p)
            else:
                persian_files.append(p)

    result.total_persian_scanned = len(persian_files)
    result.total_english_found = len(english_files)

    for fa_path in sorted(persian_files):
        # Determine expected 1:1 English counterpart in the same directory.
        # Slicing [:-3] + '.en.md' preserves exact Unicode codepoints (including combining madda).
        en_path = fa_path[:-3] + ".en.md"

        if not os.path.exists(en_path):
            result.missing_files.append(
                FileIssue(
                    file_path=en_path,
                    issue_type="missing_counterpart",
                    message=f"Missing English counterpart for Persian page '{fa_path}'",
                )
            )
            continue

        # 1. Validate file size and non-emptiness
        try:
            file_size = os.path.getsize(en_path)
        except OSError as e:
            result.other_errors.append(
                FileIssue(file_path=en_path, issue_type="os_error", message=str(e))
            )
            continue

        if file_size <= min_file_size:
            result.empty_files.append(
                FileIssue(
                    file_path=en_path,
                    issue_type="undersized_file",
                    message=f"File size is {file_size} bytes (minimum threshold > {min_file_size} bytes)",
                )
            )
            continue

        try:
            with open(en_path, "r", encoding="utf-8") as fh:
                en_content = fh.read()
        except UnicodeDecodeError as e:
            result.other_errors.append(
                FileIssue(file_path=en_path, issue_type="encoding_error", message=f"UTF-8 decode error: {e}")
            )
            continue

        if not en_content.strip():
            result.empty_files.append(
                FileIssue(
                    file_path=en_path,
                    issue_type="empty_file",
                    message="File content is empty or contains whitespace only",
                )
            )
            continue

        # 2. Parse English frontmatter
        fmt_type, en_kv, raw_fm, body = parse_frontmatter(en_content)
        if fmt_type == "none":
            result.frontmatter_errors.append(
                FileIssue(
                    file_path=en_path,
                    issue_type="invalid_delimiters",
                    message="Missing or unclosed frontmatter delimiters ('---' for YAML or '+++' for TOML)",
                )
            )
            continue

        # Read Persian frontmatter for comparative completeness checking
        fa_kv: Dict[str, Any] = {}
        if os.path.exists(fa_path):
            try:
                with open(fa_path, "r", encoding="utf-8") as fa_fh:
                    _, fa_kv, _, _ = parse_frontmatter(fa_fh.read())
            except Exception:
                fa_kv = {}

        is_index_page = os.path.basename(en_path) == "_index.en.md"
        norm_p = en_path.replace("\\", "/")
        is_book = "docs/books" in norm_p
        is_report = "docs/reports" in norm_p
        is_book_or_report = is_book or is_report

        rel_norm = os.path.relpath(en_path, content_dir).replace("\\", "/")
        is_taxonomy = is_index_page and (
            rel_norm.startswith("categories/")
            or rel_norm.startswith("tags/")
            or rel_norm == "_index.en.md"
        )

        # 3. Validate 'title'
        title = get_field_str(en_kv, "title")
        if not title:
            result.frontmatter_errors.append(
                FileIssue(
                    file_path=en_path,
                    issue_type="missing_title",
                    message="Missing or empty 'title' field in frontmatter",
                )
            )
        elif has_persian(title):
            result.frontmatter_errors.append(
                FileIssue(
                    file_path=en_path,
                    issue_type="persian_in_title",
                    message=f"Title contains untranslated Persian text: '{title}'",
                )
            )

        # 4. Validate 'date'
        # Taxonomy roots and homepage naturally omit date unless Persian counterpart explicitly has date
        persian_has_date = bool(get_field_str(fa_kv, "date"))
        if not is_taxonomy or persian_has_date:
            date_val = get_field_str(en_kv, "date")
            if not date_val:
                result.frontmatter_errors.append(
                    FileIssue(
                        file_path=en_path,
                        issue_type="missing_date",
                        message="Missing or empty 'date' field in frontmatter",
                    )
                )
            elif strict:
                try:
                    datetime.fromisoformat(date_val.replace("Z", "+00:00"))
                except Exception:
                    result.frontmatter_errors.append(
                        FileIssue(
                            file_path=en_path,
                            issue_type="invalid_date_format",
                            message=f"Date '{date_val}' is not valid ISO 8601 format",
                        )
                    )

        # 5. Validate 'description'
        # Strictly required for books and reports; for other content required when Persian counterpart has description
        persian_has_desc = bool(get_field_str(fa_kv, "description"))
        if is_book_or_report or persian_has_desc:
            desc_val = get_field_str(en_kv, "description")
            if not desc_val:
                result.frontmatter_errors.append(
                    FileIssue(
                        file_path=en_path,
                        issue_type="missing_description",
                        message="Missing or empty 'description' field in frontmatter",
                    )
                )
            elif has_persian(desc_val):
                result.frontmatter_errors.append(
                    FileIssue(
                        file_path=en_path,
                        issue_type="persian_in_description",
                        message="Description contains untranslated Persian text",
                    )
                )

        # 6. Validate Body content
        body_stripped = body.strip()
        body_bytes = len(body_stripped.encode("utf-8"))

        if not is_index_page:
            if not body_stripped:
                result.empty_files.append(
                    FileIssue(
                        file_path=en_path,
                        issue_type="empty_body",
                        message="Markdown body after frontmatter is empty",
                    )
                )
            elif is_book_or_report and body_bytes <= min_body_size:
                result.empty_files.append(
                    FileIssue(
                        file_path=en_path,
                        issue_type="undersized_body",
                        message=f"Markdown body is {body_bytes} bytes (expected > {min_body_size} bytes)",
                    )
                )
        elif strict and is_book_or_report and body_bytes < 50:
            result.empty_files.append(
                FileIssue(
                    file_path=en_path,
                    issue_type="undersized_index_body",
                    message=f"Section index body is {body_bytes} bytes (expected >= 50 bytes in strict mode)",
                )
            )

        # 7. Strict mode enhancements
        if strict:
            # Check for dummy placeholder text
            if PLACEHOLDER_REGEX.search(en_content):
                result.other_errors.append(
                    FileIssue(
                        file_path=en_path,
                        issue_type="placeholder_text",
                        message="Contains dummy placeholder text (TODO/FIXME/TBD/lorem ipsum)",
                    )
                )

            # Check download shortcode in book and report content pages
            if is_book_or_report and not is_index_page:
                if "{{< book-download" not in body and "{{<book-download" not in body:
                    result.other_errors.append(
                        FileIssue(
                            file_path=en_path,
                            issue_type="missing_download_shortcode",
                            message="Missing 'book-download' shortcode in content",
                        )
                    )

                # Check category tag presence
                cats = get_field_str(en_kv, "categories")
                if is_book and ("Books" not in cats and "کتاب" not in cats):
                    result.frontmatter_errors.append(
                        FileIssue(
                            file_path=en_path,
                            issue_type="invalid_category",
                            message="Missing 'Books' category in frontmatter",
                        )
                    )
                if is_report and ("Reports" not in cats and "گزارش" not in cats):
                    result.frontmatter_errors.append(
                        FileIssue(
                            file_path=en_path,
                            issue_type="invalid_category",
                            message="Missing 'Reports' category in frontmatter",
                        )
                    )

    return result


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint for verify_localization.py."""
    parser = argparse.ArgumentParser(
        description="Verify 1-to-1 English localization parity and frontmatter completeness for TheMiniCEO.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Support both --root and --content-dir aliases
    parser.add_argument(
        "--root",
        "--content-dir",
        dest="content_dir",
        default="content",
        help="Path to Hugo content directory (alias: --root, default: 'content')",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict checks (taxonomies, shortcodes, ISO dates, placeholders)",
    )
    parser.add_argument(
        "--min-file-size",
        type=int,
        default=50,
        help="Minimum file size in bytes for English files",
    )
    parser.add_argument(
        "--min-body-size",
        type=int,
        default=50,
        help="Minimum body size in bytes for books and reports",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display all missing files and error details without truncation",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only display summary results",
    )

    args = parser.parse_args(argv)

    result = audit(
        content_dir=args.content_dir,
        strict=args.strict,
        min_file_size=args.min_file_size,
        min_body_size=args.min_body_size,
    )

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        if not args.quiet:
            print(result.format_summary(verbose=args.verbose))
        else:
            if result.is_success:
                print("SUCCESS: 100% English localization parity verified.")
            else:
                print(f"FAILED: {result.total_issues} issues detected.")

    return 0 if result.is_success else 1


if __name__ == "__main__":
    sys.exit(main())
