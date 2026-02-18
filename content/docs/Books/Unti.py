import os
import re

# مسیر اصلی محتوا - این را روی پوشه اصلی پروژه بگذارید تا همه زیرپوشه‌ها را بگردد
content_dir = "./"

def add_leading_slash(match):
    """تابع کمکی برای اضافه کردن اسلش به تک‌تک آیتم‌های پیدا شده"""
    full_block = match.group(0)
    # پیدا کردن تمام مسیرها داخل کوتیشن یا بعد از خط تیره که با اسلش شروع نمی‌شوند
    # این ریجکس مواردی که با اسلش شروع نمی‌شوند را پیدا کرده و یک اسلش به ابتدای آن‌ها اضافه می‌کند
    fixed_block = re.sub(r'(?<=[\-\s\'"\[])([^\s\/\'"\]][^\s\'"\]]*)', r'/\1', full_block)
    return fixed_block

def fix_aliases_robust(directory):
    # الگوی پیدا کردن بلوک aliases در Front Matter (YAML یا TOML)
    # این الگو از شروع کلمه aliases تا رسیدن به کلید بعدی یا پایان Front Matter را می‌گیرد
    alias_pattern = re.compile(r'aliases\s*:\s*(?:\[.*?\]|[\s\S]*?)(?=\n\S+\s*:|\n---|\n\+\+\+)', re.MULTILINE)

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # اعمال تغییرات با استفاده از Regex
                new_content = alias_pattern.sub(add_leading_slash, content)

                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ اصلاح شد: {filename}")
                else:
                    # برای دیباگ: اگر فایلی تغییر نکرد شاید کلاً بخش aliases ندارد
                    pass

if __name__ == "__main__":
    print("🚀 در حال بررسی فایل‌ها...")
    fix_aliases_robust(content_dir)
    print("✨ عملیات به پایان رسید.")