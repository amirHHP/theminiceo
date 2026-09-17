import os
import re
import json

REPORTS_DIR = "content/docs/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

reports_map = [
    {
        "old_file": "the-2024-state-of-product-management-report.md",
        "new_file": "the-2024-state-of-product-management-report.md",
        "title": "گزارش وضعیت مدیریت محصول ۲۰۲۴ (State of PM 2024)",
        "category": "وضعیت مدیریت محصول",
        "summary": "گزارش سالانه بررسی وضعیت، چالش‌ها، ساختار تیم‌ها و ابزارهای مورد استفاده مدیران محصول در سال ۲۰۲۴.",
        "dl_url": "https://dl.theminiceo.ir/The-2024-State-of-Product-Management-Report.pdf",
        "size": "3.8 مگابایت",
        "key_points": [
            "بررسی اولویت‌های کلیدی مدیران محصول در سال ۲۰۲۴ و جایگاه هوش مصنوعی در فرایندها",
            "ساختار متداول تیم‌های محصول و میزان تعامل با تیم‌های طراحی، مهندسی و بازاریابی",
            "پرکاربردترین ابزارهای مدیریت نقشه راه، تحلیل داده و ارتباط با کاربران",
            "چالش‌های اقتصادی، بهینه‌سازی هزینه‌ها و تمرکز بر سودآوری به جای رشد پرهزینه"
        ]
    },
    {
        "old_file": "the-state-of-product-management-annual-report-2023.md",
        "new_file": "the-state-of-product-management-annual-report-2023.md",
        "title": "گزارش سالانه وضعیت مدیریت محصول ۲۰۲۳",
        "category": "وضعیت مدیریت محصول",
        "summary": "تحلیل جامع حقوق، ابزارها، اولویت‌بندی‌ها و متدولوژی‌های تیم‌های محصول در سال ۲۰۲۳.",
        "dl_url": "https://dl.theminiceo.ir/The-State-of-Product-Management-Annual-Report-2023.pdf",
        "size": "12.2 مگابایت",
        "key_points": [
            "آمارهای آماری و نظرسنجی از هزاران مدیر محصول بین‌المللی",
            "روش‌های اصلی اولویت‌بندی فیچرها و چالش‌های هماهنگی با ذی‌نفعان",
            "روند بازگشت به کار حضوری و مدل‌های ترکیبی (Hybrid)",
            "معیارهای ارزیابی عملکرد مدیران محصول و ارتقای شغلی"
        ]
    },
    {
        "old_file": "the-2022-state-of-product-management-report-by-productplan.md",
        "new_file": "the-2022-state-of-product-management-report-by-productplan.md",
        "title": "گزارش وضعیت مدیریت محصول ۲۰۲۲ (ProductPlan)",
        "category": "وضعیت مدیریت محصول",
        "summary": "گزارش ارائه‌شده توسط ProductPlan درباره روند دورکاری، نقشه راه محصول و همکاری‌های بین‌تیمی در سال ۲۰۲۲.",
        "dl_url": "https://dl.theminiceo.ir/The-2022-State-of-Product-Management-Report-by-ProductPlan.pdf",
        "size": "5.5 مگابایت",
        "key_points": [
            "تحلیل تغییرات شیوه‌های برنامه‌ریزی نقشه راه در دوران پساکرونا",
            "ابزارهای پیشرو در مدیریت تسک‌ها و همسویی استراتژیک",
            "فاصله میان انتظارات رهبران کسب‌وکار و واقعیت‌های اجرایی تیم‌های محصول",
            "بررسی نقش داده‌ها و تصمیم‌گیری مبتنی بر شواهد"
        ]
    },
    {
        "old_file": "wef-future-of-jobs-report-2025.md",
        "new_file": "wef-future-of-jobs-report-2025.md",
        "title": "گزارش آینده مشاغل ۲۰۲۵ - مجمع جهانی اقتصاد (WEF)",
        "category": "آینده بازار کار و مهارت‌ها",
        "summary": "گزارش مرجع World Economic Forum پیرامون دگرگونی بازار کار، هوش مصنوعی، اتوماسیون و مهارت‌های حیاتی مدیران و متخصصان فناوری تا سال ۲۰۲۵ و پس از آن.",
        "dl_url": "https://dl.theminiceo.ir/WEF_Future_of_Jobs_Report_2025.pdf",
        "size": "14.0 مگابایت",
        "key_points": [
            "۱۰ مهارت برتر مورد نیاز در ۵ سال آینده برای رهبران و مدیران محصول",
            "تأثیر اتوماسیون و فناوری‌های نوظهور بر نقش‌های شغلی در سطح جهان",
            "استراتژی‌های بازآموزی (Reskilling) و ارتقای مهارت (Upskilling) در سازمان‌ها",
            "چشم‌انداز جذب سرمایه انسانی و دگرگونی ساختار صنایع دیجیتال"
        ]
    },
    {
        "old_file": "product-leadership-census-2023-v2.md",
        "new_file": "product-leadership-census-2023-v2.md",
        "title": "سرشماری رهبران محصول ۲۰۲۳ (Product Leadership Census)",
        "category": "رهبری محصول و منابع انسانی",
        "summary": "پیمایش و سرشماری جامعه رهبران محصول شامل مدیران ارشد محصول (CPO)، معاونان و مدیران کلیدی درباره ساختار سازمانی و استراتژی رشد.",
        "dl_url": "https://dl.theminiceo.ir/Product%20Leadership%20Census_2023_v2.pdf",
        "size": "7.3 مگابایت",
        "key_points": [
            "ساختار گزارش‌دهی تیم‌های محصول به مدیرعامل و هیئت مدیره",
            "مدیریت بودجه و شاخص‌های سنجش ارزش‌آفرینی دپارتمان محصول",
            "استراتژی‌های حفظ نیروهای کلیدی و چالش‌های جذب استعدادها",
            "نحوه تعامل رهبران محصول با فروش و توسعه کسب‌وکار"
        ]
    },
    {
        "old_file": "fpmr-2023-enterprise.md",
        "new_file": "fpmr-2023-enterprise.md",
        "title": "گزارش آینده مدیریت محصول در شرکت‌های بزرگ (FPMR 2023 Enterprise)",
        "category": "وضعیت مدیریت محصول",
        "summary": "بررسی تحول دیجیتال و آینده شیوه‌های توسعه محصول در مقیاس سازمانی و انترپرایز.",
        "dl_url": "https://dl.theminiceo.ir/FPMR-2023_enterprise.pdf",
        "size": "1.1 مگابایت",
        "key_points": [
            "چالش‌های گذار شرکت‌های سنتی به مدل عملیاتی محصول‌محور (Product Operating Model)",
            "مدیریت وابستگی‌های پیچیده نرم‌افزاری و میراث سیستم‌های قدیمی (Legacy)",
            "حکمرانی داده‌ها و استانداردهای انطباق قانونی در مقیاس سازمانی",
            "رویکردهای چابک سازمانی (SAFe و LeSS) در برابر مدل‌های خودمختار"
        ]
    },
    {
        "old_file": "the-future-of-product-2024.md",
        "new_file": "the-future-of-product-2024.md",
        "title": "گزارش آینده محصول ۲۰۲۴ (The Future of Product)",
        "category": "آینده بازار کار و مهارت‌ها",
        "summary": "بینش‌های کلیدی درباره تأثیر هوش مصنوعی مولد، سیستم‌های خودکار و رویکردهای نوین در نسل بعدی محصولات نرم‌افزاری.",
        "dl_url": "https://dl.theminiceo.ir/The_Future_of_Product_-_2024.pdf",
        "size": "9.6 مگابایت",
        "key_points": [
            "گذار از رابط‌های کاربری سنتی (GUI) به رابط‌های مکالمه‌ای و مبتنی بر قصد کاربر (Intent-based)",
            "شخصی‌سازی آنی محصولات با مدل‌های زبانی بزرگ (LLMs)",
            "نقش ایجنت‌های هوش مصنوعی در تسریع چرخه تست و کشف محصول",
            "مسئولیت‌های اخلاقی و شفافیت الگوریتمی در محصولات دیجیتال"
        ]
    },
    {
        "old_file": "amplitude-product-report-2022.md",
        "new_file": "amplitude-product-report-2022.md",
        "title": "گزارش تحلیلی محصول ۲۰۲۲ - امپلی‌تود (Amplitude)",
        "category": "تحلیل داده و رفتار کاربران",
        "summary": "داده‌های رفتاری میلیون‌ها کاربر فعال و بررسی الگوهای تعامل (Engagement) و نگه‌داشت (Retention) در محصولات دیجیتال برتر.",
        "dl_url": "https://dl.theminiceo.ir/Amplitude%20Product%20Report%202022.pdf",
        "size": "2.0 مگابایت",
        "key_points": [
            "بنچمارک‌های نگه‌داشت (Retention) در اپلیکیشن‌های B2B و B2C",
            "رفتارهای پیش‌بینی‌کننده وفاداری کاربران و شاخص‌های Aha Moment",
            "بررسی همبستگی میان شخصی‌سازی تجربه کاربری و افزایش LTV",
            "استراتژی‌های رشد مبتنی بر محصول (Product-Led Growth)"
        ]
    },
    {
        "old_file": "airtable-product-insights-report.md",
        "new_file": "airtable-product-insights-report.md",
        "title": "گزارش بینش محصول و نوآوری ایرتیبل (Airtable Product Insights)",
        "category": "ابزارها و نوآوری سازمانی",
        "summary": "چگونگی تسریع فرایندهای کشف و عرضه محصول با ابزارهای No-code و پلتفرم‌های تعاملی سازمانی.",
        "dl_url": "https://dl.theminiceo.ir/Airtable_Product-insights-report.pdf",
        "size": "2.9 مگابایت",
        "key_points": [
            "تسهیل جریان‌های کاری بین‌تیمی با بانک‌های اطلاعاتی رابطه‌ای بصری",
            "کاهش زمان ورود به بازار (Time to Market) با نمونه‌سازی‌های منعطف",
            "یکپارچه‌سازی فرآیندهای بازخورد مشتریان و بازتاب آن در برنامه‌ریزی فصلی",
            "تجربیات سازمان‌های پیشرو در پیاده‌سازی پایپ‌لاین‌های اتوماتیک"
        ]
    },
    {
        "old_file": "heap-digital-experiences-insights-report2.md",
        "new_file": "heap-digital-experiences-insights-report2.md",
        "title": "گزارش بینش تجارب دیجیتال کاربران (Heap Insights Report)",
        "category": "تحلیل داده و رفتار کاربران",
        "summary": "تحلیل اصطکاک‌های تجربه کاربری، نقاط ریزش در فانل‌های خرید و شاخص‌های بهبود نرخ تبدیل در وب و موبایل.",
        "dl_url": "https://dl.theminiceo.ir/heap-digital-experiences-insights-report2.pdf",
        "size": "400 کیلوبایت",
        "key_points": [
            "بررسی علل ناشناخته ریزش کاربران در مراحل مختلف ثبت‌نام و آنبوردینگ",
            "مزایای ثبت خودکار رویدادها (Autocapture) در کشف رفتارهای پیش‌بینی‌نشده",
            "اثر سرعت بارگذاری و سادگی مسیر بر تعامل کاربر با فیچرهای کلیدی",
            "تکنیک‌های بهینه‌سازی قیف فروش (Funnel Optimization)"
        ]
    },
    {
        "old_file": "designvaluereport1.md",
        "new_file": "designvaluereport1.md",
        "title": "گزارش بنچمارک ارزش تجاری طراحی (Design Value Report)",
        "category": "طراحی و ارزش تجاری",
        "summary": "سنجش میزان بازگشت سرمایه (ROI) طراحی و نحوه ایجاد تمایز رقابتی شرکت‌های طراحی‌محور در بازارهای مالی.",
        "dl_url": "https://dl.theminiceo.ir/DesignValueReport1.pdf",
        "size": "1.3 مگابایت",
        "key_points": [
            "مقایسه بازدهی سهام شرکت‌های دیزاین‌محور (Design Index) با شاخص S&P 500",
            "چگونگی ترجمه تجربیات کاربری عالی به معیارهای مالی و سودآوری",
            "سطوح بلوغ طراحی در سازمان‌ها و اثر آن بر تصمیم‌گیری‌های کلان",
            "ایجاد حس تعلق عاطفی در مشتریان از طریق طراحی هویت محصول"
        ]
    },
    {
        "old_file": "گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md",
        "new_file": "گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md",
        "title": "گزارش سالانه صنعت پرداخت ایران (نسخه نهم)",
        "category": "اکوسیستم و صنایع ایران",
        "summary": "بررسی آماری تراکنش‌ها، سهم بازار شرکت‌های PSP، الگوهای پرداخت اینترنتی و شاخص‌های فین‌تک در ایران.",
        "dl_url": "https://dl.theminiceo.ir/%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B5%D9%86%D8%B9%D8%AA%20%D9%BE%D8%B1%D8%AF%D8%A7%D8%AE%D8%AA%20%D8%A7%DB%8C%D8%B1%D8%A7%D9%86%20%D9%86%D8%B3%D8%AE%D9%87%20%D9%86%D9%87%D9%85.pdf",
        "size": "5.7 مگابایت",
        "key_points": [
            "روند تغییر حجم و تعداد تراکنش‌های شاپرک و درگاه‌های پرداخت اینترنتی (IPG)",
            "سهم بازار و رتبه‌بندی شرکت‌های ارائه‌دهنده خدمات پرداخت (PSP) در ایران",
            "تحلیل رفتار کاربران در پرداخت‌های موبایلی، کدهای دستوری و اپلیکیشن‌ها",
            "چالش‌های رگولاتوری، سقف تراکنش‌ها و افق فناوری‌های نوین پرداخت الکترونیک"
        ]
    },
    {
        "old_file": "1666697156021.md",
        "new_file": "iran-startup-ecosystem-report-techrasa-1400.md",
        "title": "گزارش پیمایش اکوسیستم استارتاپی ایران - تکراسا (بهار ۱۴۰۰)",
        "category": "اکوسیستم و صنایع ایران",
        "summary": "شناسایی و پیمایش اکوسیستم استارتاپی ایران، تحلیل نظرات بیش از ۱۰۰ بنیان‌گذار و مدیرعامل و بررسی سنجه‌های رشد، ارزش‌گذاری و اثر همه‌گیری.",
        "dl_url": "https://dl.theminiceo.ir/1666697156021.pdf",
        "size": "1.8 مگابایت",
        "key_points": [
            "پیمایش میدانی از نظرات شهودی بیش از ۱۰۰ مدیرعامل و بنیان‌گذار استارتاپی ایران",
            "شاخص‌های سنجش مرحله رشد استارتاپ‌ها (Seed، Early Stage، Growth)",
            "تأثیر شرایط اقتصادی، تورم، همه‌گیری کرونا و فیلترینگ بر کسب‌وکارهای نوپا",
            "بررسی فرآیندهای ارزش‌گذاری و چالش‌های جذب سرمایه خطرپذیر (VC) در ایران"
        ]
    },
    {
        "old_file": "hbr-2022-11-12.md",
        "new_file": "hbr-2022-11-12.md",
        "title": "مجله Harvard Business Review (شماره نوامبر - دسامبر ۲۰۲۲)",
        "category": "نشریات و مقالات تخصصی ادواری",
        "summary": "نسخه کامل شماره نوامبر و دسامبر ۲۰۲۲ مجله معتبر HBR با تمرکز بر استراتژی‌های رهبری در دوران عدم قطعیت و تصمیم‌گیری‌های کلان.",
        "dl_url": "https://dl.theminiceo.ir/HBR%202022%2011%2012.pdf",
        "size": "90.4 مگابایت",
        "key_points": [
            "مقالات تحلیلی برترین اساتید مدیریت دانشگاه هاروارد درباره پایداری سازمان",
            "راهبردهای نوین قیمت‌گذاری در شرایط تورمی و مدیریت زنجیره تأمین",
            "روانشناسی رهبری تیم‌ها در بحران‌های اقتصادی و تحولات بازار",
            "مطالعات موردی شرکت‌های جهانی در تحول مدل‌های درآمدی"
        ]
    },
    {
        "old_file": "generative-ai-the-insights-you-need-from-harvard-business-review.md",
        "new_file": "generative-ai-the-insights-you-need-from-harvard-business-review.md",
        "title": "مجموعه مقالات هوش مصنوعی زاینده HBR (Generative AI Insights)",
        "category": "نشریات و مقالات تخصصی ادواری",
        "summary": "گزیده بینش‌ها و مقالات تحلیلی نویسندگان و پژوهشگران نشریه کسب‌وکار هاروارد پیرامون هوش مصنوعی زاینده و اثر آن بر استراتژی کسب‌وکار.",
        "dl_url": "https://dl.theminiceo.ir/Generative_AI_The_Insights_You_Need_From_Harvard_Business_Review.pdf",
        "size": "6.7 مگابایت",
        "key_points": [
            "چگونه هوش مصنوعی خلاقیت، بهره‌وری و ماهیت تولید محتوا را متحول می‌کند؟",
            "مدیریت ریسک‌های کپی‌رایت، توهم مدل‌ها و حریم خصوصی در استفاده تجاری از AI",
            "طراحی استراتژی برد برای کسب‌وکارهای کوچک در عصر مدل‌های زبانی عظیم",
            "بازتعریف تجربه مشتری و خدمات پشتیبانی با کمک چت‌بات‌های هوشمند"
        ]
    },
    {
        "old_file": "the-analytics-stack-guidebook.md",
        "new_file": "the-analytics-stack-guidebook.md",
        "title": "راهنمای انتخاب استک ابزارهای تحلیل محصول (The Analytics Stack Guidebook)",
        "category": "ابزارها و نوآوری سازمانی",
        "summary": "مقایسه ابزارهای مدرن جمع‌آوری، ذخیره‌سازی و تحلیل داده‌های محصول شامل Snowflake، BigQuery، Segment، Amplitude و Mixpanel.",
        "dl_url": "https://dl.theminiceo.ir/the-analytics-stack-guidebook.pdf",
        "size": "13.5 مگابایت",
        "key_points": [
            "معماری مدرن داده (Modern Data Stack) از جمع‌آوری تا داشبوردسازی نهایی",
            "تفاوت پلتفرم‌های CDP (Customer Data Platform) و Data Warehouse",
            "بهترین ترکیب ابزاری برای استارتاپ‌ها در مراحل مختلف بلوغ داده‌ای",
            "بهینه‌سازی هزینه‌های ذخیره‌سازی و پرس‌وجوهای تحلیلی در مقیاس کلان"
        ]
    },
    {
        "old_file": "heap-implicit-vs-explicit-guide-2022.md",
        "new_file": "heap-implicit-vs-explicit-guide-2022.md",
        "title": "راهنمای داده‌های صریح در برابر ضمنی (Heap Guide 2022)",
        "category": "تحلیل داده و رفتار کاربران",
        "summary": "راهنمای فنی شرکت Heap درباره ثبت خودکار رویدادها (Autocapture) و مقایسه داده‌های ضمنی و صریح در بهبود محصول.",
        "dl_url": "https://dl.theminiceo.ir/HEAP_Implicit-vs-Explicit_Guide_2022.pdf",
        "size": "1.7 مگابایت",
        "key_points": [
            "تفاوت‌های ساختاری میان رهگیری دستی رویدادها (Manual Tracking) و رهگیری خودکار",
            "چگونه داده‌های ضمنی به کشف زوایای پنهان سفر کاربر کمک می‌کنند؟",
            "کاهش هزینه‌های نگهداری کد رهگیری برای تیم‌های مهندسی نرم‌افزار",
            "تبدیل رویدادهای خام به شاخص‌های استراتژیک تصمیم‌گیری"
        ]
    }
]

