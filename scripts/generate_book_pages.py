import os
import json
import re

METADATA_FILE = "data/books_metadata.json"
OUTPUT_DIR = "content/docs/books"

# Curated metadata and Persian knowledge for flagship books
CURATED_BOOKS = {
    "continuous_discovery_habits": {
        "fa_title": "کتاب عادت‌های کشف مداوم (Continuous Discovery Habits)",
        "author": "ترزا تورس (Teresa Torres)",
        "desc": "راهنمای عملی ساخت محصولات مشتری‌محور با درخت فرصت-راه‌حل و کشف پیوسته نیازهای کاربر.",
        "summary": """کتاب **Continuous Discovery Habits** اثر ترزا تورس (Teresa Torres)، یکی از مهم‌ترین و کاربردی‌ترین مراجع مدرن مدیریت محصول در دهه اخیر است. پیام اصلی ترزا تورس این است: **«کشف محصول (Product Discovery) یک پروژه مقطعی با شروع و پایان مشخص نیست، بلکه یک عادت هفتگی و پیوسته در تمام طول عمر محصول است.»**

---

### مفاهیم کلیدی کتاب:

#### ۱. درخت فرصت-راه‌حل (Opportunity Solution Tree - OST)
مهم‌ترین ابزار بصری که تورس معرفی می‌کند، درخت OST است که به تیم محصول کمک می‌کند میان اهداف کسب‌وکار و راه‌حل‌های فنی پلی محکم بسازد:
* **هدف نتیجه‌محور (Outcome):** چه تغییری در رفتار کاربر یا بیزنس می‌خواهیم ایجاد کنیم؟ (نه لیست فیچرها)
* **فرصت‌ها (Opportunities):** نیازها، دردها و خواسته‌های برآورده‌نشده مشتریان.
* **راه‌حل‌ها (Solutions):** ایده‌های مختلف برای برطرف کردن یک فرصت خاص.
* **آزمایش‌ها (Assumptions & Experiments):** تست کوچکترین فرضیات هر راه‌حل قبل از کدنویسی.

#### ۲. عادت مصاحبه هفتگی با کاربران
تورس تأکید می‌کند که سه‌گانه رهبری محصول (Product Trio: مدیر محصول، طراح محصول و لید فنی) باید **حداقل هفته‌ای یک مصاحبه مستقیم با مشتریان** داشته باشند تا درک عمیق و به‌روزی از نیازهای بازار کسب کنند.

#### ۳. تست فرضیات به جای تست ایده‌ها
به جای اینکه یک ایده بزرگ را کامل پیاده کنید و بعد از عرضه متوجه شکست شوید، باید فرضیات نهفته در ایده (فرضیه تمایل، امکان‌سنجی، قابلیت استفاده و توجیه‌پذیری مالی) را استخراج کرده و هر کدام را سریعاً بیازمایید.
"""
    },
    "the_mom_test": {
        "fa_title": "کتاب تست مامان (The Mom Test)",
        "author": "راب فیتزپاتریک (Rob Fitzpatrick)",
        "desc": "چگونه با مشتریان صحبت کنیم و حتی از مادرمان حقیقت را بفهمیم؛ راهنمای جامع مصاحبه با کاربران بدون شنیدن دروغ.",
        "summary": """کتاب **تست مامان (The Mom Test)** اثر راب فیتزپاتریک، استاندارد طلایی پژوهش کاربری و مصاحبه با مشتریان است. حرف حساب کتاب این است: **«بسیاری از ایده‌های ناموفق به این دلیل ساخته می‌شوند که کارآفرینان در مصاحبه‌ها سوالات غلط می‌پرسند و مردم از سر تعارف یا مهربانی به آنها دروغ می‌گویند!»**

---

### ۳ قانون طلایی تست مامان:
1. **درباره زندگی و رفتارهای گذشته آن‌ها صحبت کنید، نه درباره ایده یا آینده‌تان:** مردم پیش‌بینی‌کننده‌های بسیار بدی برای رفتار آینده خود هستند، اما رفتار گذشته‌شان حقیقت محض است.
2. **درباره جزئیات و اتفاقات واقعی گذشته بپرسید، نه درباره کلیات و فرضیات:** به جای اینکه بپرسید «معمولاً چطور ورزش می‌کنی؟»، بپرسید «آخرین باری که ورزش کردی کی بود و چه مشکلی داشتی؟».
3. **کمتر حرف بزنید و بیشتر گوش کنید:** اگر در یک جلسه مصاحبه بیش از ۲۰ درصد زمان را شما صحبت می‌کنید، شما در حال مصاحبه نیستید، بلکه در حال پرزنت و فروختن ایده‌اید!
"""
    },
    "hooked": {
        "fa_title": "کتاب قلاب (Hooked)",
        "author": "نیر ایال (Nir Eyal)",
        "desc": "چگونه محصولات عادت‌ساز بسازیم؟ مدل ۴ مرحله‌ای قلاب برای جذب و بازگشت ارگانیک کاربران.",
        "summary": """کتاب **Hooked: How to Build Habit-Forming Products** اثر نیر ایال، توضیح می‌دهد که چرا و چگونه برخی اپلیکیشن‌ها و محصولات دیجیتال به بخشی جدایی‌ناپذیر از رفتارهای روزمره ما تبدیل می‌شوند.

---

### چرخه ۴ مرحله‌ای مدل قلاب (Hook Model):
1. **محرک (Trigger):**
   * *محرک بیرونی (External):* نوتیفیکیشن، ایمیل، تبلیغات.
   * *محرک درونی (Internal):* احساساتی مثل بی‌حوصلگی، استرس یا ترس از دست دادن (FOMO).
2. **اقدام (Action):** ساده‌ترین رفتاری که کاربر در پاسخ به محرک با کمترین زحمت شناختی انجام می‌دهد (مثل اسکرول کردن یا کلیک روی پلی).
3. **پاداش متغیر (Variable Reward):** پیش‌بینی‌ناپذیر بودن نتیجه که دوپامین مغز را فعال می‌کند (پاداش قبیله، پاداش شکار، پاداش تسلط بر خود).
4. **سرمایه‌گذاری (Investment):** تلاشی که کاربر در محصول انجام می‌دهد (افزودن دیتا، دنبال کردن دیگران، شخصی‌سازی) که ارزش محصول را برای دفعات بعدی افزایش می‌دهد.
"""
    },
    "empowered": {
        "fa_title": "کتاب توانمندسازی تیم‌های محصول (Empowered)",
        "author": "مارتی کاگان و کریس جونز (Marty Cagan & Chris Jones)",
        "desc": "راهنمای رهبری محصول و تبدیل تیم‌های سنتی به تیم‌های خودمختار، باانگیزه و نتیجه‌محور.",
        "summary": """اگر کتاب *Inspired* درباره اصول مدیریت محصول برای اعضای تیم بود، کتاب **Empowered** اثر مارتی کاگان و کریس جونز دقیقاً خطاب به **رهبران محصول (VP of Product, CPO, Head of Product)** نوشته شده است.

---

### آموزه‌های اصلی کتاب:
* **تیم‌های بااختیار (Empowered Teams) در برابر تیم‌های خروجی‌محور (Feature Teams):** رهبران سنتی کارها را دیکته می‌کنند؛ رهبران توانمند مسئله‌ها و سنجه‌های موفقیت را مشخص می‌کنند و پیدا کردن راه‌حل را به هوش و تخصص تیم واگذار می‌کنند.
* **نقش کوچینگ (Coaching) در رهبری:** رهبر محصول باید بخش عمده وقت خود را صرف ارتقای مهارت‌های اعضای تیم و توانمندسازی آن‌ها کند.
* **ایجاد بینش و استراتژی شفاف (Product Vision & Strategy):** بدون چشم‌انداز روشن ۱۰ ساله و استراتژی متمرکز سالانه، هیچ تیمی نمی‌تواند به معنای واقعی کلمه خودمختار عمل کند.
"""
    },
    "zero_to_one": {
        "fa_title": "کتاب صفر به یک (Zero to One)",
        "author": "پیتر تیل (Peter Thiel)",
        "desc": "یادداشت‌هایی درباره استارتاپ‌ها و چگونه ساختن آینده؛ فرار از رقابت مخرب و ایجاد ارزش بنیادین.",
        "summary": """کتاب **صفر به یک (Zero to One)** اثر پیتر تیل، هم‌بنیان‌گذار پی‌پال و پالانتیر، نگاهی عمیق و ساختارشکنانه به نوآوری، تکنولوژی و بیزنس دارد.

---

### مفاهیم کلیدی:
* **پیشرفت عمودی (۰ به ۱) در برابر پیشرفت افقی (۱ به N):** پیشرفت افقی یعنی کپی کردن چیزی که در جای دیگر جواب داده است (جهانی‌سازی)؛ پیشرفت عمودی یعنی خلق چیزی کاملاً نو که قبلاً وجود نداشته (فناوری).
* **رقابت برای بازنده‌هاست (Competition is for Losers):** برخلاف باور عمومی اقتصاد کلاسیک، تیل استدلال می‌کند که رقابت شدید سود را به صفر می‌رساند. استارتاپ‌های موفق باید به دنبال خلق انحصارهای خلاقانه بر پایه فناوری اختصاصی، اثر شبکه‌ای، صرفه‌جویی به مقیاس و برندسازی باشند.
"""
    },
    "sprint": {
        "fa_title": "کتاب اسپرینت (Sprint)",
        "author": "جیک نپ و جان زراتسکی (Jake Knapp, Google Ventures)",
        "desc": "چگونه مسائل بزرگ را در ۵ روز حل کنیم و ایده‌های جدید را تست کنیم؛ متدولوژی تست سریع گوگل ونچرز.",
        "summary": """کتاب **Sprint** فرآیند پنج‌روزه طراحی و اعتبارسنجی ایده را که در شتاب‌دهنده **Google Ventures** برای صدها استارتاپ تست شده، به صورت گام‌به‌گام آموزش می‌دهد.

---

### تقویم ۵ روزه اسپرینت:
* **دوشنبه (نقشه‌برداری):** تعریف مسئله کلیدی و انتخاب هدف اصلی اسپرینت.
* **سه‌شنبه (ایده‌پردازی و اسکچ):** ترسیم راه‌حل‌های رقیب روی کاغذ به صورت انفرادی.
* **چهارشنبه (تصمیم‌گیری):** انتخاب بهترین راه‌حل‌ها و تبدیل آن‌ها به یک استوری‌بورد منسجم.
* **پنج‌شنبه (ساخت پروتوتایپ):** ساخت یک نمونه اولیه شبیه‌سازی‌شده و واقعی‌نما در یک روز.
* **جمعه (تست با کاربران):** مصاحبه با ۵ کاربر واقعی و مشاهده نحوه تعامل آن‌ها با پروتوتایپ.
"""
    },
    "cracking_the_pm_interview": {
        "fa_title": "کتاب مصاحبه مدیریت محصول (Cracking the PM Interview)",
        "author": "گیل لاکمن مک‌داول و جکی باوارو (Gayle Laakmann McDowell, Jackie Bavaro)",
        "desc": "جامع‌ترین مرجع آمادگی برای استخدام در شغل مدیر محصول در غول‌های فناوری (Google, Meta, Amazon, Apple).",
        "summary": """کتاب **Cracking the PM Interview** یکی از معتبرترین کتاب‌های دنیا برای آماده‌سازی متقاضیان نقش‌های Product Manager و Associate PM در شرکت‌های تکنولوژی است.

---

### سرفصل‌های اصلی کتاب:
* **وظایف واقعی یک PM در شرکت‌های مختلف:** مقایسه نقش مدیر محصول در گوگل، مایکروسافت، اپل، آمازون و استارتاپ‌ها.
* **پاسخ به سوالات طراحی محصول (Product Design Questions):** استفاده از چارچوب CIRCLES برای تحلیل نیاز کاربر و ارائه فیچرهای نوآورانه.
* **سوالات استراتژی و تخمین بازار (Estimation & Strategy):** روش‌های تخمین فرمی (Fermi Problems) و استراتژی‌های ورود به بازار.
* **مصاحبه‌های رفتاری و لیدership:** نحوه مستندسازی تجربیات گذشته با روش STAR.
"""
    },
    "team_topologies": {
        "fa_title": "کتاب ساختار تیم‌ها (Team Topologies)",
        "author": "متیو اسکلتون و مانوئل پایس (Matthew Skelton, Manuel Pais)",
        "desc": "سازماندهی تیم‌های کسب‌وکار و فناوری برای تحویل سریع نرم‌افزار و جریان روان ارزش.",
        "summary": """کتاب **Team Topologies** مرجع مدرن طراحی ساختار سازمانی تیم‌های مهندسی و محصول بر پایه **قانون کانوی (Conway's Law)** و کاهش بار شناختی (Cognitive Load) است.

---

### ۴ نوع تیم بنیادین:
1. **Stream-aligned Team (تیم همراستا با جریان ارزش):** تیم‌های کراس‌فانکشنال متمرکز بر تحویل ارزش مداوم به یک بخش خاص از محصول.
2. **Enabling Team (تیم توانمندساز):** تیم‌های متخصص که ابزارها و دانش نوین را به تیم‌های جریان ارزش آموزش می‌دهند.
3. **Complicated-Subsystem Team (تیم زیرسیستم پیچیده):** تیم‌های فوق تخصصی برای مسائل پیچیده ریاضی، هوش مصنوعی یا پردازش تصویر.
4. **Platform Team (تیم پلتفرم):** تیمی که زیرساخت، ابزارها و سرویس‌های داخلی را برای آسان‌تر کردن کار تیم‌های محصول فراهم می‌کند.
"""
    }
}

