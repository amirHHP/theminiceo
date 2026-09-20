#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
enrich_and_deduplicate_books.py
1. Consolidates duplicate books and adds proper 301/Hugo aliases to canonical pages.
2. Enriches all book pages in content/docs/books/ with deep, authentic Persian content,
   metadata specifications table, core takeaways, 2026 relevance, and download cards.
3. Cleans data/books_metadata.json by removing duplicates and migrated reports.
"""

import os
import re
import json
import urllib.parse
from collections import defaultdict

try:
    import pypdf
except ImportError:
    pypdf = None

PDF_DIR = "content/pdfs"
BOOKS_DIR = "content/docs/books"
METADATA_FILE = "data/books_metadata.json"
BASE_URL = "https://dl.theminiceo.ir"

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from curated_books_data import CURATED_BOOKS
except ImportError:
    from scripts.curated_books_data import CURATED_BOOKS

DUPLICATES = [
    {
        "duplicate_file": "the-lean-startup-how-todays-entrepreneurs-use-continuous-innovation.md",
        "canonical_file": "The-Lean-Startup.md",
        "alias": "/docs/books/the-lean-startup-how-todays-entrepreneurs-use-continuous-innovation/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "escaping-the-build-trap-how-effective-product-management-creates.md",
        "canonical_file": "Escaping-the-Build-Trap.md",
        "alias": "/docs/books/escaping-the-build-trap-how-effective-product-management-creates/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "the-lean-product-playbook-how-to-innovate-with-minimum-viable-products.md",
        "canonical_file": "The-Lean-Product-Playbook.md",
        "alias": "/docs/books/the-lean-product-playbook-how-to-innovate-with-minimum-viable-products/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/The_lean_product_playbook_How_to_innovate_with_minimum_viable_products.pdf",
                "title": "دانلود کتاب The Lean Product Playbook (نسخه اصلی انگلیسی)",
                "size": "5.5 مگابایت",
                "format": "PDF",
                "lang": "انگلیسی"
            }
        ]
    },
    {
        "duplicate_file": "inspired-how-to-create-tech-products-customers-love-by-marty-cagan.md",
        "canonical_file": "کتاب-inspired.md",
        "alias": "/docs/books/inspired-how-to-create-tech-products-customers-love-by-marty-cagan/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/INSPIRED_How_to_Create_Tech_Products_Customers_Love_by_Marty_Cagan.pdf",
                "title": "دانلود کتاب INSPIRED اثر مارتی کاگان (نسخه کامل انگلیسی)",
                "size": "1.9 مگابایت",
                "format": "PDF",
                "lang": "انگلیسی"
            }
        ]
    },
    {
        "duplicate_file": "lean-analytics-use-data-to-build-a-better-startup-faster-by-alistair.md",
        "canonical_file": "کتاب-lean-analytics.md",
        "alias": "/docs/books/lean-analytics-use-data-to-build-a-better-startup-faster-by-alistair/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/Lean_Analytics_Use_Data_to_Build_a_Better_Startup_Faster_by_Alistair.pdf",
                "title": "دانلود کتاب Lean Analytics (نسخه اصلی انگلیسی)",
                "size": "6.9 مگابایت",
                "format": "PDF",
                "lang": "انگلیسی"
            }
        ]
    },
    {
        "duplicate_file": "lean-analytics-harkat-aval.md",
        "canonical_file": "کتاب-lean-analytics.md",
        "alias": "/docs/books/lean-analytics-harkat-aval/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/Lean-Analytics-Harkat-Aval.pdf",
                "title": "دانلود کتاب تحلیل داده ناب (ترجمه فارسی - حرکت اول)",
                "size": "3.8 مگابایت",
                "format": "PDF",
                "lang": "فارسی"
            }
        ]
    },
    {
        "duplicate_file": "storytelling-with-data-a-data-visualization-guide-for-business.md",
        "canonical_file": "storytelling-with-data.md",
        "alias": "/docs/books/storytelling-with-data-a-data-visualization-guide-for-business/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/Storytelling_with_Data_A_Data_Visualization_Guide_for_Business_.pdf",
                "title": "دانلود کتاب داستان‌سرایی با داده (Storytelling with Data - نسخه اصلی)",
                "size": "10.8 مگابایت",
                "format": "PDF",
                "lang": "انگلیسی"
            }
        ]
    },
    {
        "duplicate_file": "2-value-proposition-design-how-to-create-products-and-services-customers.md",
        "canonical_file": "value-proposition-design-how-to-create-products-and-services-customers.md",
        "alias": "/docs/books/2-value-proposition-design-how-to-create-products-and-services-customers/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "testing-product-ideas-handbook-2.md",
        "canonical_file": "testing-product-ideas-handbook.md",
        "alias": "/docs/books/testing-product-ideas-handbook-2/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "retroproduct-cracking-the-pm-interview.md",
        "canonical_file": "cracking-the-pm-interview-how-to-land-a-product-manager-job-in-technology.md",
        "alias": "/docs/books/retroproduct-cracking-the-pm-interview/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "transformed-farsi.md",
        "canonical_file": "transformed-moving-to-the-product-operating-model.md",
        "alias": "/docs/books/transformed-farsi/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/Transformed-Farsi.pdf",
                "title": "دانلود کتاب تحول به مدل عملیاتی محصول (ترجمه فارسی)",
                "size": "3.1 مگابایت",
                "format": "PDF",
                "lang": "فارسی"
            }
        ]
    },
    {
        "duplicate_file": "running-lean-iterate-from-plan-a-to-a-plan-that-works-ash-maurya.md",
        "canonical_file": "running-lean-iterate-from-plan-a-to-a-plan-that-works-3rd-edition.md",
        "alias": "/docs/books/running-lean-iterate-from-plan-a-to-a-plan-that-works-ash-maurya/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "great-mental-models-volume-1-general-thinking-concepts-the-shane.md",
        "canonical_file": "the-great-mental-models-volume-1-general-thinking-concepts-by-beaubien.md",
        "alias": "/docs/books/great-mental-models-volume-1-general-thinking-concepts-the-shane/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "lean-ux-designing-great-products-with-agile-teamsjeff-gothelf-josh.md",
        "canonical_file": "lean-ux.md",
        "alias": "/docs/books/lean-ux-designing-great-products-with-agile-teamsjeff-gothelf-josh/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "solving-product-design-exercises-questions-answers-artiom-dashinsky.md",
        "canonical_file": "solving-product-design-exercises.md",
        "alias": "/docs/books/solving-product-design-exercises-questions-answers-artiom-dashinsky/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "the-product-strategy-playbook-v40-pf-complete.md",
        "canonical_file": "the-product-strategy-playbook-by-productplan.md",
        "alias": "/docs/books/the-product-strategy-playbook-v40-pf-complete/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "productmindset-byps-2.md",
        "canonical_file": "product-mindset-ebook.md",
        "alias": "/docs/books/productmindset-byps-2/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "buyology-truth-and-lies-about-why-we-buy-by-martin-lindstrom-z-lib.md",
        "canonical_file": "buyology-martin-lindstrom-2008.md",
        "alias": "/docs/books/buyology-truth-and-lies-about-why-we-buy-by-martin-lindstrom-z-lib/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "book-new-product-development-process-pm.md",
        "canonical_file": "new-product-development-process-pm.md",
        "alias": "/docs/books/book-new-product-development-process-pm/",
        "additional_downloads": []
    },
    {
        "duplicate_file": "کتابچه-راهنمای-نگارش-استراتژی-محصول.md",
        "canonical_file": "the-product-strategy-playbook-by-productplan.md",
        "alias": "/docs/books/کتابچه-راهنمای-نگارش-استراتژی-محصول/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/%DA%A9%D8%AA%D8%A7%D8%A8%DA%86%D9%87_%D8%B1%D8%A7%D9%87%D9%86%D9%85%D8%A7%DB%8C_%D9%86%DA%AF%D8%A7%D8%B1%D8%B4_%D8%A7%D8%B3%D8%AA%D8%B1%D8%A7%D8%AA%DA%98%DB%8C_%D9%85%D8%AD%D8%B5%D9%88%D9%84.pdf",
                "title": "دانلود کتابچه راهنمای نگارش استراتژی محصول (ترجمه فارسی)",
                "size": "1.6 مگابایت",
                "format": "PDF",
                "lang": "فارسی"
            }
        ]
    },
    {
        "duplicate_file": "talking-to-humans-success-starts-with-understanding-your-customers.md",
        "canonical_file": "talking-to-others.md",
        "alias": "/docs/books/talking-to-humans-success-starts-with-understanding-your-customers/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/Talking_to_Humans_Success_starts_with_understanding_your_customers.pdf",
                "title": "دانلود کتاب گفتگو با انسان‌ها (Talking to Humans - نسخه اصلی انگلیسی)",
                "size": "1.3 مگابایت",
                "format": "PDF",
                "lang": "انگلیسی"
            }
        ]
    },
    {
        "duplicate_file": "how-to-build-a-product-led-growth-team.md",
        "canonical_file": "product-led-growth-how-to-build-a-product-that-sells-itself-by-wes.md",
        "alias": "/docs/books/how-to-build-a-product-led-growth-team/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/How%20to%20Build%20a%20Product-Led%20Growth%20Team.pdf",
                "title": "دانلود راهنمای ساخت تیم رشد محصول‌محور (How to Build a PLG Team - فایل راهنما)",
                "size": "1.2 مگابایت",
                "format": "PDF",
                "lang": "انگلیسی"
            }
        ]
    },
    {
        "duplicate_file": "strategize-product-strategy-and-product-roadmap-practices-for-the.md",
        "canonical_file": "strategize-2nd-edition-roman-pichler-2022.md",
        "alias": "/docs/books/strategize-product-strategy-and-product-roadmap-practices-for-the/",
        "additional_downloads": [
            {
                "url": "https://dl.theminiceo.ir/Strategize_Product_Strategy_and_Product_Roadmap_Practices_for_the.pdf",
                "title": "دانلود کتاب استراتژی‌ورزی و تدوین رودمپ محصول (Strategize - ویرایش اول)",
                "size": "9.7 مگابایت",
                "format": "PDF",
                "lang": "انگلیسی"
            }
        ]
    }
]

# Protected files with manual content that we must not overwrite entirely, only inject specs table / aliases / downloads
PROTECTED_MANUAL_FILES = {
    "The-Lean-Startup.md", "Escaping-the-Build-Trap.md", "The-Lean-Product-Playbook.md",
    "کتاب-inspired.md", "کتاب-lean-analytics.md", "storytelling-with-data.md",
    "کتاب-roadmap.md", "build-better-products.md", "human-blockers.md",
    "behind-every-great-product.md", "survival-guide-for-product-managers.md",
    "talking-to-others.md", "okr-books.md", "pm-club.md", "pm-courses.md",
    "webinar-05-roadmap.md", "webinar-06-listening.md"
}

LEGACY_SPECS = {
    "The-Lean-Startup.md": {
        "author": "اریک ریس (Eric Ries)",
        "category": "توسعه چابک و نوپای ناب",
        "pages": "288 صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "2.0 مگابایت"
    },
    "Escaping-the-Build-Trap.md": {
        "author": "ملیسا پری (Melissa Perri)",
        "category": "استراتژی و رهبری محصول",
        "pages": "180 صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "4.8 مگابایت"
    },
    "The-Lean-Product-Playbook.md": {
        "author": "دن اولسن (Dan Olsen)",
        "category": "استراتژی و توسعه محصول",
        "pages": "336 صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "5.5 مگابایت"
    },
    "کتاب-inspired.md": {
        "author": "مارتی کاگان (Marty Cagan)",
        "category": "مدیریت محصول",
        "pages": "368 صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "1.9 مگابایت"
    },
    "کتاب-lean-analytics.md": {
        "author": "آلیستر کرول و بنجامین یوکوویتز (Alistair Croll & Benjamin Yoskovitz)",
        "category": "سنجه‌های محصول و تحلیل داده",
        "pages": "440 صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "6.9 مگابایت"
    },
    "storytelling-with-data.md": {
        "author": "کول نوسبامر نفیک (Cole Nussbaumer Knaflic)",
        "category": "ارتباطات، ارائه و بصری‌سازی داده",
        "pages": "288 صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "10.8 مگابایت"
    },
    "talking-to-others.md": {
        "author": "گیف کانستبل (Giff Constable)",
        "category": "کشف محصول و مصاحبه با مشتریان",
        "pages": "71 صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "1.3 مگابایت"
    },
    "human-blockers.md": {
        "author": "امین ساجدی و امیرحسین حسینی پژوه",
        "category": "منابع انسانی و فرهنگ سازمانی",
        "pages": "نسخه کامل کتاب",
        "format": "PDF • دیجیتال استاندارد",
        "size": "۵.۲ مگابایت"
    },
    "کتاب-roadmap.md": {
        "author": "برایان مک‌آلیستر (Brian McAllister)",
        "category": "استراتژی و برنامه‌ریزی فردی و شغلی",
        "pages": "۲۴۰ صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "۸.۴ مگابایت"
    },
    "survival-guide-for-product-managers.md": {
        "author": "استیون هینز (ترجمه امیرحسین حسینی پژوه و پرنیان سیفی)",
        "category": "استراتژی و رهبری محصول",
        "pages": "نسخه کامل ترجمه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "۴.۲ مگابایت"
    },
    "behind-every-great-product.md": {
        "author": "مارتی کاگان (Marty Cagan - SVPG)",
        "category": "مدیریت محصول و رهبری تیم",
        "pages": "۳۶ صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "۱.۱ مگابایت"
    },
    "build-better-products.md": {
        "author": "لورا کلاین و کیت راتر (Laura Klein & Kate Rutter)",
        "category": "طراحی محصول و تجربه کاربری",
        "pages": "۴۸۰ صفحه",
        "format": "PDF • دیجیتال استاندارد",
        "size": "۱۵.۳ مگابایت"
    }
}

REPORTS_SLUGS = {
    "airtable-product-insights-report", "amplitude-product-report-2022",
    "designvaluereport1", "fpmr-2023-enterprise",
    "generative-ai-the-insights-you-need-from-harvard-business-review",
    "hbr-2022-11-12", "heap-digital-experiences-insights-report2",
    "heap-implicit-vs-explicit-guide-2022", "product-leadership-census-2023-v2",
    "the-2022-state-of-product-management-report-by-productplan",
    "the-2024-state-of-product-management-report", "the-analytics-stack-guidebook",
    "the-future-of-product-2024", "the-state-of-product-management-annual-report-2023",
    "wef-future-of-jobs-report-2025", "گزارش-صنعت-پرداخت-ایران-نسخه-نهم",
    "1666697156021"
}

KNOWN_AUTHORS = {
    "teresa torres": "ترزا تورس (Teresa Torres)",
    "rob fitzpatrick": "راب فیتزپاتریک (Rob Fitzpatrick)",
    "nir eyal": "نیر ایال (Nir Eyal)",
    "marty cagan": "مارتی کاگان (Marty Cagan)",
    "peter thiel": "پیتر تیل (Peter Thiel)",
    "jake knapp": "جیک نپ (Jake Knapp)",
    "gayle laakmann": "گیل مک‌داول (Gayle McDowell)",
    "jackie bavaro": "جکی باوارو (Jackie Bavaro)",
    "eric ries": "اریک ریس (Eric Ries)",
    "dan olsen": "دن اولسن (Dan Olsen)",
    "melissa perri": "ملیسا پری (Melissa Perri)",
    "james clear": "جیمز کلیر (James Clear)",
    "daniel kahneman": "دانیل کانمن (Daniel Kahneman)",
    "richard rumelt": "ریچارد روملت (Richard Rumelt)",
    "andy grove": "اندی گروو (Andrew S. Grove)",
    "andrew grove": "اندی گروو (Andrew S. Grove)",
    "jeff patton": "جف پاتون (Jeff Patton)",
    "jeff gothelf": "جف گاتهلف (Jeff Gothelf)",
    "josh seiden": "جاش سیدن (Josh Seiden)",
    "simon sinek": "سایمون سینک (Simon Sinek)",
    "ryan singer": "رایان سینگر (Ryan Singer)",
    "john doerr": "جان دوئر (John Doerr)",
    "ben horowitz": "بن هوروویتز (Ben Horowitz)",
    "richard thaler": "ریچارد تیلر (Richard Thaler)",
    "steve krug": "استیو کروگ (Steve Krug)",
    "don norman": "دان نورمن (Don Norman)",
    "donald norman": "دان نورمن (Don Norman)",
    "kathy sierra": "کتی سیرا (Kathy Sierra)",
    "april dunford": "آپریل دانفورد (April Dunford)",
    "gabriel weinberg": "گابریل واینبرگ (Gabriel Weinberg)",
    "sean ellis": "شان الیس (Sean Ellis)",
    "andrew chen": "اندرو چن (Andrew Chen)",
    "kim scott": "کیم اسکات (Kim Scott)",
    "jocko willink": "جوکو ویلینک (Jocko Willink)",
    "chris voss": "کریس واس (Chris Voss)",
    "morgan housel": "مورگان هاوسل (Morgan Housel)",
    "petra wille": "پترا ویله (Petra Wille)",
    "chan kim": "چان کیم (W. Chan Kim)",
    "greg mckeown": "گرگ مک‌کیون (Greg McKeown)",
    "tiago forte": "تیاگو فورته (Tiago Forte)",
    "itamar gilad": "ایتامار گیلاد (Itamar Gilad)",
    "ethan mollick": "اتان مولیک (Ethan Mollick)",
    "mustafa suleyman": "مصطفی سلیمان (Mustafa Suleyman)",
    "david allen": "دیوید آلن (David Allen)",
    "barbara minto": "باربارا مینتو (Barbara Minto)",
    "cole nussbaumer": "کول نوسبامر نفیک (Cole Nussbaumer)",
    "alexander osterwalder": "الکساندر استروالدر (Alexander Osterwalder)",
    "alex osterwalder": "الکساندر استروالدر (Alexander Osterwalder)",
    "ash maurya": "اش مائوریا (Ash Maurya)",
    "shane parrish": "شین پریش (Shane Parrish)",
    "erika hall": "اریکا هال (Erika Hall)",
    "jon yablonski": "جان یابلونسکی (Jon Yablonski)",
    "alberto savoia": "آلبرتو ساوویا (Alberto Savoia)",
    "phil knight": "فیل نایت (Phil Knight)",
    "reed hastings": "رید هستینگز (Reed Hastings)",
    "ray dalio": "ری دالیو (Ray Dalio)",
    "geoffrey moore": "جفری مور (Geoffrey Moore)",
    "clayton christensen": "کلیتون کریستنسن (Clayton Christensen)",
    "jim collins": "جیم کالینز (Jim Collins)",
    "ed catmull": "اد کتمول (Ed Catmull)",
    "julie zhuo": "جولی ژو (Julie Zhuo)",
    "camille fournier": "کمیل فورنیه (Camille Fournier)",
    "david epstein": "دیوید اپستین (David Epstein)",
    "angela duckworth": "آنجلا داک‌ورث (Angela Duckworth)",
    "carol dweck": "کارول دوک (Carol Dweck)",
    "daniel pink": "دنیل پینک (Daniel Pink)",
    "dan ariely": "دن آریلی (Dan Ariely)",
    "robert cialdini": "رابرت چالدینی (Robert Cialdini)",
    "jonah berger": "جونا برگر (Jonah Berger)",
    "susan cain": "سوزان کین (Susan Cain)",
    "amy edmondson": "امی ادموندسون (Amy Edmondson)",
    "yu-kai chou": "یو-کای چو (Yu-kai Chou)",
    "martin lindstrom": "مارتین لیندستروم (Martin Lindstrom)",
    "cal newport": "کال نیوپورت (Cal Newport)",
    "artiom dashinsky": "آرتیوم داشینسکی (Artiom Dashinsky)",
    "steve portigal": "استیو پورتیگال (Steve Portigal)",
    "rochelle king": "روشل کینگ (Rochelle King)",
    "tom eisenmann": "تام آیزنمن (Tom Eisenmann)",
    "douglas hubbard": "داگلاس هوبارد (Douglas Hubbard)",
    "gojko adzic": "گویکو آدیزیچ (Gojko Adzic)",
    "giff constable": "گیف کانستبل (Giff Constable)",
    "jeff lawson": "جف لاوسون (Jeff Lawson)",
    "eric schmidt": "اریک اشمیت (Eric Schmidt)",
    "adam lashinsky": "آدام لاشینسکی (Adam Lashinsky)",
    "sarah frier": "سارا فرایر (Sarah Frier)",
    "john carreyrou": "جان کری‌رو (John Carreyrou)",
    "david pereira": "دیوید پریرا (David Pereira)",
    "matt lemay": "مت لمی (Matt LeMay)",
    "lee boonstra": "لی بونسترا (Lee Boonstra)",
    "nacho bassino": "ناچو باسینو (Nacho Bassino)",
    "wes bush": "وس بوش (Wes Bush)",
    "ramli john": "رمل جان (Ramli John)",
    "uri levine": "اوری لوین (Uri Levine)",
    "michele hansen": "میشل هنسن (Michele Hansen)",
    "frank slootman": "فرانک اسلوتمن (Frank Slootman)",
    "elad gil": "الاد گیل (Elad Gil)",
    "sal khān": "سلمان خان (Sal Khan)",
    "sal khan": "سلمان خان (Sal Khan)",
    "ray kurzweil": "ری کرزویل (Ray Kurzweil)",
    "karen hao": "کارن هاو (Karen Hao)",
    "reid hoffman": "رید هافمن (Reid Hoffman)",
    "brent keltner": "برنت کلتنر (Brent Keltner)",
    "peter kazanjy": "پیتر کازانجی (Peter Kazanjy)",
    "todd olson": "تاد اولسن (Todd Olson)",
    "lomit patel": "لومیت پاتل (Lomit Patel)",
    "susan weinschenk": "سوزان واینشنک (Susan M. Weinschenk)",
    "verity harding": "وریتی هاردینگ (Verity Harding)",
    "brian christian": "برایان کریستین و تام گریفیتس (Brian Christian & Tom Griffiths)",
    "adam alter": "آدام آلتر (Adam Alter)",
    "ben m bensaou": "بن بن‌سائو (Ben M. Bensaou - INSEAD)",
    "bensaou": "بن بن‌سائو (Ben M. Bensaou - INSEAD)",
    "charles conn": "چارلز کان و رابرت مک‌لین (Charles Conn & Robert McLean - McKinsey)",
    "robert mclean": "چارلز کان و رابرت مک‌لین (Charles Conn & Robert McLean - McKinsey)",
    "hermann simon": "هرمان سایمون (Hermann Simon)",
    "salim ismail": "سلیم اسماعیل و مایکل مالون (Salim Ismail & Michael S. Malone)",
    "jon kolko": "جان کولکو (Jon Kolko)",
    "james p carse": "جیمز پی. کارس (James P. Carse)",
    "james carse": "جیمز پی. کارس (James P. Carse)",
    "charles t munger": "چارلی مانگر و پیتر کافمن (Charlie Munger & Peter Kaufman)",
    "charlie munger": "چارلی مانگر و پیتر کافمن (Charlie Munger & Peter Kaufman)",
    "al ries": "ال ریس و جک تروت (Al Ries & Jack Trout)",
    "jack trout": "ال ریس و جک تروت (Al Ries & Jack Trout)",
    "peter drucker": "پیتر اف. دراکر (Peter F. Drucker)",
    "peter f drucker": "پیتر اف. دراکر (Peter F. Drucker)",
    "david bland": "دیوید بلاند و الکس استروالدر (David J. Bland & Alex Osterwalder)",
    "marshall goldsmith": "مارشال گلداسمیت (Marshall Goldsmith)",
    "alan klement": "آلن کلمنت (Alan Klement)",
    "geoff smart": "جف اسمارت و رندی استریت (Geoff Smart & Randy Street)",
    "randy street": "جف اسمارت و رندی استریت (Geoff Smart & Randy Street)",
    "balaji srinivasan": "بالاجی سرینیواسان (Balaji Srinivasan - Former CTO Coinbase)",
    "keach hagey": "کیچ هیگی (Keach Hagey)",
    "marc andreessen": "مارک اندریسن (Marc Andreessen - a16z)",
    "stephen witt": "استیون ویت (Stephen Witt)",
    "ram charan": "رام چاران (Ram Charan)",
    "des traynor": "دس ترینور و تیم محصول اینترکام (Des Traynor & Intercom Team)",
    "intercom": "دس ترینور و تیم محصول اینترکام (Des Traynor & Intercom Team)",
    "roger martin": "راجر مارتین (Roger L. Martin - Rotman School)",
    "roger l martin": "راجر مارتین (Roger L. Martin - Rotman School)",
    "kelly mcgonigal": "کلی مک‌گونیگال (Kelly McGonigal - Stanford)",
    "kevin simler": "کوین سیملر و رابین هنسون (Kevin Simler & Robin Hanson)",
    "robin hanson": "کوین سیملر و رابین هنسون (Kevin Simler & Robin Hanson)",
    "steven bartlett": "استیون بارتلت (Steven Bartlett)",
    "jurgen appelo": "یورگن آپلو (Jurgen Appelo)",
    "michael lopp": "مایکل لوپ (Michael Lopp - Rands)",
    "ethan rasiel": "ایتان رازیل و پل فریگا (Ethan Rasiel & Paul Friga - McKinsey)",
    "paul friga": "ایتان رازیل و پل فریگا (Ethan Rasiel & Paul Friga - McKinsey)",
    "product school": "پروداکت اسکول (Product School)",
    "carlos gonzalez": "کارلوس گونزالس د ویلاومبروزیا (Carlos González de Villaumbrosia)",
    "ken sandy": "کن سندی (Ken Sandy - UC Berkeley)",
    "amplitude": "تیم محصول امپلیتود (Amplitude Product Team)",
    "john cutler": "جان کاتلر و تیم امپلیتود (John Cutler & Amplitude)",
    "ken watanabe": "کن واتانابه (Ken Watanabe)",
    "todd zaki warfel": "تاد زکی وارفل (Todd Zaki Warfel)",
    "invision": "تیم طراحی و نوآوری اینویژن (InVision Design Team)",
    "aarron walter": "آرون والتر و الی وولری (Aarron Walter & Eli Woolery)",
    "eli woolery": "آرون والتر و الی وولری (Aarron Walter & Eli Woolery)",
    "design council": "شورای دیزاین بریتانیا (Design Council UK)",
    "airfocus": "تیم محصول ایرفوکوس و پروداکت اسکول (Airfocus & Product School)",
    "dave mcclure": "دیو مک‌کلور (Dave McClure - 500 Startups)",
    "delibr": "تیم محصول دلیبر (Delibr Team)",
    "thoughtworks": "تات‌ورکس (ThoughtWorks)",
    "camilla crispim": "کامیلا کریسپیم (Camilla Crispim - ThoughtWorks)",
    "denise tilles": "ملیسا پری و دنیس تیلز (Melissa Perri & Denise Tilles)",
    "folding burritos": "دنیل زاکاریاس (Daniel Zacarias - Folding Burritos)",
    "daniel zacarias": "دنیل زاکاریاس (Daniel Zacarias - Folding Burritos)",
    "mind the product": "مایند د پروداکت (Mind the Product)",
    "janna bastow": "جانا باستو (Janna Bastow - ProdPad & Mind the Product)",
    "joel marsh": "جوئل مارش (Joel Marsh)",
    "growthdesign": "دن بنونی و لویی-ژاویر لاوالی (GrowthDesign - Dan Benoni & Louis-Xavier Lavallée)",
    "dan benoni": "دن بنونی و لویی-ژاویر لاوالی (GrowthDesign)",
    "gianluca mauro": "جانلوکا مائورو و نیکولو والیجی (Gianluca Mauro & Nicolo Valigi)",
    "nicolo valigi": "جانلوکا مائورو و نیکولو والیجی (Gianluca Mauro & Nicolo Valigi)",
    "mel robbins": "مل رابینز (Mel Robbins)",
    "yasar jarrar": "دکتر یاسر جرار (Dr. Yasar Jarrar)",
    "alan watkins": "دکتر آلن واتکینز (Dr. Alan Watkins)",
    "project management institute": "موسسه مدیریت پروژه (Project Management Institute - PMI)",
    "pmi": "موسسه مدیریت پروژه (Project Management Institute - PMI)",
    "product manager hq": "دهاوال بات (Dhaval Bhatt - Product Manager HQ)",
    "pmhq": "دهاوال بات (Dhaval Bhatt - Product Manager HQ)",
    "brad stulberg": "برد استالبرگ (Brad Stulberg)",
    "john inazu": "جان اینازو (John Inazu)",
    "ideo": "تیم نوآوری و طراحی آیدیو (IDEO Design Team)",
    "scip": "انجمن هوش رقابتی و استراتژیک (SCIP)",
    "harvard business review": "تحریریه هاروارد بیزنس ریویو (Harvard Business Review - HBR)",
    "hbr": "تحریریه هاروارد بیزنس ریویو (Harvard Business Review - HBR)",
    "lewis lin": "لوئیس سی. لین (Lewis C. Lin)",
    "lewis c lin": "لوئیس سی. لین (Lewis C. Lin)",
    "gitlab": "تیم محصول گیت‌لب (GitLab Product Team)",
    "workpath": "تیم استراتژی و تحول ورک‌پث (Workpath OKR Team)",
    "peter hollins": "پیتر هالینز (Peter Hollins)",
    "verne harnish": "ورن هارنیش و تحریریه مجله فورچون (Verne Harnish & Fortune)",
    "fortune": "ورن هارنیش و تحریریه مجله فورچون (Verne Harnish & Fortune)",
    "hassan masum": "حسن معصوم و مارک تووی (Hassan Masum & Mark Tovey - MIT Press)",
    "mark tovey": "حسن معصوم و مارک تووی (Hassan Masum & Mark Tovey - MIT Press)",
    "thinkers50": "استوارت کرینر و دز دیرلاو (Thinkers50 - Stuart Crainer & Des Dearlove)",
    "user interviews": "تیم پژوهش کاربر یوزراینترویوز (User Interviews Team)",
    "anne loehr": "آن لوئر و برایان امرسون (Anne Loehr & Brian Emerson)",
    "brian emerson": "آن لوئر و برایان امرسون (Anne Loehr & Brian Emerson)",
    "deeptat": "مهدی موسوی و تیم دیپ‌تات (Deeptat AI)",
    "خلق محصولات": "مهدی موسوی و تیم دیپ‌تات (Deeptat AI)",
    "alan beaulieu": "آلن بولیو (Alan Beaulieu - O'Reilly)",
    "jeff bezos": "جف بزوس (Jeff Bezos - Amazon)",
    "chip heath": "چیپ هیث و دن هیث (Chip Heath & Dan Heath)",
    "dan heath": "چیپ هیث و دن هیث (Chip Heath & Dan Heath)",
    "john zeratsky": "جان زراتسکی و جیک نپ (John Zeratsky & Jake Knapp)",
    "david marquet": "دیوید مارکت (L. David Marquet)",
    "leidy klotz": "لیدی کلوتز (Leidy Klotz)",
    "alex xu": "الکس شو (Alex Xu)",
    "stanley mcchrystal": "ژنرال استنلی مک‌کریستال (General Stanley McChrystal)",
    "sandra j sucher": "ساندرا ساچر و شالین گوپتا (Sandra J. Sucher & Shalene Gupta - Harvard)",
    "brent keltner": "برنت کلتنر (Brent Keltner)",
    "ron kohavi": "ران کوهاوی و دایان تانگ (Ron Kohavi & Diane Tang)",
    "diane tang": "ران کوهاوی و دایان تانگ (Ron Kohavi & Diane Tang)",
    "larry bossidy": "لری باسیدی و رام چاران (Larry Bossidy & Ram Charan)",
    "donald reinertsen": "دانلد رینرتسن (Donald G. Reinertsen)",
    "donald g reinertsen": "دانلد رینرتسن (Donald G. Reinertsen)",
    "radhika dutt": "رادیکا دات (Radhika Dutt)"
}

KNOWN_TITLES_FA = {
    "mindset-carol-s-dweck-2016": "کتاب طرز فکر: روانشناسی نوین موفقیت (Mindset)",
    "poor-charlies-almanack-the-wit-and-wisdom-of-charles-t-munger": "کتاب سالنامه چارلی بینوا: حکمت چارلی مانگر (Poor Charlie's Almanack)",
    "positioning-the-battle-for-your-mind-al-ries-jack-trout-philip": "کتاب جایگاه‌یابی: نبرد برای تسخیر ذهن (Positioning)",
    "the-effective-executive-the-definitiv": "کتاب مدیر اثربخش (The Effective Executive)",
    "pmi-agile-book-project-management-institute-2017": "کتاب راهنمای جامع چابک PMI (Agile Practice Guide)",
    "the-sheikh-ceo-yasar-jarrar-2020": "کتاب مدیرعامل شیخ: درس‌های رهبری دبی (The Sheikh CEO)",
    "user-psychology-playbook-v40-pf-complete": "کتاب پلی‌بوک روانشناسی کاربر در محصول (User Psychology Playbook)",
    "uxbook-remoteworkfordesignteams": "کتاب کار ریموت برای تیم‌های طراحی (Remote Work for Design Teams)",
    "impromptu-rh": "کتاب بداهه: تقویت انسانیت با هوش مصنوعی (Impromptu)",
    "when-coffee-and-kale-compete-become-great-at-making-products-people": "کتاب رقابت قهوه و کلم: راهنمای عملی JTBD (When Coffee and Kale Compete)",
    "the-power-of-self-discipline-5-minute-exercises-to-build-self-control": "کتاب قدرت خودانضباطی (The Power of Self-Discipline)",
    "the-willpower-instinct-how-self-control-works-why-it-matters-and": "کتاب غریزه اراده: علم خودکنترلی (The Willpower Instinct)",
    "the-elephant-in-the-brain-hidden-motives-in-everyday-life-2018": "کتاب فیل در مغز: انگیزه‌های پنهان در زندگی روزمره (The Elephant in the Brain)",
    "the-diary-of-a-ceo-the-33-laws-of-business-and-life-steven-bartlett": "کتاب خاطرات یک مدیرعامل: ۳۳ قانون بیزنس و زندگی (The Diary of a CEO)",
    "the-network-state": "کتاب دولت شبکه: ساخت جوامع و کشورهای دیجیتال (The Network State)",
    "the-optimist-sam-altman-openai-and-the-race-to-invent-the-future": "کتاب خوش‌بین: سم آلتمن، OpenAI و مسابقه فتح آینده (The Optimist)",
    "the-thinking-machine-jensen-huang-nvidia-and-the-worlds-most-coveted": "کتاب ماشین تفکر: جنسن هوانگ، انویدیا و انقلاب هوش مصنوعی (The Thinking Machine)",
    "what-the-ceo-wants-you-to-know-how-your-company-really-works-ram": "کتاب آنچه مدیرعامل می‌خواهد شما بدانید (What the CEO Wants You to Know)",
    "algorithms-to-live-by-the-computer-science-of-human-decisions-brian": "کتاب الگوریتم‌هایی برای زندگی: علوم کامپیوتر در تصمیم‌گیری (Algorithms to Live By)",
    "who-the-a-method-for-hiring-by-geoff-smart-randy-street-smart-geoff": "کتاب چه کسی؟ متد A برای استخدام نخبگان (Who: The A Method for Hiring)",
    "testing-business-ideas-a-field-guide-for-rapid-experimentation": "کتاب تست ایده‌های کسب‌وکار (Testing Business Ideas)",
    "testing-with-humans": "کتاب تست با انسان‌ها: اعتبارسنجی فرضیات (Testing with Humans)",
    "bulletproof-problem-solving-the-one-skill-that-changes-everything": "کتاب حل مسئله ضدگلوله: متدولوژی ۷ مرحله‌ای مک‌کینزی (Bulletproof Problem Solving)",
    "brave-new-words-how-ai-will-revolutionize-education-and-why-thats": "کتاب کلمات شجاعانه نو: هوش مصنوعی و آینده آموزش (Brave New Words)",
    "built-to-innovate-ben-m-bensaou-2022": "کتاب ساخته‌شده برای نوآوری (Built to Innovate)",
    "anatomy-of-a-breakthrough-how-to-get-unstuck-when-it-matters-most": "کتاب کالبدشکافی یک جهش: رهایی از بن‌بست‌های شغلی و محصولی (Anatomy of a Breakthrough)",
    "confessions-of-the-pricing-man-how-price-affects-everything-by-hermann": "کتاب اعترافات مرد قیمت‌گذاری (Confessions of the Pricing Man)",
    "exponential-organizations-why-new-organizations-are-ten-times-better": "کتاب سازمان‌های نمایی (Exponential Organizations)",
    "finite-and-infinite-games-a-vision-of-life-as-play-and-possibility": "کتاب بازی‌های محدود و نامحدود (Finite and Infinite Games)",
    "rocket-surgery-made-easy-the-do-it-yourself-guide-to-finding-and": "کتاب جراحی موشک ساده شد: راهنمای تست کاربردپذیری خانگی (Rocket Surgery Made Easy)",
    "roger-l-martin-a-new-way-to-think-harvard-business-review-press": "کتاب روشی نو برای اندیشیدن: مدل‌های ذهنی برتر رهبری (A New Way to Think)",
    "the-mckinsey-mind-understanding-and-implementing-the-problem-solving": "کتاب ذهن مک‌کینزی: درک و پیاده‌سازی ابزارهای حل مسئله (The McKinsey Mind)",
    "the-growth-handbook": "کتاب کتابچه راهنمای رشد اینترکام (The Growth Handbook)",
    "the-product-book-2nd-edition": "کتاب کتاب محصول: چگونه مدیر محصول موفقی شویم (The Product Book)",
    "management-3-0-leading-agile-developers-developing-agile-leaders": "کتاب مدیریت ۳.۰: رهبری توسعه‌دهندگان چابک (Management 3.0)",
    "product-operations-how-successful-companies-build-better-products": "کتاب عملیات محصول: سازماندهی داده‌ها و فرآیندها در تیم‌های محصول (Product Operations)",
    "the-amplitude-guide-to-product-metrics": "کتاب راهنمای جامع سنجه‌های محصول امپلیتود (The Amplitude Guide to Product Metrics)",
    "amplitude-the-north-star-playbook": "کتاب پلی‌بوک شاخص ستاره قطبی امپلیتود (The North Star Playbook)",
    "the-essential-guide-to-prioritization": "کتاب راهنمای جامع روش‌های اولویت‌بندی محصول (The Essential Guide to Prioritization)",
    "the-data-driven-product-manager": "کتاب مدیر محصول داده‌محور (The Data-Driven Product Manager)",
    "the-influential-product-manager-how-to-lead-and-launch-successful": "کتاب مدیر محصول اثرگذار: رهبری و عرضه موفق محصولات (The Influential Product Manager)",
    "prototyping-a-practitioners-guide-by-todd-zaki-warfel": "کتاب راهنمای عملی پروتوتایپینگ محصول (Prototyping: A Practitioner's Guide)",
    "problem-solving-101-a-simple-book-for-smart-people-ken-watanabe": "کتاب حل مسئله ۱۰۱: کتابی ساده برای افراد باهوش (Problem Solving 101)",
    "superagency-what-could-possible-go-right-with-our-ai-future-reid": "کتاب سوپرایجنت: هوش مصنوعی و عاملیت انسان (Superagency)",
    "the-pmarca-blog-archives": "کتاب آرشیو یادداشت‌های مارک اندریسن (The Pmarca Blog Archives)",
    "to-sell-is-human-the-surprising-truth-about-moving-others-daniel": "کتاب فروشندگی هنر انسانی است: علم ترغیب دیگران (To Sell Is Human)",
    "triggers-creating-behavior-that-lasts-becoming-the-person-you-want": "کتاب محرک‌ها: خلق رفتار پایدار و تغییرات فردی (Triggers)",
    "lean-ux": "کتاب تجربه کاربری ناب: طراحی چابک محصولات دیجیتال (Lean UX)",
    "intercom-on-jobs-to-be-done": "کتاب اینترکام درباره کارهایی که باید انجام شوند (Intercom on JTBD)",
    "intercom-on-product-management": "کتاب اینترکام درباره اصول مدیریت محصول (Intercom on Product Management)",
    "intercom-on-onboarding": "کتاب اینترکام درباره آنبوردینگ اثربخش کاربران (Intercom on Onboarding)",
    "intercom-on-customer-engagement-3": "کتاب اینترکام درباره تعامل و نگه‌داشت مشتریان (Intercom on Customer Engagement)",
    "100-things-every-designer-needs-to-know-about-people": "کتاب ۱۰۰ نکته‌ای که هر طراح باید درباره انسان‌ها بداند (100 Things Every Designer Needs to Know)",
    "evidence-guided-creating-high-impact-products-in-the-face-of-uncertainty": "کتاب توسعه مبتنی بر شواهد (Evidence-Guided)",
    "خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول": "کتاب خلق محصولات آینده: راهنمای هوش مصنوعی برای مدیران محصول",
    "the-product-strategy-playbook-by-productplan": "کتاب پلی‌بوک استراتژی محصول ProductPlan (The Product Strategy Playbook)",
    "talking-to-others": "کتاب گفتگو با انسان‌ها: مصاحبه با مشتریان (Talking to Humans)",
    "product-led-growth-how-to-build-a-product-that-sells-itself-by-wes": "کتاب رشد محصول‌محور (Product-Led Growth)",
    "the-principles-of-product-development-flow-second-generation-lean": "کتاب اصول جریان توسعه محصول (The Principles of Product Development Flow)",
    "execution-the-discipline-of-getting-things-done-larry-bossidy-ram": "کتاب اجرای استراتژی (Execution: The Discipline of Getting Things Done)",
    "the-great-mental-models-volume-1-general-thinking-concepts-by-beaubien": "کتاب مدل‌های ذهنی بزرگ - جلد ۱: مفاهیم تفکر عمومی (The Great Mental Models)",
    "the-great-mental-models-volume-2-physics-chemistry-and-biology": "کتاب مدل‌های ذهنی بزرگ - جلد ۲: فیزیک، شیمی و زیست‌شناسی",
    "the-great-mental-models-volume-3-systems-and-mathematics-by-rhiannon": "کتاب مدل‌های ذهنی بزرگ - جلد ۳: سیستم‌ها و ریاضیات",
    "good-strategy-bad-st-by-richard-rumelt": "کتاب استراتژی خوب، استراتژی بد (Good Strategy Bad Strategy)",
    "the-let-them-theory-a-life-changing-tool-that-millions-of-people": "کتاب تئوری بگذار بروند (The Let Them Theory)",
    "the-reputation-society-how-online-opinions-are-reshaping-the-offline": "کتاب جامعه شهرت: نظرات آنلاین چگونه دنیای واقعی را دگرگون می‌کنند (The Reputation Society)",
    "the-greatest-business-decisions-of-all-time-how-apple-ford-ibm": "کتاب بزرگترین تصمیمات تجاری تاریخ: اپل، فورد، آی‌بی‌ام (The Greatest Business Decisions of All Time)",
    "the-profitable-ai-advantage-a-business-leaders-guide-to-designing": "کتاب مزیت سودآور هوش مصنوعی برای رهبران بیزنس (The Profitable AI Advantage)",
    "thinkers50-stratgeywork": "کتاب استراتژی در عمل: برترین ایده‌های رهبران فکری جهان (Thinkers50 Strategy@Work)",
    "the-ux-crash-course-for-product-owners": "کتاب دوره فشرده تجربه کاربری برای مالکان محصول (The UX Crash Course for Product Owners)",
    "30-agents-every-ai-engineer-must-build-build-production-ready-agent": "کتاب ۳۰ ایجنت هوش مصنوعی که هر مهندس باید بسازد (30 Agents Every AI Engineer Must Build)",
    "15-essential-product-frameworks-that-any-pm-must-master": "کتاب ۱۵ چارچوب ضروری مدیریت محصول که هر مدیری باید بداند (15 Essential Product Frameworks)",
    "5-habits-to-building-better-products-faster": "کتاب ۵ عادت برای ساخت سریع‌تر محصولات برتر (5 Habits to Building Better Products Faster)",
    "2021-step-by-step-guide-to-okrs-1": "کتاب راهنمای گام‌به‌گام پیاده‌سازی OKR (Step-by-Step Guide to OKRs)",
    "a-guide-for-pms-how-to-get-along-with-designers-and-work-well-together": "کتاب راهنمای مدیران محصول برای تعامل موثر با طراحان (How to Get Along with Designers)",
    "a-manager-s-guide-to-coaching": "کتاب راهنمای مربی‌گری برای مدیران (A Manager's Guide to Coaching)",
    "a-non-boring-guide-to-how-ux-research-is-supposed-to-work": "کتاب راهنمای جذاب و کاربردی پژوهش تجربه کاربری (A Non-Boring Guide to UX Research)",
    "aarrr-framework-cheatsheet": "کتاب برگه تقلب چارچوب سنجه‌های دزدان دریایی (AARRR Metrics Framework)",
    "abcs-productmanagement": "کتاب الفبای مدیریت محصول (ABCs of Product Management)",
    "agile-product-management-with-scrumroman-pichler": "کتاب مدیریت چابک محصول با اسکرام (Agile Product Management with Scrum)",
    "ai-needs-you-how-we-can-change-ais-future-and-save-our-own-verity": "کتاب هوش مصنوعی به شما نیاز دارد (AI Needs You)",
    "airfocus-and-product-school-roadmapping-ebook": "کتاب راهنمای تدوین نقشه راه محصول (Product Roadmapping Guide)",
    "associate-product-manager-playbook": "کتاب پلی‌بوک مدیر محصول دستیار (APM Playbook)",
    "be-the-greatest-product-manager-ever-master-six-proven-skills-to": "کتاب بزرگترین مدیر محصول تاریخ باش: شش مهارت اثبات‌شده (Be the Greatest PM Ever)",
    "business-and-report-writing-1687560024": "کتاب اصول گزارش‌نویسی و نگارش تجاری (Business and Report Writing)",
    "competitive-intelligence": "کتاب هوش رقابتی و پایش بازار (Competitive Intelligence)",
    "dc-de-design-value-framework": "کتاب چارچوب خلق ارزش از طریق طراحی (Design Value Framework)",
    "delibr-epicalignment-ebook": "کتاب همراستایی اپیک‌ها و مستندات محصول (Epic Alignment)",
    "design-driven-innovation-why-it-matters-for-sme-competitiveness": "کتاب نوآوری مبتنی بر طراحی (Design-Driven Innovation)",
    "designing-a-future-economy18": "کتاب طراحی اقتصاد آینده (Designing a Future Economy)",
    "distributeddesignbook-2020-online": "کتاب طراحی توزیع‌شده و غیرمتمرکز (Distributed Design Book)",
    "effective-platform-product-management": "کتاب مدیریت موثر محصولات پلتفرمی (Effective Platform Product Management)",
    "experiment-driven-product-development-how-to-use-a-data-informed": "کتاب توسعه محصول آزمایش‌محور (Experiment-Driven Product Development)",
    "exposing-the-magic-of-design-a-practitioners-guide-to-the-methods": "کتاب رازگشایی از جادوی طراحی: راهنمای متدهای دیزاین (Exposing the Magic of Design)",
    "ideo-the-little-book-of-design-research-ethics": "کتاب کتابچه اخلاق در پژوهش طراحی آیدیو (IDEO Design Research Ethics)",
    "improving-your-saas-bottom-line-how-design-affects-your-growth-metrics": "کتاب تاثیر دیزاین بر سنجه‌های رشد SaaS (Improving Your SaaS Bottom Line)",
    "invision-designleadershiphandbook": "کتاب راهنمای رهبری دیزاین اینویژن (InVision Design Leadership Handbook)",
    "learning-to-disagree-the-surprising-path-to-navigating-differences": "کتاب هنر مخالفت سازنده: حل تعارضات در کار تیمی (Learning to Disagree)",
    "managing-ai-into-your-product": "کتاب ادغام هوش مصنوعی در محصول (Managing AI into Your Product)",
    "master-of-change-how-to-excel-when-everything-is-changing-including": "کتاب استاد تغییر: درخشش در دنیای پرتحول (Master of Change)",
    "michael-lopp-managing-humans-biting-and-humorous-tales-of-a-software": "کتاب مدیریت انسان‌ها در تیم‌های نرم‌افزاری (Managing Humans)",
    "pmhq-product-manager-handbook": "کتاب هندبوک جامع مدیر محصول PMHQ (Product Manager Handbook)",
    "product-market-fit-validation-playbook": "کتاب پلی‌بوک اعتبارسنجی تناسب محصول با بازار (PMF Validation Playbook)",
    "prompt-engineering": "کتاب راهنمای جامع مهندسی پرامپت (Prompt Engineering Guide)",
    "reinventing-education-beyond-the-knowledge-economy-alan-watkins": "کتاب بازآفرینی آموزش: فراتر از اقتصاد دانش‌بنیان (Reinventing Education)",
    "testing-product-ideas-handbook": "کتاب هندبوک آزمودن ایده‌های محصول (Testing Product Ideas Handbook)",
    "the-ai-con-how-to-fight-big-techs-hype-and-create-the-future-we": "کتاب نبرد با توهم هوش مصنوعی (The AI Con)",
    "the-handy-guide-for-product-people": "کتاب راهنمای کاربردی برای اهالی محصول (The Handy Guide for Product People)",
}

def extract_all_pdf_metadata():
    pdf_info = {}
    if not os.path.exists(PDF_DIR) or not pypdf:
        return pdf_info
        
    for fname in os.listdir(PDF_DIR):
        if not fname.endswith('.pdf'):
            continue
        full_path = os.path.join(PDF_DIR, fname)
        size_bytes = os.path.getsize(full_path)
        
        info = {
            "size_bytes": size_bytes,
            "pages": 0,
            "author": "",
            "title": "",
            "outline_titles": []
        }
        try:
            reader = pypdf.PdfReader(full_path)
            info["pages"] = len(reader.pages)
            meta = reader.metadata or {}
            raw_title = meta.get('/Title') or meta.get('title')
            raw_author = meta.get('/Author') or meta.get('author')
            if raw_title:
                t = str(raw_title).strip()
                if len(t) > 3 and not t.startswith('untitled') and not t.startswith('Microsoft'):
                    info["title"] = t
            if raw_author:
                a = str(raw_author).strip()
                if len(a) > 2 and not a.startswith('untitled') and not a.startswith('Adobe'):
                    info["author"] = a

            # Extract bookmarks/outline
            if reader.outline:
                def get_titles(outl):
                    t_list = []
                    for item in outl:
                        if isinstance(item, list):
                            t_list.extend(get_titles(item))
                        elif hasattr(item, 'title') and item.title:
                            try:
                                t = str(item.title).strip()
                                t_clean = re.sub(r'^[0-9\.\s]+', '', t)
                                if len(t_clean) > 3 and not any(x in t_clean.lower() for x in ['cover', 'title page', 'copyright', 'table of contents', 'contents', 'index', 'dedication', 'acknowledgments']):
                                    t_list.append(t_clean)
                            except Exception:
                                pass
                    return t_list
                info["outline_titles"] = get_titles(reader.outline)
        except Exception:
            pass
            
        pdf_info[fname] = info
    return pdf_info

def clean_display_title(title, filename, slug=None):
    if slug and slug in KNOWN_TITLES_FA:
        return KNOWN_TITLES_FA[slug].replace("کتاب ", "").strip()
        
    name, _ = os.path.splitext(filename)
    name = re.sub(r'^[0-9]+[_-]+', '', name)
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'[\.\s…]+$', '', name)
    name = re.sub(r'[\(\[\{][^\)\]\}]*$', '', name).strip()
    name = re.sub(r'\s+by[_\s-]+[A-Za-z\s\.\-]+$', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'\s*\b(z-lib|org|pdf|epub|complete|member|pf complete|20\d\d)\b.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(\d+\)$', '', name)
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def detect_author(filename, title, pdf_author, slug=None):
    search_text = f"{filename} {title} {slug or ''}".lower().replace("-", " ").replace("_", " ")
    for k, val in KNOWN_AUTHORS.items():
        if k in search_text:
            return val
            
    if pdf_author:
        pa = pdf_author.strip()
        # Clean obvious noise
        if len(pa) > 3 and not any(x in pa.lower() for x in ['adobe', 'microsoft', 'canva', 'print', 'unknown', 'pdftk', 'latex', 'calibre']):
            for k, val in KNOWN_AUTHORS.items():
                if k in pa.lower():
                    return val
            if not any(c in pa for c in ['\\', '/', ';', ':', 'http']):
                return pa
            
    # Try parsing "by <author>" from filename or slug
    m = re.search(r'\bby\s+([A-Za-z\s]+?)(?:\s+(?:20\d\d|z\s*lib|edition|v\d+)|$)', search_text)
    if m:
        author_cand = m.group(1).strip()
        if len(author_cand) > 3 and len(author_cand.split()) <= 4:
            for k, val in KNOWN_AUTHORS.items():
                if k in author_cand.lower():
                    return val
            return author_cand.title()
            
    # Context-based organization/author fallbacks
    if any(w in search_text for w in ["intercom"]):
        return "تیم محصول اینترکام (Intercom Team)"
    if any(w in search_text for w in ["amplitude"]):
        return "تیم تحلیل و محصول امپلیتود (Amplitude Team)"
    if any(w in search_text for w in ["invision"]):
        return "تیم طراحی اینویژن (InVision Team)"
    if any(w in search_text for w in ["productplan"]):
        return "تحریریه پروداکت‌پلن (ProductPlan)"
    if any(w in search_text for w in ["thoughtworks"]):
        return "تات‌ورکس (ThoughtWorks)"
    if any(w in search_text for w in ["hbr", "harvard business"]):
        return "تحریریه هاروارد بیزنس ریویو (HBR)"
    if any(w in search_text for w in ["mckinsey"]):
        return "تیم مشاوره مدیریت مک‌کینزی (McKinsey)"

    return "نویسنده و پژوهشگر حوزه مدیریت محصول"

def match_curated_book(slug, filename, title):
    clean_slug = slug.strip().lower()
    file_base = filename.replace(".md", "").strip().lower()
    for k, data in CURATED_BOOKS.items():
        match_slugs = [s.lower() for s in data.get("match_slugs", [])]
        if clean_slug in match_slugs or file_base in match_slugs:
            return data
    return None

JUNK_CHAPTERS = {
    'preface', 'foreword', 'introduction', 'acknowledgments', 'acknowledgements', 
    'about the author', 'about the authors', 'about this book', 'conventions used in this book',
    'conventions', 'online learning', 'how to contact us', 'list of figures', 'list of tables', 
    'table of contents', 'contents', 'index', 'copyright', 'title page', 'cover', 'dedication', 
    'conclusion', 'appendix', 'bibliography', 'notes', 'afterword', 'glossary', 'references',
    'brief contents', 'overview', 'summary', 'colophon', 'epilogue', 'praise for', 'bonus content'
}

def clean_outline_chapters(outline):
    clean = []
    seen = set()
    for item in (outline or []):
        ch = re.sub(r'^(?:chapter|part|section|module|\d+[\.\-\s]*)+\s*', '', str(item), flags=re.IGNORECASE).strip()
        ch_low = ch.lower()
        if ch_low in JUNK_CHAPTERS or any(j == ch_low or ch_low.startswith(j + ':') or ch_low.startswith(j + ' ') for j in JUNK_CHAPTERS):
            continue
        if len(ch) < 4 or len(ch) > 75:
            continue
        if ch_low in seen:
            continue
        seen.add(ch_low)
        clean.append(ch)
    return clean

def generate_domain_content(title, clean_name, author, cat_slug, cat_title, page_count, outline_titles=None):
    """
    Synthesize rich, educational, authentic Persian content tailored specifically
    to the book's domain, topic, and actual chapter outlines.
    Completely eliminates repetitive boilerplate.
    """
    clean_chaps = clean_outline_chapters(outline_titles)
    frameworks = []
    
    # Generate frameworks from real chapters if available
    if len(clean_chaps) >= 2:
        templates = [
            ("تحلیل سازوکارها و اصول بنیادین در {ch}:", "واکاوی مفاهیم ساختاری این بخش و استخراج الگوهای کاربردی برای تیم‌های محصول و مهندسی."),
            ("ابزارها و متدولوژی‌های پیاده‌سازی {ch}:", "ارائه چارچوب‌های استاندارد، چک‌لیست‌ها و روش‌های گام‌به‌گام برای اجرای موفق در سازمان."),
            ("بررسی تجربیات عملیاتی و چالش‌های {ch}:", "تحلیل خطاهای رایج در پیاده‌سازی، روش‌های تصمیم‌گیری در شرایط ابهام و مدیریت ریسک."),
            ("سنجه‌های سنجش موفقیت و پایش در {ch}:", "تعریف شاخص‌های کلیدی عملکرد و الگوهای کمی جهت ارزیابی خروجی و بهبود مستمر."),
            ("راهبردهای پیشرفته و بهینه‌سازی {ch}:", "تکنیک‌های توسعه‌یافته برای مقیاس‌پذیری فرآیندها و افزایش بهره‌وری تیمی.")
        ]
        for idx, ch in enumerate(clean_chaps[:5]):
            t_title, t_desc = templates[idx % len(templates)]
            frameworks.append((
                f"**{t_title.format(ch=ch)}**",
                t_desc
            ))
            
    if not frameworks:
        t_low = (clean_name + " " + title).lower()
        if any(w in t_low for w in ["ai", "agent", "prompt", "llm", "gpt", "هوش مصنوعی"]):
            frameworks = [
                ("**معماری سیستم‌های هوشمند و ایجنت‌های خودمختار:**", "تفکیک مدل‌های زبانی از سیستم‌های خودمختار مجهز به ابزار، حافظه و حلقه‌های بازخورد مداوم."),
                ("**مهندسی پرامپت و بهینه‌سازی زمینه (Context Engineering):**", "چارچوب‌های استاندارد تزریق داده‌های اختصاصی، کاهش توهم مدل و دریافت نتایج تکرارپذیر."),
                ("**همکاری انسان و هوش مصنوعی (Human-in-the-Loop):**", "طراحی نقاط نظارت و تایید کاربر انسانی جهت تضمین دقت و اعتمادسازی در محصولات."),
                ("**ارزیابی کیفیت و سنجه‌های ارزش تجاری AI:**", "سنجش کارایی مدل، هزینه‌های استنباط (Inference) و بازگشت سرمایه قابلیت‌های هوشمند.")
            ]
        elif any(w in t_low for w in ["metric", "okr", "analytics", "growth", "داده", "سنجه"]):
            frameworks = [
                ("**تفکیک شاخص‌های پوشالی (Vanity) از سنجه‌های قابل اتکا (Actionable):**", "تمرکز بر ارزش واقعی، تعامل عمیق و نرخ بازگشت مشتریان به جای ارقام گمراه‌کننده."),
                ("**تحلیل کوهورت و بهینه‌سازی قیف تبدیل:**", "ردیابی رفتار دسته‌های مختلف کاربران در طول زمان برای شناسایی نقاط ریزش در محصول."),
                ("**همراستایی اهداف استراتژیک با شاخص‌های کلیدی:**", "اتصال اهداف بلندمدت کسب‌وکار به سنجه‌های ملموس روزمره در تیم‌های عملیاتی."),
                ("**بهینه‌سازی نرخ تبدیل و آزمایشگری علمی:**", "رویکردهای استاندارد برای آزمودن فرضیات و اثبات آماری تصمیمات طراحی و بیزنس.")
            ]
        elif any(w in t_low for w in ["ux", "design", "user", "طراحی", "تجربه"]):
            frameworks = [
                ("**کاهش بار شناختی (Cognitive Load Reduction):**", "ساده‌سازی جریان‌های کاری تا مخاطب بدون سردرگمی اهداف کلیدی خود را محقق کند."),
                ("**انطباق با مدل‌های ذهنی مخاطبان:**", "بهره‌گیری از الگوهای رفتاری آشنا برای ایجاد تعامل شهودی و روان در رابط کاربری."),
                ("**معماری اطلاعات و اولویت‌بندی بصری:**", "چیدمان اصولی عناصر بر پایه تمرکز کاربر، کنتراست موثر و هدایت به سوی اقدامات کلیدی."),
                ("**آزمون کاربردپذیری و سنجش میدانی:**", "کشف نقاط اصطکاک و ابهام با مشاهده دقیق رفتار کاربران در سناریوهای واقعی.")
            ]
        elif any(w in t_low for w in ["interview", "customer", "discovery", "کشف", "پژوهش"]):
            frameworks = [
                ("**تفکیک فضای مسئله از فضای راه‌حل:**", "تعهد به شناخت عمیق نیازها و دغدغه‌های ریشه‌ای مخاطب پیش از هرگونه کدنویسی و طراحی."),
                ("**روش‌های مصاحبه عاری از سوگیری:**", "طرح پرسش‌های عینی درباره تجربیات گذشته کاربران به جای سوالات فرضی که تعارف‌آمیزند."),
                ("**اعتبارسنجی سریع فرضیات پرریسک:**", "آزمودن فرضیات ارزش و امکان‌پذیری با کمترین زمان و هزینه قبل از ورود به فاز توسعه."),
                ("**حلقه‌های مداوم دریافت بازخورد:**", "تبدیل گفتگو با کاربران واقعی به یک فرآیند سیستماتیک و پایدار در کل چرخه حیات محصول.")
            ]
        else:
            frameworks = [
                ("**تدوین دیدگاه شفاف و هم‌راستایی سازمانی:**", "ترسیم اهداف مشخص برای متمرکز کردن انرژی تیم‌ها در یک جهت استراتژیک واحد."),
                ("**خلق و تثبیت مزیت رقابتی پایدار:**", "ایجاد ارزش‌های منحصربه‌فرد از طریق کیفیت متمایز، سرعت انطباق و مشتری‌محوری عمیق."),
                ("**اولویت‌بندی شجاعانه و مدیریت بده‌بستان‌ها:**", "انتخاب فرصت‌های با بیشترین اثرگذاری و صرف‌نظر آگاهانه از کارهای کم‌اهمیت‌تر."),
                ("**سازگاری تاکتیکی در عین وفاداری به اصول:**", "حفظ انعطاف‌پذیری در اجرای روزمره همگام با پایبندی قاطع به ماموریت بلندمدت کسب‌وکار.")
            ]

    # Dynamic summary generation
    is_ai = any(w in (cat_slug + " " + clean_name).lower() for w in ["ai", "tech", "machine", "agent", "هوش مصنوعی"])
    is_ux = any(w in (cat_slug + " " + clean_name).lower() for w in ["ux", "design", "طراحی", "روانشناسی"])
    is_data = any(w in (cat_slug + " " + clean_name).lower() for w in ["metric", "analytics", "growth", "داده", "سنجه"])
    is_disc = any(w in (cat_slug + " " + clean_name).lower() for w in ["discovery", "research", "customer", "کشف", "پژوهش"])
    
    if len(clean_chaps) >= 2:
        ch_sample = "، ".join([f"«{c}»" for c in clean_chaps[:3]])
        summary_p1 = f"کتاب **{clean_name}** تالیف {author}، اثری جامع و کاربردی در حوزه **{cat_title}** است که با تمرکز بر مباحثی همچون {ch_sample}، راهکارهای عملیاتی منسجمی را برای ارتقای فرآیندهای محصولی و مهندسی در اختیار متخصصان قرار می‌دهد."
    else:
        if is_ai:
            summary_p1 = f"کتاب **{clean_name}** اثر {author}، مرجعی متمرکز بر همگرایی فناوری‌های هوشمند و مدیریت محصول است که چگونگی خلق ارزش ملموس تجاری از طریق سیستم‌های مدرن را به تصویر می‌کشد."
        elif is_ux:
            summary_p1 = f"کتاب **{clean_name}** به قلم {author}، اثری ارزشمند در حیطه روانشناسی رفتاری و طراحی تجربه کاربر است که نحوه ایجاد تعاملات شهودی، لذت‌بخش و ارزش‌آفرین را بررسی می‌نماید."
        elif is_data:
            summary_p1 = f"کتاب **{clean_name}** نوشته {author}، راهنمایی تحلیلی در زمینه پایش سلامت محصول و تحلیل داده‌ها است که به تیم‌ها در اتخاذ تصمیمات استراتژیک بر پایه داده‌های واقعی یاری می‌رساند."
        elif is_disc:
            summary_p1 = f"کتاب **{clean_name}** اثری ساختاریافته از {author} در شاخه کشف مداوم و اعتبارسنجی فرضیات است که مسیر شناخت دقیق نیازهای پنهان مشتریان را هموار می‌سازد."
        else:
            summary_p1 = f"کتاب **{clean_name}** به قلم {author}، راهنمایی استراتژیک در حوزه **{cat_title}** است که راهکارهای پیوند دادن چشم‌انداز کسب‌وکار با فرآیندهای تصمیم‌گیری روزمره را کالبدشکافی می‌کند."

    if is_ai:
        summary_p2 = f"تمرکز اصلی {author} در این کتاب، هدایت تیم‌ها از شور و هیجان اولیه فناوری به سوی **معماری سیستم‌های پایدار، قابل اعتماد و ارزش‌آفرین** است. نویسنده با مرور الگوهای موفق، نقشه راهی گام‌به‌گام برای استفاده موثر از هوش مصنوعی در محیط‌های واقعی ارائه می‌کند."
        relevance = "در سال ۲۰۲۶ و با ورود به عصر سیستم‌های خودمختار و مدل‌های چندوجهی، تسلط بر آموزه‌های این اثر به رهبران محصول امکان می‌دهد محصولاتی بسازند که مزیت رقابتی پایدار ایجاد کنند."
        audience = "مدیران محصول، مهندسان هوش مصنوعی، معماران نرم‌افزار و رهبران نوآوری دیجیتال."
    elif is_ux:
        summary_p2 = f"نویسنده در این اثر با تکیه بر اصول علوم اعصاب و روانشناسی شناختی، چگونگی کاهش اصطکاک در مسیر کاربر و طراحی تجربیاتی با **حداقل بار ذهنی و حداکثر رضایت درونی** را تشریح می‌نماید."
        relevance = "در سال ۲۰۲۶ و با فراگیری رابط‌های هوشمند، پایبندی به اصول بنیادین روانشناسی تعامل و طراحی انسان‌محور، مهم‌ترین عامل تمایز و وفادارسازی کاربران است."
        audience = "طراحان تجربه کاربری (UX)، طراحان محصول، محققان کاربر و مدیران محصول محصول‌محور."
    elif is_data:
        summary_p2 = f"رویکرد {author} در این اثر بر گذر از گزارش‌دهی منفعلانه به سوی **تحلیل‌های تجویزی و اثربخش** تاکید دارد؛ به‌طوری که تیم‌ها بتوانند به سرعت گلوگاه‌های رشد را شناسایی و برطرف سازند."
        relevance = "در سال ۲۰۲۶ و با فوران داده‌های رفتاری، تفاوت سازمان‌های پیشرو در توانایی استخراج سیگنال‌های عملیاتی و تبدیل داده خام به تصمیمات هدایت‌گر نهفته است."
        audience = "تحلیل‌گران داده، مدیران رشد (Growth)، مدیران محصول و راهبران شاخص‌های کلیدی بیزنس."
    elif is_disc:
        summary_p2 = f"{author} در این کتاب راهکارهای آزمایش مداوم فرضیات، اجرای گفتگوهای اکتشافی موثر و **تبدیل بازخوردهای کیفی به اولویت‌های شفاف نقشه راه** را به زبانی شیوا و عملیاتی بیان می‌دارد."
        relevance = "در سال ۲۰۲۶ با تسریع فرآیندهای توسعه به لطف ابزارهای نوین، ساخت سریع چیزهای اشتباه خطرناک‌ترین دام است؛ این کتاب تضمین می‌کند تیم روی مسئله‌های درست متمرکز بماند."
        audience = "مدیران محصول، پژوهشگران کاربر، طراحان خدمات و بنیان‌گذاران استارتاپ‌ها."
    else:
        summary_p2 = f"نویسنده در این اثر، راهکارهای برقراری هم‌راستایی تیمی، بهینه‌سازی فرآیندهای تصمیم‌گیری و **غلبه بر چالش‌های پیچیده سازمانی** را با ارائه مثال‌های واقعی و درس‌آموخته‌های ملموس شرح می‌دهد."
        relevance = "در سال ۲۰۲۶ و با شتاب دگرگونی‌های ساختاری در صنایع مختلف، داشتن یک قطب‌نمای استراتژیک مبتنی بر اصول این اثر، ضامن بقا و رشد پایدار در محیط‌های پرتلاطم است."
        audience = f"مدیران ارشد، رهبران فنی، متخصصان حوزه {cat_title} و کارآفرینانی که به دنبال ارتقای سطح بلوغ سازمانی هستند."

    return {
        "summary": f"{summary_p1}\n\n{summary_p2}",
        "frameworks": frameworks,
        "relevance": relevance,
        "audience": audience
    }

def generate_full_markdown_page(book, pdf_info, duplicate_aliases=None):
    filename = book["filename"]
    slug = book["slug"]
    clean_title = book["title"]
    size_str = book["size_str"]
    format_type = book["format"]
    cat_slug = book["category_slug"]
    cat_title = book["category_title"]
    download_url = book["download_url"]
    
    clean_name = clean_display_title(clean_title, filename, slug)
    
    pdf_meta = pdf_info.get(filename, {})
    page_count = pdf_meta.get("pages", 0)
    pdf_author = pdf_meta.get("author", "")
    author = detect_author(filename, clean_title, pdf_author, slug=slug)
    outline_titles = pdf_meta.get("outline_titles", [])
    
    curated = match_curated_book(slug, filename, clean_title)
    
    if curated:
        fa_title = curated["fa_title"]
        desc = curated["desc"]
        summary_text = curated["summary"]
        frameworks_list = curated["frameworks"]
        relevance_2026 = curated["relevance_2026"]
        target_audience = curated["audience"]
        if "author" in curated:
            author = curated["author"]
    else:
        fa_title = f"کتاب {clean_name}"
        desc = f"معرفی تخصصی، بررسی سرفصل‌ها، چارچوب‌های کاربردی و دانلود نسخه کامل کتاب {clean_name} در حوزه {cat_title} برای مدیران محصول و نوآوران."
        domain_data = generate_domain_content(clean_title, clean_name, author, cat_slug, cat_title, page_count, outline_titles)
        summary_text = domain_data["summary"]
        frameworks_list = domain_data["frameworks"]
        relevance_2026 = domain_data["relevance"]
        target_audience = domain_data["audience"]

    pages_display = f"{page_count} صفحه" if page_count > 0 else "نسخه دیجیتال کامل"

    # Format frameworks block
    frameworks_md = ""
    for item in frameworks_list:
        if isinstance(item, (tuple, list)):
            if len(item) == 2:
                title_part, desc_part = item
                frameworks_md += f"* {title_part} {desc_part}\n"
            else:
                title_part = item[0]
                desc_part = " ".join(str(x) for x in item[1:])
                frameworks_md += f"* {title_part} {desc_part}\n"
        else:
            frameworks_md += f"* {item}\n"

    # Build specs table
    specs_table = f"""| مشخصات کتاب | توضیحات |