def generate_report_md(report):
    points_md = "\n".join([f"* {p}" for p in report["key_points"]])
    old_slug = report["old_file"].replace(".md", "")
    new_slug = report["new_file"].replace(".md", "")
    
    aliases_yaml = f"aliases:\n  - /docs/books/{old_slug}/"
    if old_slug != new_slug:
        aliases_yaml += f"\n  - /docs/reports/{old_slug}/"
        
    return f"""---
title: "{report['title']}"
date: 2026-09-16
description: "{report['summary']}"
tags: ["گزارش‌ها", "{report['category']}", "مدیریت محصول", "تحلیل بازار"]
categories: ["گزارش‌ها"]
{aliases_yaml}
---

{report['title']} یکی از اسناد و مراجع مهم در حوزه **{report['category']}** است. این گزارش کاربردی با تکیه بر داده‌های تجربی، پژوهش‌های میدانی و تحلیل بازار، اطلاعات ارزشمندی را در اختیار مدیران محصول، کارآفرینان و تصمیم‌گیرندگان سازمان قرار می‌دهد.

### محورها و دستاوردهای کلیدی گزارش:
{points_md}

### این گزارش برای چه کسانی مفید است؟
* **مدیران و رهبران محصول (CPO/PM):** برای درک موقعیت کنونی صنعت، همگام‌سازی استراتژی‌ها با روندهای جهانی و شناسایی شکاف‌های بازار.
* **طراحان تجربه کاربری و پژوهشگران (UX Researchers):** برای دسترسی به آمارها و الگوهای کلیدی رفتار و نیازهای کاربران.
* **هم‌بنیان‌گذاران و استراتژیست‌ها:** برای تصمیم‌گیری آگاهانه درباره تخصیص منابع، جذب سرمایه و بازارهای هدف.

---

### 📥 دریافت فایل کامل گزارش

{{{{< book-download url="{report['dl_url']}" title="دانلود {report['title']}" size="{report['size']}" format="PDF" >}}}}
"""