def get_persian_friendly_title(clean_title, filename):
    lower = filename.lower()
    for key, data in CURATED_BOOKS.items():
        if key in lower or key.replace("_", "-") in lower or key.replace("_", " ") in lower:
            return data["fa_title"]
            
    # Check well known patterns
    if "continuous_discovery" in lower:
        return "کتاب عادت‌های کشف مداوم (Continuous Discovery Habits)"
    if "the mom test" in lower:
        return "کتاب تست مامان (The Mom Test)"
    if "hooked" in lower:
        return "کتاب قلاب (Hooked)"
    if "empowered" in lower:
        return "کتاب تیم‌های توانمند (Empowered)"
    if "zero to one" in lower:
        return "کتاب صفر به یک (Zero to One)"
    if "sprint" in lower and "knapp" in lower:
        return "کتاب اسپرینت (Sprint)"
    if "cracking" in lower and "interview" in lower:
        return "کتاب مصاحبه مدیریت محصول (Cracking the PM Interview)"
    if "team_topologies" in lower:
        return "کتاب توپولوژی تیم‌ها (Team Topologies)"
    if "atomic habits" in lower:
        return "کتاب عادت‌های اتمی (Atomic Habits)"
    if "good strategy bad" in lower:
        return "کتاب استراتژی خوب، استراتژی بد (Good Strategy Bad Strategy)"
    if "high output management" in lower:
        return "کتاب مدیریت با بازده بالا (High Output Management)"
    if "user story mapping" in lower:
        return "کتاب نقشه‌برداری داستان کاربر (User Story Mapping)"
    if "shape-up" in lower:
        return "کتاب Shape Up اثر Basecamp"
    if "start with why" in lower:
        return "کتاب با چرا شروع کنید (Start with Why)"
    if "thinking, fast and slow" in lower:
        return "کتاب تفکر، سریع و کند (Thinking, Fast and Slow)"
    if "lean ux" in lower:
        return "کتاب تجربه کاربری ناب (Lean UX)"
    if "transformed" in lower:
        return "کتاب تحول به مدل عملیاتی محصول (Transformed)"
        
    return f"کتاب {clean_title}"

