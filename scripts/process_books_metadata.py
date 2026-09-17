import os
import re
import json

PDF_DIR = "content/pdfs"
OUTPUT_METADATA = "data/books_metadata.json"
BASE_URL = "https://dl.theminiceo.ir"

def clean_title_and_slug(filename):
    """Clean filename into human title and url-safe slug"""
    name, ext = os.path.splitext(filename)
    format_type = ext.replace(".", "").upper()
    
    # Remove duplicate marker like (1)
    name = re.sub(r'\s*\(\d+\)$', '', name)
    
    # Check if Persian
    is_persian = any('\u0600' <= c <= '\u06FF' for c in name)
    
    # Generate human readable title
    clean_title = name.replace("_", " ").replace("-", " ")
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    
    # Generate URL safe slug
    if is_persian:
        slug = name.replace(" ", "-").replace("_", "-")
        slug = re.sub(r'-+', '-', slug).strip('-')
    else:
        # Keep alphanumeric and dashes
        slug = re.sub(r'[^\w\s-]', '', name).strip()
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-').lower()
        
    return clean_title, slug, format_type, is_persian

def categorize_book(title, filename):
    text = (title + " " + filename).lower()
    
    if any(k in text for k in ['ai', 'agent', 'machine learning', 'artificial intelligence', 'prompt', 'algorithm', 'gpt', 'هوش مصنوعی']):
        return "ai-technology", "هوش مصنوعی و فناوری"
    elif any(k in text for k in ['discovery', 'interview', 'mom test', 'research', 'testing', 'experiment', 'customer', 'talk', 'empathy', 'survey', 'user research', 'پژوهش']):
        return "discovery-research", "کشف محصول و پژوهش کاربر"
    elif any(k in text for k in ['ux', 'design', 'ui', 'prototype', 'psychology', 'behavior', 'طراحی', 'تجربه کاربری']):
        return "ux-design", "طراحی تجربه کاربری و روانشناسی"
    elif any(k in text for k in ['metric', 'analytics', 'data', 'okr', 'sql', 'measure', 'growth', 'funnel', 'traction', 'pricing', 'conversion', 'آمار', 'داده']):
        return "growth-analytics", "سنجه‌ها، رشد و تحلیل داده"
    elif any(k in text for k in ['lean', 'agile', 'scrum', 'sprint', 'kanban', 'build trap', 'mvp', 'roadmap', 'ناب', 'چابک', 'رودمپ']):
        return "lean-agile", "توسعه چابک و نوپای ناب"
    elif any(k in text for k in ['interview', 'career', 'cracking', 'resume', 'hire', 'playbook', 'handbook', 'toolkit', 'مصاحبه', 'استخدام']):
        return "management-career", "مسیر شغلی و مهارت‌های کاربردی"
    elif any(k in text for k in ['report', 'census', 'state of', 'trends', 'wef', 'گزارش']):
        return "reports-playbooks", "گزارش‌ها و آمارهای تخصصی"
    elif any(k in text for k in ['strategy', 'leadership', 'leader', 'manage', 'ceo', 'habits', 'good to great', 'atomic', 'culture', 'استراتژی', 'رهبری']):
        return "strategy-leadership", "استراتژی و رهبری محصول"
    else:
        return "strategy-leadership", "استراتژی و توسعه محصول"

def format_size(bytes_size):
    mb = bytes_size / (1024 * 1024)
    if mb >= 1:
        return f"{mb:.1f} مگابایت"
    kb = bytes_size / 1024
    return f"{kb:.0f} کیلوبایت"

def process_all_files():
    files = sorted([f for f in os.listdir(PDF_DIR) if not f.startswith('.')])
    books = []
    seen_slugs = set()
    
    for f in files:
        # Skip duplicate '(1)' if original exists
        if " (1)" in f:
            base_f = f.replace(" (1)", "")
            if os.path.exists(os.path.join(PDF_DIR, base_f)):
                print(f"Skipping duplicate: {f}")
                continue

        path = os.path.join(PDF_DIR, f)
        size_bytes = os.path.getsize(path)
        size_str = format_size(size_bytes)
        
        clean_title, slug, format_type, is_persian = clean_title_and_slug(f)
        
        # Deduplicate slug if necessary
        original_slug = slug
        counter = 2
        while slug in seen_slugs:
            slug = f"{original_slug}-{counter}"
            counter += 1
        seen_slugs.add(slug)
        
        cat_slug, cat_title = categorize_book(clean_title, f)
        
        # S3 object key / download URL
        # Note: We URL-encode special chars for the link
        import urllib.parse
        encoded_filename = urllib.parse.quote(f)
        download_url = f"{BASE_URL}/{encoded_filename}"
        
        books.append({
            "filename": f,
            "title": clean_title,
            "slug": slug,
            "format": format_type,
            "size_bytes": size_bytes,
            "size_str": size_str,
            "category_slug": cat_slug,
            "category_title": cat_title,
            "is_persian": is_persian,
            "download_url": download_url
        })
        
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_METADATA, "w", encoding="utf-8") as out:
        json.dump(books, out, ensure_ascii=False, indent=2)
        
    print(f"✅ Processed {len(books)} unique books/reports. Saved to {OUTPUT_METADATA}")

if __name__ == "__main__":
    process_all_files()