def generate_reports_index():
    return """+++
date = '2026-09-16T12:00:00+03:30'
draft = false
weight = 92
title = 'گزارش‌ها و روندهای مدیریت محصول و فناوری'
description = 'مجموعه جامع گزارش‌های سالانه، سرشماری‌ها، تحلیل‌های آماری و نشریات تخصصی مدیریت محصول و اکوسیستم فناوری.'
+++

به بخش **گزارش‌ها و روندهای تخصصی مدیرعامل کوچک** خوش آمدید. برخلاف کتاب‌های بنیادین و همیشگی کتابخانه، این بخش به **گزارش‌های داده‌محور سالانه، سرشماری‌های صنعتی، بنچمارک‌های تحلیلی و نشریات ادواری تخصصی** اختصاص یافته است که روندهای لحظه‌ای بازار کار، ابزارها و تصمیم‌گیری‌های راهبردی را به تصویر می‌کشند.

---

### 🌟 گزارش‌های شاخص و برجسته

{{< cards cols="3" >}}
  {{< card link="/docs/reports/wef-future-of-jobs-report-2025/" title="آینده مشاغل ۲۰۲۵ (WEF)" subtitle="گزارش مرجع مجمع جهانی اقتصاد درباره مهارت‌های کلیدی، هوش مصنوعی و دگرگونی بازار کار تا ۲۰۲۵." >}}
  {{< card link="/docs/reports/the-2024-state-of-product-management-report/" title="وضعیت مدیریت محصول ۲۰۲۴" subtitle="بررسی جامع ابزارها، چالش‌ها و روندهای کاری هزاران تیم محصول در سال ۲۰۲۴." >}}
  {{< card link="/docs/reports/product-leadership-census-2023-v2/" title="سرشماری رهبران محصول" subtitle="تحلیل وضعیت CPOها، ساختارهای سازمانی و چالش‌های هدایت تیم‌های محصول." >}}
  {{< card link="/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم/" title="صنعت پرداخت ایران" subtitle="گزارش سالانه سهم بازار PSPها، الگوهای تراکنش و چشم‌انداز فین‌تک در ایران." >}}
  {{< card link="/docs/reports/iran-startup-ecosystem-report-techrasa-1400/" title="اکوسیستم استارتاپی ایران" subtitle="پیمایش میدانی تکراسا از ۱۰۰ مدیرعامل، ارزش‌گذاری‌ها و سنجه‌های رشد در ایران." >}}
  {{< card link="/docs/reports/amplitude-product-report-2022/" title="گزارش محصول Amplitude" subtitle="داده‌های رفتاری کاربران، الگوهای نگه‌داشت (Retention) و شاخص‌های رشد محصول‌محور." >}}
{{< /cards >}}

---

### 📂 دسته‌بندی موضوعی گزارش‌ها

تمامی گزارش‌های این بخش در ۴ محور تخصصی گردآوری شده‌اند:

1. **وضعیت سالانه مدیریت محصول (State of PM):** گزارش‌های معتبر سالانه (۲۰۲۲ تا ۲۰۲۴) درباره حقوق، چالش‌های اولویت‌بندی و فرهنگ تیمی.
2. **آینده بازار کار و رهبری فناوری (Future of Jobs & Leadership):** گزارش‌های مجمع جهانی اقتصاد، سرشماری‌های رهبری و تحول سازمان‌ها با هوش مصنوعی.
3. **تحلیل داده‌ها، رفتار کاربر و ابزارها (Analytics & Tool Insights):** بنچمارک‌های تعامل کاربر، اصطکاک‌های تجربه دیجیتال و راهنمای استک ابزارهای مدرن داده.
4. **اکوسیستم استارتاپی و صنایع ایران (Iran Ecosystem):** گزارش‌های اختصاصی صنعت پرداخت، فین‌تک و پیمایش‌های استارتاپی داخل کشور.

---

> [!TIP]
> اگر به دنبال کتاب‌های متنی و کلاسیک مرجع مدیریت محصول هستید، به بخش [**کتابخانه جامع مدیریت محصول**](/docs/books/) مراجعه کنید.
"""