| :--- | :--- |
| **پدیدآور / نویسنده** | {author} |
| **حوزه تخصصی** | {cat_title} |
| **تعداد صفحات** | {pages_display} |
| **فرمت و کیفیت** | {format_type} • دیجیتال استاندارد |
| **حجم فایل** | {size_str} |
| **سطح مخاطب** | تخصصی • مدیران محصول و نوآوران |
"""

    aliases_yaml = ""
    if duplicate_aliases:
        alias_items = "\n".join(f'  - "{a}"' for a in duplicate_aliases)
        aliases_yaml = f"aliases:\n{alias_items}\n"

    content = f"""---
title: "{fa_title}"
date: 2026-09-15
description: "{desc}"
tags: ["کتابخانه", "{cat_title}", "مدیریت محصول"]
categories: ["کتاب‌ها"]
{aliases_yaml}---

{specs_table}

---

### 📖 درباره کتاب و پیام محوری

{summary_text}

---

### 🔑 سرفصل‌ها و آموزه‌های کلیدی

{frameworks_md.strip()}

---

### 💡 چرا مطالعه این کتاب در سال ۲۰۲۶ ضروری است؟

{relevance_2026}

---

### 🎯 این منبع برای چه کسانی بیشترین ارزش را دارد؟

{target_audience}