def get_book_description(title, cat_title):
    return f"معرفی تخصصی، بررسی سرفصل‌ها و دانلود نسخه کامل کتاب {title} در حوزه {cat_title} برای مدیران محصول و طراحان."

def generate_page_content(book):
    filename = book["filename"]
    slug = book["slug"]
    clean_title = book["title"]
    size_str = book["size_str"]
    format_type = book["format"]
    cat_title = book["category_title"]
    cat_slug = book["category_slug"]
    download_url = book["download_url"]
    
    fa_title = get_persian_friendly_title(clean_title, filename)
    desc = get_book_description(clean_title, cat_title)
    
    # Check if we have curated deep content
    curated_content = None
    for key, data in CURATED_BOOKS.items():
        if key in filename.lower() or key.replace("_", "-") in filename.lower():
            curated_content = data["summary"]
            break
            
    if not curated_content:
        curated_content = f"""کتاب **{clean_title}** یکی از مراجع معتبر و پرکاربرد در حوزه **{cat_title}** است. این اثر به بررسی راهکارها، متدولوژی‌ها و تجربیات عملی متخصصان این حوزه می‌پردازد و راهنمای مفیدی برای تیم‌های محصول، استارتاپ‌ها و مدیران کسب‌وکار به شمار می‌رود.

### موضوعات و سرفصل‌های محوری:
* درک الگوها و چارچوب‌های عملی در تصمیم‌گیری محصول
* بهینه‌سازی فرآیندهای تیم و هماهنگی میان طراحی، مهندسی و کسب‌وکار
* پیاده‌سازی کاربردی رویکردهای ارزش‌آفرین در چرخه عمر محصول
* پاسخ به چالش‌های رایج مدیران محصول و راهکارهای حل تعارضات سازمانی

### این منبع برای چه کسانی مفید است؟
* **مدیران محصول و مالکان محصول (PM/PO):** برای ارتقای تفکر استراتژیک و کشف دقیق‌تر فرصت‌های بازار.
* **طراحان تجربه و رابط کاربری (Product Designers):** برای درک عمیق‌تر اهداف کسب‌وکار و روانشناسی رفتار کاربر.
* **هم‌بنیان‌گذاران و رهبران استارتاپ:** برای اتخاذ تصمیمات اصولی در مقیاس‌پذیری و توسعه مدل کسب‌وکار.
"""

    content = f"""---
title: "{fa_title}"
date: 2026-09-15
description: "{desc}"
tags: ["کتابخانه", "{cat_title}", "مدیریت محصول"]
categories: ["کتاب‌ها"]
---

{curated_content}

---

### 📥 دریافت فایل کتاب

{{{{< book-download url="{download_url}" title="دانلود کتاب {clean_title} (نسخه کامل)" size="{size_str}" format="{format_type}" >}}}}
"""
    return content