def generate_reports_index_en():
    return """+++
date = '2026-09-16T12:00:00+03:30'
draft = false
weight = 92
title = 'Reports & Industry Benchmarks'
description = 'Annual reports, census surveys, industry benchmarks, and periodic insights for product managers and technology leaders.'
+++

Welcome to the **Reports & Industry Benchmarks** section. Here you will find data-driven annual state-of-product reports, workforce trends, analytics benchmarks, and ecosystem surveys.

For evergreen literature and classic product books, visit the [**Product Management Library**](/docs/books/).
"""

def main():
    print(f"Generating {len(reports_map)} reports in {REPORTS_DIR}...")
    
    # 1. Generate report markdown files
    for r in reports_map:
        out_path = os.path.join(REPORTS_DIR, r["new_file"])
        content = generate_report_md(r)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {out_path}")
        
        # Remove old file from books if exists
        old_path = os.path.join("content/docs/books", r["old_file"])
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f"🗑️ Removed old: {old_path}")

    # 2. Write index files
    with open(os.path.join(REPORTS_DIR, "_index.md"), "w", encoding="utf-8") as f:
        f.write(generate_reports_index())
    print("✅ Created content/docs/reports/_index.md")

    with open(os.path.join(REPORTS_DIR, "_index.en.md"), "w", encoding="utf-8") as f:
        f.write(generate_reports_index_en())
    print("✅ Created content/docs/reports/_index.en.md")

if __name__ == "__main__":
    main()