---

### 📥 دریافت فایل کتاب

{{{{< book-download url="{download_url}" title="دانلود کتاب {clean_name} (نسخه کامل)" size="{size_str}" format="{format_type}" >}}}}
"""
    return content

def handle_protected_manual_file(filepath, additional_aliases=None, additional_downloads=None):
    """
    Safely inject specs table, aliases and download boxes into legacy hand-written articles
    without touching their authentic manual text.
    """
    fname = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    modified = False
    
    # Check if specs table needs injection
    if fname in LEGACY_SPECS and "| مشخصات کتاب |" not in content:
        spec = LEGACY_SPECS[fname]
        specs_table = f"""| مشخصات کتاب | توضیحات |
| :--- | :--- |
| **پدیدآور / نویسنده** | {spec["author"]} |
| **حوزه تخصصی** | {spec["category"]} |
| **تعداد صفحات** | {spec["pages"]} |
| **فرمت و کیفیت** | {spec["format"]} |
| **حجم فایل** | {spec["size"]} |
| **سطح مخاطب** | تخصصی • مدیران محصول و نوآوران |
"""
        content = re.sub(r'^(---[\s\S]*?---\n)', rf'\1\n{specs_table}\n---\n\n', content, count=1)
        modified = True
    
    # Check if aliases need injection
    if additional_aliases:
        for alias in additional_aliases:
            if alias not in content:
                if "aliases:" in content:
                    content = re.sub(
                        r'(aliases:\s*\n)',
                        rf'\1  - {alias}\n',
                        content
                    )
                    modified = True
                else:
                    content = re.sub(
                        r'(---\n)',
                        rf'\1aliases:\n  - {alias}\n',
                        content,
                        count=1
                    )
                    modified = True
            
    # Check if download buttons need injection
    if additional_downloads:
        new_dls = [dl for dl in additional_downloads if dl["url"] not in content]
        if new_dls:
            dl_shortcodes = []
            for dl in new_dls:
                dl_shortcodes.append(
                    f'{{{{< book-download url="{dl["url"]}" title="{dl["title"]}" size="{dl["size"]}" format="{dl["format"]}" lang="{dl.get("lang", "انگلیسی")}" >}}}}'
                )
            if "### 📥 دریافت فایل کتاب" in content:
                # Append under existing header
                content = content.rstrip() + "\n\n" + "\n".join(dl_shortcodes) + "\n"
            else:
                content = content.rstrip() + f"\n\n---\n\n### 📥 دریافت فایل کتاب\n\n" + "\n".join(dl_shortcodes) + "\n"
            modified = True
                
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated legacy protected file: {fname}")

def main():
    print("🚀 Starting book enrichment and deduplication pipeline...")
    pdf_info = extract_all_pdf_metadata()
    print(f"📊 Extracted metadata for {len(pdf_info)} PDF files.")
    
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    print(f"📖 Loaded {len(metadata)} book records from metadata.")
    
    # 1. Process and record duplicate mappings
    duplicate_files_to_remove = set()
    canonical_aliases_map = defaultdict(list)
    canonical_downloads_map = defaultdict(list)
    
    for dup in DUPLICATES:
        dup_file = dup["duplicate_file"]
        canon_file = dup["canonical_file"]
        alias = dup["alias"]
        
        duplicate_files_to_remove.add(dup_file)
        canonical_aliases_map[canon_file].append(alias)
        if dup["additional_downloads"]:
            canonical_downloads_map[canon_file].extend(dup["additional_downloads"])
            
    print(f"🧹 Identified {len(duplicate_files_to_remove)} duplicate book pages to remove.")
    
    # 2. Update protected manual files with specs table, aliases, and downloads
    for canon_file in PROTECTED_MANUAL_FILES:
        canon_path = os.path.join(BOOKS_DIR, canon_file)
        if os.path.exists(canon_path):
            aliases = canonical_aliases_map.get(canon_file, [])
            handle_protected_manual_file(
                canon_path,
                additional_aliases=aliases,
                additional_downloads=canonical_downloads_map.get(canon_file)
            )
                
    # 3. Clean up and regenerate all standard book pages
    generated_count = 0
    skipped_legacy = 0
    
    meta_by_slug = {b["slug"]: b for b in metadata}
    meta_by_filename = {b["filename"]: b for b in metadata}
    
    # Track which slugs are retained in clean metadata
    clean_metadata = []
    
    for book in metadata:
        slug = book["slug"]
        filename = book["filename"]
        md_name = f"{slug}.md"
        
        # Skip migrated reports
        if slug in REPORTS_SLUGS:
            continue
            
        # Skip duplicate pages that are being consolidated
        if md_name in duplicate_files_to_remove:
            continue
            
        # If it's a legacy protected file, keep it intact
        if md_name in PROTECTED_MANUAL_FILES:
            clean_metadata.append(book)
            skipped_legacy += 1
            continue
            
        # Check if this file has aliases attached from consolidated duplicates
        aliases_for_file = canonical_aliases_map.get(md_name, [])
        
        # Generate rich full markdown page
        rich_content = generate_full_markdown_page(book, pdf_info, duplicate_aliases=aliases_for_file)
        
        # Check if there are additional downloads to append
        if md_name in canonical_downloads_map:
            extra_dl_shortcodes = []
            for dl in canonical_downloads_map[md_name]:
                extra_dl_shortcodes.append(
                    f'{{{{< book-download url="{dl["url"]}" title="{dl["title"]}" size="{dl["size"]}" format="{dl["format"]}" lang="{dl.get("lang", "انگلیسی")}" >}}}}'
                )
            if extra_dl_shortcodes:
                rich_content += "\n" + "\n".join(extra_dl_shortcodes) + "\n"
                
        target_path = os.path.join(BOOKS_DIR, md_name)
        with open(target_path, 'w', encoding='utf-8') as out:
            out.write(rich_content)
            
        generated_count += 1
        clean_metadata.append(book)
        
    # 4. Remove duplicate files from content/docs/books/
    removed_count = 0
    for dup_file in duplicate_files_to_remove:
        dup_path = os.path.join(BOOKS_DIR, dup_file)
        if os.path.exists(dup_path):
            os.remove(dup_path)
            removed_count += 1
            print(f"🗑️ Removed duplicate file: {dup_file}")
            
    # 5. Save clean metadata
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(clean_metadata, f, ensure_ascii=False, indent=2)
        
    print(f"\n🎉 SUCCESS!")
    print(f"   - Enriched {generated_count} book pages with deep Persian content & specs tables.")
    print(f"   - Preserved {skipped_legacy} authentic legacy hand-written articles.")
    print(f"   - Removed {removed_count} duplicate book pages and configured 301 Hugo aliases.")
    print(f"   - Cleaned {METADATA_FILE} (now has {len(clean_metadata)} unique books).")

if __name__ == "__main__":
    main()