def main():
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        books = json.load(f)
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Keep track of existing files to avoid overwriting manually written articles
    existing_files = set(os.listdir(OUTPUT_DIR))
    
    generated_count = 0
    skipped_count = 0
    
    legacy_files = {
        "Escaping-the-Build-Trap.md", "The-Lean-Product-Playbook.md", "The-Lean-Startup.md",
        "behind-every-great-product.md", "build-better-products.md", "human-blockers.md",
        "okr-books.md", "pm-club.md", "pm-courses.md", "storytelling-with-data.md",
        "survival-guide-for-product-managers.md", "talking-to-others.md",
        "webinar-05-roadmap.md", "webinar-06-listening.md", "کتاب-inspired.md",
        "کتاب-lean-analytics.md", "کتاب-roadmap.md", "_index.md", "_index.en.md"
    }
    
    for book in books:
        slug = book["slug"]
        filename_md = f"{slug}.md"
        
        if filename_md in legacy_files:
            skipped_count += 1
            continue
            
        target_path = os.path.join(OUTPUT_DIR, filename_md)
        page_md = generate_page_content(book)
        with open(target_path, "w", encoding="utf-8") as out:
            out.write(page_md)
        generated_count += 1
        
    print(f"🎉 Done! Generated/Updated {generated_count} book pages. (Skipped {skipped_count} legacy files).")

if __name__ == "__main__":
    main()
