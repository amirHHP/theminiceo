import re
from pathlib import Path

reports_dir = Path("content/docs/reports")
en_files = sorted([f for f in reports_dir.glob("*.en.md") if f.name != "_index.en.md"])

print(f"Total English reports to check: {len(en_files)}")

dummy_patterns = [
    re.compile(r"lorem\s+ipsum", re.I),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bplaceholder\b", re.I),
    re.compile(r"\bxxx+\b", re.I),
    re.compile(r"\btest\s+test\b", re.I),
    re.compile(r"asdf", re.I),
]

persian_regex = re.compile(r"[\u0600-\u06FF]")

results = []

for f in en_files:
    text = f.read_text(encoding="utf-8")
    fa_equiv = reports_dir / (f.name.replace(".en.md", ".md"))
    fa_text = fa_equiv.read_text(encoding="utf-8") if fa_equiv.exists() else ""
    
    # Check dummy text
    dummies = []
    for pat in dummy_patterns:
        m = pat.findall(text)
        if m:
            dummies.extend(m)
            
    # Check frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    has_fm = bool(fm_match)
    title = ""
    desc = ""
    body = ""
    categories = []
    if fm_match:
        fm_content = fm_match.group(1)
        body = fm_match.group(2)
        tm = re.search(r"^title:\s*[\"\x27]?(.*?)[\"\x27]?$", fm_content, re.M)
        if tm: title = tm.group(1)
        dm = re.search(r"^description:\s*[\"\x27]?(.*?)[\"\x27]?$", fm_content, re.M)
        if dm: desc = dm.group(1)
        cm = re.search(r"^categories:\s*\[(.*?)\]", fm_content, re.M)
        if cm: categories = [c.strip().strip("\"'") for c in cm.group(1).split(",")]
        
    # Check Persian chars outside aliases
    body_no_aliases = re.sub(r"aliases:\n(\s+-\s+.*\n)+", "", text)
    persian_in_text = persian_regex.findall(body_no_aliases)
    
    # Check sections
    has_spec = "| Report Specification | Details |" in body
    has_overview = "### 📊 Executive Overview & Core Premise" in body
    has_takeaways = "### 🔑 Key Takeaways & Research Findings" in body
    has_relevance = "### 💡 Industry & Market Relevance in 2026" in body
    has_audience = "### 🎯 Target Audience" in body
    has_shortcode = "{{< book-download" in body
    
    # Check shortcode matching dl_url with fa
    fa_url = re.search(r"\{\{<\s*book-download\s+url=[\"\'](.*?)[\"\']", fa_text)
    en_url = re.search(r"\{\{<\s*book-download\s+url=[\"\'](.*?)[\"\']", text)
    url_match = (fa_url.group(1) == en_url.group(1)) if (fa_url and en_url) else False
    
    results.append({
        "file": f.name,
        "size": len(text),
        "dummies": dummies,
        "persian_chars": len(persian_in_text),
        "has_fm": has_fm,
        "title": title,
        "categories": categories,
        "has_spec": has_spec,
        "has_overview": has_overview,
        "has_takeaways": has_takeaways,
        "has_relevance": has_relevance,
        "has_audience": has_audience,
        "has_shortcode": has_shortcode,
        "url_match": url_match,
    })

all_clean = True
for r in results:
    errors = []
    if r["dummies"]: errors.append(f"Dummies: {r['dummies']}")
    if r["persian_chars"] > 0: errors.append(f"Persian chars found: {r['persian_chars']}")
    if not r["has_fm"]: errors.append("Missing frontmatter")
    if not r["title"]: errors.append("Missing title")
    if "Reports" not in r["categories"]: errors.append(f"Missing Reports category: {r['categories']}")
    if not r["has_spec"]: errors.append("Missing specifications table")
    if not r["has_overview"]: errors.append("Missing overview")
    if not r["has_takeaways"]: errors.append("Missing takeaways")
    if not r["has_relevance"]: errors.append("Missing 2026 relevance")
    if not r["has_audience"]: errors.append("Missing audience")
    if not r["has_shortcode"]: errors.append("Missing shortcode")
    if not r["url_match"]: errors.append("URL mismatch with Persian counterpart")
    if r["size"] < 1000: errors.append(f"Undersized: {r['size']} bytes")
    
    if errors:
        all_clean = False
        print(f"FAIL: {r['file']}: {errors}")
    else:
        print(f"PASS: {r['file']} ({r['size']} bytes) - \"{r['title']}\"")

verdict_str = "100% CLEAN" if all_clean else "ISSUES FOUND"
print(f"\nALL 17 REPORTS STATUS: {verdict_str}")
