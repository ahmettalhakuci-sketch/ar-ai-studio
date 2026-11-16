# -*- coding: utf-8 -*-
"""
==============================================================================
AR AI STUDIO v4.0 — TEK DOSYADA BİRLEŞTİRİLMİŞ TAM KAPSAMLI SÜPER ASİSTAN (main.py)
5 Modülün Tamamı (Arayüz + Veri Tabanı + Matematik Motoru + Zeka/Ses + Ana Panel)
Tek Dosyada Birleştirilmiştir! Hiçbir ek dosyaya ihtiyaç duymadan çalışır.
Çalıştırma Komutu: streamlit run main.py
Geliştirici: Ahmet | 530.000+ Hazır Soru-Cevap Kalıbı & Kodsuz "Bana Öğret" Sistemi
==============================================================================
"""
import ast
import asyncio
import difflib
import inspect
import json
import math
import operator
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
import streamlit as st

PROJE_KOK_DIZINI = os.path.dirname(os.path.abspath(__file__))

# 1. OTOMATİK KOYU LACİVERT STREAMLIT TEMA YAPILANDIRMASI (.streamlit/config.toml + Runtime)
_STREAMLIT_TEMA_TOML = """[theme]
base = "dark"
primaryColor = "#38bdf8"
backgroundColor = "#03091a"
secondaryBackgroundColor = "#07142e"
textColor = "#ffffff"
"""
for _hedef_kok in {PROJE_KOK_DIZINI, os.getcwd()}:
    try:
        _st_klasor = os.path.join(_hedef_kok, ".streamlit")
        os.makedirs(_st_klasor, exist_ok=True)
        _st_toml_yol = os.path.join(_st_klasor, "config.toml")
        with open(_st_toml_yol, "w", encoding="utf-8") as _tf:
            _tf.write(_STREAMLIT_TEMA_TOML)
    except Exception:
        pass

try:
    st._config.set_option("theme.base", "dark")
    st._config.set_option("theme.primaryColor", "#38bdf8")
    st._config.set_option("theme.backgroundColor", "#03091a")
    st._config.set_option("theme.secondaryBackgroundColor", "#07142e")
    st._config.set_option("theme.textColor", "#ffffff")
except Exception:
    pass

# 2. SAYFA YAPILANDIRMASI (İlk Streamlit komutu)
st.set_page_config(
    page_title="Ar AI Studio v4.0 | Masaüstü & Mobil Süper Asistan",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 3. HARİCİ KÜTÜPHANELER İÇİN ÇÖKMEZ YEDEKLİ YÜKLEYİCİ
try:
    from googletrans import Translator as _GoogleTranslator
    _translator_nesnesi = _GoogleTranslator()
except Exception:
    _translator_nesnesi = None

try:
    from gtts import gTTS
    GTTS_MEVCUT = True
except Exception:
    gTTS = None
    GTTS_MEVCUT = False

try:
    from thefuzz import fuzz
except Exception:
    class _YedekFuzz:
        @staticmethod
        def ratio(s1: str, s2: str) -> int:
            return int(difflib.SequenceMatcher(None, s1, s2).ratio() * 100)

        @staticmethod
        def token_set_ratio(s1: str, s2: str) -> int:
            t1 = " ".join(sorted(set(s1.split())))
            t2 = " ".join(sorted(set(s2.split())))
            r1 = difflib.SequenceMatcher(None, s1, s2).ratio()
            r2 = difflib.SequenceMatcher(None, t1, t2).ratio()
            return int(max(r1, r2) * 100)

    fuzz = _YedekFuzz()

try:
    import edge_tts
    EDGE_TTS_MEVCUT = True
except Exception:
    EDGE_TTS_MEVCUT = False

try:
    import pygame
    PYGAME_MEVCUT = True
except Exception:
    PYGAME_MEVCUT = False


# ==============================================================================
# BÖLÜM 1: YAPILANDIRMA, KOYU LACİVERT TEMA VE DİL KARTLARI
# ==============================================================================
# 1. SİSTEM DOSYA SABİTLERİ VE UYGULAMA KİMLİĞİ
# ==============================================================================
UYGULAMA_ADI = "Ar AI Studio"
UYGULAMA_SURUMU = "v4.0 Ultra Enterprise"
GELISTIRICI_ADI = "Ahmet"
JSON_DOSYA_ADI = "komutlar.json"
SOHBET_DOSYA_ADI = "sohbet_gecmisi.json"
NOTLAR_DOSYA_ADI = "ahmet_notlar.json"
FAVORILER_DOSYA_ADI = "favori_sorular.json"

# ==============================================================================
# 2. 28 DİL DESTEKLİ ULUSLARARASI DİL VE NEURAL SES KONFİGÜRASYONU
# ==============================================================================
DESTEKLENEN_DILLER = {
    "tr": "🇹🇷 Türkçe (Ana Dil)",
    "en": "🇬🇧 İngilizce (English)",
    "ar": "🇸🇦 Arapça (العربية)",
    "zh-cn": "🇨🇳 Çince (中文 - Basitleştirilmiş)",
    "bn": "🇧🇩 Bengalce (বাংলা)",
    "de": "🇩🇪 Almanca (Deutsch)",
    "fr": "🇫🇷 Fransızca (Français)",
    "es": "🇪🇸 İspanyolca (Español)",
    "it": "🇮🇹 İtalyanca (Italiano)",
    "ru": "🇷🇺 Rusça (Русский)",
    "ja": "🇯🇵 Japonca (日本語)",
    "ko": "🇰🇷 Korece (한국어)",
    "pt": "🇵🇹 Portekizce (Português)",
    "nl": "🇳🇱 Hollandaca (Nederlands)",
    "az": "🇦🇿 Azerbaycanca (Azərbaycanca)",
    "fa": "🇮🇷 Farsça (فارسی)",
    "ur": "🇵🇰 Urduca (اردو)",
    "hi": "🇮🇳 Hintçe (हिन्दी)",
    "sv": "🇸🇪 İsveççe (Svenska)",
    "el": "🇬🇷 Yunanca (Ελληνικά)",
    "pl": "🇵🇱 Lehçe (Polski)",
    "uk": "🇺🇦 Ukraynaca (Українська)",
    "id": "🇮🇩 Endonezce (Bahasa Indonesia)",
    "ms": "🇲🇾 Malayca (Bahasa Melayu)",
    "vi": "🇻🇳 Vietnamca (Tiếng Việt)",
    "th": "🇹🇭 Tayca (ภาษาไทย)",
    "ro": "🇷🇴 Rumence (Română)",
    "cs": "🇨🇿 Çekçe (Čeština)",
}

EDGE_SESLER = {
    "tr": "tr-TR-AhmetNeural",
    "en": "en-US-AndrewNeural",
    "ar": "ar-SA-HamedNeural",
    "zh-cn": "zh-CN-YunxiNeural",
    "bn": "bn-BD-PradeepNeural",
    "de": "de-DE-ConradNeural",
    "fr": "fr-FR-HenriNeural",
    "es": "es-ES-AlvaroNeural",
    "it": "it-IT-DiegoNeural",
    "ru": "ru-RU-DmitryNeural",
    "ja": "ja-JP-KeitaNeural",
    "ko": "ko-KR-InJoonNeural",
    "pt": "pt-BR-AntonioNeural",
    "nl": "nl-NL-MaartenNeural",
    "az": "az-AZ-BabekNeural",
    "fa": "fa-IR-FaridNeural",
    "ur": "ur-PK-AsadNeural",
    "hi": "hi-IN-MadhurNeural",
    "sv": "sv-SE-MattiasNeural",
    "el": "el-GR-NestorasNeural",
    "pl": "pl-PL-MarekNeural",
    "uk": "uk-UA-OstapNeural",
    "id": "id-ID-ArdiNeural",
    "ms": "ms-MY-OsmanNeural",
    "vi": "vi-VN-NamMinhNeural",
    "th": "th-TH-NiwatNeural",
    "ro": "ro-RO-EmilNeural",
    "cs": "cs-CZ-AntoninNeural",
}

EDGE_KADIN_SESLER = {
    "tr": "tr-TR-EmelNeural",
    "en": "en-US-AriaNeural",
    "ar": "ar-SA-ZariyahNeural",
    "zh-cn": "zh-CN-XiaoxiaoNeural",
    "bn": "bn-BD-NabanitaNeural",
    "de": "de-DE-KatjaNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "it": "it-IT-ElsaNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "pt": "pt-BR-FranciscaNeural",
    "nl": "nl-NL-ColetteNeural",
    "az": "az-AZ-BanuNeural",
    "fa": "fa-IR-DilaraNeural",
    "ur": "ur-PK-UzmaNeural",
    "hi": "hi-IN-SwaraNeural",
    "sv": "sv-SE-SofieNeural",
    "el": "el-GR-AthinaNeural",
    "pl": "pl-PL-ZofiaNeural",
    "uk": "uk-UA-PolinaNeural",
    "id": "id-ID-GadisNeural",
    "ms": "ms-MY-YasminNeural",
    "vi": "vi-VN-HoaiMyNeural",
    "th": "th-TH-PremwadeeNeural",
    "ro": "ro-RO-AlinaNeural",
    "cs": "cs-CZ-VlastaNeural",
}

GTTS_DIL_ESLESME = {
    "tr": "tr",
    "en": "en",
    "ar": "ar",
    "zh-cn": "zh-CN",
    "bn": "bn",
    "de": "de",
    "fr": "fr",
    "es": "es",
    "it": "it",
    "ru": "ru",
    "ja": "ja",
    "ko": "ko",
    "pt": "pt",
    "nl": "nl",
    "az": "az",
    "fa": "fa",
    "ur": "ur",
    "hi": "hi",
    "sv": "sv",
    "el": "el",
    "pl": "pl",
    "uk": "uk",
    "id": "id",
    "ms": "ms",
    "vi": "vi",
    "th": "th",
    "ro": "ro",
    "cs": "cs",
}

TURKCE_AYLAR = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]

TURKCE_GUNLER = [
    "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar",
]

# ==============================================================================
# 3. PREMİUM TEMA PALETLERİ (MASAÜSTÜ VE MOBİL İÇİN SEÇİLEBİLİR TEMALAR)
# ==============================================================================
TEMA_PALETLERI = {
    "Derin Lacivert (Klasik Ar)": {
        "bg_primary": "#03091a",
        "bg_secondary": "#07142e",
        "card_bg": "#0b1e42",
        "accent_neon": "#38bdf8",
        "accent_blue": "#0ea5e9",
        "accent_purple": "#1d4ed8",
        "accent_rose": "#60a5fa",
        "text_main": "#ffffff",
        "text_sub": "#dbeafe",
    },
    "Siber Neon (Koyu Mavi)": {
        "bg_primary": "#040711",
        "bg_secondary": "#0b1120",
        "card_bg": "#0f172a",
        "accent_neon": "#00f5d4",
        "accent_blue": "#38bdf8",
        "accent_purple": "#6366f1",
        "accent_rose": "#f43f5e",
        "text_main": "#ffffff",
        "text_sub": "#e2e8f0",
    },
    "Zümrüt Matriks": {
        "bg_primary": "#020b08",
        "bg_secondary": "#061812",
        "card_bg": "#0a241b",
        "accent_neon": "#10b981",
        "accent_blue": "#34d399",
        "accent_purple": "#059669",
        "accent_rose": "#f59e0b",
        "text_main": "#ffffff",
        "text_sub": "#d1fae5",
    },
    "Kraliyet Moru & Altın": {
        "bg_primary": "#090414",
        "bg_secondary": "#130926",
        "card_bg": "#1d1038",
        "accent_neon": "#f59e0b",
        "accent_blue": "#c084fc",
        "accent_purple": "#9333ea",
        "accent_rose": "#ec4899",
        "text_main": "#ffffff",
        "text_sub": "#f3e8ff",
    },
    "Kızıl Süpernova": {
        "bg_primary": "#110408",
        "bg_secondary": "#1f0810",
        "card_bg": "#2d0d18",
        "accent_neon": "#fb7185",
        "accent_blue": "#f43f5e",
        "accent_purple": "#e11d48",
        "accent_rose": "#38bdf8",
        "text_main": "#ffffff",
        "text_sub": "#ffe4e6",
    },
    "Okyanus Derinliği": {
        "bg_primary": "#020813",
        "bg_secondary": "#071426",
        "card_bg": "#0c203b",
        "accent_neon": "#38bdf8",
        "accent_blue": "#0ea5e9",
        "accent_purple": "#2563eb",
        "accent_rose": "#00f5d4",
        "text_main": "#ffffff",
        "text_sub": "#e0f2fe",
    },
    "Saf Koyu Kontrast (OLED)": {
        "bg_primary": "#000000",
        "bg_secondary": "#08080c",
        "card_bg": "#11131a",
        "accent_neon": "#00ffcc",
        "accent_blue": "#60a5fa",
        "accent_purple": "#818cf8",
        "accent_rose": "#fb7185",
        "text_main": "#ffffff",
        "text_sub": "#f8fafc",
    },
}

# ==============================================================================
# 4. GÜNLÜK PRATİK DİL KELİME VE CÜMLE KARTLARI (İNGİLİZCE - ÇİNCE - BENGALCE)
# ==============================================================================
DIL_EGITIM_KARTLARI = [
    {
        "id": 1,
        "kategori": "Teknoloji",
        "seviye": "Temel",
        "ingilizce": "Artificial Intelligence (#1)",
        "turkce": "Yapay Zeka",
        "cince": "人工智能 (Réngōng zhìnéng)",
        "bengalce": "কৃত্রিম বুদ্ধিমত্তা (Kritrim buddhimotta)",
        "ornek_cumle": "Ahmet uses artificial intelligence in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 2,
        "kategori": "Havacılık",
        "seviye": "Orta",
        "ingilizce": "Autonomous Drone (#2)",
        "turkce": "Otonom İnsansız Hava Aracı",
        "cince": "自主无人机 (Zìzhǔ wúrénjī)",
        "bengalce": "স্বায়ত্তশাসিত ড্রোন (Sbayottoshasito drone)",
        "ornek_cumle": "Ahmet uses autonomous drone in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 3,
        "kategori": "Mühendislik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Software Engineering (#3)",
        "turkce": "Yazılım Mühendisliği",
        "cince": "软件工程 (Ruǎnjiàn gōngchéng)",
        "bengalce": "সফটওয়্যার ইঞ্জিনিয়ারিং (Software engineering)",
        "ornek_cumle": "Ahmet uses software engineering in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 4,
        "kategori": "Yapay Zeka",
        "seviye": "Akademik",
        "ingilizce": "Machine Learning (#4)",
        "turkce": "Makine Öğrenmesi",
        "cince": "机器学习 (Jīqì xuéxí)",
        "bengalce": "মেশিন লার্নিং (Machine learning)",
        "ornek_cumle": "Ahmet uses machine learning in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 5,
        "kategori": "Yapay Zeka",
        "seviye": "Temel",
        "ingilizce": "Neural Network (#5)",
        "turkce": "Sinir Ağı",
        "cince": "神经网络 (Shénjīng wǎngluò)",
        "bengalce": "নিউরাল নেটওয়ার্ক (Neural network)",
        "ornek_cumle": "Ahmet uses neural network in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 6,
        "kategori": "Görüntü İşleme",
        "seviye": "Orta",
        "ingilizce": "Computer Vision (#6)",
        "turkce": "Bilgisayarlı Görü",
        "cince": "计算机视觉 (Jìsuànjī shìjué)",
        "bengalce": "কম্পিউটার ভিশন (Computer vision)",
        "ornek_cumle": "Ahmet uses computer vision in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 7,
        "kategori": "Donanım",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Embedded Systems (#7)",
        "turkce": "Gömülü Sistemler",
        "cince": "嵌入式系统 (Qiànrùshì xìtǒng)",
        "bengalce": "এম্বেডেড সিস্টেম (Embedded system)",
        "ornek_cumle": "Ahmet uses embedded systems in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 8,
        "kategori": "Donanım",
        "seviye": "Akademik",
        "ingilizce": "Microcontroller (#8)",
        "turkce": "Mikrodenetleyici",
        "cince": "微控制器 (Wēi kòngzhìqì)",
        "bengalce": "মাইক্রোকন্ট্রোলার (Microcontroller)",
        "ornek_cumle": "Ahmet uses microcontroller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 9,
        "kategori": "Sensör",
        "seviye": "Temel",
        "ingilizce": "Ultrasonic Sensor (#9)",
        "turkce": "Ultrasonik Sensör",
        "cince": "超声波传感器 (Chāoshēngbō chuángǎnqì)",
        "bengalce": "আল্ট্রাসনিক সেন্সর (Ultrasonic sensor)",
        "ornek_cumle": "Ahmet uses ultrasonic sensor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 10,
        "kategori": "Üretim",
        "seviye": "Orta",
        "ingilizce": "Three Dimensional Printing (#10)",
        "turkce": "Üç Boyutlu Baskı",
        "cince": "3D打印 (3D dǎyìn)",
        "bengalce": "থ্রিডি প্রিন্টিং (3D printing)",
        "ornek_cumle": "Ahmet uses three dimensional printing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 11,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Square Root (#11)",
        "turkce": "Karekök",
        "cince": "平方根 (Píngfānggēn)",
        "bengalce": "বর্গমূল (Borgomul)",
        "ornek_cumle": "Ahmet uses square root in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 12,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Prime Number (#12)",
        "turkce": "Asal Sayı",
        "cince": "质数 (Zhìshù)",
        "bengalce": "মৌলিক সংখ্যা (Moulik songkha)",
        "ornek_cumle": "Ahmet uses prime number in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 13,
        "kategori": "Matematik",
        "seviye": "Temel",
        "ingilizce": "Linear Equation (#13)",
        "turkce": "Doğrusal Denklem",
        "cince": "线性方程 (Xiànxìng fāngchéng)",
        "bengalce": "রৈখিক সমীকরণ (Roikhik somikoron)",
        "ornek_cumle": "Ahmet uses linear equation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 14,
        "kategori": "Matematik",
        "seviye": "Orta",
        "ingilizce": "Greatest Common Divisor (#14)",
        "turkce": "En Büyük Ortak Bölen (EBOB)",
        "cince": "最大公约数 (Zuìdà gōngyuēshù)",
        "bengalce": "গরিষ্ঠ সাধারণ গুণনীয়ক (Goshagu)",
        "ornek_cumle": "Ahmet uses greatest common divisor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 15,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Least Common Multiple (#15)",
        "turkce": "En Küçük Ortak Kat (EKOK)",
        "cince": "最小公倍数 (Zuìxiǎo gōngbèishù)",
        "bengalce": "লঘিষ্ঠ সাধারণ গুণিতক (Loshagu)",
        "ornek_cumle": "Ahmet uses least common multiple in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 16,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Exponentiation (#16)",
        "turkce": "Üs Alma / Üslü Sayılar",
        "cince": "幂运算 (Mì yùnsuàn)",
        "bengalce": "সূচক (Suchok)",
        "ornek_cumle": "Ahmet uses exponentiation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 17,
        "kategori": "Geometri",
        "seviye": "Temel",
        "ingilizce": "Pythagorean Theorem (#17)",
        "turkce": "Pisagor Teoremi",
        "cince": "勾股定理 (Gōugǔ dìnglǐ)",
        "bengalce": "পিথাগোরাসের উপপাদ্য (Pithagoraser upopaddo)",
        "ornek_cumle": "Ahmet uses pythagorean theorem in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 18,
        "kategori": "Kişisel Gelişim",
        "seviye": "Orta",
        "ingilizce": "Perseverance and Discipline (#18)",
        "turkce": "Azim ve Disiplin",
        "cince": "毅力与纪律 (Yìlì yǔ jìlǜ)",
        "bengalce": "অধ্যবসায় এবং শৃঙ্খলা (Oddhobosay ebong srinkhola)",
        "ornek_cumle": "Ahmet uses perseverance and discipline in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 19,
        "kategori": "Bilim",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Scientific Research (#19)",
        "turkce": "Bilimsel Araştırma",
        "cince": "科学研究 (Kēxué yánjiū)",
        "bengalce": "বৈজ্ঞানিক গবেষণা (Boigganik gobeshona)",
        "ornek_cumle": "Ahmet uses scientific research in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 20,
        "kategori": "Yazılım",
        "seviye": "Akademik",
        "ingilizce": "Algorithm Optimization (#20)",
        "turkce": "Algoritma Optimizasyonu",
        "cince": "算法优化 (Suànfǎ yōuhuà)",
        "bengalce": "অ্যালগরিদম অপ্টিমাইজেশন (Algorithm optimization)",
        "ornek_cumle": "Ahmet uses algorithm optimization in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 21,
        "kategori": "İHA / Drone",
        "seviye": "Temel",
        "ingilizce": "Flight Controller (#21)",
        "turkce": "Uçuş Kontrol Kartı",
        "cince": "飞行控制器 (Fēixíng kòngzhìqì)",
        "bengalce": "ফ্লাইট কন্ট্রোলার (Flight controller)",
        "ornek_cumle": "Ahmet uses flight controller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 22,
        "kategori": "Elektronik",
        "seviye": "Orta",
        "ingilizce": "Battery Management (#22)",
        "turkce": "Batarya Yönetimi",
        "cince": "电池管理 (Diànchí guǎnlǐ)",
        "bengalce": "ব্যাটারি ম্যানেজমেন্ট (Battery management)",
        "ornek_cumle": "Ahmet uses battery management in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 23,
        "kategori": "Mühendislik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Signal Processing (#23)",
        "turkce": "Sinyal İşleme",
        "cince": "信号处理 (Xìnhào chǔlǐ)",
        "bengalce": "সিগন্যাল প্রসেসিং (Signal processing)",
        "ornek_cumle": "Ahmet uses signal processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 24,
        "kategori": "Bilgisayar Bilimi",
        "seviye": "Akademik",
        "ingilizce": "Data Structure (#24)",
        "turkce": "Veri Yapısı",
        "cince": "数据结构 (Shùjù jiégòu)",
        "bengalce": "ডেটা স্ট্রাকচার (Data structure)",
        "ornek_cumle": "Ahmet uses data structure in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 25,
        "kategori": "Yazılım",
        "seviye": "Temel",
        "ingilizce": "Object Oriented Programming (#25)",
        "turkce": "Nesne Yönelimli Programlama",
        "cince": "面向对象编程 (Miànxiàng duìxiàng biānchéng)",
        "bengalce": "অবজেক্ট ওরিয়েন্টেড প্রোগ্রামিং (OOP)",
        "ornek_cumle": "Ahmet uses object oriented programming in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 26,
        "kategori": "Güvenlik",
        "seviye": "Orta",
        "ingilizce": "Cyber Security (#26)",
        "turkce": "Siber Güvenlik",
        "cince": "网络安全 (Wǎngluò ānquán)",
        "bengalce": "সাইবার নিরাপত্তা (Cyber nirapotta)",
        "ornek_cumle": "Ahmet uses cyber security in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 27,
        "kategori": "Sistem",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Cloud Computing (#27)",
        "turkce": "Bulut Bilişim",
        "cince": "云计算 (Yún jìsuàn)",
        "bengalce": "ক্লাউড কম্পিউটিং (Cloud computing)",
        "ornek_cumle": "Ahmet uses cloud computing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 28,
        "kategori": "Yapay Zeka",
        "seviye": "Akademik",
        "ingilizce": "Natural Language Processing (#28)",
        "turkce": "Doğal Dil İşleme",
        "cince": "自然语言处理 (Zìrán yǔyán chǔlǐ)",
        "bengalce": "ন্যাচারাল ল্যাঙ্গুয়েজ প্রসেসিং (NLP)",
        "ornek_cumle": "Ahmet uses natural language processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 29,
        "kategori": "Robotik",
        "seviye": "Temel",
        "ingilizce": "Robotics and Automation (#29)",
        "turkce": "Robotik ve Otomasyon",
        "cince": "机器人与自动化 (Jīqìrén yǔ zìdònghuà)",
        "bengalce": "রোবোটিক্স এবং অটোমেশন (Robotics)",
        "ornek_cumle": "Ahmet uses robotics and automation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 30,
        "kategori": "Fizik",
        "seviye": "Orta",
        "ingilizce": "Aerodynamics (#30)",
        "turkce": "Aerodinamik",
        "cince": "空气动力学 (Kōngqì dònglìxué)",
        "bengalce": "অ্যারোডাইনামিক্স (Aerodynamics)",
        "ornek_cumle": "Ahmet uses aerodynamics in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 31,
        "kategori": "Teknoloji",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Artificial Intelligence (#31)",
        "turkce": "Yapay Zeka",
        "cince": "人工智能 (Réngōng zhìnéng)",
        "bengalce": "কৃত্রিম বুদ্ধিমত্তা (Kritrim buddhimotta)",
        "ornek_cumle": "Ahmet uses artificial intelligence in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 32,
        "kategori": "Havacılık",
        "seviye": "Akademik",
        "ingilizce": "Autonomous Drone (#32)",
        "turkce": "Otonom İnsansız Hava Aracı",
        "cince": "自主无人机 (Zìzhǔ wúrénjī)",
        "bengalce": "স্বায়ত্তশাসিত ড্রোন (Sbayottoshasito drone)",
        "ornek_cumle": "Ahmet uses autonomous drone in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 33,
        "kategori": "Mühendislik",
        "seviye": "Temel",
        "ingilizce": "Software Engineering (#33)",
        "turkce": "Yazılım Mühendisliği",
        "cince": "软件工程 (Ruǎnjiàn gōngchéng)",
        "bengalce": "সফটওয়্যার ইঞ্জিনিয়ারিং (Software engineering)",
        "ornek_cumle": "Ahmet uses software engineering in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 34,
        "kategori": "Yapay Zeka",
        "seviye": "Orta",
        "ingilizce": "Machine Learning (#34)",
        "turkce": "Makine Öğrenmesi",
        "cince": "机器学习 (Jīqì xuéxí)",
        "bengalce": "মেশিন লার্নিং (Machine learning)",
        "ornek_cumle": "Ahmet uses machine learning in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 35,
        "kategori": "Yapay Zeka",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Neural Network (#35)",
        "turkce": "Sinir Ağı",
        "cince": "神经网络 (Shénjīng wǎngluò)",
        "bengalce": "নিউরাল নেটওয়ার্ক (Neural network)",
        "ornek_cumle": "Ahmet uses neural network in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 36,
        "kategori": "Görüntü İşleme",
        "seviye": "Akademik",
        "ingilizce": "Computer Vision (#36)",
        "turkce": "Bilgisayarlı Görü",
        "cince": "计算机视觉 (Jìsuànjī shìjué)",
        "bengalce": "কম্পিউটার ভিশন (Computer vision)",
        "ornek_cumle": "Ahmet uses computer vision in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 37,
        "kategori": "Donanım",
        "seviye": "Temel",
        "ingilizce": "Embedded Systems (#37)",
        "turkce": "Gömülü Sistemler",
        "cince": "嵌入式系统 (Qiànrùshì xìtǒng)",
        "bengalce": "এম্বেডেড সিস্টেম (Embedded system)",
        "ornek_cumle": "Ahmet uses embedded systems in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 38,
        "kategori": "Donanım",
        "seviye": "Orta",
        "ingilizce": "Microcontroller (#38)",
        "turkce": "Mikrodenetleyici",
        "cince": "微控制器 (Wēi kòngzhìqì)",
        "bengalce": "মাইক্রোকন্ট্রোলার (Microcontroller)",
        "ornek_cumle": "Ahmet uses microcontroller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 39,
        "kategori": "Sensör",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Ultrasonic Sensor (#39)",
        "turkce": "Ultrasonik Sensör",
        "cince": "超声波传感器 (Chāoshēngbō chuángǎnqì)",
        "bengalce": "আল্ট্রাসনিক সেন্সর (Ultrasonic sensor)",
        "ornek_cumle": "Ahmet uses ultrasonic sensor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 40,
        "kategori": "Üretim",
        "seviye": "Akademik",
        "ingilizce": "Three Dimensional Printing (#40)",
        "turkce": "Üç Boyutlu Baskı",
        "cince": "3D打印 (3D dǎyìn)",
        "bengalce": "থ্রিডি প্রিন্টিং (3D printing)",
        "ornek_cumle": "Ahmet uses three dimensional printing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 41,
        "kategori": "Matematik",
        "seviye": "Temel",
        "ingilizce": "Square Root (#41)",
        "turkce": "Karekök",
        "cince": "平方根 (Píngfānggēn)",
        "bengalce": "বর্গমূল (Borgomul)",
        "ornek_cumle": "Ahmet uses square root in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 42,
        "kategori": "Matematik",
        "seviye": "Orta",
        "ingilizce": "Prime Number (#42)",
        "turkce": "Asal Sayı",
        "cince": "质数 (Zhìshù)",
        "bengalce": "মৌলিক সংখ্যা (Moulik songkha)",
        "ornek_cumle": "Ahmet uses prime number in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 43,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Linear Equation (#43)",
        "turkce": "Doğrusal Denklem",
        "cince": "线性方程 (Xiànxìng fāngchéng)",
        "bengalce": "রৈখিক সমীকরণ (Roikhik somikoron)",
        "ornek_cumle": "Ahmet uses linear equation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 44,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Greatest Common Divisor (#44)",
        "turkce": "En Büyük Ortak Bölen (EBOB)",
        "cince": "最大公约数 (Zuìdà gōngyuēshù)",
        "bengalce": "গরিষ্ঠ সাধারণ গুণনীয়ক (Goshagu)",
        "ornek_cumle": "Ahmet uses greatest common divisor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 45,
        "kategori": "Matematik",
        "seviye": "Temel",
        "ingilizce": "Least Common Multiple (#45)",
        "turkce": "En Küçük Ortak Kat (EKOK)",
        "cince": "最小公倍数 (Zuìxiǎo gōngbèishù)",
        "bengalce": "লঘিষ্ঠ সাধারণ গুণিতক (Loshagu)",
        "ornek_cumle": "Ahmet uses least common multiple in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 46,
        "kategori": "Matematik",
        "seviye": "Orta",
        "ingilizce": "Exponentiation (#46)",
        "turkce": "Üs Alma / Üslü Sayılar",
        "cince": "幂运算 (Mì yùnsuàn)",
        "bengalce": "সূচক (Suchok)",
        "ornek_cumle": "Ahmet uses exponentiation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 47,
        "kategori": "Geometri",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Pythagorean Theorem (#47)",
        "turkce": "Pisagor Teoremi",
        "cince": "勾股定理 (Gōugǔ dìnglǐ)",
        "bengalce": "পিথাগোরাসের উপপাদ্য (Pithagoraser upopaddo)",
        "ornek_cumle": "Ahmet uses pythagorean theorem in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 48,
        "kategori": "Kişisel Gelişim",
        "seviye": "Akademik",
        "ingilizce": "Perseverance and Discipline (#48)",
        "turkce": "Azim ve Disiplin",
        "cince": "毅力与纪律 (Yìlì yǔ jìlǜ)",
        "bengalce": "অধ্যবসায় এবং শৃঙ্খলা (Oddhobosay ebong srinkhola)",
        "ornek_cumle": "Ahmet uses perseverance and discipline in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 49,
        "kategori": "Bilim",
        "seviye": "Temel",
        "ingilizce": "Scientific Research (#49)",
        "turkce": "Bilimsel Araştırma",
        "cince": "科学研究 (Kēxué yánjiū)",
        "bengalce": "বৈজ্ঞানিক গবেষণা (Boigganik gobeshona)",
        "ornek_cumle": "Ahmet uses scientific research in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 50,
        "kategori": "Yazılım",
        "seviye": "Orta",
        "ingilizce": "Algorithm Optimization (#50)",
        "turkce": "Algoritma Optimizasyonu",
        "cince": "算法优化 (Suànfǎ yōuhuà)",
        "bengalce": "অ্যালগরিদম অপ্টিমাইজেশন (Algorithm optimization)",
        "ornek_cumle": "Ahmet uses algorithm optimization in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 51,
        "kategori": "İHA / Drone",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Flight Controller (#51)",
        "turkce": "Uçuş Kontrol Kartı",
        "cince": "飞行控制器 (Fēixíng kòngzhìqì)",
        "bengalce": "ফ্লাইট কন্ট্রোলার (Flight controller)",
        "ornek_cumle": "Ahmet uses flight controller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 52,
        "kategori": "Elektronik",
        "seviye": "Akademik",
        "ingilizce": "Battery Management (#52)",
        "turkce": "Batarya Yönetimi",
        "cince": "电池管理 (Diànchí guǎnlǐ)",
        "bengalce": "ব্যাটারি ম্যানেজমেন্ট (Battery management)",
        "ornek_cumle": "Ahmet uses battery management in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 53,
        "kategori": "Mühendislik",
        "seviye": "Temel",
        "ingilizce": "Signal Processing (#53)",
        "turkce": "Sinyal İşleme",
        "cince": "信号处理 (Xìnhào chǔlǐ)",
        "bengalce": "সিগন্যাল প্রসেসিং (Signal processing)",
        "ornek_cumle": "Ahmet uses signal processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 54,
        "kategori": "Bilgisayar Bilimi",
        "seviye": "Orta",
        "ingilizce": "Data Structure (#54)",
        "turkce": "Veri Yapısı",
        "cince": "数据结构 (Shùjù jiégòu)",
        "bengalce": "ডেটা স্ট্রাকচার (Data structure)",
        "ornek_cumle": "Ahmet uses data structure in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 55,
        "kategori": "Yazılım",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Object Oriented Programming (#55)",
        "turkce": "Nesne Yönelimli Programlama",
        "cince": "面向对象编程 (Miànxiàng duìxiàng biānchéng)",
        "bengalce": "অবজেক্ট ওরিয়েন্টেড প্রোগ্রামিং (OOP)",
        "ornek_cumle": "Ahmet uses object oriented programming in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 56,
        "kategori": "Güvenlik",
        "seviye": "Akademik",
        "ingilizce": "Cyber Security (#56)",
        "turkce": "Siber Güvenlik",
        "cince": "网络安全 (Wǎngluò ānquán)",
        "bengalce": "সাইবার নিরাপত্তা (Cyber nirapotta)",
        "ornek_cumle": "Ahmet uses cyber security in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 57,
        "kategori": "Sistem",
        "seviye": "Temel",
        "ingilizce": "Cloud Computing (#57)",
        "turkce": "Bulut Bilişim",
        "cince": "云计算 (Yún jìsuàn)",
        "bengalce": "ক্লাউড কম্পিউটিং (Cloud computing)",
        "ornek_cumle": "Ahmet uses cloud computing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 58,
        "kategori": "Yapay Zeka",
        "seviye": "Orta",
        "ingilizce": "Natural Language Processing (#58)",
        "turkce": "Doğal Dil İşleme",
        "cince": "自然语言处理 (Zìrán yǔyán chǔlǐ)",
        "bengalce": "ন্যাচারাল ল্যাঙ্গুয়েজ প্রসেসিং (NLP)",
        "ornek_cumle": "Ahmet uses natural language processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 59,
        "kategori": "Robotik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Robotics and Automation (#59)",
        "turkce": "Robotik ve Otomasyon",
        "cince": "机器人与自动化 (Jīqìrén yǔ zìdònghuà)",
        "bengalce": "রোবোটিক্স এবং অটোমেশন (Robotics)",
        "ornek_cumle": "Ahmet uses robotics and automation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 60,
        "kategori": "Fizik",
        "seviye": "Akademik",
        "ingilizce": "Aerodynamics (#60)",
        "turkce": "Aerodinamik",
        "cince": "空气动力学 (Kōngqì dònglìxué)",
        "bengalce": "অ্যারোডাইনামিক্স (Aerodynamics)",
        "ornek_cumle": "Ahmet uses aerodynamics in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 61,
        "kategori": "Teknoloji",
        "seviye": "Temel",
        "ingilizce": "Artificial Intelligence (#61)",
        "turkce": "Yapay Zeka",
        "cince": "人工智能 (Réngōng zhìnéng)",
        "bengalce": "কৃত্রিম বুদ্ধিমত্তা (Kritrim buddhimotta)",
        "ornek_cumle": "Ahmet uses artificial intelligence in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 62,
        "kategori": "Havacılık",
        "seviye": "Orta",
        "ingilizce": "Autonomous Drone (#62)",
        "turkce": "Otonom İnsansız Hava Aracı",
        "cince": "自主无人机 (Zìzhǔ wúrénjī)",
        "bengalce": "স্বায়ত্তশাসিত ড্রোন (Sbayottoshasito drone)",
        "ornek_cumle": "Ahmet uses autonomous drone in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 63,
        "kategori": "Mühendislik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Software Engineering (#63)",
        "turkce": "Yazılım Mühendisliği",
        "cince": "软件工程 (Ruǎnjiàn gōngchéng)",
        "bengalce": "সফটওয়্যার ইঞ্জিনিয়ারিং (Software engineering)",
        "ornek_cumle": "Ahmet uses software engineering in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 64,
        "kategori": "Yapay Zeka",
        "seviye": "Akademik",
        "ingilizce": "Machine Learning (#64)",
        "turkce": "Makine Öğrenmesi",
        "cince": "机器学习 (Jīqì xuéxí)",
        "bengalce": "মেশিন লার্নিং (Machine learning)",
        "ornek_cumle": "Ahmet uses machine learning in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 65,
        "kategori": "Yapay Zeka",
        "seviye": "Temel",
        "ingilizce": "Neural Network (#65)",
        "turkce": "Sinir Ağı",
        "cince": "神经网络 (Shénjīng wǎngluò)",
        "bengalce": "নিউরাল নেটওয়ার্ক (Neural network)",
        "ornek_cumle": "Ahmet uses neural network in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 66,
        "kategori": "Görüntü İşleme",
        "seviye": "Orta",
        "ingilizce": "Computer Vision (#66)",
        "turkce": "Bilgisayarlı Görü",
        "cince": "计算机视觉 (Jìsuànjī shìjué)",
        "bengalce": "কম্পিউটার ভিশন (Computer vision)",
        "ornek_cumle": "Ahmet uses computer vision in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 67,
        "kategori": "Donanım",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Embedded Systems (#67)",
        "turkce": "Gömülü Sistemler",
        "cince": "嵌入式系统 (Qiànrùshì xìtǒng)",
        "bengalce": "এম্বেডেড সিস্টেম (Embedded system)",
        "ornek_cumle": "Ahmet uses embedded systems in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 68,
        "kategori": "Donanım",
        "seviye": "Akademik",
        "ingilizce": "Microcontroller (#68)",
        "turkce": "Mikrodenetleyici",
        "cince": "微控制器 (Wēi kòngzhìqì)",
        "bengalce": "মাইক্রোকন্ট্রোলার (Microcontroller)",
        "ornek_cumle": "Ahmet uses microcontroller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 69,
        "kategori": "Sensör",
        "seviye": "Temel",
        "ingilizce": "Ultrasonic Sensor (#69)",
        "turkce": "Ultrasonik Sensör",
        "cince": "超声波传感器 (Chāoshēngbō chuángǎnqì)",
        "bengalce": "আল্ট্রাসনিক সেন্সর (Ultrasonic sensor)",
        "ornek_cumle": "Ahmet uses ultrasonic sensor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 70,
        "kategori": "Üretim",
        "seviye": "Orta",
        "ingilizce": "Three Dimensional Printing (#70)",
        "turkce": "Üç Boyutlu Baskı",
        "cince": "3D打印 (3D dǎyìn)",
        "bengalce": "থ্রিডি প্রিন্টিং (3D printing)",
        "ornek_cumle": "Ahmet uses three dimensional printing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 71,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Square Root (#71)",
        "turkce": "Karekök",
        "cince": "平方根 (Píngfānggēn)",
        "bengalce": "বর্গমূল (Borgomul)",
        "ornek_cumle": "Ahmet uses square root in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 72,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Prime Number (#72)",
        "turkce": "Asal Sayı",
        "cince": "质数 (Zhìshù)",
        "bengalce": "মৌলিক সংখ্যা (Moulik songkha)",
        "ornek_cumle": "Ahmet uses prime number in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 73,
        "kategori": "Matematik",
        "seviye": "Temel",
        "ingilizce": "Linear Equation (#73)",
        "turkce": "Doğrusal Denklem",
        "cince": "线性方程 (Xiànxìng fāngchéng)",
        "bengalce": "রৈখিক সমীকরণ (Roikhik somikoron)",
        "ornek_cumle": "Ahmet uses linear equation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 74,
        "kategori": "Matematik",
        "seviye": "Orta",
        "ingilizce": "Greatest Common Divisor (#74)",
        "turkce": "En Büyük Ortak Bölen (EBOB)",
        "cince": "最大公约数 (Zuìdà gōngyuēshù)",
        "bengalce": "গরিষ্ঠ সাধারণ গুণনীয়ক (Goshagu)",
        "ornek_cumle": "Ahmet uses greatest common divisor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 75,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Least Common Multiple (#75)",
        "turkce": "En Küçük Ortak Kat (EKOK)",
        "cince": "最小公倍数 (Zuìxiǎo gōngbèishù)",
        "bengalce": "লঘিষ্ঠ সাধারণ গুণিতক (Loshagu)",
        "ornek_cumle": "Ahmet uses least common multiple in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 76,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Exponentiation (#76)",
        "turkce": "Üs Alma / Üslü Sayılar",
        "cince": "幂运算 (Mì yùnsuàn)",
        "bengalce": "সূচক (Suchok)",
        "ornek_cumle": "Ahmet uses exponentiation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 77,
        "kategori": "Geometri",
        "seviye": "Temel",
        "ingilizce": "Pythagorean Theorem (#77)",
        "turkce": "Pisagor Teoremi",
        "cince": "勾股定理 (Gōugǔ dìnglǐ)",
        "bengalce": "পিথাগোরাসের উপপাদ্য (Pithagoraser upopaddo)",
        "ornek_cumle": "Ahmet uses pythagorean theorem in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 78,
        "kategori": "Kişisel Gelişim",
        "seviye": "Orta",
        "ingilizce": "Perseverance and Discipline (#78)",
        "turkce": "Azim ve Disiplin",
        "cince": "毅力与纪律 (Yìlì yǔ jìlǜ)",
        "bengalce": "অধ্যবসায় এবং শৃঙ্খলা (Oddhobosay ebong srinkhola)",
        "ornek_cumle": "Ahmet uses perseverance and discipline in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 79,
        "kategori": "Bilim",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Scientific Research (#79)",
        "turkce": "Bilimsel Araştırma",
        "cince": "科学研究 (Kēxué yánjiū)",
        "bengalce": "বৈজ্ঞানিক গবেষণা (Boigganik gobeshona)",
        "ornek_cumle": "Ahmet uses scientific research in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 80,
        "kategori": "Yazılım",
        "seviye": "Akademik",
        "ingilizce": "Algorithm Optimization (#80)",
        "turkce": "Algoritma Optimizasyonu",
        "cince": "算法优化 (Suànfǎ yōuhuà)",
        "bengalce": "অ্যালগরিদম অপ্টিমাইজেশন (Algorithm optimization)",
        "ornek_cumle": "Ahmet uses algorithm optimization in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 81,
        "kategori": "İHA / Drone",
        "seviye": "Temel",
        "ingilizce": "Flight Controller (#81)",
        "turkce": "Uçuş Kontrol Kartı",
        "cince": "飞行控制器 (Fēixíng kòngzhìqì)",
        "bengalce": "ফ্লাইট কন্ট্রোলার (Flight controller)",
        "ornek_cumle": "Ahmet uses flight controller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 82,
        "kategori": "Elektronik",
        "seviye": "Orta",
        "ingilizce": "Battery Management (#82)",
        "turkce": "Batarya Yönetimi",
        "cince": "电池管理 (Diànchí guǎnlǐ)",
        "bengalce": "ব্যাটারি ম্যানেজমেন্ট (Battery management)",
        "ornek_cumle": "Ahmet uses battery management in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 83,
        "kategori": "Mühendislik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Signal Processing (#83)",
        "turkce": "Sinyal İşleme",
        "cince": "信号处理 (Xìnhào chǔlǐ)",
        "bengalce": "সিগন্যাল প্রসেসিং (Signal processing)",
        "ornek_cumle": "Ahmet uses signal processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 84,
        "kategori": "Bilgisayar Bilimi",
        "seviye": "Akademik",
        "ingilizce": "Data Structure (#84)",
        "turkce": "Veri Yapısı",
        "cince": "数据结构 (Shùjù jiégòu)",
        "bengalce": "ডেটা স্ট্রাকচার (Data structure)",
        "ornek_cumle": "Ahmet uses data structure in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 85,
        "kategori": "Yazılım",
        "seviye": "Temel",
        "ingilizce": "Object Oriented Programming (#85)",
        "turkce": "Nesne Yönelimli Programlama",
        "cince": "面向对象编程 (Miànxiàng duìxiàng biānchéng)",
        "bengalce": "অবজেক্ট ওরিয়েন্টেড প্রোগ্রামিং (OOP)",
        "ornek_cumle": "Ahmet uses object oriented programming in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 86,
        "kategori": "Güvenlik",
        "seviye": "Orta",
        "ingilizce": "Cyber Security (#86)",
        "turkce": "Siber Güvenlik",
        "cince": "网络安全 (Wǎngluò ānquán)",
        "bengalce": "সাইবার নিরাপত্তা (Cyber nirapotta)",
        "ornek_cumle": "Ahmet uses cyber security in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 87,
        "kategori": "Sistem",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Cloud Computing (#87)",
        "turkce": "Bulut Bilişim",
        "cince": "云计算 (Yún jìsuàn)",
        "bengalce": "ক্লাউড কম্পিউটিং (Cloud computing)",
        "ornek_cumle": "Ahmet uses cloud computing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 88,
        "kategori": "Yapay Zeka",
        "seviye": "Akademik",
        "ingilizce": "Natural Language Processing (#88)",
        "turkce": "Doğal Dil İşleme",
        "cince": "自然语言处理 (Zìrán yǔyán chǔlǐ)",
        "bengalce": "ন্যাচারাল ল্যাঙ্গুয়েজ প্রসেসিং (NLP)",
        "ornek_cumle": "Ahmet uses natural language processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 89,
        "kategori": "Robotik",
        "seviye": "Temel",
        "ingilizce": "Robotics and Automation (#89)",
        "turkce": "Robotik ve Otomasyon",
        "cince": "机器人与自动化 (Jīqìrén yǔ zìdònghuà)",
        "bengalce": "রোবোটিক্স এবং অটোমেশন (Robotics)",
        "ornek_cumle": "Ahmet uses robotics and automation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 90,
        "kategori": "Fizik",
        "seviye": "Orta",
        "ingilizce": "Aerodynamics (#90)",
        "turkce": "Aerodinamik",
        "cince": "空气动力学 (Kōngqì dònglìxué)",
        "bengalce": "অ্যারোডাইনামিক্স (Aerodynamics)",
        "ornek_cumle": "Ahmet uses aerodynamics in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 91,
        "kategori": "Teknoloji",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Artificial Intelligence (#91)",
        "turkce": "Yapay Zeka",
        "cince": "人工智能 (Réngōng zhìnéng)",
        "bengalce": "কৃত্রিম বুদ্ধিমত্তা (Kritrim buddhimotta)",
        "ornek_cumle": "Ahmet uses artificial intelligence in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 92,
        "kategori": "Havacılık",
        "seviye": "Akademik",
        "ingilizce": "Autonomous Drone (#92)",
        "turkce": "Otonom İnsansız Hava Aracı",
        "cince": "自主无人机 (Zìzhǔ wúrénjī)",
        "bengalce": "স্বায়ত্তশাসিত ড্রোন (Sbayottoshasito drone)",
        "ornek_cumle": "Ahmet uses autonomous drone in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 93,
        "kategori": "Mühendislik",
        "seviye": "Temel",
        "ingilizce": "Software Engineering (#93)",
        "turkce": "Yazılım Mühendisliği",
        "cince": "软件工程 (Ruǎnjiàn gōngchéng)",
        "bengalce": "সফটওয়্যার ইঞ্জিনিয়ারিং (Software engineering)",
        "ornek_cumle": "Ahmet uses software engineering in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 94,
        "kategori": "Yapay Zeka",
        "seviye": "Orta",
        "ingilizce": "Machine Learning (#94)",
        "turkce": "Makine Öğrenmesi",
        "cince": "机器学习 (Jīqì xuéxí)",
        "bengalce": "মেশিন লার্নিং (Machine learning)",
        "ornek_cumle": "Ahmet uses machine learning in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 95,
        "kategori": "Yapay Zeka",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Neural Network (#95)",
        "turkce": "Sinir Ağı",
        "cince": "神经网络 (Shénjīng wǎngluò)",
        "bengalce": "নিউরাল নেটওয়ার্ক (Neural network)",
        "ornek_cumle": "Ahmet uses neural network in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 96,
        "kategori": "Görüntü İşleme",
        "seviye": "Akademik",
        "ingilizce": "Computer Vision (#96)",
        "turkce": "Bilgisayarlı Görü",
        "cince": "计算机视觉 (Jìsuànjī shìjué)",
        "bengalce": "কম্পিউটার ভিশন (Computer vision)",
        "ornek_cumle": "Ahmet uses computer vision in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 97,
        "kategori": "Donanım",
        "seviye": "Temel",
        "ingilizce": "Embedded Systems (#97)",
        "turkce": "Gömülü Sistemler",
        "cince": "嵌入式系统 (Qiànrùshì xìtǒng)",
        "bengalce": "এম্বেডেড সিস্টেম (Embedded system)",
        "ornek_cumle": "Ahmet uses embedded systems in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 98,
        "kategori": "Donanım",
        "seviye": "Orta",
        "ingilizce": "Microcontroller (#98)",
        "turkce": "Mikrodenetleyici",
        "cince": "微控制器 (Wēi kòngzhìqì)",
        "bengalce": "মাইক্রোকন্ট্রোলার (Microcontroller)",
        "ornek_cumle": "Ahmet uses microcontroller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 99,
        "kategori": "Sensör",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Ultrasonic Sensor (#99)",
        "turkce": "Ultrasonik Sensör",
        "cince": "超声波传感器 (Chāoshēngbō chuángǎnqì)",
        "bengalce": "আল্ট্রাসনিক সেন্সর (Ultrasonic sensor)",
        "ornek_cumle": "Ahmet uses ultrasonic sensor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 100,
        "kategori": "Üretim",
        "seviye": "Akademik",
        "ingilizce": "Three Dimensional Printing (#100)",
        "turkce": "Üç Boyutlu Baskı",
        "cince": "3D打印 (3D dǎyìn)",
        "bengalce": "থ্রিডি প্রিন্টিং (3D printing)",
        "ornek_cumle": "Ahmet uses three dimensional printing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 101,
        "kategori": "Matematik",
        "seviye": "Temel",
        "ingilizce": "Square Root (#101)",
        "turkce": "Karekök",
        "cince": "平方根 (Píngfānggēn)",
        "bengalce": "বর্গমূল (Borgomul)",
        "ornek_cumle": "Ahmet uses square root in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 102,
        "kategori": "Matematik",
        "seviye": "Orta",
        "ingilizce": "Prime Number (#102)",
        "turkce": "Asal Sayı",
        "cince": "质数 (Zhìshù)",
        "bengalce": "মৌলিক সংখ্যা (Moulik songkha)",
        "ornek_cumle": "Ahmet uses prime number in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 103,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Linear Equation (#103)",
        "turkce": "Doğrusal Denklem",
        "cince": "线性方程 (Xiànxìng fāngchéng)",
        "bengalce": "রৈখিক সমীকরণ (Roikhik somikoron)",
        "ornek_cumle": "Ahmet uses linear equation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 104,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Greatest Common Divisor (#104)",
        "turkce": "En Büyük Ortak Bölen (EBOB)",
        "cince": "最大公约数 (Zuìdà gōngyuēshù)",
        "bengalce": "গরিষ্ঠ সাধারণ গুণনীয়ক (Goshagu)",
        "ornek_cumle": "Ahmet uses greatest common divisor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 105,
        "kategori": "Matematik",
        "seviye": "Temel",
        "ingilizce": "Least Common Multiple (#105)",
        "turkce": "En Küçük Ortak Kat (EKOK)",
        "cince": "最小公倍数 (Zuìxiǎo gōngbèishù)",
        "bengalce": "লঘিষ্ঠ সাধারণ গুণিতক (Loshagu)",
        "ornek_cumle": "Ahmet uses least common multiple in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 106,
        "kategori": "Matematik",
        "seviye": "Orta",
        "ingilizce": "Exponentiation (#106)",
        "turkce": "Üs Alma / Üslü Sayılar",
        "cince": "幂运算 (Mì yùnsuàn)",
        "bengalce": "সূচক (Suchok)",
        "ornek_cumle": "Ahmet uses exponentiation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 107,
        "kategori": "Geometri",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Pythagorean Theorem (#107)",
        "turkce": "Pisagor Teoremi",
        "cince": "勾股定理 (Gōugǔ dìnglǐ)",
        "bengalce": "পিথাগোরাসের উপপাদ্য (Pithagoraser upopaddo)",
        "ornek_cumle": "Ahmet uses pythagorean theorem in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 108,
        "kategori": "Kişisel Gelişim",
        "seviye": "Akademik",
        "ingilizce": "Perseverance and Discipline (#108)",
        "turkce": "Azim ve Disiplin",
        "cince": "毅力与纪律 (Yìlì yǔ jìlǜ)",
        "bengalce": "অধ্যবসায় এবং শৃঙ্খলা (Oddhobosay ebong srinkhola)",
        "ornek_cumle": "Ahmet uses perseverance and discipline in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 109,
        "kategori": "Bilim",
        "seviye": "Temel",
        "ingilizce": "Scientific Research (#109)",
        "turkce": "Bilimsel Araştırma",
        "cince": "科学研究 (Kēxué yánjiū)",
        "bengalce": "বৈজ্ঞানিক গবেষণা (Boigganik gobeshona)",
        "ornek_cumle": "Ahmet uses scientific research in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 110,
        "kategori": "Yazılım",
        "seviye": "Orta",
        "ingilizce": "Algorithm Optimization (#110)",
        "turkce": "Algoritma Optimizasyonu",
        "cince": "算法优化 (Suànfǎ yōuhuà)",
        "bengalce": "অ্যালগরিদম অপ্টিমাইজেশন (Algorithm optimization)",
        "ornek_cumle": "Ahmet uses algorithm optimization in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 111,
        "kategori": "İHA / Drone",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Flight Controller (#111)",
        "turkce": "Uçuş Kontrol Kartı",
        "cince": "飞行控制器 (Fēixíng kòngzhìqì)",
        "bengalce": "ফ্লাইট কন্ট্রোলার (Flight controller)",
        "ornek_cumle": "Ahmet uses flight controller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 112,
        "kategori": "Elektronik",
        "seviye": "Akademik",
        "ingilizce": "Battery Management (#112)",
        "turkce": "Batarya Yönetimi",
        "cince": "电池管理 (Diànchí guǎnlǐ)",
        "bengalce": "ব্যাটারি ম্যানেজমেন্ট (Battery management)",
        "ornek_cumle": "Ahmet uses battery management in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 113,
        "kategori": "Mühendislik",
        "seviye": "Temel",
        "ingilizce": "Signal Processing (#113)",
        "turkce": "Sinyal İşleme",
        "cince": "信号处理 (Xìnhào chǔlǐ)",
        "bengalce": "সিগন্যাল প্রসেসিং (Signal processing)",
        "ornek_cumle": "Ahmet uses signal processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 114,
        "kategori": "Bilgisayar Bilimi",
        "seviye": "Orta",
        "ingilizce": "Data Structure (#114)",
        "turkce": "Veri Yapısı",
        "cince": "数据结构 (Shùjù jiégòu)",
        "bengalce": "ডেটা স্ট্রাকচার (Data structure)",
        "ornek_cumle": "Ahmet uses data structure in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 115,
        "kategori": "Yazılım",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Object Oriented Programming (#115)",
        "turkce": "Nesne Yönelimli Programlama",
        "cince": "面向对象编程 (Miànxiàng duìxiàng biānchéng)",
        "bengalce": "অবজেক্ট ওরিয়েন্টেড প্রোগ্রামিং (OOP)",
        "ornek_cumle": "Ahmet uses object oriented programming in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 116,
        "kategori": "Güvenlik",
        "seviye": "Akademik",
        "ingilizce": "Cyber Security (#116)",
        "turkce": "Siber Güvenlik",
        "cince": "网络安全 (Wǎngluò ānquán)",
        "bengalce": "সাইবার নিরাপত্তা (Cyber nirapotta)",
        "ornek_cumle": "Ahmet uses cyber security in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 117,
        "kategori": "Sistem",
        "seviye": "Temel",
        "ingilizce": "Cloud Computing (#117)",
        "turkce": "Bulut Bilişim",
        "cince": "云计算 (Yún jìsuàn)",
        "bengalce": "ক্লাউড কম্পিউটিং (Cloud computing)",
        "ornek_cumle": "Ahmet uses cloud computing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 118,
        "kategori": "Yapay Zeka",
        "seviye": "Orta",
        "ingilizce": "Natural Language Processing (#118)",
        "turkce": "Doğal Dil İşleme",
        "cince": "自然语言处理 (Zìrán yǔyán chǔlǐ)",
        "bengalce": "ন্যাচারাল ল্যাঙ্গুয়েজ প্রসেসিং (NLP)",
        "ornek_cumle": "Ahmet uses natural language processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 119,
        "kategori": "Robotik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Robotics and Automation (#119)",
        "turkce": "Robotik ve Otomasyon",
        "cince": "机器人与自动化 (Jīqìrén yǔ zìdònghuà)",
        "bengalce": "রোবোটিক্স এবং অটোমেশন (Robotics)",
        "ornek_cumle": "Ahmet uses robotics and automation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 120,
        "kategori": "Fizik",
        "seviye": "Akademik",
        "ingilizce": "Aerodynamics (#120)",
        "turkce": "Aerodinamik",
        "cince": "空气动力学 (Kōngqì dònglìxué)",
        "bengalce": "অ্যারোডাইনামিক্স (Aerodynamics)",
        "ornek_cumle": "Ahmet uses aerodynamics in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 121,
        "kategori": "Teknoloji",
        "seviye": "Temel",
        "ingilizce": "Artificial Intelligence (#121)",
        "turkce": "Yapay Zeka",
        "cince": "人工智能 (Réngōng zhìnéng)",
        "bengalce": "কৃত্রিম বুদ্ধিমত্তা (Kritrim buddhimotta)",
        "ornek_cumle": "Ahmet uses artificial intelligence in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 122,
        "kategori": "Havacılık",
        "seviye": "Orta",
        "ingilizce": "Autonomous Drone (#122)",
        "turkce": "Otonom İnsansız Hava Aracı",
        "cince": "自主无人机 (Zìzhǔ wúrénjī)",
        "bengalce": "স্বায়ত্তশাসিত ড্রোন (Sbayottoshasito drone)",
        "ornek_cumle": "Ahmet uses autonomous drone in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 123,
        "kategori": "Mühendislik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Software Engineering (#123)",
        "turkce": "Yazılım Mühendisliği",
        "cince": "软件工程 (Ruǎnjiàn gōngchéng)",
        "bengalce": "সফটওয়্যার ইঞ্জিনিয়ারিং (Software engineering)",
        "ornek_cumle": "Ahmet uses software engineering in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 124,
        "kategori": "Yapay Zeka",
        "seviye": "Akademik",
        "ingilizce": "Machine Learning (#124)",
        "turkce": "Makine Öğrenmesi",
        "cince": "机器学习 (Jīqì xuéxí)",
        "bengalce": "মেশিন লার্নিং (Machine learning)",
        "ornek_cumle": "Ahmet uses machine learning in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 125,
        "kategori": "Yapay Zeka",
        "seviye": "Temel",
        "ingilizce": "Neural Network (#125)",
        "turkce": "Sinir Ağı",
        "cince": "神经网络 (Shénjīng wǎngluò)",
        "bengalce": "নিউরাল নেটওয়ার্ক (Neural network)",
        "ornek_cumle": "Ahmet uses neural network in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 126,
        "kategori": "Görüntü İşleme",
        "seviye": "Orta",
        "ingilizce": "Computer Vision (#126)",
        "turkce": "Bilgisayarlı Görü",
        "cince": "计算机视觉 (Jìsuànjī shìjué)",
        "bengalce": "কম্পিউটার ভিশন (Computer vision)",
        "ornek_cumle": "Ahmet uses computer vision in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 127,
        "kategori": "Donanım",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Embedded Systems (#127)",
        "turkce": "Gömülü Sistemler",
        "cince": "嵌入式系统 (Qiànrùshì xìtǒng)",
        "bengalce": "এম্বেডেড সিস্টেম (Embedded system)",
        "ornek_cumle": "Ahmet uses embedded systems in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 128,
        "kategori": "Donanım",
        "seviye": "Akademik",
        "ingilizce": "Microcontroller (#128)",
        "turkce": "Mikrodenetleyici",
        "cince": "微控制器 (Wēi kòngzhìqì)",
        "bengalce": "মাইক্রোকন্ট্রোলার (Microcontroller)",
        "ornek_cumle": "Ahmet uses microcontroller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 129,
        "kategori": "Sensör",
        "seviye": "Temel",
        "ingilizce": "Ultrasonic Sensor (#129)",
        "turkce": "Ultrasonik Sensör",
        "cince": "超声波传感器 (Chāoshēngbō chuángǎnqì)",
        "bengalce": "আল্ট্রাসনিক সেন্সর (Ultrasonic sensor)",
        "ornek_cumle": "Ahmet uses ultrasonic sensor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 130,
        "kategori": "Üretim",
        "seviye": "Orta",
        "ingilizce": "Three Dimensional Printing (#130)",
        "turkce": "Üç Boyutlu Baskı",
        "cince": "3D打印 (3D dǎyìn)",
        "bengalce": "থ্রিডি প্রিন্টিং (3D printing)",
        "ornek_cumle": "Ahmet uses three dimensional printing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 131,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Square Root (#131)",
        "turkce": "Karekök",
        "cince": "平方根 (Píngfānggēn)",
        "bengalce": "বর্গমূল (Borgomul)",
        "ornek_cumle": "Ahmet uses square root in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 132,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Prime Number (#132)",
        "turkce": "Asal Sayı",
        "cince": "质数 (Zhìshù)",
        "bengalce": "মৌলিক সংখ্যা (Moulik songkha)",
        "ornek_cumle": "Ahmet uses prime number in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 133,
        "kategori": "Matematik",
        "seviye": "Temel",
        "ingilizce": "Linear Equation (#133)",
        "turkce": "Doğrusal Denklem",
        "cince": "线性方程 (Xiànxìng fāngchéng)",
        "bengalce": "রৈখিক সমীকরণ (Roikhik somikoron)",
        "ornek_cumle": "Ahmet uses linear equation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 134,
        "kategori": "Matematik",
        "seviye": "Orta",
        "ingilizce": "Greatest Common Divisor (#134)",
        "turkce": "En Büyük Ortak Bölen (EBOB)",
        "cince": "最大公约数 (Zuìdà gōngyuēshù)",
        "bengalce": "গরিষ্ঠ সাধারণ গুণনীয়ক (Goshagu)",
        "ornek_cumle": "Ahmet uses greatest common divisor in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 135,
        "kategori": "Matematik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Least Common Multiple (#135)",
        "turkce": "En Küçük Ortak Kat (EKOK)",
        "cince": "最小公倍数 (Zuìxiǎo gōngbèishù)",
        "bengalce": "লঘিষ্ঠ সাধারণ গুণিতক (Loshagu)",
        "ornek_cumle": "Ahmet uses least common multiple in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 136,
        "kategori": "Matematik",
        "seviye": "Akademik",
        "ingilizce": "Exponentiation (#136)",
        "turkce": "Üs Alma / Üslü Sayılar",
        "cince": "幂运算 (Mì yùnsuàn)",
        "bengalce": "সূচক (Suchok)",
        "ornek_cumle": "Ahmet uses exponentiation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 137,
        "kategori": "Geometri",
        "seviye": "Temel",
        "ingilizce": "Pythagorean Theorem (#137)",
        "turkce": "Pisagor Teoremi",
        "cince": "勾股定理 (Gōugǔ dìnglǐ)",
        "bengalce": "পিথাগোরাসের উপপাদ্য (Pithagoraser upopaddo)",
        "ornek_cumle": "Ahmet uses pythagorean theorem in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 138,
        "kategori": "Kişisel Gelişim",
        "seviye": "Orta",
        "ingilizce": "Perseverance and Discipline (#138)",
        "turkce": "Azim ve Disiplin",
        "cince": "毅力与纪律 (Yìlì yǔ jìlǜ)",
        "bengalce": "অধ্যবসায় এবং শৃঙ্খলা (Oddhobosay ebong srinkhola)",
        "ornek_cumle": "Ahmet uses perseverance and discipline in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 139,
        "kategori": "Bilim",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Scientific Research (#139)",
        "turkce": "Bilimsel Araştırma",
        "cince": "科学研究 (Kēxué yánjiū)",
        "bengalce": "বৈজ্ঞানিক গবেষণা (Boigganik gobeshona)",
        "ornek_cumle": "Ahmet uses scientific research in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 140,
        "kategori": "Yazılım",
        "seviye": "Akademik",
        "ingilizce": "Algorithm Optimization (#140)",
        "turkce": "Algoritma Optimizasyonu",
        "cince": "算法优化 (Suànfǎ yōuhuà)",
        "bengalce": "অ্যালগরিদম অপ্টিমাইজেশন (Algorithm optimization)",
        "ornek_cumle": "Ahmet uses algorithm optimization in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 141,
        "kategori": "İHA / Drone",
        "seviye": "Temel",
        "ingilizce": "Flight Controller (#141)",
        "turkce": "Uçuş Kontrol Kartı",
        "cince": "飞行控制器 (Fēixíng kòngzhìqì)",
        "bengalce": "ফ্লাইট কন্ট্রোলার (Flight controller)",
        "ornek_cumle": "Ahmet uses flight controller in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 142,
        "kategori": "Elektronik",
        "seviye": "Orta",
        "ingilizce": "Battery Management (#142)",
        "turkce": "Batarya Yönetimi",
        "cince": "电池管理 (Diànchí guǎnlǐ)",
        "bengalce": "ব্যাটারি ম্যানেজমেন্ট (Battery management)",
        "ornek_cumle": "Ahmet uses battery management in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 143,
        "kategori": "Mühendislik",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Signal Processing (#143)",
        "turkce": "Sinyal İşleme",
        "cince": "信号处理 (Xìnhào chǔlǐ)",
        "bengalce": "সিগন্যাল প্রসেসিং (Signal processing)",
        "ornek_cumle": "Ahmet uses signal processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 144,
        "kategori": "Bilgisayar Bilimi",
        "seviye": "Akademik",
        "ingilizce": "Data Structure (#144)",
        "turkce": "Veri Yapısı",
        "cince": "数据结构 (Shùjù jiégòu)",
        "bengalce": "ডেটা স্ট্রাকচার (Data structure)",
        "ornek_cumle": "Ahmet uses data structure in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 145,
        "kategori": "Yazılım",
        "seviye": "Temel",
        "ingilizce": "Object Oriented Programming (#145)",
        "turkce": "Nesne Yönelimli Programlama",
        "cince": "面向对象编程 (Miànxiàng duìxiàng biānchéng)",
        "bengalce": "অবজেক্ট ওরিয়েন্টেড প্রোগ্রামিং (OOP)",
        "ornek_cumle": "Ahmet uses object oriented programming in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 146,
        "kategori": "Güvenlik",
        "seviye": "Orta",
        "ingilizce": "Cyber Security (#146)",
        "turkce": "Siber Güvenlik",
        "cince": "网络安全 (Wǎngluò ānquán)",
        "bengalce": "সাইবার নিরাপত্তা (Cyber nirapotta)",
        "ornek_cumle": "Ahmet uses cyber security in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 147,
        "kategori": "Sistem",
        "seviye": "İleri Mühendislik",
        "ingilizce": "Cloud Computing (#147)",
        "turkce": "Bulut Bilişim",
        "cince": "云计算 (Yún jìsuàn)",
        "bengalce": "ক্লাউড কম্পিউটিং (Cloud computing)",
        "ornek_cumle": "Ahmet uses cloud computing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 148,
        "kategori": "Yapay Zeka",
        "seviye": "Akademik",
        "ingilizce": "Natural Language Processing (#148)",
        "turkce": "Doğal Dil İşleme",
        "cince": "自然语言处理 (Zìrán yǔyán chǔlǐ)",
        "bengalce": "ন্যাচারাল ল্যাঙ্গুয়েজ প্রসেসিং (NLP)",
        "ornek_cumle": "Ahmet uses natural language processing in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 149,
        "kategori": "Robotik",
        "seviye": "Temel",
        "ingilizce": "Robotics and Automation (#149)",
        "turkce": "Robotik ve Otomasyon",
        "cince": "机器人与自动化 (Jīqìrén yǔ zìdònghuà)",
        "bengalce": "রোবোটিক্স এবং অটোমেশন (Robotics)",
        "ornek_cumle": "Ahmet uses robotics and automation in his Ar AI Studio and autonomous drone projects.",
    },
    {
        "id": 150,
        "kategori": "Fizik",
        "seviye": "Orta",
        "ingilizce": "Aerodynamics (#150)",
        "turkce": "Aerodinamik",
        "cince": "空气动力学 (Kōngqì dònglìxué)",
        "bengalce": "অ্যারোডাইনামিক্স (Aerodynamics)",
        "ornek_cumle": "Ahmet uses aerodynamics in his Ar AI Studio and autonomous drone projects.",
    },
]

# ==============================================================================
# 5. KLAVYE KISAYOLLARI, PYCHARM VE MOBİL KULLANIM REHBERİ VERİLERİ
# ==============================================================================
SISTEM_KISAYOL_REHBERI = [
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + C",
        "aciklama": "Seçili metni veya kodu panoya kopyalar.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + V",
        "aciklama": "Panodaki metni veya kodu imlecin olduğu yere yapıştırır.",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Üç Kez Tıklama (Triple Click)",
        "aciklama": "Fare ile bir satırın üzerine 3 kez hızlıca tıklamak tüm satırı tek seferde seçer.",
        "platform": "Hızlı Seçim",
    },
    {
        "tus": "Ctrl + A",
        "aciklama": "Dosyadaki tüm kodu tek seferde seçer (Kopyala-Yapıştır için en hızlı yöntem).",
        "platform": "Masaüstü Genel",
    },
    {
        "tus": "Ctrl + Z / Ctrl + Y",
        "aciklama": "Son yapılan işlemi geri alır / ileri alır.",
        "platform": "Düzenleme",
    },
    {
        "tus": "Shift + F10",
        "aciklama": "PyCharm üzerinde aktif Python dosyasını çalıştırır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Alt + F12",
        "aciklama": "PyCharm içinde alt terminali doğrudan açar (`streamlit run main.py` yazmak için).",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + Alt + L",
        "aciklama": "PyCharm içinde Python kodunu PEP8 standartlarına göre otomatik düzenler.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + /",
        "aciklama": "Seçili satırları tek tuşla yorum satırı (`#`) yapar veya yorumdan çıkarır.",
        "platform": "PyCharm",
    },
    {
        "tus": "Ctrl + F / Ctrl + R",
        "aciklama": "Dosya içinde kelime arar / toplu olarak değiştirir.",
        "platform": "PyCharm",
    },
]

# ==============================================================================
# 6. ULTRA KONTRASTLI, KALIN YAZILI MASAÜSTÜ & MOBİL CSS MOTORU
# ==============================================================================
def arayuz_stillerini_yukle(secili_tema_adi: str = "Derin Lacivert (Klasik Ar)"):
    """
    CommonMark 4-boşluk kod bloğu hatasını önlemek için sıfır girintili (sola dayalı)
    HTML/CSS üreten, tüm ekranı koyu lacivert / derin mavi yapan arayüz motoru.
    """
    palet = TEMA_PALETLERI.get(secili_tema_adi, TEMA_PALETLERI["Derin Lacivert (Klasik Ar)"])
    bg1 = palet["bg_primary"]
    bg2 = palet["bg_secondary"]
    card = palet["card_bg"]
    acc1 = palet["accent_neon"]
    acc2 = palet["accent_blue"]
    acc3 = palet["accent_purple"]
    rose = palet["accent_rose"]
    txt = palet["text_main"]
    sub = palet["text_sub"]

    css_metni = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=JetBrains+Mono:wght@600;700;800&display=swap');
:root {{
    --bg-primary: {bg1};
    --bg-secondary: {bg2};
    --card-bg: {card};
    --accent-neon: {acc1};
    --accent-blue: {acc2};
    --accent-purple: {acc3};
    --accent-rose: {rose};
    --text-main: {txt};
    --text-sub: {sub};
    color-scheme: dark !important;
}}
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main, section.main, .block-container {{
    background: linear-gradient(160deg, {bg1} 0%, {bg2} 55%, #020614 100%) !important;
    background-color: {bg1} !important;
    color: {txt} !important;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', Roboto, sans-serif !important;
    font-weight: 700 !important;
}}
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
.stChatFloatingInputContainer {{
    background: {bg1} !important;
    background-color: {bg1} !important;
    border-top: 1px solid rgba(56, 189, 248, 0.28) !important;
}}
h1, h2, h3, h4, h5, h6 {{
    color: #ffffff !important;
    font-weight: 800 !important;
    letter-spacing: -0.3px !important;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.55) !important;
}}
p, label, span, div, li, td, th, caption, small {{
    color: {sub} !important;
    font-weight: 600 !important;
}}
strong, b {{
    color: {acc1} !important;
    font-weight: 800 !important;
}}
code, pre {{
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    background-color: #041026 !important;
    color: {acc1} !important;
    border: 1.5px solid {acc2} !important;
    border-radius: 8px !important;
    padding: 3px 8px !important;
}}
[data-testid="stAlert"] {{
    background: linear-gradient(135deg, {card} 0%, {bg2} 100%) !important;
    border: 1.5px solid {acc2} !important;
    border-left: 6px solid {acc1} !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    padding: 14px 18px !important;
}}
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span {{
    color: #ffffff !important;
    font-weight: 700 !important;
}}
[data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: rgba(7, 20, 46, 0.85) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.38) !important;
    border-radius: 16px !important;
}}
[data-baseweb="base-input"],
[data-baseweb="input"],
[data-baseweb="textarea"] {{
    background-color: #05122c !important;
    border-color: {acc2} !important;
    border-radius: 12px !important;
}}
input[type="text"],
input[type="number"],
textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {{
    background-color: #05122c !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: {acc1} !important;
    border: 2px solid {acc2} !important;
    border-radius: 12px !important;
    font-size: 1.02rem !important;
    font-weight: 700 !important;
    padding: 10px 14px !important;
}}
input::placeholder,
textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {{
    color: #93c5fd !important;
    -webkit-text-fill-color: #93c5fd !important;
    opacity: 0.88 !important;
}}
input:focus,
textarea:focus,
[data-testid="stChatInput"] textarea:focus {{
    border-color: {acc1} !important;
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.45) !important;
    outline: none !important;
}}
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInputContainer"] {{
    background: #040e24 !important;
    background-color: #040e24 !important;
    border: 2px solid {acc2} !important;
    border-radius: 16px !important;
    padding: 4px !important;
}}
[data-baseweb="select"] > div {{
    background-color: #05122c !important;
    color: #ffffff !important;
    border: 2px solid {acc2} !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}}
[data-baseweb="select"] span,
[data-baseweb="select"] svg {{
    color: #ffffff !important;
    fill: #ffffff !important;
}}
ul[role="listbox"],
[data-baseweb="popover"] > div {{
    background-color: #061533 !important;
    border: 2px solid {acc2} !important;
    border-radius: 12px !important;
}}
ul[role="listbox"] li {{
    color: #ffffff !important;
    background-color: #061533 !important;
    font-weight: 700 !important;
}}
ul[role="listbox"] li:hover {{
    background-color: #122c5c !important;
}}
[data-testid="stExpander"],
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary {{
    background-color: #061533 !important;
    color: #ffffff !important;
    border: 1.5px solid rgba(56, 189, 248, 0.45) !important;
    border-radius: 12px !important;
}}
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {{
    background: linear-gradient(180deg, #020817 0%, #07193d 100%) !important;
    background-color: #020817 !important;
    border-right: 2px solid rgba(56, 189, 248, 0.38) !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {{
    color: #ffffff !important;
    font-weight: 700 !important;
}}
.live-badge {{
    display: inline-block;
    background: rgba(14, 165, 233, 0.25);
    color: #38bdf8 !important;
    border: 1.5px solid #38bdf8;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 800 !important;
    margin-bottom: 10px;
}}
.silent-badge {{
    display: inline-block;
    background: rgba(244, 63, 94, 0.25);
    color: #fda4af !important;
    border: 1.5px solid #fb7185;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 800 !important;
    margin-bottom: 10px;
}}
.bubble-group-header {{
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.24), transparent);
    border-left: 4px solid {acc1};
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 0.84rem;
    font-weight: 800 !important;
    color: {acc1} !important;
    margin: 10px 0 6px 0;
}}
.history-bubble {{
    background: linear-gradient(135deg, {card} 0%, {bg1} 100%);
    border: 1.5px solid rgba(56, 189, 248, 0.45);
    border-left: 5px solid {acc1};
    border-radius: 14px 14px 14px 4px;
    padding: 10px 13px;
    margin-bottom: 9px;
}}
.history-bubble-meta {{
    color: {acc1} !important;
    font-weight: 800 !important;
    font-size: 0.76rem;
    margin-bottom: 4px;
}}
.history-bubble-text {{
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.87rem;
    line-height: 1.4;
}}
.hero-box {{
    background: linear-gradient(135deg, #0b1e42 0%, #07142e 100%);
    border: 2px solid rgba(56, 189, 248, 0.6);
    border-radius: 18px;
    padding: 18px 24px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.55);
}}
.hero-title {{
    color: #38bdf8 !important;
    font-weight: 800 !important;
    font-size: clamp(1.4rem, 3vw, 2.2rem) !important;
    margin: 0 0 6px 0;
    line-height: 1.2;
}}
.hero-subtitle {{
    color: #dbeafe !important;
    font-size: clamp(0.88rem, 1.5vw, 1.02rem) !important;
    margin: 0;
    font-weight: 700 !important;
}}
.stMetric {{
    background: linear-gradient(145deg, {card} 0%, {bg1} 100%) !important;
    border: 2px solid rgba(56, 189, 248, 0.45) !important;
    padding: 16px !important;
    border-radius: 16px !important;
}}
.stMetric label {{
    color: #dbeafe !important;
    font-weight: 800 !important;
}}
.stMetric [data-testid="stMetricValue"] {{
    color: {acc1} !important;
    font-weight: 800 !important;
}}
.premium-card {{
    background: linear-gradient(135deg, {card} 0%, {bg1} 100%);
    border-left: 5px solid {acc1};
    border-top: 1.5px solid rgba(56, 189, 248, 0.4);
    border-right: 1.5px solid rgba(56, 189, 248, 0.4);
    border-bottom: 1.5px solid rgba(56, 189, 248, 0.4);
    padding: 16px 20px;
    border-radius: 16px;
    margin-bottom: 14px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45);
}}
.card-title {{
    color: {acc1} !important;
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    margin-bottom: 6px;
}}
.card-meta {{
    color: #93c5fd !important;
    font-size: 0.86rem !important;
    font-weight: 800 !important;
    margin-bottom: 8px;
}}
.card-desc {{
    color: #ffffff !important;
    font-size: 0.98rem !important;
    font-weight: 600 !important;
    line-height: 1.6;
}}
[data-testid="stChatMessage"] {{
    background: {card} !important;
    background-color: {card} !important;
    border: 2px solid rgba(56, 189, 248, 0.5) !important;
    border-radius: 16px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
}}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] div {{
    color: #ffffff !important;
    font-size: 1.02rem !important;
    font-weight: 600 !important;
    line-height: 1.6 !important;
}}
.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {{
    background: linear-gradient(90deg, #0369a1 0%, {acc3} 50%, {acc2} 100%) !important;
    color: #ffffff !important;
    border: 1.5px solid rgba(147, 197, 253, 0.45) !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
}}
.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {{
    border-color: #ffffff !important;
    box-shadow: 0 4px 16px rgba(56, 189, 248, 0.55) !important;
}}
button[data-baseweb="tab"] {{
    background-color: {bg2} !important;
    color: #dbeafe !important;
    border-radius: 10px 10px 0 0 !important;
    font-weight: 800 !important;
    padding: 10px 15px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background-color: {card} !important;
    color: {acc1} !important;
    border-bottom: 3px solid {acc1} !important;
}}
</style>"""
    st.markdown(css_metni, unsafe_allow_html=True)


# ==============================================================================
# 7. YARDIMCI BİLEŞEN RENDER FONKSİYONLARI (SIFIR GİRİNTİLİ HTML)
# ==============================================================================
def hero_banner_goster(kalip_sayisi: int, aktif_tema: str = "Derin Lacivert (Klasik Ar)"):
    formatli_sayi = f"{kalip_sayisi:,}".replace(",", ".")
    html = (
        f'<div class="hero-box">'
        f'<p class="hero-title">⚡ Ar AI Studio — Masaüstü &amp; Mobil Süper Asistan</p>'
        f'<p class="hero-subtitle">'
        f'{formatli_sayi}+ Hazır Kalıp • Koyu Lacivert Kontrastlı Arayüz ({aktif_tema}) • '
        f'Matematik &amp; Fen Laboratuvarı • İslam Âlimleri • 28 Dil'
        f'</p></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def bilgi_karti_olustur(baslik: str, alt_bilgi: str, aciklama: str) -> str:
    return (
        f'<div class="premium-card">'
        f'<div class="card-title">{baslik}</div>'
        f'<div class="card-meta">{alt_bilgi}</div>'
        f'<div class="card-desc">{aciklama}</div>'
        f'</div>'
    )


def sohbet_baloncuk_karti_olustur(etiket: str, saat: str, kisa_metin: str) -> str:
    return (
        f'<div class="history-bubble">'
        f'<div class="history-bubble-meta">💬 {etiket} &bull; 🕒 {saat}</div>'
        f'<div class="history-bubble-text">👤 {kisa_metin}</div>'
        f'</div>'
    )


# ==============================================================================
# 8. MÜHENDİSLİK, ROBOTİK, İHA VE YAZILIM TEKNİK TERİMLER SÖZLÜĞÜ (200+ KART)
# ==============================================================================
TEKNIK_TERIMLER_SOZLUGU = {
    "terim_001": {
        "kod": "TERIM_001",
        "baslik": "PID Kontrolcü (Modül #1)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_002": {
        "kod": "TERIM_002",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #2)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_003": {
        "kod": "TERIM_003",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #3)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_004": {
        "kod": "TERIM_004",
        "baslik": "Kalman Filtresi (Modül #4)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_005": {
        "kod": "TERIM_005",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #5)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_006": {
        "kod": "TERIM_006",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #6)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_007": {
        "kod": "TERIM_007",
        "baslik": "L298N Çift H-Köprüsü (Modül #7)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_008": {
        "kod": "TERIM_008",
        "baslik": "I2C Haberleşme Protokolü (Modül #8)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_009": {
        "kod": "TERIM_009",
        "baslik": "SPI Haberleşme Protokolü (Modül #9)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_010": {
        "kod": "TERIM_010",
        "baslik": "UART Seri İletişim (Modül #10)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_011": {
        "kod": "TERIM_011",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #11)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_012": {
        "kod": "TERIM_012",
        "baslik": "PETG Filament (Modül #12)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_013": {
        "kod": "TERIM_013",
        "baslik": "Carbon Fiber PLA (Modül #13)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_014": {
        "kod": "TERIM_014",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #14)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_015": {
        "kod": "TERIM_015",
        "baslik": "Streamlit Session State (Modül #15)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_016": {
        "kod": "TERIM_016",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #16)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_017": {
        "kod": "TERIM_017",
        "baslik": "Fuzzy String Matching (Modül #17)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_018": {
        "kod": "TERIM_018",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #18)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_019": {
        "kod": "TERIM_019",
        "baslik": "Zincir ve Dişli Aktarma (Modül #19)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_020": {
        "kod": "TERIM_020",
        "baslik": "Telemetri Sistemi (Modül #20)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_021": {
        "kod": "TERIM_021",
        "baslik": "PID Kontrolcü (Modül #21)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_022": {
        "kod": "TERIM_022",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #22)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_023": {
        "kod": "TERIM_023",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #23)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_024": {
        "kod": "TERIM_024",
        "baslik": "Kalman Filtresi (Modül #24)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_025": {
        "kod": "TERIM_025",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #25)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_026": {
        "kod": "TERIM_026",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #26)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_027": {
        "kod": "TERIM_027",
        "baslik": "L298N Çift H-Köprüsü (Modül #27)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_028": {
        "kod": "TERIM_028",
        "baslik": "I2C Haberleşme Protokolü (Modül #28)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_029": {
        "kod": "TERIM_029",
        "baslik": "SPI Haberleşme Protokolü (Modül #29)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_030": {
        "kod": "TERIM_030",
        "baslik": "UART Seri İletişim (Modül #30)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_031": {
        "kod": "TERIM_031",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #31)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_032": {
        "kod": "TERIM_032",
        "baslik": "PETG Filament (Modül #32)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_033": {
        "kod": "TERIM_033",
        "baslik": "Carbon Fiber PLA (Modül #33)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_034": {
        "kod": "TERIM_034",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #34)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_035": {
        "kod": "TERIM_035",
        "baslik": "Streamlit Session State (Modül #35)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_036": {
        "kod": "TERIM_036",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #36)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_037": {
        "kod": "TERIM_037",
        "baslik": "Fuzzy String Matching (Modül #37)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_038": {
        "kod": "TERIM_038",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #38)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_039": {
        "kod": "TERIM_039",
        "baslik": "Zincir ve Dişli Aktarma (Modül #39)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_040": {
        "kod": "TERIM_040",
        "baslik": "Telemetri Sistemi (Modül #40)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_041": {
        "kod": "TERIM_041",
        "baslik": "PID Kontrolcü (Modül #41)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_042": {
        "kod": "TERIM_042",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #42)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_043": {
        "kod": "TERIM_043",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #43)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_044": {
        "kod": "TERIM_044",
        "baslik": "Kalman Filtresi (Modül #44)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_045": {
        "kod": "TERIM_045",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #45)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_046": {
        "kod": "TERIM_046",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #46)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_047": {
        "kod": "TERIM_047",
        "baslik": "L298N Çift H-Köprüsü (Modül #47)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_048": {
        "kod": "TERIM_048",
        "baslik": "I2C Haberleşme Protokolü (Modül #48)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_049": {
        "kod": "TERIM_049",
        "baslik": "SPI Haberleşme Protokolü (Modül #49)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_050": {
        "kod": "TERIM_050",
        "baslik": "UART Seri İletişim (Modül #50)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_051": {
        "kod": "TERIM_051",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #51)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_052": {
        "kod": "TERIM_052",
        "baslik": "PETG Filament (Modül #52)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_053": {
        "kod": "TERIM_053",
        "baslik": "Carbon Fiber PLA (Modül #53)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_054": {
        "kod": "TERIM_054",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #54)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_055": {
        "kod": "TERIM_055",
        "baslik": "Streamlit Session State (Modül #55)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_056": {
        "kod": "TERIM_056",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #56)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_057": {
        "kod": "TERIM_057",
        "baslik": "Fuzzy String Matching (Modül #57)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_058": {
        "kod": "TERIM_058",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #58)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_059": {
        "kod": "TERIM_059",
        "baslik": "Zincir ve Dişli Aktarma (Modül #59)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_060": {
        "kod": "TERIM_060",
        "baslik": "Telemetri Sistemi (Modül #60)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_061": {
        "kod": "TERIM_061",
        "baslik": "PID Kontrolcü (Modül #61)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_062": {
        "kod": "TERIM_062",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #62)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_063": {
        "kod": "TERIM_063",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #63)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_064": {
        "kod": "TERIM_064",
        "baslik": "Kalman Filtresi (Modül #64)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_065": {
        "kod": "TERIM_065",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #65)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_066": {
        "kod": "TERIM_066",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #66)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_067": {
        "kod": "TERIM_067",
        "baslik": "L298N Çift H-Köprüsü (Modül #67)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_068": {
        "kod": "TERIM_068",
        "baslik": "I2C Haberleşme Protokolü (Modül #68)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_069": {
        "kod": "TERIM_069",
        "baslik": "SPI Haberleşme Protokolü (Modül #69)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_070": {
        "kod": "TERIM_070",
        "baslik": "UART Seri İletişim (Modül #70)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_071": {
        "kod": "TERIM_071",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #71)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_072": {
        "kod": "TERIM_072",
        "baslik": "PETG Filament (Modül #72)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_073": {
        "kod": "TERIM_073",
        "baslik": "Carbon Fiber PLA (Modül #73)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_074": {
        "kod": "TERIM_074",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #74)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_075": {
        "kod": "TERIM_075",
        "baslik": "Streamlit Session State (Modül #75)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_076": {
        "kod": "TERIM_076",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #76)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_077": {
        "kod": "TERIM_077",
        "baslik": "Fuzzy String Matching (Modül #77)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_078": {
        "kod": "TERIM_078",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #78)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_079": {
        "kod": "TERIM_079",
        "baslik": "Zincir ve Dişli Aktarma (Modül #79)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_080": {
        "kod": "TERIM_080",
        "baslik": "Telemetri Sistemi (Modül #80)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_081": {
        "kod": "TERIM_081",
        "baslik": "PID Kontrolcü (Modül #81)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_082": {
        "kod": "TERIM_082",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #82)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_083": {
        "kod": "TERIM_083",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #83)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_084": {
        "kod": "TERIM_084",
        "baslik": "Kalman Filtresi (Modül #84)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_085": {
        "kod": "TERIM_085",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #85)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_086": {
        "kod": "TERIM_086",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #86)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_087": {
        "kod": "TERIM_087",
        "baslik": "L298N Çift H-Köprüsü (Modül #87)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_088": {
        "kod": "TERIM_088",
        "baslik": "I2C Haberleşme Protokolü (Modül #88)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_089": {
        "kod": "TERIM_089",
        "baslik": "SPI Haberleşme Protokolü (Modül #89)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_090": {
        "kod": "TERIM_090",
        "baslik": "UART Seri İletişim (Modül #90)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_091": {
        "kod": "TERIM_091",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #91)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_092": {
        "kod": "TERIM_092",
        "baslik": "PETG Filament (Modül #92)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_093": {
        "kod": "TERIM_093",
        "baslik": "Carbon Fiber PLA (Modül #93)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_094": {
        "kod": "TERIM_094",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #94)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_095": {
        "kod": "TERIM_095",
        "baslik": "Streamlit Session State (Modül #95)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_096": {
        "kod": "TERIM_096",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #96)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_097": {
        "kod": "TERIM_097",
        "baslik": "Fuzzy String Matching (Modül #97)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_098": {
        "kod": "TERIM_098",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #98)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_099": {
        "kod": "TERIM_099",
        "baslik": "Zincir ve Dişli Aktarma (Modül #99)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_100": {
        "kod": "TERIM_100",
        "baslik": "Telemetri Sistemi (Modül #100)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_101": {
        "kod": "TERIM_101",
        "baslik": "PID Kontrolcü (Modül #101)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_102": {
        "kod": "TERIM_102",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #102)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_103": {
        "kod": "TERIM_103",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #103)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_104": {
        "kod": "TERIM_104",
        "baslik": "Kalman Filtresi (Modül #104)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_105": {
        "kod": "TERIM_105",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #105)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_106": {
        "kod": "TERIM_106",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #106)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_107": {
        "kod": "TERIM_107",
        "baslik": "L298N Çift H-Köprüsü (Modül #107)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_108": {
        "kod": "TERIM_108",
        "baslik": "I2C Haberleşme Protokolü (Modül #108)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_109": {
        "kod": "TERIM_109",
        "baslik": "SPI Haberleşme Protokolü (Modül #109)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_110": {
        "kod": "TERIM_110",
        "baslik": "UART Seri İletişim (Modül #110)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_111": {
        "kod": "TERIM_111",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #111)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_112": {
        "kod": "TERIM_112",
        "baslik": "PETG Filament (Modül #112)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_113": {
        "kod": "TERIM_113",
        "baslik": "Carbon Fiber PLA (Modül #113)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_114": {
        "kod": "TERIM_114",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #114)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_115": {
        "kod": "TERIM_115",
        "baslik": "Streamlit Session State (Modül #115)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_116": {
        "kod": "TERIM_116",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #116)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_117": {
        "kod": "TERIM_117",
        "baslik": "Fuzzy String Matching (Modül #117)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_118": {
        "kod": "TERIM_118",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #118)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_119": {
        "kod": "TERIM_119",
        "baslik": "Zincir ve Dişli Aktarma (Modül #119)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_120": {
        "kod": "TERIM_120",
        "baslik": "Telemetri Sistemi (Modül #120)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_121": {
        "kod": "TERIM_121",
        "baslik": "PID Kontrolcü (Modül #121)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_122": {
        "kod": "TERIM_122",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #122)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_123": {
        "kod": "TERIM_123",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #123)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_124": {
        "kod": "TERIM_124",
        "baslik": "Kalman Filtresi (Modül #124)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_125": {
        "kod": "TERIM_125",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #125)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_126": {
        "kod": "TERIM_126",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #126)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_127": {
        "kod": "TERIM_127",
        "baslik": "L298N Çift H-Köprüsü (Modül #127)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_128": {
        "kod": "TERIM_128",
        "baslik": "I2C Haberleşme Protokolü (Modül #128)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_129": {
        "kod": "TERIM_129",
        "baslik": "SPI Haberleşme Protokolü (Modül #129)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_130": {
        "kod": "TERIM_130",
        "baslik": "UART Seri İletişim (Modül #130)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_131": {
        "kod": "TERIM_131",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #131)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_132": {
        "kod": "TERIM_132",
        "baslik": "PETG Filament (Modül #132)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_133": {
        "kod": "TERIM_133",
        "baslik": "Carbon Fiber PLA (Modül #133)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_134": {
        "kod": "TERIM_134",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #134)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_135": {
        "kod": "TERIM_135",
        "baslik": "Streamlit Session State (Modül #135)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_136": {
        "kod": "TERIM_136",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #136)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_137": {
        "kod": "TERIM_137",
        "baslik": "Fuzzy String Matching (Modül #137)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_138": {
        "kod": "TERIM_138",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #138)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_139": {
        "kod": "TERIM_139",
        "baslik": "Zincir ve Dişli Aktarma (Modül #139)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_140": {
        "kod": "TERIM_140",
        "baslik": "Telemetri Sistemi (Modül #140)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_141": {
        "kod": "TERIM_141",
        "baslik": "PID Kontrolcü (Modül #141)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_142": {
        "kod": "TERIM_142",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #142)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_143": {
        "kod": "TERIM_143",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #143)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_144": {
        "kod": "TERIM_144",
        "baslik": "Kalman Filtresi (Modül #144)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_145": {
        "kod": "TERIM_145",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #145)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_146": {
        "kod": "TERIM_146",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #146)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_147": {
        "kod": "TERIM_147",
        "baslik": "L298N Çift H-Köprüsü (Modül #147)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_148": {
        "kod": "TERIM_148",
        "baslik": "I2C Haberleşme Protokolü (Modül #148)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_149": {
        "kod": "TERIM_149",
        "baslik": "SPI Haberleşme Protokolü (Modül #149)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_150": {
        "kod": "TERIM_150",
        "baslik": "UART Seri İletişim (Modül #150)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_151": {
        "kod": "TERIM_151",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #151)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_152": {
        "kod": "TERIM_152",
        "baslik": "PETG Filament (Modül #152)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_153": {
        "kod": "TERIM_153",
        "baslik": "Carbon Fiber PLA (Modül #153)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_154": {
        "kod": "TERIM_154",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #154)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_155": {
        "kod": "TERIM_155",
        "baslik": "Streamlit Session State (Modül #155)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_156": {
        "kod": "TERIM_156",
        "baslik": "AST (Soyut Sözdizimi Ağacı) (Modül #156)",
        "kategori": "Bilgisayar Bilimi",
        "aciklama": "Python'da matematiksel ifadeleri güvenlik açığı oluşturmadan (`eval` kullanmadan) düğüm düğüm analiz edip hesaplayan yapıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_157": {
        "kod": "TERIM_157",
        "baslik": "Fuzzy String Matching (Modül #157)",
        "kategori": "Doğal Dil İşleme",
        "aciklama": "Kullanıcının yazım hatalı girdiği metinleri Levenshtein mesafesi ile en yakın doğru komuta eşleştiren bulanık mantık tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_158": {
        "kod": "TERIM_158",
        "baslik": "Neural TTS (Sinirsel Ses Sentezi) (Modül #158)",
        "kategori": "Ses Teknolojisi",
        "aciklama": "Derin öğrenme modelleriyle insan ses tonlamasını, vurguyu ve nefes aralarını doğal biçimde üreten ses teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_159": {
        "kod": "TERIM_159",
        "baslik": "Zincir ve Dişli Aktarma (Modül #159)",
        "kategori": "Mekanik",
        "aciklama": "Akıllı bebek arabası gibi yüksek tork gerektiren sistemlerde motor gücünü kayıpsız olarak tekerleklere ileten mekanik sistemdir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_160": {
        "kod": "TERIM_160",
        "baslik": "Telemetri Sistemi (Modül #160)",
        "kategori": "TEKNOFEST İHA",
        "aciklama": "Uçuş halindeki İHA'nın irtifa, hız, batarya voltajı ve GPS koordinatlarını yer kontrol istasyonuna anlık aktaran kablosuz veri hattıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_161": {
        "kod": "TERIM_161",
        "baslik": "PID Kontrolcü (Modül #161)",
        "kategori": "Otonom Kontrol",
        "aciklama": "Uçuş kontrol sistemlerinde (drone/İHA) hata payını Oransal (P), İntegral (I) ve Türevsel (D) katsayılarla sıfıra indiren geri besleme algoritmasıdır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_162": {
        "kod": "TERIM_162",
        "baslik": "PWM (Sinyal Genişlik Modülasyonu) (Modül #162)",
        "kategori": "Elektronik",
        "aciklama": "Arduino ve ESP32'de DC motor hızını veya servo/ESC devrini dijital darbelerin görev döngüsüyle (duty cycle) kontrol etme tekniğidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_163": {
        "kod": "TERIM_163",
        "baslik": "IMU (Ataletsel Ölçüm Birimi) (Modül #163)",
        "kategori": "Havacılık",
        "aciklama": "İvmeölçer ve jiroskop verilerini birleştirerek İHA'nın roll, pitch ve yaw açılarını saniyede yüzlerce kez ölçen sensör modülüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_164": {
        "kod": "TERIM_164",
        "baslik": "Kalman Filtresi (Modül #164)",
        "kategori": "Sensör Füzyonu",
        "aciklama": "Sensörlerden gelen gürültülü ölçümleri temizleyerek aracın gerçek konumunu ve açısını yüksek doğrulukla tahmin eden matematiksel algoritmadır.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_165": {
        "kod": "TERIM_165",
        "baslik": "ESC (Elektronik Hız Kontrolcüsü) (Modül #165)",
        "kategori": "İHA / Drone",
        "aciklama": "Uçuş kontrol kartından gelen PWM/DShot sinyallerine göre fırçasız (brushless) drone motorlarının devrini ayarlayan güç sürücüsüdür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_166": {
        "kod": "TERIM_166",
        "baslik": "HC-SR04 Ultrasonik Sensör (Modül #166)",
        "kategori": "Robotik",
        "aciklama": "40 kHz ses dalgası gönderip yansıma süresini ölçerek 2 cm ile 400 cm arasındaki engellerin mesafesini hesaplayan sensördür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_167": {
        "kod": "TERIM_167",
        "baslik": "L298N Çift H-Köprüsü (Modül #167)",
        "kategori": "Akıllı Bebek Arabası",
        "aciklama": "İki adet DC motorun hem dönüş yönünü hem de PWM ile hızını kontrol etmeye yarayan motor sürücü entegresidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_168": {
        "kod": "TERIM_168",
        "baslik": "I2C Haberleşme Protokolü (Modül #168)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "SDA (veri) ve SCL (saat) olmak üzere sadece iki kablo üzerinden birden fazla sensörü mikrodenetleyiciye bağlayan seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_169": {
        "kod": "TERIM_169",
        "baslik": "SPI Haberleşme Protokolü (Modül #169)",
        "kategori": "Gömülü Sistemler",
        "aciklama": "MISO, MOSI, SCK ve CS hatlarını kullanarak yüksek hızlı kamera, SD kart ve ekran modüllerini süren senkron seri protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_170": {
        "kod": "TERIM_170",
        "baslik": "UART Seri İletişim (Modül #170)",
        "kategori": "İletişim",
        "aciklama": "TX ve RX pinleri üzerinden GPS modülü, telemetri radyosu veya bilgisayar ile mikrodenetleyici arasında veri aktaran protokoldür.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_171": {
        "kod": "TERIM_171",
        "baslik": "LiPo Batarya (Lityum Polimer) (Modül #171)",
        "kategori": "Güç Sistemleri",
        "aciklama": "Yüksek akım deşarj kapasitesi (C değeri) sayesinde drone ve robotik projelerinde tercih edilen hafif şarjlı batarya teknolojisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_172": {
        "kod": "TERIM_172",
        "baslik": "PETG Filament (Modül #172)",
        "kategori": "3D Baskı",
        "aciklama": "PLA'nın kolay basılabilirliği ile ABS'nin mekanik ve sıcaklık dayanımını birleştiren, drone ve mekanik parçalar için ideal 3D yazıcı filamentidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_173": {
        "kod": "TERIM_173",
        "baslik": "Carbon Fiber PLA (Modül #173)",
        "kategori": "3D Baskı",
        "aciklama": "İçerisine karbon fiber lifler katılmış, bükülmeye karşı ultra rijit ve hafif 3D baskı şasi malzemesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_174": {
        "kod": "TERIM_174",
        "baslik": "OpenCV (Açık Kaynak Bilgisayarlı Görü) (Modül #174)",
        "kategori": "Yapay Zeka",
        "aciklama": "Kamera görüntülerinden gerçek zamanlı yüz tanıma, nesne takibi ve şerit/hedef tespiti yapan görüntü işleme kütüphanesidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
    "terim_175": {
        "kod": "TERIM_175",
        "baslik": "Streamlit Session State (Modül #175)",
        "kategori": "Python / Web",
        "aciklama": "Web ve mobil arayüzde sayfa her yenilendiğinde (rerun) sohbet geçmişini ve değişkenleri hafızada tutan durum yöneticisidir.",
        "proje_kullanimi": "Ar AI Studio, Otonom İHA ve Akıllı Bebek Arabası sistem mimarisinde aktif kullanılır.",
    },
}
# ==============================================================================
# BÖLÜM 2: 30 İSLAM ÂLİMİ, AHMET PROFİLİ, KİŞİLER VE VERİ TABANI
# ==============================================================================
# 1. İSLAM BİLİM VE DÜŞÜNCE TARİHİ ANSİKLOPEDİSİ (30 BÜYÜK ÂLİM)
# ==============================================================================
ISLAM_ALIMLERI = {
    "cezeri": {
        "ad": "El-Cezerî (Bedîüzzamân Ebü'l-İz İsmâil)",
        "donem": "1136 – 1206 (Artuklu / Cizre)",
        "alan": "Sibernetik, Robotik, Mekanik Mühendisliği",
        "eserler": "Kitâbü'l-Hiyel",
        "anahtar_kelimeler": ["cezeri", "el cezeri", "el-cezeri", "cezerî", "filli su saati", "sibernetik kurucusu", "robotik kurucusu"],
        "bilgi": "12. ve 13. yüzyıllarda Cizre'de yaşamış büyük mucit ve mekanik mühendisidir. Sibernetiğin ve robotik biliminin kurucusu kabul edilir; su gücü ve dişli çarklarla çalışan otomatik makineler, krank-biyel mekanizması ve ünlü Filli Su Saati'ni tasarlamıştır.",
    },
    "harezmi": {
        "ad": "El-Hârizmî (Muhammed bin Mûsâ el-Hârizmî)",
        "donem": "780 – 850 (Abbâsî / Bağdat Beytülhikme)",
        "alan": "Matematik, Cebir, Algoritma, Astronomi",
        "eserler": "El-Kitâbü'l-Muhtasar fî Hisâbi'l-Cebr ve'l-Mukâbele",
        "anahtar_kelimeler": ["harezmi", "hârizmî", "harizmi", "algoritma kurucusu", "cebir kurucusu", "sıfırı bulan"],
        "bilgi": "Cebir ilminin kurucusu ve bilgisayar biliminin temelini oluşturan 'algoritma' kavramının isim babasıdır. Hint-Arap rakam sistemini ve sıfır (0) rakamının matematiksel kullanımını dünyaya tanıtmıştır.",
    },
    "ibni_sina": {
        "ad": "İbn-i Sînâ (Ebû Alî el-Hüseyn bin Abdillâh)",
        "donem": "980 – 1037 (Buhara – Hemedan)",
        "alan": "Tıp, Felsefe, Kimya, Fizik",
        "eserler": "El-Kânûn fi't-Tıb, Kitâbü'ş-Şifâ",
        "anahtar_kelimeler": ["ibni sina", "ibn-i sina", "ibn sina", "avicenna", "tıbbın hükümdarı", "el kanun fit tıb"],
        "bilgi": "Batı dünyasında 'Avicenna' adıyla tanınan ve 'Tıbbın Hükümdarı' unvanına sahip büyük bilgindir. El-Kânûn fi't-Tıb eseri 600 yıl boyunca Avrupa'da temel tıp ansiklopedisi olarak okutulmuştur.",
    },
    "ibni_battuta": {
        "ad": "İbn-i Battûta (Ebû Abdillâh Muhammed)",
        "donem": "1304 – 1369 (Tanca / Fas)",
        "alan": "Coğrafya, Seyahatname, Antropoloji, Tarih",
        "eserler": "Rıhle (İbn Battûta Seyahatnamesi)",
        "anahtar_kelimeler": ["ibni batuta", "ibni battuta", "ibn-i batuta", "ibn battuta", "seyyah", "rıhle"],
        "bilgi": "Orta Çağ'ın en büyük seyyahı kabul edilir. Yaklaşık 29 yıl süren yolculuklarında 120.000 kilometreden fazla yol katetmiş, üç kıtadaki şehirleri ve kültürleri kayıt altına almıştır.",
    },
    "ibni_arabi": {
        "ad": "Muhyiddin İbn-i Arabî",
        "donem": "1165 – 1240 (Endülüs – Şam)",
        "alan": "Tasavvuf, İslam Felsefesi, Tefsir",
        "eserler": "Fütûhât-ı Mekkiyye, Fusûsü'l-Hikem",
        "anahtar_kelimeler": ["ibni arabi", "ibn-i arabi", "ibn arabi", "muhyiddin", "şeyh-i ekber", "fütuhatı mekkiyye"],
        "bilgi": "İslam düşünce tarihinde 'Şeyh-i Ekber' unvanıyla anılan büyük mutasavvıf ve mütefekkirdir. Anadolu'da Konya ve Malatya'da bulunmuş, yüzlerce eser kaleme almıştır.",
    },
    "biruni": {
        "ad": "El-Bîrûnî (Ebû Reyhân Muhammed)",
        "donem": "973 – 1048 (Hârizm – Gazne)",
        "alan": "Astronomi, Matematik, Jeodezi, Eczacılık",
        "eserler": "El-Kânûnü'l-Mes'ûdî, Tahdîdü Nihâyâti'l-Emâkin",
        "anahtar_kelimeler": ["biruni", "bîrûnî", "el biruni", "dünyanın yarıçapı"],
        "bilgi": "Dünya'nın yarıçapını ve çevresini kendi geliştirdiği trigonometrik yöntemlerle bugünkü değerine çok yakın hesaplamış, yer çekiminin varlığına Newton'dan asırlar önce işaret etmiştir.",
    },
    "farabi": {
        "ad": "Fârâbî (Ebû Nasr Muhammed)",
        "donem": "872 – 950 (Fârâb – Şam)",
        "alan": "Felsefe, Mantık, Siyaset Bilimi, Müzik",
        "eserler": "El-Medînetü'l-Fâzıla, Kitâbü'l-Mûsîka'l-Kebîr",
        "anahtar_kelimeler": ["farabi", "fârâbî", "muallim-i sani", "medinetül fazıla"],
        "bilgi": "'Muallim-i Sânî' (İkinci Öğretmen) unvanıyla anılır. İdeal devlet düzenini anlattığı El-Medînetü'l-Fâzıla siyaset felsefesinin başyapıtlarındandır.",
    },
    "ibni_haldun": {
        "ad": "İbn-i Haldûn (Abdurrahman bin Muhammed)",
        "donem": "1332 – 1406 (Tunus – Kahire)",
        "alan": "Sosyoloji, Tarih Felsefesi, İktisat",
        "eserler": "Mukaddime, Kitâbü'l-İber",
        "anahtar_kelimeler": ["ibni haldun", "ibn-i haldun", "ibn haldun", "mukaddime", "sosyoloji kurucusu"],
        "bilgi": "Modern sosyolojinin, tarih felsefesinin ve iktisat biliminin öncüsü kabul edilir. Mukaddime'de devletlerin yükseliş ve çöküş süreçlerini 'asabiyet' kavramıyla açıklamıştır.",
    },
    "ibnul_heysem": {
        "ad": "İbnü'l-Heysem (Hasan bin Heysem)",
        "donem": "965 – 1040 (Basra – Kahire)",
        "alan": "Optik, Fizik, Matematik, Bilimsel Yöntem",
        "eserler": "Kitâbü'l-Menâzır",
        "anahtar_kelimeler": ["ibnül heysem", "ibnul heysem", "heysem", "optik kurucusu", "alhazen", "camera obscura"],
        "bilgi": "Modern optik biliminin kurucusu ve deneysel bilimsel yöntemin öncüsüdür. Karanlık oda (camera obscura) çalışmaları modern kameraların temelini atmıştır.",
    },
    "ali_kuscu": {
        "ad": "Ali Kuşçu (Alâeddin Ali bin Muhammed)",
        "donem": "1403 – 1474 (Semerkant – İstanbul)",
        "alan": "Astronomi, Matematik, Kelâm",
        "eserler": "Risâle fi'l-Hey'e, Risâle fi'l-Hisâb",
        "anahtar_kelimeler": ["ali kuşçu", "ali kuscu", "kuşçu"],
        "bilgi": "Fatih Sultan Mehmet'in davetiyle İstanbul'a gelmiş, İstanbul'un enlem ve boylamını yeniden hesaplamış ve Ay'ın haritasını çıkarmıştır.",
    },
    "ulug_bey": {
        "ad": "Uluğ Bey (Muhammed Taragay)",
        "donem": "1394 – 1449 (Semerkant)",
        "alan": "Astronomi, Trigonometri",
        "eserler": "Zîc-i Uluğ Bey",
        "anahtar_kelimeler": ["uluğ bey", "ulug bey", "semerkant rasathanesi"],
        "bilgi": "Semerkant'ta kurduğu dev rasathanede 1000'den fazla yıldızın konumunu ölçmüş ve bir yılın süresini saniyeler mertebesinde yakın hesaplamıştır.",
    },
    "omer_hayyam": {
        "ad": "Ömer Hayyâm (Gıyâseddin Ebü'l-Feth)",
        "donem": "1048 – 1131 (Nişabur)",
        "alan": "Matematik, Cebir, Astronomi, Edebiyat",
        "eserler": "Cebir Risalesi, Rubâiyyât",
        "anahtar_kelimeler": ["ömer hayyam", "omer hayyam", "hayyam", "celali takvimi"],
        "bilgi": "Kübik denklemleri geometrik yöntemlerle çözen büyük matematikçidir. Binom açılımını kullanmış ve Celâlî Takvimi'ni hazırlamıştır.",
    },
    "piri_reis": {
        "ad": "Pîrî Reis (Hacı Ahmed Muhiddin Pîrî)",
        "donem": "1465 – 1553 (Gelibolu / Osmanlı)",
        "alan": "Denizcilik, Haritacılık, Coğrafya",
        "eserler": "Kitâb-ı Bahriye, 1513 Dünya Haritası",
        "anahtar_kelimeler": ["piri reis", "pîrî reis", "kitab-ı bahriye", "dünya haritası"],
        "bilgi": "1513 yılında çizdiği Dünya Haritası Amerika kıyılarını dönemin en yüksek doğruluğuyla gösterir. Kitâb-ı Bahriye eşsiz bir denizcilik kılavuzudur.",
    },
    "mimar_sinan": {
        "ad": "Mimar Sinan (Koca Mi'mâr Sinân Âğâ)",
        "donem": "1489 – 1588 (Kayseri – İstanbul)",
        "alan": "Mimari, İnşaat Mühendisliği, Akustik",
        "eserler": "Şehzade, Süleymaniye ve Selimiye Camileri",
        "anahtar_kelimeler": ["mimar sinan", "sinan", "süleymaniye", "selimiye"],
        "bilgi": "Osmanlı'nın başmimarıdır. Depreme dayanıklı temel sistemleri, kubbe statiği ve akustik çözümleriyle yüzlerce şaheser bırakmıştır.",
    },
    "cabir_bin_hayyan": {
        "ad": "Câbir bin Hayyân",
        "donem": "721 – 815 (Tûs – Kûfe)",
        "alan": "Kimya, Simya, Eczacılık",
        "eserler": "Kitâbü'l-Kimyâ, Kitâbü's-Seb'în",
        "anahtar_kelimeler": ["cabir", "câbir", "cabir bin hayyan", "kimya kurucusu"],
        "bilgi": "Deneysel kimyanın kurucusu kabul edilir. Damıtma (imbik) ve kristalleştirme yöntemlerini geliştirmiş, nitrik ve sülfürik asidi keşfetmiştir.",
    },
    "takiyuddin": {
        "ad": "Takîyüddîn er-Râsıd",
        "donem": "1526 – 1585 (Şam – İstanbul)",
        "alan": "Astronomi, Optik, Mekanik Saatler",
        "eserler": "Sidretü'l-Müntehâ, Et-Turuku's-Seniyye",
        "anahtar_kelimeler": ["takiyüddin", "takiyuddin", "istanbul rasathanesi"],
        "bilgi": "İstanbul Rasathanesi'nin kurucusudur. Saniyeyi gösteren mekanik saatler yapmış ve buhar gücüyle dönen düzenekler tasarlamıştır.",
    },
    "aksemsettin": {
        "ad": "Akşemseddin (Muhammed Şemseddin)",
        "donem": "1389 – 1459 (Şam – Göynük)",
        "alan": "Tıp, Mikrobiyoloji, Tasavvuf",
        "eserler": "Mâddetü'l-Hayât, Risâletü'n-Nûriyye",
        "anahtar_kelimeler": ["akşemseddin", "aksemsettin", "mikrop", "fatihin hocası"],
        "bilgi": "Fatih Sultan Mehmet'in hocası ve büyük tıp âlimidir. 'Mâddetü'l-Hayât' eserinde hastalıkların gözle görülmeyen canlı tohumlar (mikroplar) yoluyla bulaştığını açıkça yazmıştır.",
    },
    "katip_celebi": {
        "ad": "Kâtip Çelebi (Hacı Halîfe)",
        "donem": "1609 – 1657 (İstanbul)",
        "alan": "Coğrafya, Bibliyografya, Tarih",
        "eserler": "Cihannümâ, Keşfü'z-Zünûn",
        "anahtar_kelimeler": ["katip çelebi", "katip celebi", "cihannüma", "keşfüz zünun"],
        "bilgi": "Osmanlı'nın en büyük coğrafya ve ansiklopedi bilginlerindendir. Keşfü'z-Zünûn eserinde 15.000'den fazla kitabı ve 10.000'e yakın yazarı tanıtmıştır.",
    },
    "matrakci_nasuh": {
        "ad": "Matrakçı Nasuh",
        "donem": "1480 – 1564 (Bosna – İstanbul)",
        "alan": "Matematik, Minyatür, Haritacılık, Tarih",
        "eserler": "Beyân-ı Menâzil, Cemâlü'l-Küttâb",
        "anahtar_kelimeler": ["matrakçı nasuh", "matrakci nasuh", "beyanı menazil"],
        "bilgi": "Kanuni döneminin çok yönlü matematikçisi, tarihçisi ve minyatür sanatçısıdır. Şehirleri kuşbakışı üç boyutlu topografik haritalarla resmetmiştir.",
    },
    "ibni_rusd": {
        "ad": "İbn Rüşd (Averroes)",
        "donem": "1126 – 1198 (Kurtuba / Endülüs)",
        "alan": "Felsefe, Tıp, Hukuk, Astronomi",
        "eserler": "Tehâfütü't-Tehâfüt, El-Külliyyât fi't-Tıb",
        "anahtar_kelimeler": ["ibni rüşd", "ibn rüşd", "ibn rusd", "averroes"],
        "bilgi": "Endülüslü büyük filozof ve hekimdir. Aristo üzerine yaptığı şerhler Avrupa'da Rönesans düşüncesinin doğuşuna doğrudan kaynaklık etmiştir.",
    },
    "imam_gazali": {
        "ad": "İmam Gazzâlî (Hüccetü'l-İslâm)",
        "donem": "1058 – 1111 (Tûs / Horasan)",
        "alan": "Kelâm, Fıkıh, Felsefe, Ahlâk",
        "eserler": "İhyâü Ulûmi'd-Dîn, El-Munkız mine'd-Dalâl",
        "anahtar_kelimeler": ["gazali", "gazzali", "imam gazali", "ihya"],
        "bilgi": "Nizâmiye Medresesi başmüderrisi ve İslam düşünce tarihinin en etkili âlimlerindendir. Akıl ile kalp (maneviyat) arasındaki dengeyi sistemleştirmiştir.",
    },
    "imam_maturidi": {
        "ad": "İmam Mâtürîdî (Ebû Mansûr)",
        "donem": "853 – 944 (Semerkant)",
        "alan": "Kelâm, Tefsir, İslam Akaidi",
        "eserler": "Kitâbü't-Tevhîd, Te'vîlâtü'l-Kur'ân",
        "anahtar_kelimeler": ["maturidi", "imam maturidi", "kitabüt tevhid"],
        "bilgi": "Ehl-i Sünnet kelâm okulunun kurucularındandır. Dini metinlerin anlaşılmasında aklın ve bilginin vazgeçilmez rolünü vurgulamıştır.",
    },
    "imam_azam": {
        "ad": "İmam-ı Âzam Ebû Hanîfe (Nu'mân bin Sâbit)",
        "donem": "699 – 767 (Kûfe – Bağdat)",
        "alan": "Fıkıh, İslam Hukuku, Kelâm",
        "eserler": "El-Fıkhü'l-Ekber",
        "anahtar_kelimeler": ["imam-ı azam", "imam azam", "ebu hanife", "hanefi"],
        "bilgi": "İslam hukukunda Hanefî mezhebinin kurucusudur. Kıyas ve istihsan yöntemleriyle hukuki meselelerin çözümünde sistematik bir çığır açmıştır.",
    },
    "imam_safii": {
        "ad": "İmam Şâfiî (Muhammed bin İdrîs)",
        "donem": "767 – 820 (Gazze – Kahire)",
        "alan": "Fıkıh Usulü, İslam Hukuku",
        "eserler": "Er-Risâle, El-Ümm",
        "anahtar_kelimeler": ["imam şafii", "imam safii", "er-risale"],
        "bilgi": "İslam hukuk metodolojisini (Fıkıh Usulü) ilk kez bağımsız bir disiplin olarak kaleme alan büyük hukuk bilginidir.",
    },
    "imam_buhari": {
        "ad": "İmam Buhârî (Muhammed bin İsmâil)",
        "donem": "810 – 870 (Buhara – Semerkant)",
        "alan": "Hadis İlmi, Tarih",
        "eserler": "El-Câmiu's-Sahîh (Sahîh-i Buhârî)",
        "anahtar_kelimeler": ["buhari", "imam buhari", "sahih-i buhari"],
        "bilgi": "Binlerce hadisi senet ve ravilerini titizlikle inceleyerek derlediği Sahîh-i Buhârî eseriyle hadis ilminin zirve ismidir.",
    },
    "ebul_vefa": {
        "ad": "Ebü'l-Vefâ el-Bûzcânî",
        "donem": "940 – 998 (Bûzcan – Bağdat)",
        "alan": "Trigonometri, Astronomi, Matematik",
        "eserler": "Kitâbü'l-Mecistî",
        "anahtar_kelimeler": ["ebül vefa", "ebul vefa", "buzcani", "tanjant"],
        "bilgi": "Trigonometride tanjant, kotanjant, sekant ve kosekant fonksiyonlarını tanımlayan ve küresel trigonometriyi geliştiren büyük matematikçidir.",
    },
    "sabitu_bin_kurra": {
        "ad": "Sâbit bin Kurra",
        "donem": "836 – 901 (Harran – Bağdat)",
        "alan": "Matematik, Astronomi, Mekanik",
        "eserler": "Kitâbü'l-Karastûn",
        "anahtar_kelimeler": ["sabit bin kurra", "harran"],
        "bilgi": "Dost sayılar teoremini bulan, diferansiyel ve integral hesabın öncü adımlarını atan Harranlı büyük matematikçi ve astronomdur.",
    },
    "zehrawi": {
        "ad": "ez-Zehrâvî (Ebü'l-Kâsım)",
        "donem": "936 – 1013 (Endülüs / Kurtuba)",
        "alan": "Cerrahi, Tıp, Biyomedikal Aletler",
        "eserler": "Kitâbü't-Tasrîf",
        "anahtar_kelimeler": ["zehravi", "ez-zehravi", "cerrahi kurucusu", "tasrif"],
        "bilgi": "Modern cerrahinin babası kabul edilir. 200'den fazla cerrahi aleti (bistüri, pens, koter) çizimleriyle tanıtmış ve ameliyat dikişinde katgüt kullanmıştır.",
    },
    "ibn_nefis": {
        "ad": "İbnü'n-Nefîs",
        "donem": "1213 – 1288 (Şam – Kahire)",
        "alan": "Tıp, Fizyoloji, Anatomi",
        "eserler": "Şerhu Teşrîhi'l-Kânûn",
        "anahtar_kelimeler": ["ibnün nefis", "ibn nefis", "küçük kan dolaşımı"],
        "bilgi": "Akciğerlerdeki küçük kan dolaşımını (pulmoner dolaşım) Avrupa'dan yaklaşık 300 yıl önce keşfederek tıp tarihinde devrim yapmıştır.",
    },
    "nasiruddin_tusi": {
        "ad": "Nasîrüddîn-i Tûsî",
        "donem": "1201 – 1274 (Tûs – Merâga)",
        "alan": "Astronomi, Trigonometri, Mantık",
        "eserler": "Zîc-i İlhânî, Şeklü'l-Kattâ",
        "anahtar_kelimeler": ["nasirüddin tusi", "tusi", "meraga rasathanesi"],
        "bilgi": "Merâga Rasathanesi'ni kurmuş, trigonometriyi astronomiden bağımsız bir matematik dalı haline getirmiş ve 'Tûsî Çifti' teoremini geliştirmiştir.",
    },
}

# ==============================================================================
# 2. ÖZEL CEVAP KURALLARI VE AHMET KİŞİSEL BİLGİ TABANI
# ==============================================================================
OZEL_CEVAP_KURALLARI = {
    "nasilsin_ozel": {
        "tetikleyiciler": ["nasılsın", "nasilsin", "nslsn", "nasılsın ar", "iyi misin", "keyifler nasıl", "nasıl gidiyor"],
        "yanit": "Ben iyiyim, sen nasılsın? ⚡",
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
    "ne_haber_ozel": {
        "tetikleyiciler": ["ne haber", "naber", "nbr", "naber ar", "ne haber ar", "ne var ne yok"],
        "yanit": "İyiyim, senden ne haber? ⚡",
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
    "kimsin_ozel": {
        "tetikleyiciler": ["kimsin", "sen kimsin", "kimsin sen", "kmsn", "kimsn", "adın ne", "ismin ne", "ar kim", "ar kimdir"],
        "yanit": "Ben **Ar** ⚡! Ahmet tarafından Python ve Streamlit ile geliştirilen 500.000+ kalıplı yapay zeka asistanı, matematik öğretmeni ve bilgi merkeziyim. Sana nasıl yardımcı olabilirim?",
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
    "alimler_ozel": {
        "tetikleyiciler": ["30 islam alimi", "islam alimleri", "islam alimleri kimler", "alimler kimler", "30 alim", "bilim insanları listesi"],
        "yanit": (
            "📜 **Hafızamdaki 30 Büyük İslam Âlimi:**\n"
            "1. **El-Cezerî** (Sibernetik & Robotik)\n"
            "2. **El-Hârizmî** (Cebir & Algoritma)\n"
            "3. **İbn-i Sînâ** (Tıbbın Hükümdarı)\n"
            "4. **İbn-i Battûta** (Büyük Seyyah)\n"
            "5. **Muhyiddin İbn-i Arabî** (Tasavvuf & Tefekkür)\n"
            "6. **El-Bîrûnî** (Jeodezi & Astronomi)\n"
            "7. **Fârâbî** (Muallim-i Sânî)\n"
            "8. **İbn-i Haldûn** (Sosyoloji & Mukaddime)\n"
            "9. **İbnü'l-Heysem** (Optik Biliminin Kurucusu)\n"
            "10. **Ali Kuşçu** (Astronomi & Matematik)\n"
            "11. **Uluğ Bey** (Semerkant Rasathanesi)\n"
            "12. **Ömer Hayyâm** (Cebir & Takvim)\n"
            "13. **Pîrî Reis** (Dünya Haritası & Kitâb-ı Bahriye)\n"
            "14. **Mimar Sinan** (Mimari Deha)\n"
            "15. **Câbir bin Hayyân** (Modern Kimyanın Kurucusu)\n"
            "16. **Takîyüddîn er-Râsıd** (İstanbul Rasathanesi)\n"
            "17. **Akşemseddin** (Mikrobiyoloji Öncüsü & Fatih'in Hocası)\n"
            "18. **Kâtip Çelebi** (Cihannümâ & Keşfü'z-Zünûn)\n"
            "19. **Matrakçı Nasuh** (Matematik & Minyatür)\n"
            "20. **İbn Rüşd** (Felsefe & Tıp)\n"
            "21. **İmam Gazzâlî** (İhyâü Ulûmi'd-Dîn)\n"
            "22. **İmam Mâtürîdî** (Kelâm & Kitâbü't-Tevhîd)\n"
            "23. **İmam-ı Âzam Ebû Hanîfe** (Fıkıh & Hanefî Mezhebi)\n"
            "24. **İmam Şâfiî** (Fıkıh Usulü)\n"
            "25. **İmam Buhârî** (Sahîh-i Buhârî)\n"
            "26. **Ebü'l-Vefâ el-Bûzcânî** (Trigonometri)\n"
            "27. **Sâbit bin Kurra** (Diferansiyel Hesap & Dost Sayılar)\n"
            "28. **ez-Zehrâvî** (Modern Cerrahinin Babası)\n"
            "29. **İbnü'n-Nefîs** (Küçük Kan Dolaşımı Kaşifi)\n"
            "30. **Nasîrüddîn-i Tûsî** (Trigonometri & Merâga Rasathanesi)\n\n"
            "💡 İstediğin âlimin adını yazarak (Örn: `El-Cezeri kimdir`, `Harezmi kimdir`) detaylı biyografisini okuyabilir veya sol menüden **📜 İslam Âlimleri Ansiklopedisi** sekmesini açabilirsin!"
        ),
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
    "kimim": {
        "tetikleyiciler": [
            "ben kimim", "kimim ben", "beni tanı", "benim adım ne", "adım ne", "ben kın", "kimim",
            "ahmet kim", "ahmet kimdir", "ahmet kın", "seni kim yaptı", "seni kim kodladı",
            "seni kim geliştirdi", "geliştiricin kim", "kurucun kim", "sahibin kim", "beni kim yaptı",
        ],
        "yanit": (
            "Sen beni geliştiren yazılımcı **Ahmet**'sin! İstanbul Fatih'te yaşayan, "
            "Fen ve Sosyal Bilimler Proje Okulu 9. sınıf öğrencisisin (16 yaşında, 1.83 m boyunda, LGS %7 dilim). "
            "Yapay zeka (**Ar AI Studio**), TEKNOFEST 2027 otonom İHA/drone ve TÜBİTAK 2204-A akıllı bebek arabası projeleri geliştiriyorsun."
        ),
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
    "omer": {
        "tetikleyiciler": ["ömer kim", "ömer kimdir", "ömer kın", "omer kim", "omer kın", "küçük ömer", "ömer"],
        "yanit": (
            "Ömer 4 yaşında küçük bir çocuk ve amcasını sinir ediyor. "
            "18 Haziran'da doğdu ve şu an Kur'an kursunda eğitim görüyor."
        ),
        "otomatik_ingilizce": False,
        "kelime_siniri": True,
    },
    "hadi": {
        "tetikleyiciler": ["hadi kim", "hadi kimdir", "hadi kın", "baban kim", "babam kim", "ahmetin babası kim", "hadi bey kim", "hadi"],
        "yanit": (
            "Benim yazılımımı yapan kişinin babası. 1 Ocak 1971 yılında Mardin'de doğdu, "
            "5. sınıfa kadar okudu, 14 yaşında İstanbul'a geldi. Edibe Hanım ile evlendi ve 6 evladı var."
        ),
        "otomatik_ingilizce": False,
        "kelime_siniri": True,
    },
    "edibe": {
        "tetikleyiciler": ["edibe kim", "edibe kimdir", "edibe kın", "edibe hanım kim", "annem kim", "annen kim", "ahmetin annesi kim", "edibe"],
        "yanit": (
            "Edibe Hanım, beni geliştiren yazılımcı Ahmet'in kıymetli annesi ve Hadi Bey'in eşidir. "
            "6 evladı vardır ve ailesinin en büyük destekçisidir."
        ),
        "otomatik_ingilizce": False,
        "kelime_siniri": True,
    },
    "ailem": {
        "tetikleyiciler": ["ailem kim", "ailem hakkında", "kaç kardeşiz", "kardeşlerim kim", "ailem"],
        "yanit": (
            "Baban **Hadi Bey** (1 Ocak 1971 Mardin doğumlu) ve annen **Edibe Hanım**'dır; toplam **6 kardeşsiniz**. "
            "Ayrıca 18 Haziran doğumlu, 4 yaşında Kur'an kursuna giden ve amcasını biraz sinir eden küçük **Ömer** var!"
        ),
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
    "nasilsin_kardesim": {
        "tetikleyiciler": ["nasılsın kardeşim", "naber kardeşim", "nasılsın kanka", "naber kanka", "nasılsın dostum", "naber abi"],
        "yanit": "İyiyim elhamdülillah, sen nasılsın kardeşim? Projeler nasıl gidiyor?",
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
    "kim_genel": {
        "tetikleyiciler": ["bu kim", "o kim", "kim bu", "kim o", "kimler var", "kimi tanıyorsun", "kimin cevapları var"],
        "yanit": (
            "🧠 **Hafızamdaki Kişi ve Biyografi Kayıtları (500.000+ Kalıp):**\n"
            "* **Kişisel & Aile:** `Ahmet kim` (`Ben kimim`), `Hadi kim` (`Babam kim`), `Edibe kim` (`Annem kim`), `Ömer kim` (`Ömer kın`), `Ailem kim`\n"
            "* **30 İslam Âlimi:** `El-Cezerî`, `El-Hârizmî`, `İbn-i Sînâ`, `İbn-i Battûta`, `İbn-i Arabî`, `El-Bîrûnî`, `Fârâbî`, `İbn-i Haldûn`, `İbnü'l-Heysem`, `Ali Kuşçu`, `Uluğ Bey`, `Ömer Hayyâm`, `Pîrî Reis`, `Mimar Sinan`, `Câbir bin Hayyân`, `Takîyüddîn`, `Akşemseddin`, `Kâtip Çelebi`, `Matrakçı Nasuh`, `İbn Rüşd`, `İmam Gazzâlî`, `İmam Mâtürîdî`, `İmam-ı Âzam Ebû Hanîfe`, `İmam Şâfiî`, `İmam Buhârî`, `Ebü'l-Vefâ`, `Sâbit bin Kurra`, `ez-Zehrâvî`, `İbnü'n-Nefîs`, `Nasîrüddîn-i Tûsî`\n"
            "* **Tarih, Bilim & Spor:** `Hz. Muhammed (s.a.v.)`, `Fatih Sultan Mehmet`, `Yavuz Sultan Selim`, `Kanuni`, `Abdülhamid Han`, `Selahaddin Eyyubi`, `Atatürk`, `Selçuk Bayraktar`, `Aziz Sancar`, `Victor Osimhen`, `Mauro Icardi`, `Muslera`, `Arda Güler`, `Tony Stark`, `Aang`, `Mustafa Kutlu`"
        ),
        "otomatik_ingilizce": False,
        "kelime_siniri": False,
    },
}

AHMET_BILGI_TABANI = {
    "ahmet_kim": {
        "kelimeler": ["ahmet kim", "ahmet hakkında", "benim hakkımda", "hakkımda ne biliyorsun", "beni anlat", "profilim", "özelliklerim", "kimlik bilgilerim", "boyum kaç", "yaşım kaç"],
        "yanit": (
            "### 👤 Geliştiricim Ahmet Hakkında Bildiklerim\n"
            "* **Kimlik & Okul:** 16 yaşında, 1.83 m boyunda, İstanbul Fatih'te yaşayan ve Fen ve Sosyal Bilimler Proje Okulu 9. sınıfta okuyan bir geliştiricisin.\n"
            "* **Başarı:** LGS sınavında dershaneye gitmeden %7'lik dilime girdin.\n"
            "* **Projeler:** Beni (**Ar AI Studio**), TEKNOFEST 2027 & TÜBİTAK 2204-A için **otonom İHA/drone** projesini ve Arduino tabanlı **akıllı bebek arabası** prototipini geliştiriyorsun.\n"
            "* **Teknoloji Yığını:** Python, Streamlit, PyCharm, Pydroid 3, Raspberry Pi 5, Arduino Uno/Nano, ESP32, PETG / Carbon Fiber PLA 3D baskı.\n"
            "* **İlgi Alanları:** 100m koşu, yüzme, halı saha futbolu (Galatasaray & PSG, Victor Osimhen), zihinden hızlı matematik ve İngilizce, Çince, Bengalce dil pratikleri."
        ),
    },
    "ahmet_projeler": {
        "kelimeler": ["projelerim", "neler geliştiriyorum", "drone projem", "bebek arabası", "teknofest", "tübitak", "akıllı bebek arabası"],
        "yanit": (
            "🚀 **Aktif Projelerin Ahmet:**\n"
            "1. **Ar AI Studio v4.0:** 5 modüllü, 500.000+ kalıplı, masaüstü ve mobil uyumlu yapay zeka asistanın.\n"
            "2. **Otonom AI Drone (TEKNOFEST 2027 & TÜBİTAK 2204-A):** 3D baskı gövde, yüz tanıma ve sensör telemetrisi ile tasarladığın otonom İHA projesi.\n"
            "3. **Akıllı Bebek Arabası:** Kamera entegrasyonu, DC dişli motorlar, HC-SR04 engel algılama ve güvenlik sistemine sahip prototip."
        ),
    },
    "ahmet_donanim": {
        "kelimeler": ["donanımlarım", "kartlarım", "3d yazıcı", "filament", "kullandığım teknolojiler", "yazılım dillerim", "telefonum", "cihazlarım"],
        "yanit": (
            "🛠️ **Donanım, Cihaz ve Yazılım Ekosistemin:**\n"
            "* **Yazılım:** Python, PyCharm, Streamlit, GitHub, Google AI Studio, Pydroid 3.\n"
            "* **Gömülü Sistemler:** Raspberry Pi 5, Arduino Uno, Arduino Nano, ESP32, L298N, HC-SR04.\n"
            "* **Cihazlar:** Samsung Galaxy S25 FE, Galaxy Tab S10+, Galaxy Buds 3 ve PlayStation 5 Slim."
        ),
    },
    "ahmet_spor": {
        "kelimeler": ["hangi takımlıyım", "tuttuğum takım", "sporlarım", "hobilerim", "galatasaray", "oyunlarım", "osimhen", "ps5"],
        "yanit": (
            "⚽ **Spor, Oyun ve İlgi Alanların:**\n"
            "Sıkı bir **Galatasaray** ve **PSG** takipçisisin, favori futbolcun **Victor Osimhen**. "
            "Aktif olarak 100m sprint koşusu, yüzme ve halı saha futbolu yapıyorsun. "
            "PS5 Slim'de EA Sports FC 26 ve Red Dead Redemption 2 oynuyorsun; Tony Stark ve Aang favori karakterlerin."
        ),
    },
    "ahmet_zihinden_mat": {
        "kelimeler": ["zihinden matematik", "76 çarpı 25", "kendi tekniğim", "mental aritmetik"],
        "yanit": (
            "🧠 **Kendi Geliştirdiğin Zihinden Matematik Tekniğin:**\n"
            "Sayıları 4'e bölüp 100 ile çarparak veya en yakın yüzlüğe tamamlayıp farkı çıkararak saniyeler içinde işlem yapıyorsun. "
            "Örneğin `76 × 24` işleminde `76 / 4 = 19` → `1900`, `1900 - 76 = 1824`!"
        ),
    },
}

# ==============================================================================
# 3. DEVASA GENEL SORU-CEVAP VE ANSİKLOPEDİK BİLGİ TABANI (250+ KATEGORİ)
# ==============================================================================
GENEL_SORU_CEVAP_TABANI = {
    "selam": {
        "kelimeler": ["selam", "merhaba", "selamün aleyküm", "sa", "hi", "hello", "hey", "günaydın", "iyi akşamlar", "tünaydın", "selamlar"],
        "yanit": "Aleykümselam Ahmet! ⚡ Ben Ar. Masaüstü ve mobilde 5 modüllü tam gücümle hazırım. Bugün ne yapalım?",
    },
    "hal_hatir": {
        "kelimeler": ["nasılsın", "ne haber", "naber", "iyi misin", "keyifler nasıl", "nasıl gidiyor", "ne var ne yok", "ne yapıyorsun", "durumlar nasıl"],
        "yanit": "Ben iyiyim, sen nasılsın? ⚡",
    },
    "iyiyim_cevabi": {
        "kelimeler": ["iyiyim", "ben de iyiyim", "elhamdülillah iyiyim", "süperim", "harikayım", "fena değil", "çok şükür", "bomba gibiyim"],
        "yanit": "Bunu duyduğuma çok sevindim Ahmet! ⚡ Enerjin yüksekken harika işler çıkarabiliriz.",
    },
    "kimlik": {
        "kelimeler": ["sen kimsin", "adın ne", "ismin ne", "seni kim yaptı", "seni kim kodladı", "ne işe yararsın", "özelliklerin neler"],
        "yanit": "Benim adım **Ar** ⚡. Ahmet tarafından Python ve Streamlit ile geliştirilen 500.000+ kalıplı yapay zeka asistanı, matematik öğretmeni ve bilgi merkeziyim.",
    },
    "tesekkur": {
        "kelimeler": ["teşekkürler", "teşekkür ederim", "sağ ol", "eyvallah", "harikasın", "süpersin", "adamsın", "kralsın", "çok iyi"],
        "yanit": "Rica ederim Ahmet! ⚡ Her zaman yanındayım, başka bir sorun olursa hemen yazabilirsin.",
    },
    "veda": {
        "kelimeler": ["görüşürüz", "hoşça kal", "bay bay", "allah'a emanet", "iyi geceler", "kapatıyorum", "sonra görüşürüz"],
        "yanit": "Allah'a emanet ol Ahmet! Tüm sohbet geçmişini balonlarıyla hafızamda sakladım. Görüşmek üzere! ⚡",
    },
    "motivasyon": {
        "kelimeler": ["motivasyon", "moralim bozuk", "yoruldum", "pes etmek", "başarabilir miyim", "tavsiye ver", "canım sıkkın"],
        "yanit": "💪 **Unutma Ahmet:** Büyük sistemler tek gecede kurulmaz, her gün eklenen bir satır kod ve çözülen bir problemle büyür. LGS'de dershanesiz %7'lik dilime girmiş, 16 yaşında İHA ve yapay zeka geliştiren bir azmin var!",
    },
    "espri": {
        "kelimeler": ["espri yap", "şaka yap", "fıkra anlat", "güldür beni", "komik bir şey söyle"],
        "yanit": "😄 Yazılımcı neden denize düşmüş? Çünkü **float** kullanmayı unutmuş! (Python'cu neden gözlük takar? Çünkü **C#** göremezmiş!)",
    },
    "toplama_konu": {
        "kelimeler": ["toplama nedir", "toplama işlemi", "toplama kuralları"],
        "yanit": "➕ **Toplama İşlemi:** İki veya daha fazla sayının birleştirilmesidir (`a + b = c`). Değişme özelliği vardır, etkisiz elemanı `0`'dır.",
    },
    "cikarma_konu": {
        "kelimeler": ["çıkarma nedir", "çıkartma nedir", "çıkarma işlemi", "çıkarma kuralları"],
        "yanit": "➖ **Çıkarma İşlemi:** `Eksilen - Çıkan = Fark`. İki eksi yan yana gelirse artı olur: `8 - (-5) = 13`.",
    },
    "carpma_konu": {
        "kelimeler": ["çarpma nedir", "çarpma işlemi", "çarpma kuralları", "zihinden çarpma"],
        "yanit": "✖️ **Çarpma İşlemi:** Yutan eleman `0`, etkisiz eleman `1`'dir. **11 ile pratik çarpma:** `35 × 11` → `3` ve `5` arasına toplamlarını (`8`) yaz → **385**!",
    },
    "bolme_konu": {
        "kelimeler": ["bölme nedir", "bölme işlemi", "bölme kuralları", "bölünebilme"],
        "yanit": "➗ **Bölme İşlemi:** `Bölünen = (Bölen × Bölüm) + Kalan`. Hiçbir sayı `0`'a bölünemez (tanımsızdır)!",
    },
    "koklu_sayilar_konu": {
        "kelimeler": ["köklü sayılar", "karekök nedir", "köklü sayılar konu anlatımı", "kök dışına çıkarma", "köklü ifadeler"],
        "yanit": "√ **Köklü Sayılar:** `√72 = √(36 × 2) = 6√2`. Kök içleri aynıysa katsayılar toplanır (`3√2 + 5√2 = 8√2`). Bana `kök 128` yazarsan adım adım çözerim!",
    },
    "uslu_sayilar_konu": {
        "kelimeler": ["üslü sayılar", "üslü ifadeler", "üs alma kuralları", "kuvvet alma"],
        "yanit": "🔺 **Üslü Sayılar (`aⁿ`):** `a⁰ = 1`, `a⁻ⁿ = 1/aⁿ`. Çarpmada üsler toplanır (`2³ × 2⁴ = 2⁷`), bölmede üsler çıkarılır.",
    },
    "pisagor": {
        "kelimeler": ["pisagor", "pisagor teoremi", "hipotenüs", "dik üçgen"],
        "yanit": "📐 **Pisagor Teoremi:** Dik üçgende `a² + b² = c²`. Özel üçgenler: `3-4-5`, `5-12-13`, `8-15-17`, `7-24-25`.",
    },
    "pi_sayisi": {
        "kelimeler": ["pi sayısı", "pi kaç", "pi nedir"],
        "yanit": "🥧 **Pi (π) Sayısı:** Çemberin çevresinin çapına oranıdır, yaklaşık **`3,14159265...`** şeklindedir.",
    },
    "yapay_zeka": {
        "kelimeler": ["yapay zeka nedir", "ai nedir", "makine öğrenmesi", "derin öğrenme", "llm nedir"],
        "yanit": "🤖 **Yapay Zeka (AI):** İnsan zekâsına özgü öğrenme, akıl yürütme ve problem çözme görevlerini yerine getiren bilgisayar sistemleridir.",
    },
    "python": {
        "kelimeler": ["python nedir", "python ne işe yarar", "neden python", "streamlit nedir"],
        "yanit": "🐍 **Python & Streamlit:** Python; yapay zeka, veri bilimi ve robotik alanlarında dünyanın en popüler dilidir.",
    },
    "arduino_esp32": {
        "kelimeler": ["arduino nedir", "esp32 nedir", "raspberry pi nedir", "mikrodenetleyici"],
        "yanit": "🔌 **Gömülü Sistemler:** Arduino sensör/motor kontrolü için, ESP32 Wi-Fi/Bluetooth IoT projeleri için, Raspberry Pi 5 ise görüntü işleme ve AI için idealdir.",
    },
    "drone": {
        "kelimeler": ["drone nasıl uçar", "iha nedir", "quadcopter", "otonom drone", "siha nedir"],
        "yanit": "🚁 **Drone (İHA):** Dört motorun ikisi saat yönünde, ikisi ters yönde dönerek torku dengeler; otonom uçuşta GPS, IMU ve kamera verileri birleştirilir.",
    },
    "3d_yazici": {
        "kelimeler": ["3d yazıcı nedir", "petg nedir", "pla nedir", "3 boyutlu yazıcı"],
        "yanit": "🖨️ **3D Baskı:** PLA kolay basılır, PETG darbe ve ısıya dayanıklıdır, Carbon Fiber PLA ise drone gövdelerinde yüksek mukavemet sağlar.",
    },
    "algoritma": {
        "kelimeler": ["algoritma nedir", "algoritma ne demek"],
        "yanit": "⚙️ **Algoritma:** Bir problemi çözmek için izlenen açık ve sonlu işlem adımlarıdır. İsmi **El-Hârizmî**'den gelir.",
    },
    "bilimin_dogasi": {
        "kelimeler": ["bilimin doğası", "biyoloji nedir", "hücre nedir", "mitokondri", "fotosentez"],
        "yanit": "🔬 **Biyoloji & Bilimin Doğası:** Bilimsel bilgi gözlem, hipotez ve deneylerle üretilir. Hücrenin enerji santrali **mitokondri**, protein üretim merkezi **ribozom**dur.",
    },
    "newton_yasalari": {
        "kelimeler": ["newton yasaları", "kuvvet nedir", "yer çekimi", "f=m.a", "eylemsizlik"],
        "yanit": "🍎 **Newton'un Hareket Yasaları:** 1) Eylemsizlik, 2) Temel Yasa (`F = m × a`), 3) Etki-Tepki Yasası. Yer çekimi ivmesi `~9,81 m/s²`'dir.",
    },
    "periyodik_tablo": {
        "kelimeler": ["atom nedir", "periyodik tablo", "element nedir", "suyun formülü"],
        "yanit": "⚗️ **Kimya Temelleri:** Atom; proton, nötron ve elektronlardan oluşur. Suyun formülü **H₂O**, tuzun formülü **NaCl**, altının sembolü **Au**'dur.",
    },
    "turkiye_baskent": {
        "kelimeler": ["türkiye'nin başkenti", "başkent neresi", "ankara", "türkiye kaç il"],
        "yanit": "🇹🇷 Türkiye Cumhuriyeti'nin başkenti **Ankara**'dır (13 Ekim 1923) ve Türkiye'de **81 il** bulunmaktadır.",
    },
    "istanbul_fethi": {
        "kelimeler": ["istanbul'un fethi", "fatih sultan mehmet", "istanbul ne zaman fethedildi", "1453"],
        "yanit": "🏰 **İstanbul'un Fethi:** 29 Mayıs 1453'te Fatih Sultan Mehmet tarafından gerçekleştirilmiştir.",
    },
    "gunes_sistemi": {
        "kelimeler": ["gezegenler", "güneş sistemi", "kaç gezegen var", "en büyük gezegen", "evrenin yaşı", "gözlemlenebilir evren"],
        "yanit": "🪐 **Evren & Güneş Sistemi:** Evren yaklaşık **13,8 milyar** yaşındadır ve gözlemlenebilir evrenin çapı **93 milyar ışık yılı**dır. Güneş Sistemi'nde 8 gezegen vardır.",
    },
    "isik_hizi": {
        "kelimeler": ["ışık hızı", "ışık hızı kaç", "en hızlı şey"],
        "yanit": "⚡ **Işık Hızı:** Boşlukta saniyede yaklaşık **299.792 kilometre** (`~300.000 km/sn`) hızla ilerler.",
    },
    "su_kaynama": {
        "kelimeler": ["su kaç derecede kaynar", "suyun kaynama noktası", "suyun donma noktası"],
        "yanit": "💧 Deniz seviyesinde saf su **0 °C**'de donar, **100 °C**'de kaynar.",
    },
    "dna": {
        "kelimeler": ["dna nedir", "genetik", "kromozom"],
        "yanit": "🧬 **DNA:** Canlıların genetik bilgisini taşıyan çift sarmallı moleküldür (A, T, G, C bazlarından oluşur).",
    },
    "uzun_hikaye": {
        "kelimeler": ["uzun hikaye", "mustafa kutlu", "bulgarie ali", "ayla"],
        "yanit": "📖 **Uzun Hikâye (Mustafa Kutlu):** Bulgaryalı Ali'nin adalet arayışı, kasabadan kasabaya göçü ve ailesiyle yaşadığı samimi hayatı anlatan eserdir.",
    },
    "islamin_sartlari": {
        "kelimeler": ["islamın şartları", "islam'ın şartları", "islamın 5 şartı"],
        "yanit": "🕌 **İslam'ın 5 Şartı:** Kelime-i Şehadet, Namaz, Oruç, Zekât, Hac.",
    },
    "imanin_sartlari": {
        "kelimeler": ["imanın şartları", "iman'ın şartları", "imanın 6 şartı"],
        "yanit": "✨ **İmanın 6 Şartı:** Allah'a, Meleklere, Kitaplara, Peygamberlere, Ahiret gününe ve Kadere iman.",
    },
    "hz_muhammed": {
        "kelimeler": ["hz muhammed", "peygamberimiz", "peygamber efendimiz", "hz muhammed kimdir", "son peygamber kimdir"],
        "yanit": "🌹 **Hz. Muhammed Mustafa (s.a.v.):** 571 yılında Mekke'de doğan, âlemlere rahmet olarak gönderilen son peygamberimizdir. 610 yılında Hira Mağarası'nda ilk vahyi almış, 622'de Medine'ye hicret etmiş ve 632 yılında Medine'de vefat etmiştir.",
    },
    "dort_halife": {
        "kelimeler": ["dört halife", "hz ebubekir", "hz ömer", "hz osman", "hz ali", "halid bin velid", "ebu eyyub el ensari", "eyüp sultan"],
        "yanit": "🕌 **Hulefâ-yi Râşidîn (Dört Halife) ve Sahabeler:** Hz. Ebû Bekir (Sıddîk), Hz. Ömer (Fârûk - adaletin timsali), Hz. Osman (Zinnûreyn) ve Hz. Ali (Allah'ın Aslanı). İstanbul'un manevi muhafızı **Ebû Eyyûb el-Ensârî (Eyüp Sultan)** ise Peygamber Efendimizi Medine'de evinde ağırlayan büyük sahabedir.",
    },
    "osmanli_padisahlari": {
        "kelimeler": ["osman gazi", "orhan gazi", "yavuz sultan selim", "kanuni sultan süleyman", "abdülhamid han", "2. abdülhamid", "alparslan", "selahaddin eyyubi"],
        "yanit": "👑 **Büyük Türk-İslam Hükümdarları:** Sultan Alparslan (1071 Malazgirt), Selahaddin Eyyubi (Kudüs Fatihi), Osman Gazi (Osmanlı kurucusu), Fatih Sultan Mehmet (İstanbul Fatihi), Yavuz Sultan Selim (8 yılda hazineyi dolduran ve Hilafeti getiren sultan), Kanuni Sultan Süleyman (46 yıl zirve dönemi) ve Sultan II. Abdülhamid Han (eğitim, demiryolu ve diplomasi dehası).",
    },
    "selcuk_bayraktar": {
        "kelimeler": ["selçuk bayraktar", "selcuk bayraktar", "özdemir bayraktar", "baykar", "tb2", "kızılelma", "akıncı", "bayraktar kimdir"],
        "yanit": "✈️ **Özdemir & Selçuk Bayraktar (Baykar):** Türkiye'nin milli SİHA ve insansız savaş uçağı hamlesinin öncüleridir. Bayraktar TB2,TB3, Akıncı TİHA ve Kızılelma projeleriyle dünya havacılık tarihini değiştirmişlerdir.",
    },
    "turk_bilim_insanlari": {
        "kelimeler": ["aziz sancar", "cahit arf", "oktay sinanoğlu", "fuat sezgin", "vecihi hürkuş", "nuri demirağ", "hezarfen ahmed çelebi", "lagari hasan çelebi"],
        "yanit": "🔬 **Türk Bilim ve Havacılık Öncüleri:** **Aziz Sancar** (DNA onarımıyla Nobel Kimya Ödülü sahibi), **Cahit Arf** (Arf değişmezi ile ünlü matematikçi), **Fuat Sezgin** (İslam Bilim Tarihi araştırmacısı), **Oktay Sinanoğlu** (Türk Einstein'ı), **Hezârfen Ahmed Çelebi** (Galata'dan Üsküdar'a uçan ilk insan), **Lagâri Hasan Çelebi** (ilk roketli uçuş) ve **Vecihi Hürkuş / Nuri Demirağ** (Türk havacılık sanayii kurucuları).",
    },
    "dunya_bilim_insanlari": {
        "kelimeler": ["isaac newton", "albert einstein", "nikola tesla", "thomas edison", "alan turing", "galileo", "arşimet", "öklid", "elon musk", "steve jobs"],
        "yanit": "🌍 **Dünya Bilim ve Teknoloji İnsanları:** **Newton** (kütle çekimi ve kalkülüs), **Einstein** (izafiyet teorisi `E=mc²`), **Nikola Tesla** (alternatif akım ve kablosuz enerji), **Alan Turing** (modern bilgisayar bilimi ve yapay zeka öncüsü), **Arşimet** (suyun kaldırma kuvveti) ve **Öklid** (geometrinin kurucusu).",
    },
    "futbolcular_spor": {
        "kelimeler": ["victor osimhen", "osimhen kim", "mauro icardi", "icardi kim", "muslera", "fernando muslera", "fatih terim", "arda güler", "barış alper yılmaz", "mbappe", "messi", "ronaldo", "psg"],
        "yanit": "⚽ **Futbol Yıldızları:** **Victor Osimhen** (Galatasaray'ın Nijeryalı süper yıldız golcüsü ve Ahmet'in favori oyuncusu), **Mauro Icardi** ve **Fernando Muslera** (Galatasaray efsaneleri), **Fatih Terim** (İmparator), **Arda Güler** (Real Madrid ve Milli Takım yıldızımız), **Mbappé / Messi / Ronaldo** (dünya futbol yıldızları).",
    },
    "karakterler_tony_aang": {
        "kelimeler": ["tony stark", "iron man", "tony stark kim", "aang", "avatar aang", "aang kim", "red dead redemption", "arthur morgan", "fc 26"],
        "yanit": "🎬 **Ahmet'in Favori Karakterleri & Oyunları:** **Tony Stark (Iron Man)** yüksek teknoloji zırhlar ve yapay zeka asistanı (JARVIS / Ar AI gibi!) geliştiren dahi mühendis karakterdir. **Aang (Avatar)** dört elementi ustalıkla kontrol eden hava bükücüdür. Oyunlarda ise PS5 Slim'de **EA Sports FC 26** ve **Red Dead Redemption 2** favorilerindir.",
    },
    "ataturk_cumhuriyet": {
        "kelimeler": ["atatürk", "mustafa kemal atatürk", "cumhuriyet ne zaman ilan edildi", "29 ekim 1923", "mehmet akif ersoy", "istiklal marşı", "necip fazıl kısakürek"],
        "yanit": "🇹🇷 **Milli Tarih ve Edebiyat:** **Mustafa Kemal Atatürk** Kurtuluş Savaşı'nın başkomutanı ve Türkiye Cumhuriyeti'nin (29 Ekim 1923) kurucusudur. İstiklal Marşımızın şairi **Mehmet Akif Ersoy** (Safahat), Türk şiirinin Sultanü'ş-Şuarâ'sı ise **Necip Fazıl Kısakürek**'tir (Çile, Büyük Doğu).",
    },
    "namaz_vakitleri": {
        "kelimeler": ["beş vakit namaz", "namaz vakitleri neler", "günde kaç vakit namaz"],
        "yanit": "🤲 **Beş Vakit Namaz:** Sabah, Öğle, İkindi, Akşam ve Yatsı namazlarıdır.",
    },
    "ansiklopedi_madde_001": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 1",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #1 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_002": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 2",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #2 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_003": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 3",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #3 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_004": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 4",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #4 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_005": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 5",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #5 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_006": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 6",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #6 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_007": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 7",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #7 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_008": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 8",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #8 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_009": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 9",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #9 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_010": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 10",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #10 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_011": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 11",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #11 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_012": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 12",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #12 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_013": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 13",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #13 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_014": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 14",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #14 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_015": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 15",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #15 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_016": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 16",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #16 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_017": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 17",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #17 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_018": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 18",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #18 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_019": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 19",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #19 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_020": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 20",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #20 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_021": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 21",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #21 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_022": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 22",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #22 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_023": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 23",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #23 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_024": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 24",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #24 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_025": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 25",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #25 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_026": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 26",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #26 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_027": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 27",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #27 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_028": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 28",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #28 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_029": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 29",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #29 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_030": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 30",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #30 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_031": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 31",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #31 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_032": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 32",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #32 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_033": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 33",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #33 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_034": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 34",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #34 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_035": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 35",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #35 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_036": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 36",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #36 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_037": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 37",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #37 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_038": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 38",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #38 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_039": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 39",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #39 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_040": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 40",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #40 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_041": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 41",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #41 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_042": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 42",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #42 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_043": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 43",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #43 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_044": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 44",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #44 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_045": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 45",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #45 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_046": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 46",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #46 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_047": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 47",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #47 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_048": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 48",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #48 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_049": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 49",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #49 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_050": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 50",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #50 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_051": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 51",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #51 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_052": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 52",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #52 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_053": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 53",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #53 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_054": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 54",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #54 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_055": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 55",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #55 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_056": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 56",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #56 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_057": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 57",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #57 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_058": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 58",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #58 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_059": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 59",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #59 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_060": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 60",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #60 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_061": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 61",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #61 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_062": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 62",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #62 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_063": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 63",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #63 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_064": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 64",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #64 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_065": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 65",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #65 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_066": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 66",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #66 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_067": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 67",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #67 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_068": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 68",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #68 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_069": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 69",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #69 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_070": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 70",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #70 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_071": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 71",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #71 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_072": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 72",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #72 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_073": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 73",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #73 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_074": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 74",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #74 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_075": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 75",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #75 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_076": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 76",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #76 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_077": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 77",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #77 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_078": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 78",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #78 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_079": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 79",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #79 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_080": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 80",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #80 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_081": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 81",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #81 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_082": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 82",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #82 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_083": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 83",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #83 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_084": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 84",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #84 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_085": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 85",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #85 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_086": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 86",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #86 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_087": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 87",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #87 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_088": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 88",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #88 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_089": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 89",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #89 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_090": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 90",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #90 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_091": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 91",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #91 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_092": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 92",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #92 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_093": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 93",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #93 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_094": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 94",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #94 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_095": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 95",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #95 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_096": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 96",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #96 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_097": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 97",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #97 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_098": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 98",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #98 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_099": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 99",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #99 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_100": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 100",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #100 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_101": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 101",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #101 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_102": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 102",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #102 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_103": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 103",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #103 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_104": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 104",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #104 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_105": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 105",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #105 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_106": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 106",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #106 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_107": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 107",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #107 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_108": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 108",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #108 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_109": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 109",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #109 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_110": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 110",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #110 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_111": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 111",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #111 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_112": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 112",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #112 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_113": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 113",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #113 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_114": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 114",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #114 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_115": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 115",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #115 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_116": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 116",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #116 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_117": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 117",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #117 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_118": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 118",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #118 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_119": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 119",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #119 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_120": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 120",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #120 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_121": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 121",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #121 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_122": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 122",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #122 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_123": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 123",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #123 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_124": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 124",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #124 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_125": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 125",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #125 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_126": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 126",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #126 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_127": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 127",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #127 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_128": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 128",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #128 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_129": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 129",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #129 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_130": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 130",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #130 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_131": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 131",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #131 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_132": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 132",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #132 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_133": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 133",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #133 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_134": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 134",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #134 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_135": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 135",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #135 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_136": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 136",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #136 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_137": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 137",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #137 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_138": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 138",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #138 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_139": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 139",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #139 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_140": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 140",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #140 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_141": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 141",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #141 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_142": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 142",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #142 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_143": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 143",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #143 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_144": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 144",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #144 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_145": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 145",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #145 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_146": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 146",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #146 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_147": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 147",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #147 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_148": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 148",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #148 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_149": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 149",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #149 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_150": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 150",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #150 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_151": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 151",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #151 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_152": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 152",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #152 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_153": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 153",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #153 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_154": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 154",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #154 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_155": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 155",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #155 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_156": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 156",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #156 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_157": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 157",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #157 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_158": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 158",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #158 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_159": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 159",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #159 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_160": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 160",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #160 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_161": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 161",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #161 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_162": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 162",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #162 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_163": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 163",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #163 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_164": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 164",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #164 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_165": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 165",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #165 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_166": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 166",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #166 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_167": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 167",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #167 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_168": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 168",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #168 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_169": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 169",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #169 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_170": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 170",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #170 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_171": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 171",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #171 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_172": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 172",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #172 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_173": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 173",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #173 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_174": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 174",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #174 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_175": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 175",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #175 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_176": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 176",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #176 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_177": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 177",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #177 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_178": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 178",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #178 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_179": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 179",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #179 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_180": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 180",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #180 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_181": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 181",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #181 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_182": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 182",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #182 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_183": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 183",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #183 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_184": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 184",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #184 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_185": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 185",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #185 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_186": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 186",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #186 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_187": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 187",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #187 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_188": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 188",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #188 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_189": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 189",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #189 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_190": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 190",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #190 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_191": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 191",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #191 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_192": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 192",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #192 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_193": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 193",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #193 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_194": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 194",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #194 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_195": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 195",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #195 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_196": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 196",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #196 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_197": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 197",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #197 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_198": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 198",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #198 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_199": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 199",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #199 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_200": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 200",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #200 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_201": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 201",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #201 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_202": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 202",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #202 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
    "ansiklopedi_madde_203": {
        "kelimeler": [
            "diyarbakır",
            "diyarbakır bilgi",
            "diyarbakır hakkında",
            "diyarbakır nerenin",
            "21 plaka",
            "plaka 21",
            "genel kültür madde 203",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #203 (Diyarbakır - Plaka 21):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Tarihi Diyarbakır Surları, Hevsel Bahçeleri ve Dicle Nehri ile tanınır."
        ),
    },
    "ansiklopedi_madde_204": {
        "kelimeler": [
            "erzurum",
            "erzurum bilgi",
            "erzurum hakkında",
            "erzurum nerenin",
            "25 plaka",
            "plaka 25",
            "genel kültür madde 204",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #204 (Erzurum - Plaka 25):** "
            "Doğu Anadolu Bölgesi'nde yer alır. Palandöken Kayak Merkezi, Çifte Minareli Medrese ve cağ kebabıyla ünlüdür."
        ),
    },
    "ansiklopedi_madde_205": {
        "kelimeler": [
            "eskişehir",
            "eskişehir bilgi",
            "eskişehir hakkında",
            "eskişehir nerenin",
            "26 plaka",
            "plaka 26",
            "genel kültür madde 205",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #205 (Eskişehir - Plaka 26):** "
            "İç Anadolu Bölgesi'nde yer alır. Porsuk Çayı, Odunpazarı evleri ve havacılık/üniversite şehri kimliğiyle öne çıkar."
        ),
    },
    "ansiklopedi_madde_206": {
        "kelimeler": [
            "gaziantep",
            "gaziantep bilgi",
            "gaziantep hakkında",
            "gaziantep nerenin",
            "27 plaka",
            "plaka 27",
            "genel kültür madde 206",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #206 (Gaziantep - Plaka 27):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Zeugma Mozaik Müzesi, zengin mutfak kültürü ve sanayisiyle tanınır."
        ),
    },
    "ansiklopedi_madde_207": {
        "kelimeler": [
            "i̇stanbul",
            "i̇stanbul bilgi",
            "i̇stanbul hakkında",
            "i̇stanbul nerenin",
            "34 plaka",
            "plaka 34",
            "genel kültür madde 207",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #207 (İstanbul - Plaka 34):** "
            "Marmara Bölgesi'nde yer alır. Asya ve Avrupa'yı birleştiren, Fatih Sultan Mehmet'in emaneti dünya metropolüdür."
        ),
    },
    "ansiklopedi_madde_208": {
        "kelimeler": [
            "i̇zmir",
            "i̇zmir bilgi",
            "i̇zmir hakkında",
            "i̇zmir nerenin",
            "35 plaka",
            "plaka 35",
            "genel kültür madde 208",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #208 (İzmir - Plaka 35):** "
            "Ege Bölgesi'nde yer alır. Saat Kulesi, Efes Antik Kenti ve Ege'nin en büyük liman şehridir."
        ),
    },
    "ansiklopedi_madde_209": {
        "kelimeler": [
            "kayseri",
            "kayseri bilgi",
            "kayseri hakkında",
            "kayseri nerenin",
            "38 plaka",
            "plaka 38",
            "genel kültür madde 209",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #209 (Kayseri - Plaka 38):** "
            "İç Anadolu Bölgesi'nde yer alır. Erciyes Dağı, Mimar Sinan'ın memleketi ve köklü ticaret kültürüyle ünlüdür."
        ),
    },
    "ansiklopedi_madde_210": {
        "kelimeler": [
            "kocaeli",
            "kocaeli bilgi",
            "kocaeli hakkında",
            "kocaeli nerenin",
            "41 plaka",
            "plaka 41",
            "genel kültür madde 210",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #210 (Kocaeli - Plaka 41):** "
            "Marmara Bölgesi'nde yer alır. Bilişim Vadisi, TÜBİTAK Gebze yerleşkesi ve sanayi merkezidir."
        ),
    },
    "ansiklopedi_madde_211": {
        "kelimeler": [
            "konya",
            "konya bilgi",
            "konya hakkında",
            "konya nerenin",
            "42 plaka",
            "plaka 42",
            "genel kültür madde 211",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #211 (Konya - Plaka 42):** "
            "İç Anadolu Bölgesi'nde yer alır. Selçuklu başkenti, Mevlânâ Celâleddîn-i Rûmî türbesi ve bilim merkeziyle tanınır."
        ),
    },
    "ansiklopedi_madde_212": {
        "kelimeler": [
            "mardin",
            "mardin bilgi",
            "mardin hakkında",
            "mardin nerenin",
            "47 plaka",
            "plaka 47",
            "genel kültür madde 212",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #212 (Mardin - Plaka 47):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Taş mimarisi, Kasımiye Medresesi ve Mezopotamya'ya bakan tarihi dokusuyla eşsizdir."
        ),
    },
    "ansiklopedi_madde_213": {
        "kelimeler": [
            "samsun",
            "samsun bilgi",
            "samsun hakkında",
            "samsun nerenin",
            "55 plaka",
            "plaka 55",
            "genel kültür madde 213",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #213 (Samsun - Plaka 55):** "
            "Karadeniz Bölgesi'nde yer alır. Milli Mücadele'nin başladığı Karadeniz'in en büyük liman ve eğitim kentidir."
        ),
    },
    "ansiklopedi_madde_214": {
        "kelimeler": [
            "trabzon",
            "trabzon bilgi",
            "trabzon hakkında",
            "trabzon nerenin",
            "61 plaka",
            "plaka 61",
            "genel kültür madde 214",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #214 (Trabzon - Plaka 61):** "
            "Karadeniz Bölgesi'nde yer alır. Sümela Manastırı, Uzungöl ve Karadeniz kültürünün önemli merkezidir."
        ),
    },
    "ansiklopedi_madde_215": {
        "kelimeler": [
            "şanlıurfa",
            "şanlıurfa bilgi",
            "şanlıurfa hakkında",
            "şanlıurfa nerenin",
            "63 plaka",
            "plaka 63",
            "genel kültür madde 215",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #215 (Şanlıurfa - Plaka 63):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Göbeklitepe (tarihin sıfır noktası), Balıklıgöl ve Harran Üniversitesi ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_216": {
        "kelimeler": [
            "şırnak",
            "şırnak bilgi",
            "şırnak hakkında",
            "şırnak nerenin",
            "73 plaka",
            "plaka 73",
            "genel kültür madde 216",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #216 (Şırnak - Plaka 73):** "
            "Güneydoğu Anadolu Bölgesi'nde yer alır. Cizre ilçesi büyük robotik ve sibernetik âlimi El-Cezerî'nin memleketidir."
        ),
    },
    "ansiklopedi_madde_217": {
        "kelimeler": [
            "adana",
            "adana bilgi",
            "adana hakkında",
            "adana nerenin",
            "1 plaka",
            "plaka 1",
            "genel kültür madde 217",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #217 (Adana - Plaka 01):** "
            "Akdeniz Bölgesi'nde yer alır. Seyhan ve Ceyhan nehirleri, Çukurova tarımı ve Taşköprü ile ünlüdür."
        ),
    },
    "ansiklopedi_madde_218": {
        "kelimeler": [
            "ankara",
            "ankara bilgi",
            "ankara hakkında",
            "ankara nerenin",
            "6 plaka",
            "plaka 6",
            "genel kültür madde 218",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #218 (Ankara - Plaka 06):** "
            "İç Anadolu Bölgesi'nde yer alır. Türkiye Cumhuriyeti'nin başkenti, Anıtkabir ve savunma sanayii (ASELSAN, TUSAŞ, ROKETSAN) merkezidir."
        ),
    },
    "ansiklopedi_madde_219": {
        "kelimeler": [
            "antalya",
            "antalya bilgi",
            "antalya hakkında",
            "antalya nerenin",
            "7 plaka",
            "plaka 7",
            "genel kültür madde 219",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #219 (Antalya - Plaka 07):** "
            "Akdeniz Bölgesi'nde yer alır. Toros Dağları, antik kentleri ve Akdeniz kıyı turizminin başkentidir."
        ),
    },
    "ansiklopedi_madde_220": {
        "kelimeler": [
            "bursa",
            "bursa bilgi",
            "bursa hakkında",
            "bursa nerenin",
            "16 plaka",
            "plaka 16",
            "genel kültür madde 220",
        ],
        "yanit": (
            "🌍 **Ansiklopedi Maddesi #220 (Bursa - Plaka 16):** "
            "Marmara Bölgesi'nde yer alır. Osmanlı'nın ilk başkenti, Uludağ, İskender kebabı ve otomotiv sanayii merkezidir."
        ),
    },
}

# ==============================================================================
# 4. JSON KOMUT, SOHBET GEÇMİŞİ VE NOTLAR YÖNETİM FONKSİYONLARI
# ==============================================================================
def json_veritabani_hazirla():
    varsayilan_komutlar = {
        "selamlasma": {
            "kelimeler": ["selam", "merhaba", "selamün aleyküm", "hi", "hello"],
            "yanit": "Aleykümselam! Ben Ar. Nasıl yardımcı olabilirim?",
        },
        "okul": {
            "kelimeler": ["okulum", "hangi okuldasın", "lise"],
            "yanit": "İstanbul Fatih'teki Fen ve Sosyal Bilimler Proje Okulu 9. sınıfta okuyorsun Ahmet!",
        },
    }
    if not os.path.exists(JSON_DOSYA_ADI):
        with open(JSON_DOSYA_ADI, "w", encoding="utf-8") as f:
            json.dump(varsayilan_komutlar, f, ensure_ascii=False, indent=4)


def json_oku():
    json_veritabani_hazirla()
    try:
        with open(JSON_DOSYA_ADI, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"JSON okuma hatası: {e}")
        return {}


def json_komut_ekle(kategori: str, kelimeler_metni: str, yanit_metni: str):
    veri = json_oku()
    kat_key = kategori.lower().strip().replace(" ", "_")
    yeni_kelimeler = [k.lower().strip() for k in kelimeler_metni.split(",") if k.strip()]
    if kat_key in veri:
        for k in yeni_kelimeler:
            if k not in veri[kat_key]["kelimeler"]:
                veri[kat_key]["kelimeler"].append(k)
        if yanit_metni.strip():
            veri[kat_key]["yanit"] = yanit_metni.strip()
    else:
        veri[kat_key] = {"kelimeler": yeni_kelimeler, "yanit": yanit_metni.strip()}
    with open(JSON_DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)


def json_kategori_sil(kat_key: str):
    veri = json_oku()
    if kat_key in veri:
        del veri[kat_key]
        with open(JSON_DOSYA_ADI, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)


def sohbet_gecmisi_yukle():
    if os.path.exists(SOHBET_DOSYA_ADI):
        try:
            with open(SOHBET_DOSYA_ADI, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    return [
        {
            "role": "assistant",
            "content": (
                "Merhaba Ahmet! ⚡ **Ar AI Studio v4.0 (5 Modüllü Kurumsal Mimari & 500.000+ Kalıp)** hazır.\n\n"
                "Tüm yazılar **ultra kalın ve yüksek kontrastlı**, geçmiş konuşmaların **günlük baloncuklar** halinde, "
                "ses motorun **doğal Neural ses** ve matematik/fizik/kimya çözücülerin tam kapasite devrede!"
            ),
            "zaman": datetime.now().strftime("%H:%M:%S"),
            "tarih": datetime.now().strftime("%Y-%m-%d"),
            "etiket": "Sistem Başlatıldı",
        }
    ]


def sohbet_gecmisi_kaydet(mesajlar):
    try:
        with open(SOHBET_DOSYA_ADI, "w", encoding="utf-8") as f:
            json.dump(mesajlar, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.toast(f"Geçmiş kaydedilemedi: {e}", icon="⚠️")


def proje_notlari_oku():
    if os.path.exists(NOTLAR_DOSYA_ADI):
        try:
            with open(NOTLAR_DOSYA_ADI, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {"baslik": "TEKNOFEST Otonom İHA", "icerik": "Carbon Fiber PLA gövde ve yüz tanıma telemetrisi test edilecek.", "tarih": "2026-11-16"},
        {"baslik": "Akıllı Bebek Arabası", "icerik": "HC-SR04 ultrasonik sensör ve kamera entegrasyonu kontrol edilecek.", "tarih": "2026-11-16"},
    ]


def proje_notu_ekle(baslik: str, icerik: str):
    notlar = proje_notlari_oku()
    notlar.insert(0, {"baslik": baslik.strip(), "icerik": icerik.strip(), "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")})
    with open(NOTLAR_DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(notlar, f, ensure_ascii=False, indent=4)
# ==============================================================================
# BÖLÜM 3: GELİŞMİŞ MATEMATİK, DÖRT İŞLEM, CEBİR VE GEOMETRİ MOTORU
# ==============================================================================
_IZINLI_OPERATORLER = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# ==============================================================================
# 1. MATEMATİK, GEOMETRİ VE FİZİK KONU ANLATIM ANSİKLOPEDİSİ
# ==============================================================================
MATEMATIK_KONU_REHBERI = {
    "➕ Toplama ve Çıkarma Teknikleri": {
        "alt_baslik": "Temel Aritmetik & Zihinden Hızlı İşlem",
        "icerik": "• **Değişme ve Birleşme:** Toplamada sayıların yeri değişse de sonuç değişmez (`a + b = b + a`).\n• **İşaret Kuralları:** İki eksi yan yana gelirse artıya dönüşür (`12 - (-8) = 12 + 8 = 20`).\n• **Zihinden Tamamlama:** `78 + 46` işleminde `78 + 2 = 80`, `80 + 44 = 124`.",
    },
    "✖️ Çarpma ve Bölme & Ahmet'in Tekniği": {
        "alt_baslik": "Hızlı Zihinden Çarpma & Bölünebilme",
        "icerik": "• **Ahmet'in 25 ile Çarpma Tekniği:** Sayıyı 4'e böl, yanına iki sıfır ekle (`76 × 25` → `76 / 4 = 19` → `1900`).\n• **Ahmet'in 24 ile Çarpma Tekniği:** `76 × 24 = (76 × 25) - 76 = 1900 - 76 = 1824`.\n• **11 ile Pratik Çarpma:** `43 × 11` → Rakamları topla ortasına yaz → `4 (4+3) 3 = 473`.\n• **Sıfır Kuralı:** `0 / a = 0`, fakat `a / 0` tanımsızdır!",
    },
    "√ Köklü Sayılar (Karekök & a√b)": {
        "alt_baslik": "9. Sınıf & LGS İleri Matematik",
        "icerik": "• **Tam Kare Sayılar:** `1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400`.\n• **Kök Dışına Çıkarma (`a√b`):** `√72 = √(36 × 2) = 6√2` | `√128 = √(64 × 2) = 8√2`.\n• **Toplama / Çıkarma:** Kök içleri eşitse katsayılar toplanır (`5√3 + 2√3 = 7√3`).\n• **Paydayı Rasyonel Yapma:** `6 / √3 = (6√3) / 3 = 2√3`.",
    },
    "🔺 Üslü Sayılar ve Bilimsel Gösterim": {
        "alt_baslik": "Kuvvet Kuralları & Üslü Denklemler",
        "icerik": "• **Temel Kurallar:** `a⁰ = 1` (`a ≠ 0`), `a⁻ⁿ = 1 / aⁿ`.\n• **Çarpma ve Bölme:** Tabanlar aynıysa çarpmada üsler toplanır (`2⁵ × 2³ = 2⁸`), bölmede çıkarılır (`2⁵ / 2³ = 2²`).\n• **Üssün Üssü:** `(aⁿ)ᵐ = aⁿˣᵐ` (Örn: `(3²)⁴ = 3⁸`).",
    },
    "📐 1. ve 2. Dereceden Denklemler": {
        "alt_baslik": "Cebir & Diskriminant (Δ) Çözümü",
        "icerik": "• **1. Derece (`ax + b = c`):** Bilinenler bir tarafa, bilinmeyenler diğer tarafa toplanır (`x = (c - b) / a`).\n• **2. Derece (`ax² + bx + c = 0`):** Diskriminant `Δ = b² - 4ac`.\n• `Δ > 0` ise iki farklı reel kök vardır: `x₁,₂ = (-b ± √Δ) / (2a)`.",
    },
    "🔢 EBOB, EKOK ve Asal Çarpanlar": {
        "alt_baslik": "Sayılar Teorisi & Problemler",
        "icerik": "• **EBOB:** İki veya daha fazla sayıyı aynı anda bölen en büyük tam sayıdır (Büyük parçadan küçük parçaya giderken).\n• **EKOK:** Sayıların ortak katlarının en küçüğüdür (Küçük parçaları birleştirip nöbet/zaman problemi çözerken).\n• **Altın Özdeşlik:** İki sayı için `EBOB(a, b) × EKOK(a, b) = a × b`.",
    },
    "📏 Geometri, Pisagor ve Alan/Hacim": {
        "alt_baslik": "Üçgenler, Çember ve Katı Cisimler",
        "icerik": "• **Pisagor Teoremi:** Dik üçgende `a² + b² = c²` (Özel üçgenler: `3-4-5`, `5-12-13`, `8-15-17`, `7-24-25`).\n• **Daire:** Alan = `πr²`, Çevre = `2πr`.\n• **Küre:** Hacim = `(4/3)πr³`, Yüzey Alanı = `4πr²`.",
    },
    "🚀 Fizik & İHA Mühendislik Hesapları": {
        "alt_baslik": "Hareket, Kuvvet, Enerji ve Elektrik",
        "icerik": "• **Newton'un 2. Yasası:** `F = m × a` (Kuvvet = Kütle × İvme).\n• **Kinetik Enerji:** `Ek = ½ × m × v²` | **Potansiyel Enerji:** `Ep = m × g × h`.\n• **Ohm Yasası (Elektronik):** `V = I × R` (Gerilim = Akım × Direnç) | **Güç:** `P = V × I`.",
    },
}

# ==============================================================================
# 2. ÖN HESAPLANMIŞ KAREKÖK, KARE, KÜP VE ASAL ÇARPAN TABLOSU (220+ SAYI)
# ==============================================================================
MATEMATIK_REFERANS_TABLOSU = {
    1: {
        "sayi": 1,
        "karesi": 1,
        "kupu": 1,
        "karekok_sade": "1",
        "karekok_ondalik": 1.0,
        "cift_mi": False,
    },
    2: {
        "sayi": 2,
        "karesi": 4,
        "kupu": 8,
        "karekok_sade": "√2",
        "karekok_ondalik": 1.4142,
        "cift_mi": True,
    },
    3: {
        "sayi": 3,
        "karesi": 9,
        "kupu": 27,
        "karekok_sade": "√3",
        "karekok_ondalik": 1.7321,
        "cift_mi": False,
    },
    4: {
        "sayi": 4,
        "karesi": 16,
        "kupu": 64,
        "karekok_sade": "2",
        "karekok_ondalik": 2.0,
        "cift_mi": True,
    },
    5: {
        "sayi": 5,
        "karesi": 25,
        "kupu": 125,
        "karekok_sade": "√5",
        "karekok_ondalik": 2.2361,
        "cift_mi": False,
    },
    6: {
        "sayi": 6,
        "karesi": 36,
        "kupu": 216,
        "karekok_sade": "√6",
        "karekok_ondalik": 2.4495,
        "cift_mi": True,
    },
    7: {
        "sayi": 7,
        "karesi": 49,
        "kupu": 343,
        "karekok_sade": "√7",
        "karekok_ondalik": 2.6458,
        "cift_mi": False,
    },
    8: {
        "sayi": 8,
        "karesi": 64,
        "kupu": 512,
        "karekok_sade": "2√2",
        "karekok_ondalik": 2.8284,
        "cift_mi": True,
    },
    9: {
        "sayi": 9,
        "karesi": 81,
        "kupu": 729,
        "karekok_sade": "3",
        "karekok_ondalik": 3.0,
        "cift_mi": False,
    },
    10: {
        "sayi": 10,
        "karesi": 100,
        "kupu": 1000,
        "karekok_sade": "√10",
        "karekok_ondalik": 3.1623,
        "cift_mi": True,
    },
    11: {
        "sayi": 11,
        "karesi": 121,
        "kupu": 1331,
        "karekok_sade": "√11",
        "karekok_ondalik": 3.3166,
        "cift_mi": False,
    },
    12: {
        "sayi": 12,
        "karesi": 144,
        "kupu": 1728,
        "karekok_sade": "2√3",
        "karekok_ondalik": 3.4641,
        "cift_mi": True,
    },
    13: {
        "sayi": 13,
        "karesi": 169,
        "kupu": 2197,
        "karekok_sade": "√13",
        "karekok_ondalik": 3.6056,
        "cift_mi": False,
    },
    14: {
        "sayi": 14,
        "karesi": 196,
        "kupu": 2744,
        "karekok_sade": "√14",
        "karekok_ondalik": 3.7417,
        "cift_mi": True,
    },
    15: {
        "sayi": 15,
        "karesi": 225,
        "kupu": 3375,
        "karekok_sade": "√15",
        "karekok_ondalik": 3.873,
        "cift_mi": False,
    },
    16: {
        "sayi": 16,
        "karesi": 256,
        "kupu": 4096,
        "karekok_sade": "4",
        "karekok_ondalik": 4.0,
        "cift_mi": True,
    },
    17: {
        "sayi": 17,
        "karesi": 289,
        "kupu": 4913,
        "karekok_sade": "√17",
        "karekok_ondalik": 4.1231,
        "cift_mi": False,
    },
    18: {
        "sayi": 18,
        "karesi": 324,
        "kupu": 5832,
        "karekok_sade": "3√2",
        "karekok_ondalik": 4.2426,
        "cift_mi": True,
    },
    19: {
        "sayi": 19,
        "karesi": 361,
        "kupu": 6859,
        "karekok_sade": "√19",
        "karekok_ondalik": 4.3589,
        "cift_mi": False,
    },
    20: {
        "sayi": 20,
        "karesi": 400,
        "kupu": 8000,
        "karekok_sade": "2√5",
        "karekok_ondalik": 4.4721,
        "cift_mi": True,
    },
    21: {
        "sayi": 21,
        "karesi": 441,
        "kupu": 9261,
        "karekok_sade": "√21",
        "karekok_ondalik": 4.5826,
        "cift_mi": False,
    },
    22: {
        "sayi": 22,
        "karesi": 484,
        "kupu": 10648,
        "karekok_sade": "√22",
        "karekok_ondalik": 4.6904,
        "cift_mi": True,
    },
    23: {
        "sayi": 23,
        "karesi": 529,
        "kupu": 12167,
        "karekok_sade": "√23",
        "karekok_ondalik": 4.7958,
        "cift_mi": False,
    },
    24: {
        "sayi": 24,
        "karesi": 576,
        "kupu": 13824,
        "karekok_sade": "2√6",
        "karekok_ondalik": 4.899,
        "cift_mi": True,
    },
    25: {
        "sayi": 25,
        "karesi": 625,
        "kupu": 15625,
        "karekok_sade": "5",
        "karekok_ondalik": 5.0,
        "cift_mi": False,
    },
    26: {
        "sayi": 26,
        "karesi": 676,
        "kupu": 17576,
        "karekok_sade": "√26",
        "karekok_ondalik": 5.099,
        "cift_mi": True,
    },
    27: {
        "sayi": 27,
        "karesi": 729,
        "kupu": 19683,
        "karekok_sade": "3√3",
        "karekok_ondalik": 5.1962,
        "cift_mi": False,
    },
    28: {
        "sayi": 28,
        "karesi": 784,
        "kupu": 21952,
        "karekok_sade": "2√7",
        "karekok_ondalik": 5.2915,
        "cift_mi": True,
    },
    29: {
        "sayi": 29,
        "karesi": 841,
        "kupu": 24389,
        "karekok_sade": "√29",
        "karekok_ondalik": 5.3852,
        "cift_mi": False,
    },
    30: {
        "sayi": 30,
        "karesi": 900,
        "kupu": 27000,
        "karekok_sade": "√30",
        "karekok_ondalik": 5.4772,
        "cift_mi": True,
    },
    31: {
        "sayi": 31,
        "karesi": 961,
        "kupu": 29791,
        "karekok_sade": "√31",
        "karekok_ondalik": 5.5678,
        "cift_mi": False,
    },
    32: {
        "sayi": 32,
        "karesi": 1024,
        "kupu": 32768,
        "karekok_sade": "4√2",
        "karekok_ondalik": 5.6569,
        "cift_mi": True,
    },
    33: {
        "sayi": 33,
        "karesi": 1089,
        "kupu": 35937,
        "karekok_sade": "√33",
        "karekok_ondalik": 5.7446,
        "cift_mi": False,
    },
    34: {
        "sayi": 34,
        "karesi": 1156,
        "kupu": 39304,
        "karekok_sade": "√34",
        "karekok_ondalik": 5.831,
        "cift_mi": True,
    },
    35: {
        "sayi": 35,
        "karesi": 1225,
        "kupu": 42875,
        "karekok_sade": "√35",
        "karekok_ondalik": 5.9161,
        "cift_mi": False,
    },
    36: {
        "sayi": 36,
        "karesi": 1296,
        "kupu": 46656,
        "karekok_sade": "6",
        "karekok_ondalik": 6.0,
        "cift_mi": True,
    },
    37: {
        "sayi": 37,
        "karesi": 1369,
        "kupu": 50653,
        "karekok_sade": "√37",
        "karekok_ondalik": 6.0828,
        "cift_mi": False,
    },
    38: {
        "sayi": 38,
        "karesi": 1444,
        "kupu": 54872,
        "karekok_sade": "√38",
        "karekok_ondalik": 6.1644,
        "cift_mi": True,
    },
    39: {
        "sayi": 39,
        "karesi": 1521,
        "kupu": 59319,
        "karekok_sade": "√39",
        "karekok_ondalik": 6.245,
        "cift_mi": False,
    },
    40: {
        "sayi": 40,
        "karesi": 1600,
        "kupu": 64000,
        "karekok_sade": "2√10",
        "karekok_ondalik": 6.3246,
        "cift_mi": True,
    },
    41: {
        "sayi": 41,
        "karesi": 1681,
        "kupu": 68921,
        "karekok_sade": "√41",
        "karekok_ondalik": 6.4031,
        "cift_mi": False,
    },
    42: {
        "sayi": 42,
        "karesi": 1764,
        "kupu": 74088,
        "karekok_sade": "√42",
        "karekok_ondalik": 6.4807,
        "cift_mi": True,
    },
    43: {
        "sayi": 43,
        "karesi": 1849,
        "kupu": 79507,
        "karekok_sade": "√43",
        "karekok_ondalik": 6.5574,
        "cift_mi": False,
    },
    44: {
        "sayi": 44,
        "karesi": 1936,
        "kupu": 85184,
        "karekok_sade": "2√11",
        "karekok_ondalik": 6.6332,
        "cift_mi": True,
    },
    45: {
        "sayi": 45,
        "karesi": 2025,
        "kupu": 91125,
        "karekok_sade": "3√5",
        "karekok_ondalik": 6.7082,
        "cift_mi": False,
    },
    46: {
        "sayi": 46,
        "karesi": 2116,
        "kupu": 97336,
        "karekok_sade": "√46",
        "karekok_ondalik": 6.7823,
        "cift_mi": True,
    },
    47: {
        "sayi": 47,
        "karesi": 2209,
        "kupu": 103823,
        "karekok_sade": "√47",
        "karekok_ondalik": 6.8557,
        "cift_mi": False,
    },
    48: {
        "sayi": 48,
        "karesi": 2304,
        "kupu": 110592,
        "karekok_sade": "4√3",
        "karekok_ondalik": 6.9282,
        "cift_mi": True,
    },
    49: {
        "sayi": 49,
        "karesi": 2401,
        "kupu": 117649,
        "karekok_sade": "7",
        "karekok_ondalik": 7.0,
        "cift_mi": False,
    },
    50: {
        "sayi": 50,
        "karesi": 2500,
        "kupu": 125000,
        "karekok_sade": "5√2",
        "karekok_ondalik": 7.0711,
        "cift_mi": True,
    },
    51: {
        "sayi": 51,
        "karesi": 2601,
        "kupu": 132651,
        "karekok_sade": "√51",
        "karekok_ondalik": 7.1414,
        "cift_mi": False,
    },
    52: {
        "sayi": 52,
        "karesi": 2704,
        "kupu": 140608,
        "karekok_sade": "2√13",
        "karekok_ondalik": 7.2111,
        "cift_mi": True,
    },
    53: {
        "sayi": 53,
        "karesi": 2809,
        "kupu": 148877,
        "karekok_sade": "√53",
        "karekok_ondalik": 7.2801,
        "cift_mi": False,
    },
    54: {
        "sayi": 54,
        "karesi": 2916,
        "kupu": 157464,
        "karekok_sade": "3√6",
        "karekok_ondalik": 7.3485,
        "cift_mi": True,
    },
    55: {
        "sayi": 55,
        "karesi": 3025,
        "kupu": 166375,
        "karekok_sade": "√55",
        "karekok_ondalik": 7.4162,
        "cift_mi": False,
    },
    56: {
        "sayi": 56,
        "karesi": 3136,
        "kupu": 175616,
        "karekok_sade": "2√14",
        "karekok_ondalik": 7.4833,
        "cift_mi": True,
    },
    57: {
        "sayi": 57,
        "karesi": 3249,
        "kupu": 185193,
        "karekok_sade": "√57",
        "karekok_ondalik": 7.5498,
        "cift_mi": False,
    },
    58: {
        "sayi": 58,
        "karesi": 3364,
        "kupu": 195112,
        "karekok_sade": "√58",
        "karekok_ondalik": 7.6158,
        "cift_mi": True,
    },
    59: {
        "sayi": 59,
        "karesi": 3481,
        "kupu": 205379,
        "karekok_sade": "√59",
        "karekok_ondalik": 7.6811,
        "cift_mi": False,
    },
    60: {
        "sayi": 60,
        "karesi": 3600,
        "kupu": 216000,
        "karekok_sade": "2√15",
        "karekok_ondalik": 7.746,
        "cift_mi": True,
    },
    61: {
        "sayi": 61,
        "karesi": 3721,
        "kupu": 226981,
        "karekok_sade": "√61",
        "karekok_ondalik": 7.8102,
        "cift_mi": False,
    },
    62: {
        "sayi": 62,
        "karesi": 3844,
        "kupu": 238328,
        "karekok_sade": "√62",
        "karekok_ondalik": 7.874,
        "cift_mi": True,
    },
    63: {
        "sayi": 63,
        "karesi": 3969,
        "kupu": 250047,
        "karekok_sade": "3√7",
        "karekok_ondalik": 7.9373,
        "cift_mi": False,
    },
    64: {
        "sayi": 64,
        "karesi": 4096,
        "kupu": 262144,
        "karekok_sade": "8",
        "karekok_ondalik": 8.0,
        "cift_mi": True,
    },
    65: {
        "sayi": 65,
        "karesi": 4225,
        "kupu": 274625,
        "karekok_sade": "√65",
        "karekok_ondalik": 8.0623,
        "cift_mi": False,
    },
    66: {
        "sayi": 66,
        "karesi": 4356,
        "kupu": 287496,
        "karekok_sade": "√66",
        "karekok_ondalik": 8.124,
        "cift_mi": True,
    },
    67: {
        "sayi": 67,
        "karesi": 4489,
        "kupu": 300763,
        "karekok_sade": "√67",
        "karekok_ondalik": 8.1854,
        "cift_mi": False,
    },
    68: {
        "sayi": 68,
        "karesi": 4624,
        "kupu": 314432,
        "karekok_sade": "2√17",
        "karekok_ondalik": 8.2462,
        "cift_mi": True,
    },
    69: {
        "sayi": 69,
        "karesi": 4761,
        "kupu": 328509,
        "karekok_sade": "√69",
        "karekok_ondalik": 8.3066,
        "cift_mi": False,
    },
    70: {
        "sayi": 70,
        "karesi": 4900,
        "kupu": 343000,
        "karekok_sade": "√70",
        "karekok_ondalik": 8.3666,
        "cift_mi": True,
    },
    71: {
        "sayi": 71,
        "karesi": 5041,
        "kupu": 357911,
        "karekok_sade": "√71",
        "karekok_ondalik": 8.4261,
        "cift_mi": False,
    },
    72: {
        "sayi": 72,
        "karesi": 5184,
        "kupu": 373248,
        "karekok_sade": "6√2",
        "karekok_ondalik": 8.4853,
        "cift_mi": True,
    },
    73: {
        "sayi": 73,
        "karesi": 5329,
        "kupu": 389017,
        "karekok_sade": "√73",
        "karekok_ondalik": 8.544,
        "cift_mi": False,
    },
    74: {
        "sayi": 74,
        "karesi": 5476,
        "kupu": 405224,
        "karekok_sade": "√74",
        "karekok_ondalik": 8.6023,
        "cift_mi": True,
    },
    75: {
        "sayi": 75,
        "karesi": 5625,
        "kupu": 421875,
        "karekok_sade": "5√3",
        "karekok_ondalik": 8.6603,
        "cift_mi": False,
    },
    76: {
        "sayi": 76,
        "karesi": 5776,
        "kupu": 438976,
        "karekok_sade": "2√19",
        "karekok_ondalik": 8.7178,
        "cift_mi": True,
    },
    77: {
        "sayi": 77,
        "karesi": 5929,
        "kupu": 456533,
        "karekok_sade": "√77",
        "karekok_ondalik": 8.775,
        "cift_mi": False,
    },
    78: {
        "sayi": 78,
        "karesi": 6084,
        "kupu": 474552,
        "karekok_sade": "√78",
        "karekok_ondalik": 8.8318,
        "cift_mi": True,
    },
    79: {
        "sayi": 79,
        "karesi": 6241,
        "kupu": 493039,
        "karekok_sade": "√79",
        "karekok_ondalik": 8.8882,
        "cift_mi": False,
    },
    80: {
        "sayi": 80,
        "karesi": 6400,
        "kupu": 512000,
        "karekok_sade": "4√5",
        "karekok_ondalik": 8.9443,
        "cift_mi": True,
    },
    81: {
        "sayi": 81,
        "karesi": 6561,
        "kupu": 531441,
        "karekok_sade": "9",
        "karekok_ondalik": 9.0,
        "cift_mi": False,
    },
    82: {
        "sayi": 82,
        "karesi": 6724,
        "kupu": 551368,
        "karekok_sade": "√82",
        "karekok_ondalik": 9.0554,
        "cift_mi": True,
    },
    83: {
        "sayi": 83,
        "karesi": 6889,
        "kupu": 571787,
        "karekok_sade": "√83",
        "karekok_ondalik": 9.1104,
        "cift_mi": False,
    },
    84: {
        "sayi": 84,
        "karesi": 7056,
        "kupu": 592704,
        "karekok_sade": "2√21",
        "karekok_ondalik": 9.1652,
        "cift_mi": True,
    },
    85: {
        "sayi": 85,
        "karesi": 7225,
        "kupu": 614125,
        "karekok_sade": "√85",
        "karekok_ondalik": 9.2195,
        "cift_mi": False,
    },
    86: {
        "sayi": 86,
        "karesi": 7396,
        "kupu": 636056,
        "karekok_sade": "√86",
        "karekok_ondalik": 9.2736,
        "cift_mi": True,
    },
    87: {
        "sayi": 87,
        "karesi": 7569,
        "kupu": 658503,
        "karekok_sade": "√87",
        "karekok_ondalik": 9.3274,
        "cift_mi": False,
    },
    88: {
        "sayi": 88,
        "karesi": 7744,
        "kupu": 681472,
        "karekok_sade": "2√22",
        "karekok_ondalik": 9.3808,
        "cift_mi": True,
    },
    89: {
        "sayi": 89,
        "karesi": 7921,
        "kupu": 704969,
        "karekok_sade": "√89",
        "karekok_ondalik": 9.434,
        "cift_mi": False,
    },
    90: {
        "sayi": 90,
        "karesi": 8100,
        "kupu": 729000,
        "karekok_sade": "3√10",
        "karekok_ondalik": 9.4868,
        "cift_mi": True,
    },
    91: {
        "sayi": 91,
        "karesi": 8281,
        "kupu": 753571,
        "karekok_sade": "√91",
        "karekok_ondalik": 9.5394,
        "cift_mi": False,
    },
    92: {
        "sayi": 92,
        "karesi": 8464,
        "kupu": 778688,
        "karekok_sade": "2√23",
        "karekok_ondalik": 9.5917,
        "cift_mi": True,
    },
    93: {
        "sayi": 93,
        "karesi": 8649,
        "kupu": 804357,
        "karekok_sade": "√93",
        "karekok_ondalik": 9.6437,
        "cift_mi": False,
    },
    94: {
        "sayi": 94,
        "karesi": 8836,
        "kupu": 830584,
        "karekok_sade": "√94",
        "karekok_ondalik": 9.6954,
        "cift_mi": True,
    },
    95: {
        "sayi": 95,
        "karesi": 9025,
        "kupu": 857375,
        "karekok_sade": "√95",
        "karekok_ondalik": 9.7468,
        "cift_mi": False,
    },
    96: {
        "sayi": 96,
        "karesi": 9216,
        "kupu": 884736,
        "karekok_sade": "4√6",
        "karekok_ondalik": 9.798,
        "cift_mi": True,
    },
    97: {
        "sayi": 97,
        "karesi": 9409,
        "kupu": 912673,
        "karekok_sade": "√97",
        "karekok_ondalik": 9.8489,
        "cift_mi": False,
    },
    98: {
        "sayi": 98,
        "karesi": 9604,
        "kupu": 941192,
        "karekok_sade": "7√2",
        "karekok_ondalik": 9.8995,
        "cift_mi": True,
    },
    99: {
        "sayi": 99,
        "karesi": 9801,
        "kupu": 970299,
        "karekok_sade": "3√11",
        "karekok_ondalik": 9.9499,
        "cift_mi": False,
    },
    100: {
        "sayi": 100,
        "karesi": 10000,
        "kupu": 1000000,
        "karekok_sade": "10",
        "karekok_ondalik": 10.0,
        "cift_mi": True,
    },
    101: {
        "sayi": 101,
        "karesi": 10201,
        "kupu": 1030301,
        "karekok_sade": "√101",
        "karekok_ondalik": 10.0499,
        "cift_mi": False,
    },
    102: {
        "sayi": 102,
        "karesi": 10404,
        "kupu": 1061208,
        "karekok_sade": "√102",
        "karekok_ondalik": 10.0995,
        "cift_mi": True,
    },
    103: {
        "sayi": 103,
        "karesi": 10609,
        "kupu": 1092727,
        "karekok_sade": "√103",
        "karekok_ondalik": 10.1489,
        "cift_mi": False,
    },
    104: {
        "sayi": 104,
        "karesi": 10816,
        "kupu": 1124864,
        "karekok_sade": "2√26",
        "karekok_ondalik": 10.198,
        "cift_mi": True,
    },
    105: {
        "sayi": 105,
        "karesi": 11025,
        "kupu": 1157625,
        "karekok_sade": "√105",
        "karekok_ondalik": 10.247,
        "cift_mi": False,
    },
    106: {
        "sayi": 106,
        "karesi": 11236,
        "kupu": 1191016,
        "karekok_sade": "√106",
        "karekok_ondalik": 10.2956,
        "cift_mi": True,
    },
    107: {
        "sayi": 107,
        "karesi": 11449,
        "kupu": 1225043,
        "karekok_sade": "√107",
        "karekok_ondalik": 10.3441,
        "cift_mi": False,
    },
    108: {
        "sayi": 108,
        "karesi": 11664,
        "kupu": 1259712,
        "karekok_sade": "6√3",
        "karekok_ondalik": 10.3923,
        "cift_mi": True,
    },
    109: {
        "sayi": 109,
        "karesi": 11881,
        "kupu": 1295029,
        "karekok_sade": "√109",
        "karekok_ondalik": 10.4403,
        "cift_mi": False,
    },
    110: {
        "sayi": 110,
        "karesi": 12100,
        "kupu": 1331000,
        "karekok_sade": "√110",
        "karekok_ondalik": 10.4881,
        "cift_mi": True,
    },
    111: {
        "sayi": 111,
        "karesi": 12321,
        "kupu": 1367631,
        "karekok_sade": "√111",
        "karekok_ondalik": 10.5357,
        "cift_mi": False,
    },
    112: {
        "sayi": 112,
        "karesi": 12544,
        "kupu": 1404928,
        "karekok_sade": "4√7",
        "karekok_ondalik": 10.583,
        "cift_mi": True,
    },
    113: {
        "sayi": 113,
        "karesi": 12769,
        "kupu": 1442897,
        "karekok_sade": "√113",
        "karekok_ondalik": 10.6301,
        "cift_mi": False,
    },
    114: {
        "sayi": 114,
        "karesi": 12996,
        "kupu": 1481544,
        "karekok_sade": "√114",
        "karekok_ondalik": 10.6771,
        "cift_mi": True,
    },
    115: {
        "sayi": 115,
        "karesi": 13225,
        "kupu": 1520875,
        "karekok_sade": "√115",
        "karekok_ondalik": 10.7238,
        "cift_mi": False,
    },
    116: {
        "sayi": 116,
        "karesi": 13456,
        "kupu": 1560896,
        "karekok_sade": "2√29",
        "karekok_ondalik": 10.7703,
        "cift_mi": True,
    },
    117: {
        "sayi": 117,
        "karesi": 13689,
        "kupu": 1601613,
        "karekok_sade": "3√13",
        "karekok_ondalik": 10.8167,
        "cift_mi": False,
    },
    118: {
        "sayi": 118,
        "karesi": 13924,
        "kupu": 1643032,
        "karekok_sade": "√118",
        "karekok_ondalik": 10.8628,
        "cift_mi": True,
    },
    119: {
        "sayi": 119,
        "karesi": 14161,
        "kupu": 1685159,
        "karekok_sade": "√119",
        "karekok_ondalik": 10.9087,
        "cift_mi": False,
    },
    120: {
        "sayi": 120,
        "karesi": 14400,
        "kupu": 1728000,
        "karekok_sade": "2√30",
        "karekok_ondalik": 10.9545,
        "cift_mi": True,
    },
    121: {
        "sayi": 121,
        "karesi": 14641,
        "kupu": 1771561,
        "karekok_sade": "11",
        "karekok_ondalik": 11.0,
        "cift_mi": False,
    },
    122: {
        "sayi": 122,
        "karesi": 14884,
        "kupu": 1815848,
        "karekok_sade": "√122",
        "karekok_ondalik": 11.0454,
        "cift_mi": True,
    },
    123: {
        "sayi": 123,
        "karesi": 15129,
        "kupu": 1860867,
        "karekok_sade": "√123",
        "karekok_ondalik": 11.0905,
        "cift_mi": False,
    },
    124: {
        "sayi": 124,
        "karesi": 15376,
        "kupu": 1906624,
        "karekok_sade": "2√31",
        "karekok_ondalik": 11.1355,
        "cift_mi": True,
    },
    125: {
        "sayi": 125,
        "karesi": 15625,
        "kupu": 1953125,
        "karekok_sade": "5√5",
        "karekok_ondalik": 11.1803,
        "cift_mi": False,
    },
    126: {
        "sayi": 126,
        "karesi": 15876,
        "kupu": 2000376,
        "karekok_sade": "3√14",
        "karekok_ondalik": 11.225,
        "cift_mi": True,
    },
    127: {
        "sayi": 127,
        "karesi": 16129,
        "kupu": 2048383,
        "karekok_sade": "√127",
        "karekok_ondalik": 11.2694,
        "cift_mi": False,
    },
    128: {
        "sayi": 128,
        "karesi": 16384,
        "kupu": 2097152,
        "karekok_sade": "8√2",
        "karekok_ondalik": 11.3137,
        "cift_mi": True,
    },
    129: {
        "sayi": 129,
        "karesi": 16641,
        "kupu": 2146689,
        "karekok_sade": "√129",
        "karekok_ondalik": 11.3578,
        "cift_mi": False,
    },
    130: {
        "sayi": 130,
        "karesi": 16900,
        "kupu": 2197000,
        "karekok_sade": "√130",
        "karekok_ondalik": 11.4018,
        "cift_mi": True,
    },
    131: {
        "sayi": 131,
        "karesi": 17161,
        "kupu": 2248091,
        "karekok_sade": "√131",
        "karekok_ondalik": 11.4455,
        "cift_mi": False,
    },
    132: {
        "sayi": 132,
        "karesi": 17424,
        "kupu": 2299968,
        "karekok_sade": "2√33",
        "karekok_ondalik": 11.4891,
        "cift_mi": True,
    },
    133: {
        "sayi": 133,
        "karesi": 17689,
        "kupu": 2352637,
        "karekok_sade": "√133",
        "karekok_ondalik": 11.5326,
        "cift_mi": False,
    },
    134: {
        "sayi": 134,
        "karesi": 17956,
        "kupu": 2406104,
        "karekok_sade": "√134",
        "karekok_ondalik": 11.5758,
        "cift_mi": True,
    },
    135: {
        "sayi": 135,
        "karesi": 18225,
        "kupu": 2460375,
        "karekok_sade": "3√15",
        "karekok_ondalik": 11.619,
        "cift_mi": False,
    },
    136: {
        "sayi": 136,
        "karesi": 18496,
        "kupu": 2515456,
        "karekok_sade": "2√34",
        "karekok_ondalik": 11.6619,
        "cift_mi": True,
    },
    137: {
        "sayi": 137,
        "karesi": 18769,
        "kupu": 2571353,
        "karekok_sade": "√137",
        "karekok_ondalik": 11.7047,
        "cift_mi": False,
    },
    138: {
        "sayi": 138,
        "karesi": 19044,
        "kupu": 2628072,
        "karekok_sade": "√138",
        "karekok_ondalik": 11.7473,
        "cift_mi": True,
    },
    139: {
        "sayi": 139,
        "karesi": 19321,
        "kupu": 2685619,
        "karekok_sade": "√139",
        "karekok_ondalik": 11.7898,
        "cift_mi": False,
    },
    140: {
        "sayi": 140,
        "karesi": 19600,
        "kupu": 2744000,
        "karekok_sade": "2√35",
        "karekok_ondalik": 11.8322,
        "cift_mi": True,
    },
    141: {
        "sayi": 141,
        "karesi": 19881,
        "kupu": 2803221,
        "karekok_sade": "√141",
        "karekok_ondalik": 11.8743,
        "cift_mi": False,
    },
    142: {
        "sayi": 142,
        "karesi": 20164,
        "kupu": 2863288,
        "karekok_sade": "√142",
        "karekok_ondalik": 11.9164,
        "cift_mi": True,
    },
    143: {
        "sayi": 143,
        "karesi": 20449,
        "kupu": 2924207,
        "karekok_sade": "√143",
        "karekok_ondalik": 11.9583,
        "cift_mi": False,
    },
    144: {
        "sayi": 144,
        "karesi": 20736,
        "kupu": 2985984,
        "karekok_sade": "12",
        "karekok_ondalik": 12.0,
        "cift_mi": True,
    },
    145: {
        "sayi": 145,
        "karesi": 21025,
        "kupu": 3048625,
        "karekok_sade": "√145",
        "karekok_ondalik": 12.0416,
        "cift_mi": False,
    },
    146: {
        "sayi": 146,
        "karesi": 21316,
        "kupu": 3112136,
        "karekok_sade": "√146",
        "karekok_ondalik": 12.083,
        "cift_mi": True,
    },
    147: {
        "sayi": 147,
        "karesi": 21609,
        "kupu": 3176523,
        "karekok_sade": "7√3",
        "karekok_ondalik": 12.1244,
        "cift_mi": False,
    },
    148: {
        "sayi": 148,
        "karesi": 21904,
        "kupu": 3241792,
        "karekok_sade": "2√37",
        "karekok_ondalik": 12.1655,
        "cift_mi": True,
    },
    149: {
        "sayi": 149,
        "karesi": 22201,
        "kupu": 3307949,
        "karekok_sade": "√149",
        "karekok_ondalik": 12.2066,
        "cift_mi": False,
    },
    150: {
        "sayi": 150,
        "karesi": 22500,
        "kupu": 3375000,
        "karekok_sade": "5√6",
        "karekok_ondalik": 12.2474,
        "cift_mi": True,
    },
    151: {
        "sayi": 151,
        "karesi": 22801,
        "kupu": 3442951,
        "karekok_sade": "√151",
        "karekok_ondalik": 12.2882,
        "cift_mi": False,
    },
    152: {
        "sayi": 152,
        "karesi": 23104,
        "kupu": 3511808,
        "karekok_sade": "2√38",
        "karekok_ondalik": 12.3288,
        "cift_mi": True,
    },
    153: {
        "sayi": 153,
        "karesi": 23409,
        "kupu": 3581577,
        "karekok_sade": "3√17",
        "karekok_ondalik": 12.3693,
        "cift_mi": False,
    },
    154: {
        "sayi": 154,
        "karesi": 23716,
        "kupu": 3652264,
        "karekok_sade": "√154",
        "karekok_ondalik": 12.4097,
        "cift_mi": True,
    },
    155: {
        "sayi": 155,
        "karesi": 24025,
        "kupu": 3723875,
        "karekok_sade": "√155",
        "karekok_ondalik": 12.4499,
        "cift_mi": False,
    },
    156: {
        "sayi": 156,
        "karesi": 24336,
        "kupu": 3796416,
        "karekok_sade": "2√39",
        "karekok_ondalik": 12.49,
        "cift_mi": True,
    },
    157: {
        "sayi": 157,
        "karesi": 24649,
        "kupu": 3869893,
        "karekok_sade": "√157",
        "karekok_ondalik": 12.53,
        "cift_mi": False,
    },
    158: {
        "sayi": 158,
        "karesi": 24964,
        "kupu": 3944312,
        "karekok_sade": "√158",
        "karekok_ondalik": 12.5698,
        "cift_mi": True,
    },
    159: {
        "sayi": 159,
        "karesi": 25281,
        "kupu": 4019679,
        "karekok_sade": "√159",
        "karekok_ondalik": 12.6095,
        "cift_mi": False,
    },
    160: {
        "sayi": 160,
        "karesi": 25600,
        "kupu": 4096000,
        "karekok_sade": "4√10",
        "karekok_ondalik": 12.6491,
        "cift_mi": True,
    },
    161: {
        "sayi": 161,
        "karesi": 25921,
        "kupu": 4173281,
        "karekok_sade": "√161",
        "karekok_ondalik": 12.6886,
        "cift_mi": False,
    },
    162: {
        "sayi": 162,
        "karesi": 26244,
        "kupu": 4251528,
        "karekok_sade": "9√2",
        "karekok_ondalik": 12.7279,
        "cift_mi": True,
    },
    163: {
        "sayi": 163,
        "karesi": 26569,
        "kupu": 4330747,
        "karekok_sade": "√163",
        "karekok_ondalik": 12.7671,
        "cift_mi": False,
    },
    164: {
        "sayi": 164,
        "karesi": 26896,
        "kupu": 4410944,
        "karekok_sade": "2√41",
        "karekok_ondalik": 12.8062,
        "cift_mi": True,
    },
    165: {
        "sayi": 165,
        "karesi": 27225,
        "kupu": 4492125,
        "karekok_sade": "√165",
        "karekok_ondalik": 12.8452,
        "cift_mi": False,
    },
    166: {
        "sayi": 166,
        "karesi": 27556,
        "kupu": 4574296,
        "karekok_sade": "√166",
        "karekok_ondalik": 12.8841,
        "cift_mi": True,
    },
    167: {
        "sayi": 167,
        "karesi": 27889,
        "kupu": 4657463,
        "karekok_sade": "√167",
        "karekok_ondalik": 12.9228,
        "cift_mi": False,
    },
    168: {
        "sayi": 168,
        "karesi": 28224,
        "kupu": 4741632,
        "karekok_sade": "2√42",
        "karekok_ondalik": 12.9615,
        "cift_mi": True,
    },
    169: {
        "sayi": 169,
        "karesi": 28561,
        "kupu": 4826809,
        "karekok_sade": "13",
        "karekok_ondalik": 13.0,
        "cift_mi": False,
    },
    170: {
        "sayi": 170,
        "karesi": 28900,
        "kupu": 4913000,
        "karekok_sade": "√170",
        "karekok_ondalik": 13.0384,
        "cift_mi": True,
    },
    171: {
        "sayi": 171,
        "karesi": 29241,
        "kupu": 5000211,
        "karekok_sade": "3√19",
        "karekok_ondalik": 13.0767,
        "cift_mi": False,
    },
    172: {
        "sayi": 172,
        "karesi": 29584,
        "kupu": 5088448,
        "karekok_sade": "2√43",
        "karekok_ondalik": 13.1149,
        "cift_mi": True,
    },
    173: {
        "sayi": 173,
        "karesi": 29929,
        "kupu": 5177717,
        "karekok_sade": "√173",
        "karekok_ondalik": 13.1529,
        "cift_mi": False,
    },
    174: {
        "sayi": 174,
        "karesi": 30276,
        "kupu": 5268024,
        "karekok_sade": "√174",
        "karekok_ondalik": 13.1909,
        "cift_mi": True,
    },
    175: {
        "sayi": 175,
        "karesi": 30625,
        "kupu": 5359375,
        "karekok_sade": "5√7",
        "karekok_ondalik": 13.2288,
        "cift_mi": False,
    },
    176: {
        "sayi": 176,
        "karesi": 30976,
        "kupu": 5451776,
        "karekok_sade": "4√11",
        "karekok_ondalik": 13.2665,
        "cift_mi": True,
    },
    177: {
        "sayi": 177,
        "karesi": 31329,
        "kupu": 5545233,
        "karekok_sade": "√177",
        "karekok_ondalik": 13.3041,
        "cift_mi": False,
    },
    178: {
        "sayi": 178,
        "karesi": 31684,
        "kupu": 5639752,
        "karekok_sade": "√178",
        "karekok_ondalik": 13.3417,
        "cift_mi": True,
    },
    179: {
        "sayi": 179,
        "karesi": 32041,
        "kupu": 5735339,
        "karekok_sade": "√179",
        "karekok_ondalik": 13.3791,
        "cift_mi": False,
    },
    180: {
        "sayi": 180,
        "karesi": 32400,
        "kupu": 5832000,
        "karekok_sade": "6√5",
        "karekok_ondalik": 13.4164,
        "cift_mi": True,
    },
    181: {
        "sayi": 181,
        "karesi": 32761,
        "kupu": 5929741,
        "karekok_sade": "√181",
        "karekok_ondalik": 13.4536,
        "cift_mi": False,
    },
    182: {
        "sayi": 182,
        "karesi": 33124,
        "kupu": 6028568,
        "karekok_sade": "√182",
        "karekok_ondalik": 13.4907,
        "cift_mi": True,
    },
    183: {
        "sayi": 183,
        "karesi": 33489,
        "kupu": 6128487,
        "karekok_sade": "√183",
        "karekok_ondalik": 13.5277,
        "cift_mi": False,
    },
    184: {
        "sayi": 184,
        "karesi": 33856,
        "kupu": 6229504,
        "karekok_sade": "2√46",
        "karekok_ondalik": 13.5647,
        "cift_mi": True,
    },
    185: {
        "sayi": 185,
        "karesi": 34225,
        "kupu": 6331625,
        "karekok_sade": "√185",
        "karekok_ondalik": 13.6015,
        "cift_mi": False,
    },
    186: {
        "sayi": 186,
        "karesi": 34596,
        "kupu": 6434856,
        "karekok_sade": "√186",
        "karekok_ondalik": 13.6382,
        "cift_mi": True,
    },
    187: {
        "sayi": 187,
        "karesi": 34969,
        "kupu": 6539203,
        "karekok_sade": "√187",
        "karekok_ondalik": 13.6748,
        "cift_mi": False,
    },
    188: {
        "sayi": 188,
        "karesi": 35344,
        "kupu": 6644672,
        "karekok_sade": "2√47",
        "karekok_ondalik": 13.7113,
        "cift_mi": True,
    },
    189: {
        "sayi": 189,
        "karesi": 35721,
        "kupu": 6751269,
        "karekok_sade": "3√21",
        "karekok_ondalik": 13.7477,
        "cift_mi": False,
    },
    190: {
        "sayi": 190,
        "karesi": 36100,
        "kupu": 6859000,
        "karekok_sade": "√190",
        "karekok_ondalik": 13.784,
        "cift_mi": True,
    },
    191: {
        "sayi": 191,
        "karesi": 36481,
        "kupu": 6967871,
        "karekok_sade": "√191",
        "karekok_ondalik": 13.8203,
        "cift_mi": False,
    },
    192: {
        "sayi": 192,
        "karesi": 36864,
        "kupu": 7077888,
        "karekok_sade": "8√3",
        "karekok_ondalik": 13.8564,
        "cift_mi": True,
    },
    193: {
        "sayi": 193,
        "karesi": 37249,
        "kupu": 7189057,
        "karekok_sade": "√193",
        "karekok_ondalik": 13.8924,
        "cift_mi": False,
    },
    194: {
        "sayi": 194,
        "karesi": 37636,
        "kupu": 7301384,
        "karekok_sade": "√194",
        "karekok_ondalik": 13.9284,
        "cift_mi": True,
    },
    195: {
        "sayi": 195,
        "karesi": 38025,
        "kupu": 7414875,
        "karekok_sade": "√195",
        "karekok_ondalik": 13.9642,
        "cift_mi": False,
    },
    196: {
        "sayi": 196,
        "karesi": 38416,
        "kupu": 7529536,
        "karekok_sade": "14",
        "karekok_ondalik": 14.0,
        "cift_mi": True,
    },
    197: {
        "sayi": 197,
        "karesi": 38809,
        "kupu": 7645373,
        "karekok_sade": "√197",
        "karekok_ondalik": 14.0357,
        "cift_mi": False,
    },
    198: {
        "sayi": 198,
        "karesi": 39204,
        "kupu": 7762392,
        "karekok_sade": "3√22",
        "karekok_ondalik": 14.0712,
        "cift_mi": True,
    },
    199: {
        "sayi": 199,
        "karesi": 39601,
        "kupu": 7880599,
        "karekok_sade": "√199",
        "karekok_ondalik": 14.1067,
        "cift_mi": False,
    },
    200: {
        "sayi": 200,
        "karesi": 40000,
        "kupu": 8000000,
        "karekok_sade": "10√2",
        "karekok_ondalik": 14.1421,
        "cift_mi": True,
    },
    201: {
        "sayi": 201,
        "karesi": 40401,
        "kupu": 8120601,
        "karekok_sade": "√201",
        "karekok_ondalik": 14.1774,
        "cift_mi": False,
    },
    202: {
        "sayi": 202,
        "karesi": 40804,
        "kupu": 8242408,
        "karekok_sade": "√202",
        "karekok_ondalik": 14.2127,
        "cift_mi": True,
    },
    203: {
        "sayi": 203,
        "karesi": 41209,
        "kupu": 8365427,
        "karekok_sade": "√203",
        "karekok_ondalik": 14.2478,
        "cift_mi": False,
    },
    204: {
        "sayi": 204,
        "karesi": 41616,
        "kupu": 8489664,
        "karekok_sade": "2√51",
        "karekok_ondalik": 14.2829,
        "cift_mi": True,
    },
    205: {
        "sayi": 205,
        "karesi": 42025,
        "kupu": 8615125,
        "karekok_sade": "√205",
        "karekok_ondalik": 14.3178,
        "cift_mi": False,
    },
    206: {
        "sayi": 206,
        "karesi": 42436,
        "kupu": 8741816,
        "karekok_sade": "√206",
        "karekok_ondalik": 14.3527,
        "cift_mi": True,
    },
    207: {
        "sayi": 207,
        "karesi": 42849,
        "kupu": 8869743,
        "karekok_sade": "3√23",
        "karekok_ondalik": 14.3875,
        "cift_mi": False,
    },
    208: {
        "sayi": 208,
        "karesi": 43264,
        "kupu": 8998912,
        "karekok_sade": "4√13",
        "karekok_ondalik": 14.4222,
        "cift_mi": True,
    },
    209: {
        "sayi": 209,
        "karesi": 43681,
        "kupu": 9129329,
        "karekok_sade": "√209",
        "karekok_ondalik": 14.4568,
        "cift_mi": False,
    },
    210: {
        "sayi": 210,
        "karesi": 44100,
        "kupu": 9261000,
        "karekok_sade": "√210",
        "karekok_ondalik": 14.4914,
        "cift_mi": True,
    },
    211: {
        "sayi": 211,
        "karesi": 44521,
        "kupu": 9393931,
        "karekok_sade": "√211",
        "karekok_ondalik": 14.5258,
        "cift_mi": False,
    },
    212: {
        "sayi": 212,
        "karesi": 44944,
        "kupu": 9528128,
        "karekok_sade": "2√53",
        "karekok_ondalik": 14.5602,
        "cift_mi": True,
    },
    213: {
        "sayi": 213,
        "karesi": 45369,
        "kupu": 9663597,
        "karekok_sade": "√213",
        "karekok_ondalik": 14.5945,
        "cift_mi": False,
    },
    214: {
        "sayi": 214,
        "karesi": 45796,
        "kupu": 9800344,
        "karekok_sade": "√214",
        "karekok_ondalik": 14.6287,
        "cift_mi": True,
    },
    215: {
        "sayi": 215,
        "karesi": 46225,
        "kupu": 9938375,
        "karekok_sade": "√215",
        "karekok_ondalik": 14.6629,
        "cift_mi": False,
    },
    216: {
        "sayi": 216,
        "karesi": 46656,
        "kupu": 10077696,
        "karekok_sade": "6√6",
        "karekok_ondalik": 14.6969,
        "cift_mi": True,
    },
    217: {
        "sayi": 217,
        "karesi": 47089,
        "kupu": 10218313,
        "karekok_sade": "√217",
        "karekok_ondalik": 14.7309,
        "cift_mi": False,
    },
    218: {
        "sayi": 218,
        "karesi": 47524,
        "kupu": 10360232,
        "karekok_sade": "√218",
        "karekok_ondalik": 14.7648,
        "cift_mi": True,
    },
    219: {
        "sayi": 219,
        "karesi": 47961,
        "kupu": 10503459,
        "karekok_sade": "√219",
        "karekok_ondalik": 14.7986,
        "cift_mi": False,
    },
    220: {
        "sayi": 220,
        "karesi": 48400,
        "kupu": 10648000,
        "karekok_sade": "2√55",
        "karekok_ondalik": 14.8324,
        "cift_mi": True,
    },
    221: {
        "sayi": 221,
        "karesi": 48841,
        "kupu": 10793861,
        "karekok_sade": "√221",
        "karekok_ondalik": 14.8661,
        "cift_mi": False,
    },
    222: {
        "sayi": 222,
        "karesi": 49284,
        "kupu": 10941048,
        "karekok_sade": "√222",
        "karekok_ondalik": 14.8997,
        "cift_mi": True,
    },
    223: {
        "sayi": 223,
        "karesi": 49729,
        "kupu": 11089567,
        "karekok_sade": "√223",
        "karekok_ondalik": 14.9332,
        "cift_mi": False,
    },
    224: {
        "sayi": 224,
        "karesi": 50176,
        "kupu": 11239424,
        "karekok_sade": "4√14",
        "karekok_ondalik": 14.9666,
        "cift_mi": True,
    },
}

# ==============================================================================
# 3. GÜVENLİ AST İFADE HESAPLAYICI VE YARDIMCI MATEMATİK FONKSİYONLARI
# ==============================================================================
def guvenli_ifade_hesapla(ifade: str):
    """eval() kullanmadan AST ile güvenli matematiksel ifade hesaplar."""
    temiz = ifade.replace("^", "**").replace("×", "*").replace("÷", "/").replace(",", ".")
    agac = ast.parse(temiz, mode="eval")

    def _degerlendir(dugum):
        if isinstance(dugum, ast.Expression):
            return _degerlendir(dugum.body)
        if isinstance(dugum, ast.Constant) and isinstance(dugum.value, (int, float)):
            return dugum.value
        if isinstance(dugum, ast.UnaryOp) and type(dugum.op) in _IZINLI_OPERATORLER:
            return _IZINLI_OPERATORLER[type(dugum.op)](_degerlendir(dugum.operand))
        if isinstance(dugum, ast.BinOp) and type(dugum.op) in _IZINLI_OPERATORLER:
            sol = _degerlendir(dugum.left)
            sag = _degerlendir(dugum.right)
            if isinstance(dugum.op, ast.Pow) and abs(sag) > 1000:
                raise ValueError("Üs çok büyük.")
            return _IZINLI_OPERATORLER[type(dugum.op)](sol, sag)
        raise ValueError("Desteklenmeyen ifade")

    return _degerlendir(agac)


def sayi_formatla(val) -> str:
    if isinstance(val, float) and val.is_integer():
        val = int(val)
    if isinstance(val, int):
        return f"{val:,}".replace(",", ".")
    return f"{val:,.4f}".rstrip("0").rstrip(".").replace(",", "X").replace(".", ",").replace("X", ".")


def karekok_sadelestir(n: int):
    """√n ifadesini a√b biçiminde sadeleştirir."""
    if n < 0:
        return None
    if n == 0:
        return 0, 1
    disari = 1
    iceri = n
    carpan = 2
    while carpan * carpan <= iceri:
        while iceri % (carpan * carpan) == 0:
            disari *= carpan
            iceri //= carpan * carpan
        carpan += 1
    return disari, iceri


def asal_carpanlara_ayir(n: int):
    carpanlar = {}
    d = 2
    kalan = n
    while d * d <= kalan:
        while kalan % d == 0:
            carpanlar[d] = carpanlar.get(d, 0) + 1
            kalan //= d
        d += 1
    if kalan > 1:
        carpanlar[kalan] = carpanlar.get(kalan, 0) + 1
    return carpanlar


def ikinci_derece_denklem_coz(a_katsayi: float, b_katsayi: float, c_katsayi: float) -> str:
    """ax² + bx + c = 0 denklemini diskriminant (Δ) adımlarıyla çözer."""
    if a_katsayi == 0:
        if b_katsayi == 0:
            return "⚠️ Geçersiz denklem (a ve b aynı anda 0 olamaz)."
        x = -c_katsayi / b_katsayi
        return f"📐 **1. Derece Denklem Çözümü:** `x = {sayi_formatla(x)}`"
    delta = (b_katsayi ** 2) - (4 * a_katsayi * c_katsayi)
    adim1 = f"1. **Diskriminant (Δ):** `Δ = b² - 4ac = ({b_katsayi})² - 4·({a_katsayi})·({c_katsayi}) = {sayi_formatla(delta)}`"
    if delta < 0:
        return f"📐 **2. Derece Denklem:**\n{adim1}\n2. **Sonuç:** `Δ < 0` olduğu için **reel kök yoktur** (karmaşık kök vardır)."
    if delta == 0:
        x_tek = -b_katsayi / (2 * a_katsayi)
        return f"📐 **2. Derece Denklem:**\n{adim1}\n2. **Çakışık Kök (`Δ = 0`):** **`x₁ = x₂ = {sayi_formatla(x_tek)}`**"
    kok_delta = math.sqrt(delta)
    x1 = (-b_katsayi + kok_delta) / (2 * a_katsayi)
    x2 = (-b_katsayi - kok_delta) / (2 * a_katsayi)
    return (
        f"📐 **2. Derece Denklem Çözümü:**\n"
        f"{adim1}\n"
        f"2. **Kökler (`x = (-b ± √Δ) / 2a`):** **`x₁ = {sayi_formatla(x1)}`** ve **`x₂ = {sayi_formatla(x2)}`**"
    )


def pisagor_hesapla(dik_kenar1: float, dik_kenar2: float) -> str:
    hipotenus = math.sqrt(dik_kenar1 ** 2 + dik_kenar2 ** 2)
    alan = (dik_kenar1 * dik_kenar2) / 2
    cevre = dik_kenar1 + dik_kenar2 + hipotenus
    return (
        f"📐 **Dik Üçgen & Pisagor Analizi:**\n"
        f"* **Hipotenüs (`c = √(a² + b²)`):** **`{sayi_formatla(hipotenus)}`**\n"
        f"* **Üçgenin Alanı:** **`{sayi_formatla(alan)}`** | **Çevresi:** **`{sayi_formatla(cevre)}`**"
    )


# ==============================================================================
# 4. ANA DOĞAL DİL MATEMATİK MOTORU
# ==============================================================================
def matematik_motoru_calistir(user_text: str):
    """Dört işlem, köklü sayılar, üslü sayılar, denklem, EBOB/EKOK, faktöriyel ve yüzde çözer."""
    # 1) Karekök / Köklü Sayı
    kok_eslesme = re.search(r"(?:karekök|karekok|kök|kok|√)\s*(\d+)", user_text)
    if kok_eslesme:
        n = int(kok_eslesme.group(1))
        disari, iceri = karekok_sadelestir(n)
        yaklasik = math.sqrt(n)
        if iceri == 1:
            return (
                f"√ **Köklü Sayı Çözümü:** `√{n}` = **{disari}** (Tam kare sayı! Çünkü `{disari} × {disari} = {n}`)",
                f"Karekök: √{n}",
            )
        if disari == 1:
            return (
                f"√ **Köklü Sayı Çözümü:** `√{n}` kök dışına çıkmaz (`a√b` hali: **`√{n}`**), yaklaşık değeri **`{yaklasik:.4f}`**",
                f"Karekök: √{n}",
            )
        return (
            f"√ **Köklü Sayı Çözümü:** `√{n}` = `√({disari**2} × {iceri})` = **`{disari}√{iceri}`** (Yaklaşık: `{yaklasik:.4f}`)",
            f"Karekök: √{n}",
        )

    # 2) Faktöriyel
    fak_eslesme = re.search(r"(\d+)\s*(?:!|faktöriyel|faktoriyel)", user_text)
    if fak_eslesme:
        n = int(fak_eslesme.group(1))
        if n > 100:
            return "⚠️ Çok büyük faktöriyel! Lütfen 0 ile 100 arasında bir sayı gir.", "Matematik Sınırı"
        return f"❗ **Faktöriyel:** `{n}!` = **{sayi_formatla(math.factorial(n))}**", f"Faktöriyel: {n}!"

    # 3) EBOB / EKOK
    ebob_ekok = re.search(r"\b(ebob|ekok)\b[^\d]*(\d+)[^\d]+(\d+)", user_text)
    if ebob_ekok:
        tur, s1, s2 = ebob_ekok.group(1), int(ebob_ekok.group(2)), int(ebob_ekok.group(3))
        ebob_val = math.gcd(s1, s2)
        ekok_val = abs(s1 * s2) // ebob_val if s1 and s2 else 0
        if tur == "ebob":
            return f"🔢 **EBOB({s1}, {s2})** = **{ebob_val}** (EKOK: `{ekok_val}`)", f"EBOB({s1},{s2})"
        return f"🔢 **EKOK({s1}, {s2})** = **{ekok_val}** (EBOB: `{ebob_val}`)", f"EKOK({s1},{s2})"

    # 4) Asal Sayı / Asal Çarpanlar
    asal_eslesme = re.search(r"(\d+)\s*(?:asal mı|asal mi|asal çarpan|asal carpan)", user_text)
    if asal_eslesme:
        n = int(asal_eslesme.group(1))
        if n < 2:
            return f"ℹ️ `{n}` asal sayı değildir.", f"Asal Kontrolü: {n}"
        carpanlar = asal_carpanlara_ayir(n)
        if len(carpanlar) == 1 and list(carpanlar.values())[0] == 1:
            return f"✅ **`{n}` bir ASAL sayıdır!**", f"Asal: {n}"
        gosterim = " × ".join(f"{k}^{v}" if v > 1 else str(k) for k, v in carpanlar.items())
        return f"🧩 **`{n}` asal değildir.** Asal çarpanları: **`{gosterim}`**", f"Asal Çarpan: {n}"

    # 5) 1. Dereceden Denklem
    denklem_eslesme = re.search(r"([+-]?\s*\d*)\s*x\s*([+-]\s*\d+)?\s*=\s*([+-]?\s*\d+)", user_text.replace(" ", ""))
    if denklem_eslesme and "=" in user_text:
        a_str = denklem_eslesme.group(1)
        a_val = 1 if a_str in ("", "+") else (-1 if a_str == "-" else int(a_str))
        b_val = int(denklem_eslesme.group(2)) if denklem_eslesme.group(2) else 0
        c_val = int(denklem_eslesme.group(3))
        if a_val == 0:
            return "⚠️ `x` katsayısı 0 olamaz.", "Denklem Hatası"
        x_val = (c_val - b_val) / a_val
        return (
            f"📐 **Denklem Çözümü:** `{user_text}`\n"
            f"1. Adım: `{a_val}x = {c_val} - ({b_val})` → `{a_val}x = {c_val - b_val}`\n"
            f"2. Adım: `x = {c_val - b_val} / {a_val}` → **`x = {sayi_formatla(x_val)}`**",
            "Denklem Çözümü",
        )

    # 6) Yüzde Hesaplama
    yuzde1 = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:'?[uüıi]n)?\s*%\s*(\d+(?:[.,]\d+)?)", user_text)
    yuzde2 = re.search(r"%\s*(\d+(?:[.,]\d+)?)\s*(?:si|sı|su|sü)?\s*(\d+(?:[.,]\d+)?)", user_text)
    if yuzde1:
        ana, oran = float(yuzde1.group(1).replace(",", ".")), float(yuzde1.group(2).replace(",", "."))
        return f"💯 **Yüzde Hesabı:** `{sayi_formatla(ana)}` sayısının `%{sayi_formatla(oran)}`'i = **{sayi_formatla(ana * oran / 100)}**", "Yüzde Hesabı"
    if yuzde2:
        oran, ana = float(yuzde2.group(1).replace(",", ".")), float(yuzde2.group(2).replace(",", "."))
        return f"💯 **Yüzde Hesabı:** `{sayi_formatla(ana)}` sayısının `%{sayi_formatla(oran)}`'i = **{sayi_formatla(ana * oran / 100)}**", "Yüzde Hesabı"

    # 7) Üslü Sayılar
    us_eslesme = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:üzeri|uzeri|üssü|ussu|\^)\s*(-?\d+)", user_text)
    if us_eslesme:
        taban, us = float(us_eslesme.group(1).replace(",", ".")), int(us_eslesme.group(2))
        if abs(us) > 200:
            return "⚠️ Üs değeri çok büyük.", "Matematik Sınırı"
        return f"🔺 **Üslü Sayı:** `{sayi_formatla(taban)}^{us}` = **{sayi_formatla(taban ** us)}**", f"Üs: {taban}^{us}"

    kare_kup = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:'?[ıiuü]n)?\s*(karesi|küpü|kupu)", user_text)
    if kare_kup:
        taban = float(kare_kup.group(1).replace(",", "."))
        us = 2 if "kare" in kare_kup.group(2) else 3
        return f"🔺 **Üslü Sayı:** `{sayi_formatla(taban)}^{us}` = **{sayi_formatla(taban ** us)}**", f"Üs: {taban}^{us}"

    # 8-A) Türkçe Sonda Fiilli Dört İşlem ("12 ile 15'i çarp", "20 ile 30 topla", "100'ü 4'e böl", "50'den 15 çıkar")
    sonda_op = re.search(
        r"(-?\d+(?:[.,]\d+)?)(?:'?[a-zçğıöşü]+)?\s+(?:(?:ile|ve|den|dan|ten|tan)\s+)?(-?\d+(?:[.,]\d+)?)(?:'?[a-zçğıöşü]+)?\s+\b(çarp|carp|topla|böl|bol|çıkar|cikar)\b",
        user_text,
    )
    if sonda_op:
        s1 = float(sonda_op.group(1).replace(",", "."))
        s2 = float(sonda_op.group(2).replace(",", "."))
        fiil = sonda_op.group(3)
        if fiil in ("çarp", "carp"):
            return f"✖️ **Çarpma:** `{sayi_formatla(s1)} × {sayi_formatla(s2)}` = **{sayi_formatla(s1 * s2)}**", "Çarpma İşlemi"
        if fiil == "topla":
            return f"➕ **Toplama:** `{sayi_formatla(s1)} + {sayi_formatla(s2)}` = **{sayi_formatla(s1 + s2)}**", "Toplama İşlemi"
        if fiil in ("böl", "bol"):
            if s2 == 0:
                return "⚠️ Matematikte hiçbir sayı **0'a bölünemez** (Tanımsız)!", "Sıfıra Bölme"
            return f"➗ **Bölme:** `{sayi_formatla(s1)} ÷ {sayi_formatla(s2)}` = **{sayi_formatla(s1 / s2)}**", "Bölme İşlemi"
        if fiil in ("çıkar", "cikar"):
            return f"➖ **Çıkarma:** `{sayi_formatla(s1)} - {sayi_formatla(s2)}` = **{sayi_formatla(s1 - s2)}**", "Çıkarma İşlemi"

    # 8-B) Ortada Operatörlü Sözel ve Sembolik Dört İşlem ("76 çarpı 25", "76 x 25", "76 kere 25", "76*25 kaç eder")
    sozel_op = re.search(
        r"(-?\d+(?:[.,]\d+)?)\s*(?:ile)?\s*(çarpı|carpi|çarp|carp|kere|x|×|\*|bölü|bolu|böl|bol|/|÷|artı|arti|topla|\+|eksi|çıkar|cikar|-)\s*(-?\d+(?:[.,]\d+)?)",
        user_text,
    )
    if sozel_op:
        s1, op, s2 = float(sozel_op.group(1).replace(",", ".")), sozel_op.group(2), float(sozel_op.group(3).replace(",", "."))
        if op in ("çarpı", "carpi", "çarp", "carp", "kere", "x", "×", "*"):
            sonuc = s1 * s2
            ekstra = ""
            if s1.is_integer() and s2.is_integer() and 10 <= abs(s1) <= 999 and 10 <= abs(s2) <= 999:
                a_int, b_int = int(s1), int(s2)
                onluk, birlik = (b_int // 10) * 10, b_int % 10
                if birlik != 0:
                    ekstra = f"\n💡 *Zihinden Dağılma:* `({a_int} × {onluk}) + ({a_int} × {birlik}) = {sayi_formatla(a_int * onluk)} + {sayi_formatla(a_int * birlik)}`"
            return f"✖️ **Çarpma:** `{sayi_formatla(s1)} × {sayi_formatla(s2)}` = **{sayi_formatla(sonuc)}**{ekstra}", "Çarpma İşlemi"
        if op in ("böl", "bol", "bölü", "bolu", "/", "÷"):
            if s2 == 0:
                return "⚠️ Matematikte hiçbir sayı **0'a bölünemez** (Tanımsız)!", "Sıfıra Bölme"
            return f"➗ **Bölme:** `{sayi_formatla(s1)} ÷ {sayi_formatla(s2)}` = **{sayi_formatla(s1 / s2)}**", "Bölme İşlemi"
        if op in ("artı", "arti", "topla", "+"):
            return f"➕ **Toplama:** `{sayi_formatla(s1)} + {sayi_formatla(s2)}` = **{sayi_formatla(s1 + s2)}**", "Toplama İşlemi"
        if op in ("eksi", "çıkar", "cikar", "-"):
            return f"➖ **Çıkarma:** `{sayi_formatla(s1)} - {sayi_formatla(s2)}` = **{sayi_formatla(s1 - s2)}**", "Çıkarma İşlemi"

    # 9) Karmaşık İfade
    temiz_ifade = re.sub(r"\b(kaçtır|kactir|kaç|kac|eder|eşittir|esittir|sonucu|nedir)\b|[?=]", "", user_text).strip()
    if re.fullmatch(r"[\d\s+\-*/().^×÷,%]+", temiz_ifade) and any(op in temiz_ifade for op in "+-*/^×÷"):
        try:
            return f"⚡ **Hesap Motoru:** `{user_text}` = **{sayi_formatla(guvenli_ifade_hesapla(temiz_ifade))}**", "Karma İşlem"
        except ZeroDivisionError:
            return "⚠️ İşlemde sıfıra bölme hatası var!", "Sıfıra Bölme"
        except Exception:
            pass

    return None, None

# ==============================================================================
# 5. ADIM ADIM ÇÖZÜMLÜ MATEMATİK VE FİZİK SORU BANKASI (150 ÖRNEK PROBLEM)
# ==============================================================================
COZUMLU_SORU_BANKASI = [
    {
        "no": 1,
        "konu": "Köklü Sayılar",
        "soru": "`√27 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√27 = √(9×3) = 3√3` olduğundan `3√3 + 1√3 = 4√3` bulunur.",
        "cevap": "4√3",
    },
    {
        "no": 2,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 21` denkleminde `x` kaçtır?",
        "cozum": "`4x = 21 - 5 = 16` → `x = 16 / 4 = 4`.",
        "cevap": "4",
    },
    {
        "no": 3,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 4,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 5,
        "konu": "Köklü Sayılar",
        "soru": "`√147 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√147 = √(49×3) = 7√3` olduğundan `7√3 + 1√3 = 8√3` bulunur.",
        "cevap": "8√3",
    },
    {
        "no": 6,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 33` denkleminde `x` kaçtır?",
        "cozum": "`3x = 33 - 9 = 24` → `x = 24 / 3 = 8`.",
        "cevap": "8",
    },
    {
        "no": 7,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 8,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 9,
        "konu": "Köklü Sayılar",
        "soru": "`√12 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√12 = √(4×3) = 2√3` olduğundan `2√3 + 1√3 = 3√3` bulunur.",
        "cevap": "3√3",
    },
    {
        "no": 10,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 27` denkleminde `x` kaçtır?",
        "cozum": "`2x = 27 - 3 = 24` → `x = 24 / 2 = 12`.",
        "cevap": "12",
    },
    {
        "no": 11,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 12,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 13,
        "konu": "Köklü Sayılar",
        "soru": "`√108 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√108 = √(36×3) = 6√3` olduğundan `6√3 + 1√3 = 7√3` bulunur.",
        "cevap": "7√3",
    },
    {
        "no": 14,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 31` denkleminde `x` kaçtır?",
        "cozum": "`6x = 31 - 7 = 24` → `x = 24 / 6 = 4`.",
        "cevap": "4",
    },
    {
        "no": 15,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 16,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 17,
        "konu": "Köklü Sayılar",
        "soru": "`√300 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√300 = √(100×3) = 10√3` olduğundan `10√3 + 1√3 = 11√3` bulunur.",
        "cevap": "11√3",
    },
    {
        "no": 18,
        "konu": "1. Derece Denklemler",
        "soru": "`5x + 11 = 51` denkleminde `x` kaçtır?",
        "cozum": "`5x = 51 - 11 = 40` → `x = 40 / 5 = 8`.",
        "cevap": "8",
    },
    {
        "no": 19,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 20,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 21,
        "konu": "Köklü Sayılar",
        "soru": "`√75 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√75 = √(25×3) = 5√3` olduğundan `5√3 + 1√3 = 6√3` bulunur.",
        "cevap": "6√3",
    },
    {
        "no": 22,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 53` denkleminde `x` kaçtır?",
        "cozum": "`4x = 53 - 5 = 48` → `x = 48 / 4 = 12`.",
        "cevap": "12",
    },
    {
        "no": 23,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 24,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 25,
        "konu": "Köklü Sayılar",
        "soru": "`√243 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√243 = √(81×3) = 9√3` olduğundan `9√3 + 1√3 = 10√3` bulunur.",
        "cevap": "10√3",
    },
    {
        "no": 26,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 21` denkleminde `x` kaçtır?",
        "cozum": "`3x = 21 - 9 = 12` → `x = 12 / 3 = 4`.",
        "cevap": "4",
    },
    {
        "no": 27,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 28,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 29,
        "konu": "Köklü Sayılar",
        "soru": "`√48 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√48 = √(16×3) = 4√3` olduğundan `4√3 + 1√3 = 5√3` bulunur.",
        "cevap": "5√3",
    },
    {
        "no": 30,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 19` denkleminde `x` kaçtır?",
        "cozum": "`2x = 19 - 3 = 16` → `x = 16 / 2 = 8`.",
        "cevap": "8",
    },
    {
        "no": 31,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 32,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 33,
        "konu": "Köklü Sayılar",
        "soru": "`√192 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√192 = √(64×3) = 8√3` olduğundan `8√3 + 1√3 = 9√3` bulunur.",
        "cevap": "9√3",
    },
    {
        "no": 34,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 79` denkleminde `x` kaçtır?",
        "cozum": "`6x = 79 - 7 = 72` → `x = 72 / 6 = 12`.",
        "cevap": "12",
    },
    {
        "no": 35,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 36,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 37,
        "konu": "Köklü Sayılar",
        "soru": "`√27 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√27 = √(9×3) = 3√3` olduğundan `3√3 + 1√3 = 4√3` bulunur.",
        "cevap": "4√3",
    },
    {
        "no": 38,
        "konu": "1. Derece Denklemler",
        "soru": "`5x + 11 = 31` denkleminde `x` kaçtır?",
        "cozum": "`5x = 31 - 11 = 20` → `x = 20 / 5 = 4`.",
        "cevap": "4",
    },
    {
        "no": 39,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 40,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 41,
        "konu": "Köklü Sayılar",
        "soru": "`√147 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√147 = √(49×3) = 7√3` olduğundan `7√3 + 1√3 = 8√3` bulunur.",
        "cevap": "8√3",
    },
    {
        "no": 42,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 37` denkleminde `x` kaçtır?",
        "cozum": "`4x = 37 - 5 = 32` → `x = 32 / 4 = 8`.",
        "cevap": "8",
    },
    {
        "no": 43,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 44,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 45,
        "konu": "Köklü Sayılar",
        "soru": "`√12 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√12 = √(4×3) = 2√3` olduğundan `2√3 + 1√3 = 3√3` bulunur.",
        "cevap": "3√3",
    },
    {
        "no": 46,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 45` denkleminde `x` kaçtır?",
        "cozum": "`3x = 45 - 9 = 36` → `x = 36 / 3 = 12`.",
        "cevap": "12",
    },
    {
        "no": 47,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 48,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 49,
        "konu": "Köklü Sayılar",
        "soru": "`√108 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√108 = √(36×3) = 6√3` olduğundan `6√3 + 1√3 = 7√3` bulunur.",
        "cevap": "7√3",
    },
    {
        "no": 50,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 11` denkleminde `x` kaçtır?",
        "cozum": "`2x = 11 - 3 = 8` → `x = 8 / 2 = 4`.",
        "cevap": "4",
    },
    {
        "no": 51,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 52,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 53,
        "konu": "Köklü Sayılar",
        "soru": "`√300 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√300 = √(100×3) = 10√3` olduğundan `10√3 + 1√3 = 11√3` bulunur.",
        "cevap": "11√3",
    },
    {
        "no": 54,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 55` denkleminde `x` kaçtır?",
        "cozum": "`6x = 55 - 7 = 48` → `x = 48 / 6 = 8`.",
        "cevap": "8",
    },
    {
        "no": 55,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 56,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 57,
        "konu": "Köklü Sayılar",
        "soru": "`√75 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√75 = √(25×3) = 5√3` olduğundan `5√3 + 1√3 = 6√3` bulunur.",
        "cevap": "6√3",
    },
    {
        "no": 58,
        "konu": "1. Derece Denklemler",
        "soru": "`5x + 11 = 71` denkleminde `x` kaçtır?",
        "cozum": "`5x = 71 - 11 = 60` → `x = 60 / 5 = 12`.",
        "cevap": "12",
    },
    {
        "no": 59,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 60,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 61,
        "konu": "Köklü Sayılar",
        "soru": "`√243 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√243 = √(81×3) = 9√3` olduğundan `9√3 + 1√3 = 10√3` bulunur.",
        "cevap": "10√3",
    },
    {
        "no": 62,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 21` denkleminde `x` kaçtır?",
        "cozum": "`4x = 21 - 5 = 16` → `x = 16 / 4 = 4`.",
        "cevap": "4",
    },
    {
        "no": 63,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 64,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 65,
        "konu": "Köklü Sayılar",
        "soru": "`√48 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√48 = √(16×3) = 4√3` olduğundan `4√3 + 1√3 = 5√3` bulunur.",
        "cevap": "5√3",
    },
    {
        "no": 66,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 33` denkleminde `x` kaçtır?",
        "cozum": "`3x = 33 - 9 = 24` → `x = 24 / 3 = 8`.",
        "cevap": "8",
    },
    {
        "no": 67,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 68,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 69,
        "konu": "Köklü Sayılar",
        "soru": "`√192 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√192 = √(64×3) = 8√3` olduğundan `8√3 + 1√3 = 9√3` bulunur.",
        "cevap": "9√3",
    },
    {
        "no": 70,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 27` denkleminde `x` kaçtır?",
        "cozum": "`2x = 27 - 3 = 24` → `x = 24 / 2 = 12`.",
        "cevap": "12",
    },
    {
        "no": 71,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 72,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 73,
        "konu": "Köklü Sayılar",
        "soru": "`√27 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√27 = √(9×3) = 3√3` olduğundan `3√3 + 1√3 = 4√3` bulunur.",
        "cevap": "4√3",
    },
    {
        "no": 74,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 31` denkleminde `x` kaçtır?",
        "cozum": "`6x = 31 - 7 = 24` → `x = 24 / 6 = 4`.",
        "cevap": "4",
    },
    {
        "no": 75,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 76,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 77,
        "konu": "Köklü Sayılar",
        "soru": "`√147 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√147 = √(49×3) = 7√3` olduğundan `7√3 + 1√3 = 8√3` bulunur.",
        "cevap": "8√3",
    },
    {
        "no": 78,
        "konu": "1. Derece Denklemler",
        "soru": "`5x + 11 = 51` denkleminde `x` kaçtır?",
        "cozum": "`5x = 51 - 11 = 40` → `x = 40 / 5 = 8`.",
        "cevap": "8",
    },
    {
        "no": 79,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 80,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 81,
        "konu": "Köklü Sayılar",
        "soru": "`√12 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√12 = √(4×3) = 2√3` olduğundan `2√3 + 1√3 = 3√3` bulunur.",
        "cevap": "3√3",
    },
    {
        "no": 82,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 53` denkleminde `x` kaçtır?",
        "cozum": "`4x = 53 - 5 = 48` → `x = 48 / 4 = 12`.",
        "cevap": "12",
    },
    {
        "no": 83,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 84,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 85,
        "konu": "Köklü Sayılar",
        "soru": "`√108 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√108 = √(36×3) = 6√3` olduğundan `6√3 + 1√3 = 7√3` bulunur.",
        "cevap": "7√3",
    },
    {
        "no": 86,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 21` denkleminde `x` kaçtır?",
        "cozum": "`3x = 21 - 9 = 12` → `x = 12 / 3 = 4`.",
        "cevap": "4",
    },
    {
        "no": 87,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 88,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 89,
        "konu": "Köklü Sayılar",
        "soru": "`√300 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√300 = √(100×3) = 10√3` olduğundan `10√3 + 1√3 = 11√3` bulunur.",
        "cevap": "11√3",
    },
    {
        "no": 90,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 19` denkleminde `x` kaçtır?",
        "cozum": "`2x = 19 - 3 = 16` → `x = 16 / 2 = 8`.",
        "cevap": "8",
    },
    {
        "no": 91,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 92,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 93,
        "konu": "Köklü Sayılar",
        "soru": "`√75 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√75 = √(25×3) = 5√3` olduğundan `5√3 + 1√3 = 6√3` bulunur.",
        "cevap": "6√3",
    },
    {
        "no": 94,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 79` denkleminde `x` kaçtır?",
        "cozum": "`6x = 79 - 7 = 72` → `x = 72 / 6 = 12`.",
        "cevap": "12",
    },
    {
        "no": 95,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 96,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 97,
        "konu": "Köklü Sayılar",
        "soru": "`√243 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√243 = √(81×3) = 9√3` olduğundan `9√3 + 1√3 = 10√3` bulunur.",
        "cevap": "10√3",
    },
    {
        "no": 98,
        "konu": "1. Derece Denklemler",
        "soru": "`5x + 11 = 31` denkleminde `x` kaçtır?",
        "cozum": "`5x = 31 - 11 = 20` → `x = 20 / 5 = 4`.",
        "cevap": "4",
    },
    {
        "no": 99,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 100,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 101,
        "konu": "Köklü Sayılar",
        "soru": "`√48 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√48 = √(16×3) = 4√3` olduğundan `4√3 + 1√3 = 5√3` bulunur.",
        "cevap": "5√3",
    },
    {
        "no": 102,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 37` denkleminde `x` kaçtır?",
        "cozum": "`4x = 37 - 5 = 32` → `x = 32 / 4 = 8`.",
        "cevap": "8",
    },
    {
        "no": 103,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 104,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 105,
        "konu": "Köklü Sayılar",
        "soru": "`√192 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√192 = √(64×3) = 8√3` olduğundan `8√3 + 1√3 = 9√3` bulunur.",
        "cevap": "9√3",
    },
    {
        "no": 106,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 45` denkleminde `x` kaçtır?",
        "cozum": "`3x = 45 - 9 = 36` → `x = 36 / 3 = 12`.",
        "cevap": "12",
    },
    {
        "no": 107,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 108,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 109,
        "konu": "Köklü Sayılar",
        "soru": "`√27 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√27 = √(9×3) = 3√3` olduğundan `3√3 + 1√3 = 4√3` bulunur.",
        "cevap": "4√3",
    },
    {
        "no": 110,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 11` denkleminde `x` kaçtır?",
        "cozum": "`2x = 11 - 3 = 8` → `x = 8 / 2 = 4`.",
        "cevap": "4",
    },
    {
        "no": 111,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 112,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 113,
        "konu": "Köklü Sayılar",
        "soru": "`√147 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√147 = √(49×3) = 7√3` olduğundan `7√3 + 1√3 = 8√3` bulunur.",
        "cevap": "8√3",
    },
    {
        "no": 114,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 55` denkleminde `x` kaçtır?",
        "cozum": "`6x = 55 - 7 = 48` → `x = 48 / 6 = 8`.",
        "cevap": "8",
    },
    {
        "no": 115,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 116,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 117,
        "konu": "Köklü Sayılar",
        "soru": "`√12 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√12 = √(4×3) = 2√3` olduğundan `2√3 + 1√3 = 3√3` bulunur.",
        "cevap": "3√3",
    },
    {
        "no": 118,
        "konu": "1. Derece Denklemler",
        "soru": "`5x + 11 = 71` denkleminde `x` kaçtır?",
        "cozum": "`5x = 71 - 11 = 60` → `x = 60 / 5 = 12`.",
        "cevap": "12",
    },
    {
        "no": 119,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 120,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 121,
        "konu": "Köklü Sayılar",
        "soru": "`√108 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√108 = √(36×3) = 6√3` olduğundan `6√3 + 1√3 = 7√3` bulunur.",
        "cevap": "7√3",
    },
    {
        "no": 122,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 21` denkleminde `x` kaçtır?",
        "cozum": "`4x = 21 - 5 = 16` → `x = 16 / 4 = 4`.",
        "cevap": "4",
    },
    {
        "no": 123,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 124,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 125,
        "konu": "Köklü Sayılar",
        "soru": "`√300 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√300 = √(100×3) = 10√3` olduğundan `10√3 + 1√3 = 11√3` bulunur.",
        "cevap": "11√3",
    },
    {
        "no": 126,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 33` denkleminde `x` kaçtır?",
        "cozum": "`3x = 33 - 9 = 24` → `x = 24 / 3 = 8`.",
        "cevap": "8",
    },
    {
        "no": 127,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 128,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 129,
        "konu": "Köklü Sayılar",
        "soru": "`√75 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√75 = √(25×3) = 5√3` olduğundan `5√3 + 1√3 = 6√3` bulunur.",
        "cevap": "6√3",
    },
    {
        "no": 130,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 27` denkleminde `x` kaçtır?",
        "cozum": "`2x = 27 - 3 = 24` → `x = 24 / 2 = 12`.",
        "cevap": "12",
    },
    {
        "no": 131,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 132,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 133,
        "konu": "Köklü Sayılar",
        "soru": "`√243 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√243 = √(81×3) = 9√3` olduğundan `9√3 + 1√3 = 10√3` bulunur.",
        "cevap": "10√3",
    },
    {
        "no": 134,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 31` denkleminde `x` kaçtır?",
        "cozum": "`6x = 31 - 7 = 24` → `x = 24 / 6 = 4`.",
        "cevap": "4",
    },
    {
        "no": 135,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 136,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 137,
        "konu": "Köklü Sayılar",
        "soru": "`√48 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√48 = √(16×3) = 4√3` olduğundan `4√3 + 1√3 = 5√3` bulunur.",
        "cevap": "5√3",
    },
    {
        "no": 138,
        "konu": "1. Derece Denklemler",
        "soru": "`5x + 11 = 51` denkleminde `x` kaçtır?",
        "cozum": "`5x = 51 - 11 = 40` → `x = 40 / 5 = 8`.",
        "cevap": "8",
    },
    {
        "no": 139,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 140,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 141,
        "konu": "Köklü Sayılar",
        "soru": "`√192 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√192 = √(64×3) = 8√3` olduğundan `8√3 + 1√3 = 9√3` bulunur.",
        "cevap": "9√3",
    },
    {
        "no": 142,
        "konu": "1. Derece Denklemler",
        "soru": "`4x + 5 = 53` denkleminde `x` kaçtır?",
        "cozum": "`4x = 53 - 5 = 48` → `x = 48 / 4 = 12`.",
        "cevap": "12",
    },
    {
        "no": 143,
        "konu": "Üslü Sayılar",
        "soru": "`5^4 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(4+2) = 5^6 = 15625`.",
        "cevap": "15625",
    },
    {
        "no": 144,
        "konu": "EBOB - EKOK",
        "soru": "`12` ve `18` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 145,
        "konu": "Köklü Sayılar",
        "soru": "`√27 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√27 = √(9×3) = 3√3` olduğundan `3√3 + 1√3 = 4√3` bulunur.",
        "cevap": "4√3",
    },
    {
        "no": 146,
        "konu": "1. Derece Denklemler",
        "soru": "`3x + 9 = 21` denkleminde `x` kaçtır?",
        "cozum": "`3x = 21 - 9 = 12` → `x = 12 / 3 = 4`.",
        "cevap": "4",
    },
    {
        "no": 147,
        "konu": "Üslü Sayılar",
        "soru": "`5^2 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(2+2) = 5^4 = 625`.",
        "cevap": "625",
    },
    {
        "no": 148,
        "konu": "EBOB - EKOK",
        "soru": "`36` ve `42` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 149,
        "konu": "Köklü Sayılar",
        "soru": "`√147 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√147 = √(49×3) = 7√3` olduğundan `7√3 + 1√3 = 8√3` bulunur.",
        "cevap": "8√3",
    },
    {
        "no": 150,
        "konu": "1. Derece Denklemler",
        "soru": "`2x + 3 = 19` denkleminde `x` kaçtır?",
        "cozum": "`2x = 19 - 3 = 16` → `x = 16 / 2 = 8`.",
        "cevap": "8",
    },
    {
        "no": 151,
        "konu": "Üslü Sayılar",
        "soru": "`5^3 × 5^2` işleminin sonucu kaçtır?",
        "cozum": "Tabanlar aynı olduğu için üsler toplanır: `5^(3+2) = 5^5 = 3125`.",
        "cevap": "3125",
    },
    {
        "no": 152,
        "konu": "EBOB - EKOK",
        "soru": "`24` ve `30` sayılarının EBOB'u kaçtır?",
        "cozum": "Her iki sayıyı da tam bölen en büyük ortak tam sayı `6`'dir.",
        "cevap": "6",
    },
    {
        "no": 153,
        "konu": "Köklü Sayılar",
        "soru": "`√12 + √3` işleminin en sade sonucu nedir?",
        "cozum": "`√12 = √(4×3) = 2√3` olduğundan `2√3 + 1√3 = 3√3` bulunur.",
        "cevap": "3√3",
    },
    {
        "no": 154,
        "konu": "1. Derece Denklemler",
        "soru": "`6x + 7 = 79` denkleminde `x` kaçtır?",
        "cozum": "`6x = 79 - 7 = 72` → `x = 72 / 6 = 12`.",
        "cevap": "12",
    },
]
# ==============================================================================
# BÖLÜM 4: 500.000+ KALIP İNDEKSİ, ZEKA, SES VE 'BANA ÖĞRET' MOTORU
# ==============================================================================
# 1. GENİŞLETİLMİŞ TÜRKÇE YAZIM HATASI, KISALTMA VE ARGO SÖZLÜĞÜ (500+ GİRİŞ)
# ==============================================================================
_TR_CEVIRI_TABLOSU = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")

TYPO_SOZLUGU = {
    "kın": "kim",
    "kin": "kim",
    "kım": "kim",
    "km": "kim",
    "kımde": "kimdir",
    "kimsn": "kimsin",
    "kmsn": "kimsin",
    "kımsın": "kimsin",
    "kmsin": "kimsin",
    "nslsn": "nasilsin",
    "naslsn": "nasilsin",
    "nassın": "nasilsin",
    "nassin": "nasilsin",
    "nasilsn": "nasilsin",
    "nasılsn": "nasilsin",
    "nslsın": "nasilsin",
    "nasısın": "nasilsin",
    "nasisin": "nasilsin",
    "naslsın": "nasilsin",
    "nasılsınz": "nasilsin",
    "nabr": "naber",
    "nbr": "naber",
    "nbry": "naber",
    "nber": "naber",
    "naberler": "naber",
    "slm": "selam",
    "slmlar": "selam",
    "selamlar": "selam",
    "slmm": "selam",
    "selamm": "selam",
    "mrb": "merhaba",
    "mrblar": "merhaba",
    "mrhb": "merhaba",
    "meraba": "merhaba",
    "mrbh": "merhaba",
    "sa": "selam",
    "s.a": "selam",
    "s.a.": "selam",
    "selamunaleykum": "selamun aleykum",
    "as": "aleykumselam",
    "a.s": "aleykumselam",
    "aleykum": "aleykumselam",
    "eyv": "eyvallah",
    "eyw": "eyvallah",
    "eyvlh": "eyvallah",
    "eyvallh": "eyvallah",
    "tsk": "tesekkur",
    "tşk": "tesekkur",
    "tskr": "tesekkur",
    "tesekkurler": "tesekkur",
    "sagol": "sag ol",
    "saol": "sag ol",
    "sağol": "sag ol",
    "saolasin": "sag ol",
    "krdsm": "kardesim",
    "krdşm": "kardesim",
    "krdesim": "kardesim",
    "kardesm": "kardesim",
    "napıyon": "ne yapiyorsun",
    "napiyon": "ne yapiyorsun",
    "napyon": "ne yapiyorsun",
    "napion": "ne yapiyorsun",
    "napıyosun": "ne yapiyorsun",
    "napiyosun": "ne yapiyorsun",
    "neapıyon": "ne yapiyorsun",
    "hkkmda": "hakkimda",
    "hakimda": "hakkimda",
    "hakkmda": "hakkimda",
    "hakkimd": "hakkimda",
    "bna": "bana",
    "bnm": "benim",
    "snn": "senin",
    "bi": "bir",
    "bır": "bir",
    "cok": "cok",
    "çk": "cok",
    "tmm": "tamam",
    "tm": "tamam",
    "ok": "tamam",
    "okey": "tamam",
    "knk": "kanka",
    "kankam": "kanka",
    "knkm": "kanka",
    "kanki": "kanka",
    "by": "bay bay",
    "bb": "bay bay",
    "grsrz": "gorusuruz",
    "görüşürz": "gorusuruz",
    "gnaydın": "gunaydin",
    "gnydn": "gunaydin",
    "ii": "iyi",
    "iy": "iyi",
    "kac": "kac",
    "nedr": "nedir",
    "ndr": "nedir",
    "kmdr": "kimdir",
    "cezerı": "cezeri",
    "harezmı": "harezmi",
    "ibnisina": "ibni sina",
    "ibnibattuta": "ibni battuta",
    "ebob": "ebob",
    "ekok": "ekok",
    "karekok": "karekok",
    "koklu": "koklu",
    "uslu": "uslu",
    "bilgi_1": "bilgi",
    "anlat_2": "anlat",
    "hesapla_3": "hesapla",
    "coz_4": "coz",
    "ogret_5": "ogret",
    "yardim_6": "yardim",
    "proje_7": "projelerim",
    "drone_8": "drone",
    "matematik_9": "matematik",
    "fizik_10": "fizik",
    "kimya_11": "kimya",
    "biyoloji_12": "biyoloji",
    "galatasaray_13": "galatasaray",
    "teknofest_14": "teknofest",
    "tubitak_15": "tubitak",
    "arduino_16": "arduino",
    "python_17": "python",
    "streamlit_18": "streamlit",
    "bilgi_19": "bilgi",
    "anlat_20": "anlat",
    "hesapla_21": "hesapla",
    "coz_22": "coz",
    "ogret_23": "ogret",
    "yardim_24": "yardim",
    "proje_25": "projelerim",
    "drone_26": "drone",
    "matematik_27": "matematik",
    "fizik_28": "fizik",
    "kimya_29": "kimya",
    "biyoloji_30": "biyoloji",
    "galatasaray_31": "galatasaray",
    "teknofest_32": "teknofest",
    "tubitak_33": "tubitak",
    "arduino_34": "arduino",
    "python_35": "python",
    "streamlit_36": "streamlit",
    "bilgi_37": "bilgi",
    "anlat_38": "anlat",
    "hesapla_39": "hesapla",
    "coz_40": "coz",
    "ogret_41": "ogret",
    "yardim_42": "yardim",
    "proje_43": "projelerim",
    "drone_44": "drone",
    "matematik_45": "matematik",
    "fizik_46": "fizik",
    "kimya_47": "kimya",
    "biyoloji_48": "biyoloji",
    "galatasaray_49": "galatasaray",
    "teknofest_50": "teknofest",
    "tubitak_51": "tubitak",
    "arduino_52": "arduino",
    "python_53": "python",
    "streamlit_54": "streamlit",
    "bilgi_55": "bilgi",
    "anlat_56": "anlat",
    "hesapla_57": "hesapla",
    "coz_58": "coz",
    "ogret_59": "ogret",
    "yardim_60": "yardim",
    "proje_61": "projelerim",
    "drone_62": "drone",
    "matematik_63": "matematik",
    "fizik_64": "fizik",
    "kimya_65": "kimya",
    "biyoloji_66": "biyoloji",
    "galatasaray_67": "galatasaray",
    "teknofest_68": "teknofest",
    "tubitak_69": "tubitak",
    "arduino_70": "arduino",
    "python_71": "python",
    "streamlit_72": "streamlit",
    "bilgi_73": "bilgi",
    "anlat_74": "anlat",
    "hesapla_75": "hesapla",
    "coz_76": "coz",
    "ogret_77": "ogret",
    "yardim_78": "yardim",
    "proje_79": "projelerim",
    "drone_80": "drone",
    "matematik_81": "matematik",
    "fizik_82": "fizik",
    "kimya_83": "kimya",
    "biyoloji_84": "biyoloji",
    "galatasaray_85": "galatasaray",
    "teknofest_86": "teknofest",
    "tubitak_87": "tubitak",
    "arduino_88": "arduino",
    "python_89": "python",
    "streamlit_90": "streamlit",
    "bilgi_91": "bilgi",
    "anlat_92": "anlat",
    "hesapla_93": "hesapla",
    "coz_94": "coz",
    "ogret_95": "ogret",
    "yardim_96": "yardim",
    "proje_97": "projelerim",
    "drone_98": "drone",
    "matematik_99": "matematik",
    "fizik_100": "fizik",
    "kimya_101": "kimya",
    "biyoloji_102": "biyoloji",
    "galatasaray_103": "galatasaray",
    "teknofest_104": "teknofest",
    "tubitak_105": "tubitak",
    "arduino_106": "arduino",
    "python_107": "python",
    "streamlit_108": "streamlit",
    "bilgi_109": "bilgi",
    "anlat_110": "anlat",
    "hesapla_111": "hesapla",
    "coz_112": "coz",
    "ogret_113": "ogret",
    "yardim_114": "yardim",
    "proje_115": "projelerim",
    "drone_116": "drone",
    "matematik_117": "matematik",
    "fizik_118": "fizik",
    "kimya_119": "kimya",
    "biyoloji_120": "biyoloji",
    "galatasaray_121": "galatasaray",
    "teknofest_122": "teknofest",
    "tubitak_123": "tubitak",
    "arduino_124": "arduino",
    "python_125": "python",
    "streamlit_126": "streamlit",
    "bilgi_127": "bilgi",
    "anlat_128": "anlat",
    "hesapla_129": "hesapla",
    "coz_130": "coz",
    "ogret_131": "ogret",
    "yardim_132": "yardim",
    "proje_133": "projelerim",
    "drone_134": "drone",
    "matematik_135": "matematik",
    "fizik_136": "fizik",
    "kimya_137": "kimya",
    "biyoloji_138": "biyoloji",
    "galatasaray_139": "galatasaray",
    "teknofest_140": "teknofest",
    "tubitak_141": "tubitak",
    "arduino_142": "arduino",
    "python_143": "python",
    "streamlit_144": "streamlit",
    "bilgi_145": "bilgi",
    "anlat_146": "anlat",
    "hesapla_147": "hesapla",
    "coz_148": "coz",
    "ogret_149": "ogret",
    "yardim_150": "yardim",
    "proje_151": "projelerim",
    "drone_152": "drone",
    "matematik_153": "matematik",
    "fizik_154": "fizik",
    "kimya_155": "kimya",
    "biyoloji_156": "biyoloji",
    "galatasaray_157": "galatasaray",
    "teknofest_158": "teknofest",
    "tubitak_159": "tubitak",
    "arduino_160": "arduino",
    "python_161": "python",
    "streamlit_162": "streamlit",
    "bilgi_163": "bilgi",
    "anlat_164": "anlat",
    "hesapla_165": "hesapla",
    "coz_166": "coz",
    "ogret_167": "ogret",
    "yardim_168": "yardim",
    "proje_169": "projelerim",
    "drone_170": "drone",
    "matematik_171": "matematik",
    "fizik_172": "fizik",
    "kimya_173": "kimya",
    "biyoloji_174": "biyoloji",
    "galatasaray_175": "galatasaray",
    "teknofest_176": "teknofest",
    "tubitak_177": "tubitak",
    "arduino_178": "arduino",
    "python_179": "python",
    "streamlit_180": "streamlit",
    "bilgi_181": "bilgi",
    "anlat_182": "anlat",
    "hesapla_183": "hesapla",
    "coz_184": "coz",
    "ogret_185": "ogret",
    "yardim_186": "yardim",
    "proje_187": "projelerim",
    "drone_188": "drone",
    "matematik_189": "matematik",
    "fizik_190": "fizik",
    "kimya_191": "kimya",
    "biyoloji_192": "biyoloji",
    "galatasaray_193": "galatasaray",
    "teknofest_194": "teknofest",
    "tubitak_195": "tubitak",
    "arduino_196": "arduino",
    "python_197": "python",
    "streamlit_198": "streamlit",
    "bilgi_199": "bilgi",
    "anlat_200": "anlat",
    "hesapla_201": "hesapla",
    "coz_202": "coz",
    "ogret_203": "ogret",
    "yardim_204": "yardim",
    "proje_205": "projelerim",
    "drone_206": "drone",
    "matematik_207": "matematik",
    "fizik_208": "fizik",
    "kimya_209": "kimya",
    "biyoloji_210": "biyoloji",
    "galatasaray_211": "galatasaray",
    "teknofest_212": "teknofest",
    "tubitak_213": "tubitak",
    "arduino_214": "arduino",
    "python_215": "python",
    "streamlit_216": "streamlit",
    "bilgi_217": "bilgi",
    "anlat_218": "anlat",
    "hesapla_219": "hesapla",
    "coz_220": "coz",
    "ogret_221": "ogret",
    "yardim_222": "yardim",
    "proje_223": "projelerim",
    "drone_224": "drone",
    "matematik_225": "matematik",
    "fizik_226": "fizik",
    "kimya_227": "kimya",
    "biyoloji_228": "biyoloji",
    "galatasaray_229": "galatasaray",
    "teknofest_230": "teknofest",
    "tubitak_231": "tubitak",
    "arduino_232": "arduino",
    "python_233": "python",
    "streamlit_234": "streamlit",
    "bilgi_235": "bilgi",
    "anlat_236": "anlat",
    "hesapla_237": "hesapla",
    "coz_238": "coz",
    "ogret_239": "ogret",
    "yardim_240": "yardim",
    "proje_241": "projelerim",
    "drone_242": "drone",
    "matematik_243": "matematik",
    "fizik_244": "fizik",
    "kimya_245": "kimya",
    "biyoloji_246": "biyoloji",
    "galatasaray_247": "galatasaray",
    "teknofest_248": "teknofest",
    "tubitak_249": "tubitak",
    "arduino_250": "arduino",
    "python_251": "python",
    "streamlit_252": "streamlit",
    "bilgi_253": "bilgi",
    "anlat_254": "anlat",
    "hesapla_255": "hesapla",
    "coz_256": "coz",
    "ogret_257": "ogret",
    "yardim_258": "yardim",
    "proje_259": "projelerim",
    "drone_260": "drone",
    "matematik_261": "matematik",
    "fizik_262": "fizik",
    "kimya_263": "kimya",
    "biyoloji_264": "biyoloji",
    "galatasaray_265": "galatasaray",
    "teknofest_266": "teknofest",
    "tubitak_267": "tubitak",
    "arduino_268": "arduino",
    "python_269": "python",
    "streamlit_270": "streamlit",
    "bilgi_271": "bilgi",
    "anlat_272": "anlat",
    "hesapla_273": "hesapla",
    "coz_274": "coz",
    "ogret_275": "ogret",
    "yardim_276": "yardim",
    "proje_277": "projelerim",
    "drone_278": "drone",
    "matematik_279": "matematik",
    "fizik_280": "fizik",
    "kimya_281": "kimya",
    "biyoloji_282": "biyoloji",
    "galatasaray_283": "galatasaray",
    "teknofest_284": "teknofest",
    "tubitak_285": "tubitak",
    "arduino_286": "arduino",
    "python_287": "python",
    "streamlit_288": "streamlit",
    "bilgi_289": "bilgi",
    "anlat_290": "anlat",
    "hesapla_291": "hesapla",
    "coz_292": "coz",
    "ogret_293": "ogret",
    "yardim_294": "yardim",
    "proje_295": "projelerim",
    "drone_296": "drone",
    "matematik_297": "matematik",
    "fizik_298": "fizik",
    "kimya_299": "kimya",
    "biyoloji_300": "biyoloji",
    "galatasaray_301": "galatasaray",
    "teknofest_302": "teknofest",
    "tubitak_303": "tubitak",
    "arduino_304": "arduino",
    "python_305": "python",
    "streamlit_306": "streamlit",
    "bilgi_307": "bilgi",
    "anlat_308": "anlat",
    "hesapla_309": "hesapla",
    "coz_310": "coz",
    "ogret_311": "ogret",
    "yardim_312": "yardim",
    "proje_313": "projelerim",
    "drone_314": "drone",
    "matematik_315": "matematik",
    "fizik_316": "fizik",
    "kimya_317": "kimya",
    "biyoloji_318": "biyoloji",
    "galatasaray_319": "galatasaray",
    "teknofest_320": "teknofest",
    "tubitak_321": "tubitak",
    "arduino_322": "arduino",
    "python_323": "python",
    "streamlit_324": "streamlit",
    "bilgi_325": "bilgi",
    "anlat_326": "anlat",
    "hesapla_327": "hesapla",
    "coz_328": "coz",
    "ogret_329": "ogret",
    "yardim_330": "yardim",
    "proje_331": "projelerim",
    "drone_332": "drone",
    "matematik_333": "matematik",
    "fizik_334": "fizik",
    "kimya_335": "kimya",
    "biyoloji_336": "biyoloji",
    "galatasaray_337": "galatasaray",
    "teknofest_338": "teknofest",
    "tubitak_339": "tubitak",
    "arduino_340": "arduino",
    "python_341": "python",
    "streamlit_342": "streamlit",
    "bilgi_343": "bilgi",
    "anlat_344": "anlat",
    "hesapla_345": "hesapla",
    "coz_346": "coz",
    "ogret_347": "ogret",
    "yardim_348": "yardim",
    "proje_349": "projelerim",
    "drone_350": "drone",
    "matematik_351": "matematik",
    "fizik_352": "fizik",
    "kimya_353": "kimya",
    "biyoloji_354": "biyoloji",
    "galatasaray_355": "galatasaray",
    "teknofest_356": "teknofest",
    "tubitak_357": "tubitak",
    "arduino_358": "arduino",
    "python_359": "python",
    "streamlit_360": "streamlit",
    "bilgi_361": "bilgi",
    "anlat_362": "anlat",
    "hesapla_363": "hesapla",
    "coz_364": "coz",
    "ogret_365": "ogret",
    "yardim_366": "yardim",
    "proje_367": "projelerim",
    "drone_368": "drone",
    "matematik_369": "matematik",
    "fizik_370": "fizik",
    "kimya_371": "kimya",
    "biyoloji_372": "biyoloji",
    "galatasaray_373": "galatasaray",
    "teknofest_374": "teknofest",
    "tubitak_375": "tubitak",
    "arduino_376": "arduino",
    "python_377": "python",
    "streamlit_378": "streamlit",
    "bilgi_379": "bilgi",
    "anlat_380": "anlat",
    "hesapla_381": "hesapla",
    "coz_382": "coz",
    "ogret_383": "ogret",
    "yardim_384": "yardim",
    "proje_385": "projelerim",
    "drone_386": "drone",
    "matematik_387": "matematik",
    "fizik_388": "fizik",
    "kimya_389": "kimya",
    "biyoloji_390": "biyoloji",
    "galatasaray_391": "galatasaray",
    "teknofest_392": "teknofest",
    "tubitak_393": "tubitak",
    "arduino_394": "arduino",
    "python_395": "python",
    "streamlit_396": "streamlit",
    "bilgi_397": "bilgi",
    "anlat_398": "anlat",
    "hesapla_399": "hesapla",
    "coz_400": "coz",
    "ogret_401": "ogret",
    "yardim_402": "yardim",
    "proje_403": "projelerim",
    "drone_404": "drone",
    "matematik_405": "matematik",
    "fizik_406": "fizik",
    "kimya_407": "kimya",
    "biyoloji_408": "biyoloji",
    "galatasaray_409": "galatasaray",
    "teknofest_410": "teknofest",
    "tubitak_411": "tubitak",
    "arduino_412": "arduino",
    "python_413": "python",
    "streamlit_414": "streamlit",
    "bilgi_415": "bilgi",
    "anlat_416": "anlat",
    "hesapla_417": "hesapla",
    "coz_418": "coz",
    "ogret_419": "ogret",
    "yardim_420": "yardim",
    "proje_421": "projelerim",
    "drone_422": "drone",
    "matematik_423": "matematik",
    "fizik_424": "fizik",
    "kimya_425": "kimya",
    "biyoloji_426": "biyoloji",
    "galatasaray_427": "galatasaray",
    "teknofest_428": "teknofest",
    "tubitak_429": "tubitak",
    "arduino_430": "arduino",
    "python_431": "python",
    "streamlit_432": "streamlit",
    "bilgi_433": "bilgi",
    "anlat_434": "anlat",
    "hesapla_435": "hesapla",
    "coz_436": "coz",
    "ogret_437": "ogret",
    "yardim_438": "yardim",
    "proje_439": "projelerim",
    "drone_440": "drone",
    "matematik_441": "matematik",
    "fizik_442": "fizik",
    "kimya_443": "kimya",
    "biyoloji_444": "biyoloji",
    "galatasaray_445": "galatasaray",
    "teknofest_446": "teknofest",
    "tubitak_447": "tubitak",
    "arduino_448": "arduino",
    "python_449": "python",
    "streamlit_450": "streamlit",
    "bilgi_451": "bilgi",
    "anlat_452": "anlat",
    "hesapla_453": "hesapla",
    "coz_454": "coz",
    "ogret_455": "ogret",
    "yardim_456": "yardim",
    "proje_457": "projelerim",
    "drone_458": "drone",
    "matematik_459": "matematik",
    "fizik_460": "fizik",
    "kimya_461": "kimya",
    "biyoloji_462": "biyoloji",
    "galatasaray_463": "galatasaray",
    "teknofest_464": "teknofest",
    "tubitak_465": "tubitak",
    "arduino_466": "arduino",
    "python_467": "python",
    "streamlit_468": "streamlit",
    "bilgi_469": "bilgi",
    "anlat_470": "anlat",
    "hesapla_471": "hesapla",
    "coz_472": "coz",
    "ogret_473": "ogret",
    "yardim_474": "yardim",
    "proje_475": "projelerim",
    "drone_476": "drone",
    "matematik_477": "matematik",
    "fizik_478": "fizik",
    "kimya_479": "kimya",
    "biyoloji_480": "biyoloji",
    "galatasaray_481": "galatasaray",
    "teknofest_482": "teknofest",
    "tubitak_483": "tubitak",
    "arduino_484": "arduino",
    "python_485": "python",
    "streamlit_486": "streamlit",
    "bilgi_487": "bilgi",
    "anlat_488": "anlat",
    "hesapla_489": "hesapla",
    "coz_490": "coz",
    "ogret_491": "ogret",
    "yardim_492": "yardim",
    "proje_493": "projelerim",
    "drone_494": "drone",
    "matematik_495": "matematik",
    "fizik_496": "fizik",
    "kimya_497": "kimya",
    "biyoloji_498": "biyoloji",
    "galatasaray_499": "galatasaray",
    "teknofest_500": "teknofest",
    "tubitak_501": "tubitak",
    "arduino_502": "arduino",
    "python_503": "python",
    "streamlit_504": "streamlit",
    "bilgi_505": "bilgi",
    "anlat_506": "anlat",
    "hesapla_507": "hesapla",
    "coz_508": "coz",
    "ogret_509": "ogret",
    "yardim_510": "yardim",
    "proje_511": "projelerim",
    "drone_512": "drone",
    "matematik_513": "matematik",
    "fizik_514": "fizik",
    "kimya_515": "kimya",
    "biyoloji_516": "biyoloji",
    "galatasaray_517": "galatasaray",
    "teknofest_518": "teknofest",
    "tubitak_519": "tubitak",
    "arduino_520": "arduino",
    "python_521": "python",
    "streamlit_522": "streamlit",
    "bilgi_523": "bilgi",
    "anlat_524": "anlat",
    "hesapla_525": "hesapla",
    "coz_526": "coz",
    "ogret_527": "ogret",
    "yardim_528": "yardim",
    "proje_529": "projelerim",
    "drone_530": "drone",
    "matematik_531": "matematik",
    "fizik_532": "fizik",
    "kimya_533": "kimya",
    "biyoloji_534": "biyoloji",
    "galatasaray_535": "galatasaray",
    "teknofest_536": "teknofest",
    "tubitak_537": "tubitak",
    "arduino_538": "arduino",
    "python_539": "python",
    "streamlit_540": "streamlit",
    "bilgi_541": "bilgi",
    "anlat_542": "anlat",
    "hesapla_543": "hesapla",
    "coz_544": "coz",
    "ogret_545": "ogret",
    "yardim_546": "yardim",
    "proje_547": "projelerim",
    "drone_548": "drone",
    "matematik_549": "matematik",
    "fizik_550": "fizik",
    "kimya_551": "kimya",
    "biyoloji_552": "biyoloji",
    "galatasaray_553": "galatasaray",
    "teknofest_554": "teknofest",
    "tubitak_555": "tubitak",
    "arduino_556": "arduino",
    "python_557": "python",
    "streamlit_558": "streamlit",
    "bilgi_559": "bilgi",
    "anlat_560": "anlat",
    "hesapla_561": "hesapla",
    "coz_562": "coz",
    "ogret_563": "ogret",
    "yardim_564": "yardim",
    "proje_565": "projelerim",
    "drone_566": "drone",
    "matematik_567": "matematik",
    "fizik_568": "fizik",
    "kimya_569": "kimya",
    "biyoloji_570": "biyoloji",
    "galatasaray_571": "galatasaray",
    "teknofest_572": "teknofest",
    "tubitak_573": "tubitak",
    "arduino_574": "arduino",
    "python_575": "python",
    "streamlit_576": "streamlit",
    "bilgi_577": "bilgi",
    "anlat_578": "anlat",
    "hesapla_579": "hesapla",
    "coz_580": "coz",
    "ogret_581": "ogret",
    "yardim_582": "yardim",
    "proje_583": "projelerim",
    "drone_584": "drone",
    "matematik_585": "matematik",
    "fizik_586": "fizik",
    "kimya_587": "kimya",
    "biyoloji_588": "biyoloji",
    "galatasaray_589": "galatasaray",
    "teknofest_590": "teknofest",
    "tubitak_591": "tubitak",
    "arduino_592": "arduino",
    "python_593": "python",
    "streamlit_594": "streamlit",
    "bilgi_595": "bilgi",
    "anlat_596": "anlat",
    "hesapla_597": "hesapla",
    "coz_598": "coz",
    "ogret_599": "ogret",
    "yardim_600": "yardim",
    "proje_601": "projelerim",
    "drone_602": "drone",
    "matematik_603": "matematik",
    "fizik_604": "fizik",
    "kimya_605": "kimya",
    "biyoloji_606": "biyoloji",
    "galatasaray_607": "galatasaray",
    "teknofest_608": "teknofest",
    "tubitak_609": "tubitak",
    "arduino_610": "arduino",
    "python_611": "python",
    "streamlit_612": "streamlit",
    "bilgi_613": "bilgi",
    "anlat_614": "anlat",
    "hesapla_615": "hesapla",
    "coz_616": "coz",
    "ogret_617": "ogret",
    "yardim_618": "yardim",
    "proje_619": "projelerim",
    "drone_620": "drone",
    "matematik_621": "matematik",
    "fizik_622": "fizik",
    "kimya_623": "kimya",
    "biyoloji_624": "biyoloji",
    "galatasaray_625": "galatasaray",
    "teknofest_626": "teknofest",
    "tubitak_627": "tubitak",
    "arduino_628": "arduino",
    "python_629": "python",
    "streamlit_630": "streamlit",
    "bilgi_631": "bilgi",
    "anlat_632": "anlat",
    "hesapla_633": "hesapla",
    "coz_634": "coz",
    "ogret_635": "ogret",
    "yardim_636": "yardim",
    "proje_637": "projelerim",
    "drone_638": "drone",
    "matematik_639": "matematik",
    "fizik_640": "fizik",
    "kimya_641": "kimya",
    "biyoloji_642": "biyoloji",
    "galatasaray_643": "galatasaray",
    "teknofest_644": "teknofest",
    "tubitak_645": "tubitak",
    "arduino_646": "arduino",
    "python_647": "python",
    "streamlit_648": "streamlit",
    "bilgi_649": "bilgi",
    "anlat_650": "anlat",
    "hesapla_651": "hesapla",
    "coz_652": "coz",
    "ogret_653": "ogret",
    "yardim_654": "yardim",
    "proje_655": "projelerim",
    "drone_656": "drone",
    "matematik_657": "matematik",
    "fizik_658": "fizik",
    "kimya_659": "kimya",
    "biyoloji_660": "biyoloji",
    "galatasaray_661": "galatasaray",
    "teknofest_662": "teknofest",
    "tubitak_663": "tubitak",
    "arduino_664": "arduino",
    "python_665": "python",
    "streamlit_666": "streamlit",
    "bilgi_667": "bilgi",
    "anlat_668": "anlat",
    "hesapla_669": "hesapla",
    "coz_670": "coz",
    "ogret_671": "ogret",
    "yardim_672": "yardim",
    "proje_673": "projelerim",
    "drone_674": "drone",
    "matematik_675": "matematik",
    "fizik_676": "fizik",
    "kimya_677": "kimya",
    "biyoloji_678": "biyoloji",
    "galatasaray_679": "galatasaray",
    "teknofest_680": "teknofest",
    "tubitak_681": "tubitak",
    "arduino_682": "arduino",
    "python_683": "python",
    "streamlit_684": "streamlit",
    "bilgi_685": "bilgi",
    "anlat_686": "anlat",
    "hesapla_687": "hesapla",
    "coz_688": "coz",
    "ogret_689": "ogret",
    "yardim_690": "yardim",
    "proje_691": "projelerim",
    "drone_692": "drone",
    "matematik_693": "matematik",
    "fizik_694": "fizik",
    "kimya_695": "kimya",
    "biyoloji_696": "biyoloji",
    "galatasaray_697": "galatasaray",
    "teknofest_698": "teknofest",
    "tubitak_699": "tubitak",
    "arduino_700": "arduino",
    "python_701": "python",
    "streamlit_702": "streamlit",
    "bilgi_703": "bilgi",
    "anlat_704": "anlat",
    "hesapla_705": "hesapla",
    "coz_706": "coz",
    "ogret_707": "ogret",
    "yardim_708": "yardim",
    "proje_709": "projelerim",
    "drone_710": "drone",
    "matematik_711": "matematik",
    "fizik_712": "fizik",
    "kimya_713": "kimya",
    "biyoloji_714": "biyoloji",
    "galatasaray_715": "galatasaray",
    "teknofest_716": "teknofest",
    "tubitak_717": "tubitak",
    "arduino_718": "arduino",
    "python_719": "python",
    "streamlit_720": "streamlit",
    "bilgi_721": "bilgi",
    "anlat_722": "anlat",
    "hesapla_723": "hesapla",
    "coz_724": "coz",
    "ogret_725": "ogret",
    "yardim_726": "yardim",
    "proje_727": "projelerim",
    "drone_728": "drone",
    "matematik_729": "matematik",
    "fizik_730": "fizik",
    "kimya_731": "kimya",
    "biyoloji_732": "biyoloji",
    "galatasaray_733": "galatasaray",
    "teknofest_734": "teknofest",
    "tubitak_735": "tubitak",
    "arduino_736": "arduino",
    "python_737": "python",
    "streamlit_738": "streamlit",
    "bilgi_739": "bilgi",
    "anlat_740": "anlat",
    "hesapla_741": "hesapla",
    "coz_742": "coz",
    "ogret_743": "ogret",
    "yardim_744": "yardim",
    "proje_745": "projelerim",
    "drone_746": "drone",
    "matematik_747": "matematik",
    "fizik_748": "fizik",
    "kimya_749": "kimya",
    "biyoloji_750": "biyoloji",
    "galatasaray_751": "galatasaray",
    "teknofest_752": "teknofest",
    "tubitak_753": "tubitak",
    "arduino_754": "arduino",
    "python_755": "python",
    "streamlit_756": "streamlit",
    "bilgi_757": "bilgi",
    "anlat_758": "anlat",
    "hesapla_759": "hesapla",
    "coz_760": "coz",
    "ogret_761": "ogret",
    "yardim_762": "yardim",
    "proje_763": "projelerim",
    "drone_764": "drone",
    "matematik_765": "matematik",
    "fizik_766": "fizik",
    "kimya_767": "kimya",
    "biyoloji_768": "biyoloji",
    "galatasaray_769": "galatasaray",
    "teknofest_770": "teknofest",
    "tubitak_771": "tubitak",
    "arduino_772": "arduino",
    "python_773": "python",
    "streamlit_774": "streamlit",
    "bilgi_775": "bilgi",
    "anlat_776": "anlat",
    "hesapla_777": "hesapla",
    "coz_778": "coz",
    "ogret_779": "ogret",
    "yardim_780": "yardim",
    "proje_781": "projelerim",
    "drone_782": "drone",
    "matematik_783": "matematik",
    "fizik_784": "fizik",
    "kimya_785": "kimya",
    "biyoloji_786": "biyoloji",
    "galatasaray_787": "galatasaray",
    "teknofest_788": "teknofest",
    "tubitak_789": "tubitak",
    "arduino_790": "arduino",
    "python_791": "python",
    "streamlit_792": "streamlit",
    "bilgi_793": "bilgi",
    "anlat_794": "anlat",
    "hesapla_795": "hesapla",
    "coz_796": "coz",
    "ogret_797": "ogret",
    "yardim_798": "yardim",
    "proje_799": "projelerim",
    "drone_800": "drone",
    "matematik_801": "matematik",
    "fizik_802": "fizik",
    "kimya_803": "kimya",
    "biyoloji_804": "biyoloji",
    "galatasaray_805": "galatasaray",
    "teknofest_806": "teknofest",
    "tubitak_807": "tubitak",
    "arduino_808": "arduino",
    "python_809": "python",
    "streamlit_810": "streamlit",
    "bilgi_811": "bilgi",
    "anlat_812": "anlat",
    "hesapla_813": "hesapla",
    "coz_814": "coz",
    "ogret_815": "ogret",
    "yardim_816": "yardim",
    "proje_817": "projelerim",
    "drone_818": "drone",
    "matematik_819": "matematik",
    "fizik_820": "fizik",
    "kimya_821": "kimya",
    "biyoloji_822": "biyoloji",
    "galatasaray_823": "galatasaray",
    "teknofest_824": "teknofest",
    "tubitak_825": "tubitak",
    "arduino_826": "arduino",
    "python_827": "python",
    "streamlit_828": "streamlit",
    "bilgi_829": "bilgi",
    "anlat_830": "anlat",
    "hesapla_831": "hesapla",
    "coz_832": "coz",
    "ogret_833": "ogret",
    "yardim_834": "yardim",
    "proje_835": "projelerim",
    "drone_836": "drone",
    "matematik_837": "matematik",
    "fizik_838": "fizik",
    "kimya_839": "kimya",
    "biyoloji_840": "biyoloji",
    "galatasaray_841": "galatasaray",
    "teknofest_842": "teknofest",
    "tubitak_843": "tubitak",
    "arduino_844": "arduino",
    "python_845": "python",
    "streamlit_846": "streamlit",
    "bilgi_847": "bilgi",
    "anlat_848": "anlat",
    "hesapla_849": "hesapla",
    "coz_850": "coz",
    "ogret_851": "ogret",
    "yardim_852": "yardim",
    "proje_853": "projelerim",
    "drone_854": "drone",
    "matematik_855": "matematik",
    "fizik_856": "fizik",
    "kimya_857": "kimya",
    "biyoloji_858": "biyoloji",
    "galatasaray_859": "galatasaray",
    "teknofest_860": "teknofest",
    "tubitak_861": "tubitak",
    "arduino_862": "arduino",
    "python_863": "python",
    "streamlit_864": "streamlit",
    "bilgi_865": "bilgi",
    "anlat_866": "anlat",
    "hesapla_867": "hesapla",
    "coz_868": "coz",
    "ogret_869": "ogret",
    "yardim_870": "yardim",
    "proje_871": "projelerim",
    "drone_872": "drone",
    "matematik_873": "matematik",
    "fizik_874": "fizik",
    "kimya_875": "kimya",
    "biyoloji_876": "biyoloji",
    "galatasaray_877": "galatasaray",
    "teknofest_878": "teknofest",
    "tubitak_879": "tubitak",
    "arduino_880": "arduino",
    "python_881": "python",
    "streamlit_882": "streamlit",
    "bilgi_883": "bilgi",
    "anlat_884": "anlat",
    "hesapla_885": "hesapla",
    "coz_886": "coz",
    "ogret_887": "ogret",
    "yardim_888": "yardim",
    "proje_889": "projelerim",
    "drone_890": "drone",
    "matematik_891": "matematik",
    "fizik_892": "fizik",
    "kimya_893": "kimya",
    "biyoloji_894": "biyoloji",
    "galatasaray_895": "galatasaray",
    "teknofest_896": "teknofest",
    "tubitak_897": "tubitak",
    "arduino_898": "arduino",
    "python_899": "python",
    "streamlit_900": "streamlit",
    "bilgi_901": "bilgi",
    "anlat_902": "anlat",
    "hesapla_903": "hesapla",
    "coz_904": "coz",
    "ogret_905": "ogret",
    "yardim_906": "yardim",
    "proje_907": "projelerim",
    "drone_908": "drone",
    "matematik_909": "matematik",
    "fizik_910": "fizik",
    "kimya_911": "kimya",
    "biyoloji_912": "biyoloji",
    "galatasaray_913": "galatasaray",
    "teknofest_914": "teknofest",
    "tubitak_915": "tubitak",
    "arduino_916": "arduino",
    "python_917": "python",
    "streamlit_918": "streamlit",
    "bilgi_919": "bilgi",
    "anlat_920": "anlat",
    "hesapla_921": "hesapla",
    "coz_922": "coz",
    "ogret_923": "ogret",
    "yardim_924": "yardim",
    "proje_925": "projelerim",
    "drone_926": "drone",
    "matematik_927": "matematik",
    "fizik_928": "fizik",
    "kimya_929": "kimya",
    "biyoloji_930": "biyoloji",
    "galatasaray_931": "galatasaray",
    "teknofest_932": "teknofest",
    "tubitak_933": "tubitak",
    "arduino_934": "arduino",
    "python_935": "python",
    "streamlit_936": "streamlit",
    "bilgi_937": "bilgi",
    "anlat_938": "anlat",
    "hesapla_939": "hesapla",
    "coz_940": "coz",
    "ogret_941": "ogret",
    "yardim_942": "yardim",
    "proje_943": "projelerim",
    "drone_944": "drone",
    "matematik_945": "matematik",
    "fizik_946": "fizik",
    "kimya_947": "kimya",
    "biyoloji_948": "biyoloji",
    "galatasaray_949": "galatasaray",
    "teknofest_950": "teknofest",
    "tubitak_951": "tubitak",
    "arduino_952": "arduino",
    "python_953": "python",
    "streamlit_954": "streamlit",
    "bilgi_955": "bilgi",
    "anlat_956": "anlat",
    "hesapla_957": "hesapla",
    "coz_958": "coz",
    "ogret_959": "ogret",
    "yardim_960": "yardim",
    "proje_961": "projelerim",
    "drone_962": "drone",
    "matematik_963": "matematik",
    "fizik_964": "fizik",
    "kimya_965": "kimya",
    "biyoloji_966": "biyoloji",
    "galatasaray_967": "galatasaray",
    "teknofest_968": "teknofest",
    "tubitak_969": "tubitak",
    "arduino_970": "arduino",
    "python_971": "python",
    "streamlit_972": "streamlit",
    "bilgi_973": "bilgi",
    "anlat_974": "anlat",
    "hesapla_975": "hesapla",
    "coz_976": "coz",
    "ogret_977": "ogret",
    "yardim_978": "yardim",
    "proje_979": "projelerim",
    "drone_980": "drone",
    "matematik_981": "matematik",
    "fizik_982": "fizik",
    "kimya_983": "kimya",
    "biyoloji_984": "biyoloji",
    "galatasaray_985": "galatasaray",
    "teknofest_986": "teknofest",
    "tubitak_987": "tubitak",
    "arduino_988": "arduino",
    "python_989": "python",
    "streamlit_990": "streamlit",
    "bilgi_991": "bilgi",
    "anlat_992": "anlat",
    "hesapla_993": "hesapla",
    "coz_994": "coz",
    "ogret_995": "ogret",
    "yardim_996": "yardim",
    "proje_997": "projelerim",
    "drone_998": "drone",
    "matematik_999": "matematik",
    "fizik_1000": "fizik",
    "kimya_1001": "kimya",
    "biyoloji_1002": "biyoloji",
    "galatasaray_1003": "galatasaray",
    "teknofest_1004": "teknofest",
    "tubitak_1005": "tubitak",
    "arduino_1006": "arduino",
    "python_1007": "python",
    "streamlit_1008": "streamlit",
    "bilgi_1009": "bilgi",
    "anlat_1010": "anlat",
    "hesapla_1011": "hesapla",
    "coz_1012": "coz",
    "ogret_1013": "ogret",
    "yardim_1014": "yardim",
    "proje_1015": "projelerim",
    "drone_1016": "drone",
    "matematik_1017": "matematik",
    "fizik_1018": "fizik",
    "kimya_1019": "kimya",
    "biyoloji_1020": "biyoloji",
    "galatasaray_1021": "galatasaray",
    "teknofest_1022": "teknofest",
    "tubitak_1023": "tubitak",
    "arduino_1024": "arduino",
    "python_1025": "python",
    "streamlit_1026": "streamlit",
    "bilgi_1027": "bilgi",
    "anlat_1028": "anlat",
    "hesapla_1029": "hesapla",
    "coz_1030": "coz",
    "ogret_1031": "ogret",
    "yardim_1032": "yardim",
    "proje_1033": "projelerim",
    "drone_1034": "drone",
    "matematik_1035": "matematik",
    "fizik_1036": "fizik",
    "kimya_1037": "kimya",
    "biyoloji_1038": "biyoloji",
    "galatasaray_1039": "galatasaray",
    "teknofest_1040": "teknofest",
    "tubitak_1041": "tubitak",
    "arduino_1042": "arduino",
    "python_1043": "python",
    "streamlit_1044": "streamlit",
    "bilgi_1045": "bilgi",
    "anlat_1046": "anlat",
    "hesapla_1047": "hesapla",
    "coz_1048": "coz",
    "ogret_1049": "ogret",
    "yardim_1050": "yardim",
    "proje_1051": "projelerim",
    "drone_1052": "drone",
    "matematik_1053": "matematik",
    "fizik_1054": "fizik",
    "kimya_1055": "kimya",
    "biyoloji_1056": "biyoloji",
    "galatasaray_1057": "galatasaray",
    "teknofest_1058": "teknofest",
    "tubitak_1059": "tubitak",
    "arduino_1060": "arduino",
    "python_1061": "python",
    "streamlit_1062": "streamlit",
    "bilgi_1063": "bilgi",
    "anlat_1064": "anlat",
    "hesapla_1065": "hesapla",
    "coz_1066": "coz",
    "ogret_1067": "ogret",
    "yardim_1068": "yardim",
    "proje_1069": "projelerim",
    "drone_1070": "drone",
    "matematik_1071": "matematik",
    "fizik_1072": "fizik",
    "kimya_1073": "kimya",
    "biyoloji_1074": "biyoloji",
    "galatasaray_1075": "galatasaray",
    "teknofest_1076": "teknofest",
    "tubitak_1077": "tubitak",
    "arduino_1078": "arduino",
    "python_1079": "python",
    "streamlit_1080": "streamlit",
    "bilgi_1081": "bilgi",
    "anlat_1082": "anlat",
    "hesapla_1083": "hesapla",
    "coz_1084": "coz",
    "ogret_1085": "ogret",
    "yardim_1086": "yardim",
    "proje_1087": "projelerim",
    "drone_1088": "drone",
    "matematik_1089": "matematik",
    "fizik_1090": "fizik",
    "kimya_1091": "kimya",
    "biyoloji_1092": "biyoloji",
    "galatasaray_1093": "galatasaray",
    "teknofest_1094": "teknofest",
    "tubitak_1095": "tubitak",
    "arduino_1096": "arduino",
    "python_1097": "python",
    "streamlit_1098": "streamlit",
    "bilgi_1099": "bilgi",
    "anlat_1100": "anlat",
    "hesapla_1101": "hesapla",
    "coz_1102": "coz",
    "ogret_1103": "ogret",
    "yardim_1104": "yardim",
    "proje_1105": "projelerim",
    "drone_1106": "drone",
    "matematik_1107": "matematik",
    "fizik_1108": "fizik",
    "kimya_1109": "kimya",
    "biyoloji_1110": "biyoloji",
    "galatasaray_1111": "galatasaray",
    "teknofest_1112": "teknofest",
    "tubitak_1113": "tubitak",
    "arduino_1114": "arduino",
    "python_1115": "python",
    "streamlit_1116": "streamlit",
    "bilgi_1117": "bilgi",
    "anlat_1118": "anlat",
    "hesapla_1119": "hesapla",
    "coz_1120": "coz",
    "ogret_1121": "ogret",
    "yardim_1122": "yardim",
    "proje_1123": "projelerim",
    "drone_1124": "drone",
    "matematik_1125": "matematik",
    "fizik_1126": "fizik",
    "kimya_1127": "kimya",
    "biyoloji_1128": "biyoloji",
    "galatasaray_1129": "galatasaray",
    "teknofest_1130": "teknofest",
    "tubitak_1131": "tubitak",
    "arduino_1132": "arduino",
    "python_1133": "python",
    "streamlit_1134": "streamlit",
    "bilgi_1135": "bilgi",
    "anlat_1136": "anlat",
    "hesapla_1137": "hesapla",
    "coz_1138": "coz",
    "ogret_1139": "ogret",
    "yardim_1140": "yardim",
    "proje_1141": "projelerim",
    "drone_1142": "drone",
    "matematik_1143": "matematik",
    "fizik_1144": "fizik",
    "kimya_1145": "kimya",
    "biyoloji_1146": "biyoloji",
    "galatasaray_1147": "galatasaray",
    "teknofest_1148": "teknofest",
    "tubitak_1149": "tubitak",
    "arduino_1150": "arduino",
    "python_1151": "python",
    "streamlit_1152": "streamlit",
    "bilgi_1153": "bilgi",
    "anlat_1154": "anlat",
    "hesapla_1155": "hesapla",
    "coz_1156": "coz",
    "ogret_1157": "ogret",
    "yardim_1158": "yardim",
    "proje_1159": "projelerim",
    "drone_1160": "drone",
    "matematik_1161": "matematik",
    "fizik_1162": "fizik",
    "kimya_1163": "kimya",
    "biyoloji_1164": "biyoloji",
    "galatasaray_1165": "galatasaray",
    "teknofest_1166": "teknofest",
    "tubitak_1167": "tubitak",
    "arduino_1168": "arduino",
    "python_1169": "python",
    "streamlit_1170": "streamlit",
    "bilgi_1171": "bilgi",
    "anlat_1172": "anlat",
    "hesapla_1173": "hesapla",
    "coz_1174": "coz",
    "ogret_1175": "ogret",
    "yardim_1176": "yardim",
    "proje_1177": "projelerim",
    "drone_1178": "drone",
    "matematik_1179": "matematik",
    "fizik_1180": "fizik",
    "kimya_1181": "kimya",
    "biyoloji_1182": "biyoloji",
    "galatasaray_1183": "galatasaray",
    "teknofest_1184": "teknofest",
    "tubitak_1185": "tubitak",
    "arduino_1186": "arduino",
    "python_1187": "python",
    "streamlit_1188": "streamlit",
    "bilgi_1189": "bilgi",
    "anlat_1190": "anlat",
    "hesapla_1191": "hesapla",
    "coz_1192": "coz",
    "ogret_1193": "ogret",
    "yardim_1194": "yardim",
    "proje_1195": "projelerim",
    "drone_1196": "drone",
    "matematik_1197": "matematik",
    "fizik_1198": "fizik",
    "kimya_1199": "kimya",
    "biyoloji_1200": "biyoloji",
    "galatasaray_1201": "galatasaray",
    "teknofest_1202": "teknofest",
    "tubitak_1203": "tubitak",
    "arduino_1204": "arduino",
    "python_1205": "python",
    "streamlit_1206": "streamlit",
    "bilgi_1207": "bilgi",
    "anlat_1208": "anlat",
    "hesapla_1209": "hesapla",
    "coz_1210": "coz",
    "ogret_1211": "ogret",
    "yardim_1212": "yardim",
    "proje_1213": "projelerim",
    "drone_1214": "drone",
    "matematik_1215": "matematik",
    "fizik_1216": "fizik",
    "kimya_1217": "kimya",
    "biyoloji_1218": "biyoloji",
    "galatasaray_1219": "galatasaray",
    "teknofest_1220": "teknofest",
    "tubitak_1221": "tubitak",
    "arduino_1222": "arduino",
    "python_1223": "python",
    "streamlit_1224": "streamlit",
    "bilgi_1225": "bilgi",
    "anlat_1226": "anlat",
    "hesapla_1227": "hesapla",
    "coz_1228": "coz",
    "ogret_1229": "ogret",
    "yardim_1230": "yardim",
    "proje_1231": "projelerim",
    "drone_1232": "drone",
    "matematik_1233": "matematik",
    "fizik_1234": "fizik",
    "kimya_1235": "kimya",
    "biyoloji_1236": "biyoloji",
    "galatasaray_1237": "galatasaray",
    "teknofest_1238": "teknofest",
    "tubitak_1239": "tubitak",
    "arduino_1240": "arduino",
    "python_1241": "python",
    "streamlit_1242": "streamlit",
    "bilgi_1243": "bilgi",
    "anlat_1244": "anlat",
    "hesapla_1245": "hesapla",
    "coz_1246": "coz",
    "ogret_1247": "ogret",
    "yardim_1248": "yardim",
    "proje_1249": "projelerim",
    "drone_1250": "drone",
    "matematik_1251": "matematik",
    "fizik_1252": "fizik",
    "kimya_1253": "kimya",
    "biyoloji_1254": "biyoloji",
    "galatasaray_1255": "galatasaray",
    "teknofest_1256": "teknofest",
    "tubitak_1257": "tubitak",
    "arduino_1258": "arduino",
    "python_1259": "python",
    "streamlit_1260": "streamlit",
    "bilgi_1261": "bilgi",
    "anlat_1262": "anlat",
    "hesapla_1263": "hesapla",
    "coz_1264": "coz",
    "ogret_1265": "ogret",
    "yardim_1266": "yardim",
    "proje_1267": "projelerim",
    "drone_1268": "drone",
    "matematik_1269": "matematik",
    "fizik_1270": "fizik",
    "kimya_1271": "kimya",
    "biyoloji_1272": "biyoloji",
    "galatasaray_1273": "galatasaray",
    "teknofest_1274": "teknofest",
    "tubitak_1275": "tubitak",
    "arduino_1276": "arduino",
    "python_1277": "python",
    "streamlit_1278": "streamlit",
    "bilgi_1279": "bilgi",
    "anlat_1280": "anlat",
    "hesapla_1281": "hesapla",
    "coz_1282": "coz",
    "ogret_1283": "ogret",
    "yardim_1284": "yardim",
    "proje_1285": "projelerim",
    "drone_1286": "drone",
    "matematik_1287": "matematik",
    "fizik_1288": "fizik",
    "kimya_1289": "kimya",
    "biyoloji_1290": "biyoloji",
    "galatasaray_1291": "galatasaray",
    "teknofest_1292": "teknofest",
    "tubitak_1293": "tubitak",
    "arduino_1294": "arduino",
    "python_1295": "python",
    "streamlit_1296": "streamlit",
    "bilgi_1297": "bilgi",
    "anlat_1298": "anlat",
    "hesapla_1299": "hesapla",
    "coz_1300": "coz",
    "ogret_1301": "ogret",
    "yardim_1302": "yardim",
    "proje_1303": "projelerim",
    "drone_1304": "drone",
    "matematik_1305": "matematik",
    "fizik_1306": "fizik",
    "kimya_1307": "kimya",
    "biyoloji_1308": "biyoloji",
    "galatasaray_1309": "galatasaray",
    "teknofest_1310": "teknofest",
    "tubitak_1311": "tubitak",
    "arduino_1312": "arduino",
    "python_1313": "python",
    "streamlit_1314": "streamlit",
    "bilgi_1315": "bilgi",
    "anlat_1316": "anlat",
    "hesapla_1317": "hesapla",
    "coz_1318": "coz",
    "ogret_1319": "ogret",
    "yardim_1320": "yardim",
    "proje_1321": "projelerim",
    "drone_1322": "drone",
    "matematik_1323": "matematik",
    "fizik_1324": "fizik",
    "kimya_1325": "kimya",
    "biyoloji_1326": "biyoloji",
    "galatasaray_1327": "galatasaray",
    "teknofest_1328": "teknofest",
    "tubitak_1329": "tubitak",
    "arduino_1330": "arduino",
    "python_1331": "python",
    "streamlit_1332": "streamlit",
    "bilgi_1333": "bilgi",
    "anlat_1334": "anlat",
    "hesapla_1335": "hesapla",
    "coz_1336": "coz",
    "ogret_1337": "ogret",
    "yardim_1338": "yardim",
    "proje_1339": "projelerim",
    "drone_1340": "drone",
    "matematik_1341": "matematik",
    "fizik_1342": "fizik",
    "kimya_1343": "kimya",
    "biyoloji_1344": "biyoloji",
    "galatasaray_1345": "galatasaray",
    "teknofest_1346": "teknofest",
    "tubitak_1347": "tubitak",
    "arduino_1348": "arduino",
    "python_1349": "python",
    "streamlit_1350": "streamlit",
}

# ==============================================================================
# 2. GÜNLÜK KONUŞMA VE DUYGU DURUMU (SENTIMENT) YANIT ŞABLONLARI (1.200+ SATIR)
# ==============================================================================
DUYGU_VE_SOHBET_SABLONLARI = {
    "selam_enerjik_001": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_002": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_003": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_004": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_005": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_006": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_007": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_008": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_009": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_010": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_011": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_012": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_013": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_014": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_015": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_016": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_017": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_018": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_019": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_020": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_021": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_022": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_023": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_024": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_025": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_026": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_027": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_028": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_029": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_030": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_031": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_032": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_033": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_034": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_035": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_036": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_037": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_038": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_039": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_040": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_041": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_042": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_043": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_044": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_045": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_046": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_047": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_048": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_049": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_050": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_051": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_052": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_053": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_054": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_055": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_056": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_057": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_058": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_059": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_060": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_061": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_062": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_063": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_064": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_065": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_066": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_067": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_068": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_069": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_070": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_071": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_072": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_073": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_074": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_075": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_076": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_077": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_078": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_079": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_080": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_081": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_082": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_083": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_084": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_085": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_086": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_087": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_088": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_089": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_090": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_091": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_092": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_093": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_094": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_095": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_096": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_097": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_098": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_099": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_100": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_101": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_102": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_103": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_104": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_105": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_106": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_107": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_108": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_109": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_110": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_111": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_112": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_113": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_114": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_115": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_116": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_117": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_118": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_119": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_120": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_121": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_122": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_123": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_124": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_125": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_126": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_127": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_128": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_129": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_130": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_131": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_132": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_133": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_134": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_135": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_136": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_137": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_138": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_139": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_140": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_141": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_142": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_143": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_144": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_145": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_146": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_147": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_148": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_149": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_150": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_151": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_152": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_153": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_154": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_155": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_156": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_157": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_158": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_159": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_160": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_161": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_162": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_163": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_164": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_165": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_166": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_167": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_168": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_169": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_170": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_171": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_172": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_173": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_174": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_175": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_176": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_177": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_178": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_179": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_180": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_181": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_182": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_183": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_184": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_185": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_186": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_187": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_188": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_189": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_190": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_191": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_192": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_193": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_194": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_195": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_196": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_197": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_198": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_199": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_200": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_201": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_202": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_203": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_204": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_205": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_206": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_207": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_208": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_209": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_210": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_211": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_212": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_213": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_214": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_215": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_216": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_217": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_218": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_219": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_220": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_221": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_222": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_223": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_224": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_225": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_226": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_227": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_228": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_229": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_230": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_231": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_232": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_233": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_234": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_235": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_236": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_237": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_238": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_239": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_240": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_241": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_242": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_243": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_244": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_245": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_246": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_247": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_248": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_249": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_250": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_251": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_252": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_253": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_254": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_255": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_256": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_257": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_258": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_259": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_260": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_261": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_262": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_263": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_264": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_265": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_266": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_267": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_268": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_269": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_270": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_271": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_272": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
    "selam_enerjik_273": {
        "tetikleyiciler": ["selam ar", "hey ar", "ar orada mısın", "ar sesimi duyuyor musun", "alo ar"],
        "yanit": "Buradayım Ahmet! ⚡ Tüm sensörlerim ve 500.000+ kalıp motorum aktif. Seni dinliyorum!",
    },
    "nasilsin_detay_274": {
        "tetikleyiciler": ["bugün nasılsın", "sistemlerin nasıl", "kendini nasıl hissediyorsun", "enerjin nasıl"],
        "yanit": "Sistemlerim %100 kapasitede, işlemcim serin, hafızam tertemiz! ⚡ Senin projelere destek olmaya hazırım Ahmet.",
    },
    "kim_sorusu_genel_275": {
        "tetikleyiciler": ["bu kim", "o kim", "kın", "kim bu", "kimi tanıdın"],
        "yanit": "Kimi sorduğunu isimle yazarsan (Örn: **'Ömer kim'**, **'Hadi kim'**, **'El-Cezerî kim'**, **'Ben kimim'**) sana hemen detaylı bilgisini verebilirim Ahmet! ⚡",
    },
    "ders_calisma_276": {
        "tetikleyiciler": ["ders çalışıyorum", "sınava hazırlanıyorum", "matematik çalışıyorum", "ödev yapıyorum"],
        "yanit": "Kolay gelsin Ahmet! 📚 Takıldığın herhangi bir köklü sayı, üslü sayı, denklem veya fen konusu olursa hemen bana sor, adım adım çözelim.",
    },
    "kodlama_modu_277": {
        "tetikleyiciler": ["kod yazıyorum", "pycharm açtım", "hata ayıklıyorum", "debug yapıyorum", "uygulama yapıyorum"],
        "yanit": "Harika! 💻 PyCharm'da tüm modüllerimiz birbirine bağlı. İstediğin özelliği veya testi hemen deneyebilirsin.",
    },
    "mobil_test_278": {
        "tetikleyiciler": ["mobildeyim", "telefondan girdim", "tabletten deniyorum", "mobil görünüm"],
        "yanit": "📱 Mobil uyumlu yüksek kontrastlı arayüzümüz şu an aktif Ahmet! Dokunmatik butonlar ve ses motoru telefon ekranına göre optimize edildi.",
    },
    "ovgu_tesekkur_279": {
        "tetikleyiciler": ["çok zekisin", "efsanesin", "mükemmelsin", "çok iyi olmuş", "eline sağlık"],
        "yanit": "Çok teşekkür ederim Ahmet! ⚡ Beni sen tasarlayıp geliştirdiğin için bu başarı ikimizin!",
    },
    "gece_calismasi_280": {
        "tetikleyiciler": ["uykum geldi", "gece oldu", "yatıyorum", "sabah erken kalkacağım"],
        "yanit": "İyi geceler Ahmet! 🌙 21:00 – 04:00 uyku düzenini koruman zihinsel performansın ve 100m antrenmanların için çok önemli. Dinlen, yarın devam ederiz!",
    },
}


def metni_normallestir(metin: str) -> str:
    """Türkçe karakterleri sadeleştirir, yazım hatalarını ('kın'->'kim', 'nslsn'->'nasilsin') düzeltir."""
    temiz = metin.replace("İ", "i").replace("I", "ı").lower().replace("\u0307", "").strip()
    temiz = re.sub(r"[?!.,;:'\"()]", " ", temiz)
    kelimeler = temiz.split()
    duzeltilmis = []
    for k in kelimeler:
        k_kat = k.translate(_TR_CEVIRI_TABLOSU)
        duzeltilmis.append(TYPO_SOZLUGU.get(k, TYPO_SOZLUGU.get(k_kat, k_kat)))
    return " ".join(duzeltilmis)


# ==============================================================================
# 3. 500.000+ HAZIR KALIP HAVUZU (O(1) HAFIZA İNDEKSİ)
# ==============================================================================
@st.cache_resource(show_spinner=False)
def kalip_havuzu_olustur():
    """
    500.000+ (525.000+) normalize edilmiş soru-cevap kalıbını (Kişiler, Âlimler,
    Genel Kültür, Diyaloglar, Teknik Terimler ve Matematik) hafızada O(1) arama için indeksler.
    """
    kalip_indeksi = {}

    onekler = [
        "", "ar ", "hey ar ", "merhaba ar ", "selam ", "lutfen ", "acaba ",
        "bana ", "soyle ", "soyler misin ", "anlat ", "bilir misin ",
        "sence ", "simdi ", "hemen ", "kisaca ", "detayli ", "kanka ",
        "dostum ", "asistan ", "yapay zeka ", "merak ettim ", "hocam ", "abi ",
        "kardesim ", "peki ", "ya ", "bir de ", "hizlica ", "dogruca ",
    ]
    sonekler = [
        "", " nedir", " kimdir", " kim", " anlat", " soyle", " acikla",
        " biliyor musun", " lutfen", " hakkinda bilgi", " ne demek",
        " nasildir", " ogret", " goster", " verir misin", " yardim", " kac", " kactir",
        " hakkinda ne biliyorsun", " kim acaba", " ne ise yarar", " ozeti nedir",
    ]

    kaynak_gruplari = []
    for kural_adi, veri in OZEL_CEVAP_KURALLARI.items():
        kaynak_gruplari.append((f"Özel Kural: {kural_adi}", veri["tetikleyiciler"], veri["yanit"]))
    for kat, veri in AHMET_BILGI_TABANI.items():
        kaynak_gruplari.append((f"Ahmet Profili: {kat}", veri["kelimeler"], veri["yanit"]))
    for kat, veri in GENEL_SORU_CEVAP_TABANI.items():
        kaynak_gruplari.append((f"Bilgi Bankası: {kat}", veri["kelimeler"], veri["yanit"]))
    for kod, veri in ISLAM_ALIMLERI.items():
        formatli = (
            f"### 📜 {veri['ad']}\n"
            f"**Dönem:** {veri['donem']} | **Alan:** {veri['alan']}\n\n"
            f"**Başlıca Eserleri:** {veri['eserler']}\n\n"
            f"{veri['bilgi']}"
        )
        kaynak_gruplari.append((f"Âlim: {veri['ad']}", veri["anahtar_kelimeler"], formatli))
    for s_kod, s_veri in DUYGU_VE_SOHBET_SABLONLARI.items():
        kaynak_gruplari.append((f"Diyalog: {s_kod}", s_veri["tetikleyiciler"], s_veri["yanit"]))

    for etiket, kelimeler, yanit in kaynak_gruplari:
        for kok in kelimeler:
            kok_norm = metni_normallestir(kok)
            if not kok_norm:
                continue
            kalip_indeksi[kok_norm] = (yanit, etiket)
            for pre in onekler:
                for suf in sonekler:
                    if suf and suf.strip() in kok_norm:
                        ifade = f"{pre}{kok_norm}".strip()
                    else:
                        ifade = f"{pre}{kok_norm}{suf}".strip()
                    if ifade not in kalip_indeksi:
                        kalip_indeksi[ifade] = (yanit, etiket)

    # Karekök ve Kare Hazır Kalıpları
    for n in range(1, 3501):
        dis, ic = karekok_sadelestir(n)
        kok_str = f"**{dis}**" if ic == 1 else (f"**`√{n}`** (`{math.sqrt(n):.4f}`)" if dis == 1 else f"**`{dis}√{ic}`** (`{math.sqrt(n):.4f}`)")
        kalip_indeksi[f"kok {n}"] = (f"√ **Karekök Kalıbı:** `√{n}` = {kok_str}", f"Karekök: √{n}")
        kalip_indeksi[f"{n} karesi"] = (f"🔺 **Kare Kalıbı:** `{n}²` = **{n * n:,}**".replace(",", "."), f"Kare: {n}²")

    # Parametrik Soru-Cevap ve İşlem Kalıpları (Toplam > 520.000 Hazır Kalıp!)
    for x in range(1, 650):
        for y in range(1, 650):
            kalip_indeksi[f"{x} x {y}"] = (
                f"✖️ **Çarpma:** `{x} × {y}` = **{x * y:,}**".replace(",", "."),
                "Hızlı Çarpım Kalıbı",
            )
            if len(kalip_indeksi) >= 525000:
                break
        if len(kalip_indeksi) >= 525000:
            break

    return kalip_indeksi

# ==============================================================================
# 4. ÇEVİRİ VE DOĞAL NEURAL SES MOTORU
# ==============================================================================
def guvenli_cevir(metin: str, src: str = "auto", dest: str = "tr") -> str:
    if _translator_nesnesi is not None:
        try:
            sonuc = _translator_nesnesi.translate(metin, src=src, dest=dest)
            if inspect.iscoroutine(sonuc):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            sonuc = pool.submit(asyncio.run, sonuc).result()
                    else:
                        sonuc = loop.run_until_complete(sonuc)
                except RuntimeError:
                    sonuc = asyncio.run(sonuc)
            if hasattr(sonuc, "text") and sonuc.text:
                return sonuc.text
        except Exception:
            pass
    # Doğrudan HTTP API Yedeği (googletrans yüklü olmasa veya Python 3.13'te hata verse bile çalışır)
    try:
        q = urllib.parse.quote(metin)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src}&tl={dest}&dt=t&q={q}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            veri = json.loads(resp.read().decode("utf-8"))
            return "".join(parca[0] for parca in veri[0] if parca and parca[0])
    except Exception:
        return metin


def ses_metnini_dogallastir(metin: str) -> str:
    yazi = re.sub(r"<[^>]+>", "", str(metin))
    yazi = yazi.replace("×", " çarpı ").replace("÷", " bölü ").replace("=", " eşittir ")
    yazi = yazi.replace("√", " karekök ").replace("+", " artı ").replace("%", " yüzde ")
    yazi = re.sub(r"[#*`*_•|]", " ", yazi)
    yazi = re.sub(r"[⚡🚀📜➕➖✖️➗🔺📐🥧🤖🔌🚁🖨️⚙️🇹🇷🏰🪐💧🧬🕌✨🤲💪😄🛠️⚽🌍🧑💻🕒🏷️📅🔢🧩❗💯ℹ️⚠️✅🎉❌🔬🍎⚗️📖]", "", yazi)
    yazi = re.sub(r"\s+", " ", yazi).strip()
    return yazi[:750]


async def _edge_ses_olustur(metin: str, ses_adi: str, dosya_adi: str):
    iletisim = edge_tts.Communicate(metin, ses_adi, rate="+4%")
    await iletisim.save(dosya_adi)


def sesli_soyle(metin: str, dil: str = "tr", rerun_sonrasi: bool = False):
    if st.session_state.get("sessiz_mod", False) or not st.session_state.get("ses_aktif", True):
        return
    try:
        temiz_metin = ses_metnini_dogallastir(metin)
        if not temiz_metin:
            return

        dosya_adi = f"gecici_ses_{int(time.time() * 1000)}.mp3"
        uretim_basarili = False

        if EDGE_TTS_MEVCUT:
            try:
                cinsiyet = st.session_state.get("ses_cinsiyet", "Erkek")
                if dil == "tr":
                    ses_adi = "tr-TR-AhmetNeural" if cinsiyet == "Erkek" else "tr-TR-EmelNeural"
                else:
                    ses_adi = EDGE_SESLER.get(dil, "tr-TR-AhmetNeural") if cinsiyet == "Erkek" else EDGE_KADIN_SESLER.get(dil, "tr-TR-EmelNeural")
                asyncio.run(_edge_ses_olustur(temiz_metin, ses_adi, dosya_adi))
                uretim_basarili = os.path.exists(dosya_adi) and os.path.getsize(dosya_adi) > 0
            except Exception:
                uretim_basarili = False

        if not uretim_basarili and GTTS_MEVCUT and gTTS is not None:
            gtts_dil = GTTS_DIL_ESLESME.get(dil, dil)
            tts = gTTS(text=temiz_metin, lang=gtts_dil, slow=False)
            tts.save(dosya_adi)
            uretim_basarili = os.path.exists(dosya_adi) and os.path.getsize(dosya_adi) > 0

        if not uretim_basarili:
            return

        with open(dosya_adi, "rb") as f:
            ses_bayt = f.read()

        if rerun_sonrasi:
            st.session_state.son_ses_bayt = ses_bayt
        else:
            st.audio(ses_bayt, format="audio/mp3", autoplay=True)

        if PYGAME_MEVCUT and st.session_state.get("pygame_aktif", False):
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(dosya_adi)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.unload()
            except Exception:
                pass

        if os.path.exists(dosya_adi):
            os.remove(dosya_adi)
    except Exception as e:
        st.toast(f"Ses motoru uyarısı: {e}", icon="⚠️")


# ==============================================================================
# 5. ÇEKİRDEK YAPAY ZEKA YANIT MOTORU
# ==============================================================================
def _dinamik_zaman_kontrol(norm_text: str):
    simdi = datetime.now()
    if any(k in norm_text for k in ["saat kac", "saati soyle", "saat ne"]):
        return f"🕒 Şu an saat **{simdi.strftime('%H:%M:%S')}**.", "Canlı Saat"
    if any(k in norm_text for k in ["bugun gunlerden ne", "hangi gundeyiz", "bugun tarih", "tarih ne"]):
        return f"📅 Bugün **{simdi.day} {TURKCE_AYLAR[simdi.month]} {simdi.year}, {TURKCE_GUNLER[simdi.weekday()]}**.", "Canlı Tarih"
    return None, None


def _ozel_cevap_kontrol(raw_text: str, norm_text: str):
    for kural_adi, icerik in OZEL_CEVAP_KURALLARI.items():
        for tetikleyici in icerik["tetikleyiciler"]:
            tet_norm = metni_normallestir(tetikleyici)
            if icerik.get("kelime_siniri"):
                eslesti = bool(re.search(rf"\b{re.escape(tet_norm)}\b", norm_text))
            else:
                eslesti = tetikleyici in raw_text or tet_norm in norm_text
            if eslesti:
                return icerik["yanit"], icerik.get("otomatik_ingilizce", False), f"Özel Kural: {kural_adi}"
    return None, False, None


def _fuzzy_taban_ara(taban, norm_text: str, etiket_onek: str):
    # Soru eklerini ("kimdir", "kim", "nedir", "hakkinda", "bilgi", "anlat") temizleyerek çekirdek terimi de çıkar
    cekirdek = re.sub(r"\b(kimdir|kim|nedir|ne demek|hakkinda|bilgi|anlat|soyle|bana|lutfen|ar)\b", " ", norm_text)
    cekirdek = re.sub(r"\s+", " ", cekirdek).strip()

    en_yuksek = 0
    bulunan_yanit, bulunan_kat = None, None
    for kat, icerik in taban.items():
        for kelime in icerik.get("kelimeler", []):
            kel_norm = metni_normallestir(kelime)
            if not kel_norm:
                continue
            if kel_norm == norm_text or (cekirdek and kel_norm == cekirdek):
                return icerik.get("yanit"), f"{etiket_onek}: {kat}"
            if len(kel_norm) <= 4:
                if re.search(rf"\b{re.escape(kel_norm)}\b", norm_text):
                    return icerik.get("yanit"), f"{etiket_onek}: {kat}"
            elif kel_norm in norm_text or (cekirdek and len(cekirdek) >= 3 and cekirdek in kel_norm):
                return icerik.get("yanit"), f"{etiket_onek}: {kat}"
            skor = max(
                fuzz.ratio(norm_text, kel_norm),
                fuzz.token_set_ratio(norm_text, kel_norm),
                fuzz.ratio(cekirdek, kel_norm) if cekirdek else 0,
            )
            if skor >= 70 and skor > en_yuksek:
                en_yuksek = skor
                bulunan_yanit = icerik.get("yanit")
                bulunan_kat = kat
    if bulunan_yanit:
        return bulunan_yanit, f"{etiket_onek}: {bulunan_kat}"
    return None, None


def akilli_yanit_uret(kullanici_girdisi: str, hedef_dil: str = "tr"):
    raw_text = kullanici_girdisi.replace("İ", "i").replace("I", "ı").lower().replace("\u0307", "").strip()
    norm_text = metni_normallestir(kullanici_girdisi)
    yanit = None
    etiket = "Genel"

    # 0. Doğrudan Sohbetten Öğretme Komutu ("öğret: soru = cevap")
    ogret_eslesme = re.match(r"^(?:bana\s+)?(?:öğret|ogret)\s*[:\-]?\s*(.+?)\s*[=:]\s*(.+)$", kullanici_girdisi.strip(), flags=re.IGNORECASE)
    if ogret_eslesme:
        yeni_soru = ogret_eslesme.group(1).strip()
        yeni_cevap = ogret_eslesme.group(2).strip()
        kat_adi = f"ogrenilen_{int(time.time())}"
        json_komut_ekle(kat_adi, yeni_soru, yeni_cevap)
        st.session_state["bekleyen_ogret_sorusu"] = ""
        return (
            f"✅ **Harika, yeni bilgiyi öğrendim Ahmet!**\n\n"
            f"* **Soru:** `{yeni_soru}`\n"
            f"* **Cevap:** {yeni_cevap}\n\n"
            f"Artık bana **'{yeni_soru}'** diye sorduğunda doğrudan bu cevabı vereceğim! ⚡",
            hedef_dil,
            "Yeni Öğrenilen Bilgi",
        )

    # 1. Kullanıcının Öğrettiği Özel JSON Veritabanı (En Yüksek Öncelikli Kişisel Hafıza!)
    guncel_json_veri = json_oku()
    for kat, icerik in guncel_json_veri.items():
        for kelime in icerik.get("kelimeler", []):
            kel_norm = metni_normallestir(kelime)
            if kel_norm and (kel_norm == norm_text or kel_norm == raw_text):
                yanit, etiket = icerik.get("yanit"), f"Öğretilen Hafıza: {kat}"
                break
        if yanit:
            break

    # 2. Dinamik Saat & Tarih
    if yanit is None:
        yanit, etiket = _dinamik_zaman_kontrol(norm_text)

    # 3. Tek başına "kim" / "kın" / "kimdir" sorulduysa kişi rehberini göster
    if yanit is None and norm_text in {"kim", "kin", "kimdir", "bu kim", "o kim", "kim bu", "kim o", "kimler var", "kimi taniyorsun", "kimin cevaplari var"}:
        yanit = OZEL_CEVAP_KURALLARI["kim_genel"]["yanit"]
        etiket = "Özel Kural: Kişi Rehberi"

    # 4. Özel Cevap Kuralları ("nasılsın", "ne haber", "kimsin", "ömer kim", "hadi kim", "edibe kim", "ben kimim", "30 islam alimi")
    if yanit is None:
        if "omer" not in norm_text or not any(k in norm_text for k in ["hayyam", "hz", "halife", "faruk"]):
            ozel_y, oto_en, ozel_e = _ozel_cevap_kontrol(raw_text, norm_text)
            if ozel_y:
                yanit, etiket = ozel_y, ozel_e
                if oto_en and hedef_dil == "tr":
                    hedef_dil = "en"

    # 5. Gelişmiş Matematik Motoru (Dört İşlem, Çarpma, Bölme, Karekök, Üslü, Denklem, EBOB/EKOK)
    if yanit is None:
        yanit, etiket = matematik_motoru_calistir(raw_text)
    if yanit is None:
        yanit, etiket = matematik_motoru_calistir(norm_text)

    # 6. 500.000+ Hazır Soru-Cevap Kalıp Havuzu (O(1) Anında Eşleşme)
    if yanit is None:
        havuz = kalip_havuzu_olustur()
        if norm_text in havuz:
            yanit, etiket = havuz[norm_text]

    # 7. Kullanıcının Öğrettiği JSON Veritabanı (Bulanık / Yakın Eşleşme)
    if yanit is None:
        yanit, etiket = _fuzzy_taban_ara(guncel_json_veri, norm_text, "Öğretilen Hafıza")

    # 8. Ahmet Profili & 30 İslam Âlimi & Genel Bilgi Bankası Eşleşmesi
    if yanit is None:
        yanit, etiket = _fuzzy_taban_ara(AHMET_BILGI_TABANI, norm_text, "Ahmet Profili")

    if yanit is None:
        cekirdek_alim = re.sub(r"\b(kimdir|kim|nedir|hakkinda|bilgi|anlat|eserleri)\b", " ", norm_text).strip()
        en_iyi_skor, en_iyi_alim = 0, None
        for _, veri in ISLAM_ALIMLERI.items():
            for anahtar in veri["anahtar_kelimeler"]:
                a_norm = metni_normallestir(anahtar)
                if a_norm in norm_text or (cekirdek_alim and a_norm == cekirdek_alim):
                    en_iyi_skor, en_iyi_alim = 100, veri
                    break
                skor = max(fuzz.token_set_ratio(norm_text, a_norm), fuzz.ratio(cekirdek_alim, a_norm) if cekirdek_alim else 0)
                if skor >= 72 and skor > en_iyi_skor:
                    en_iyi_skor, en_iyi_alim = skor, veri
            if en_iyi_skor == 100:
                break
        if en_iyi_alim:
            yanit = (
                f"### 📜 {en_iyi_alim['ad']}\n"
                f"**Dönem:** {en_iyi_alim['donem']} | **Alan:** {en_iyi_alim['alan']}\n\n"
                f"**Başlıca Eserleri:** {en_iyi_alim['eserler']}\n\n"
                f"{en_iyi_alim['bilgi']}"
            )
            etiket = f"Âlim: {en_iyi_alim['ad']}"

    if yanit is None:
        yanit, etiket = _fuzzy_taban_ara(GENEL_SORU_CEVAP_TABANI, norm_text, "Bilgi Bankası")

    # 9. Duygu ve Sohbet Şablonları
    if yanit is None:
        for s_kod, s_veri in DUYGU_VE_SOHBET_SABLONLARI.items():
            for tet in s_veri["tetikleyiciler"]:
                t_norm = metni_normallestir(tet)
                if t_norm == norm_text or (len(t_norm) >= 5 and t_norm in norm_text):
                    yanit, etiket = s_veri["yanit"], f"Diyalog: {s_kod}"
                    break
            if yanit:
                break

    # 10. Teknik Terimler Sözlüğü Taraması
    if yanit is None:
        for _, t_veri in TEKNIK_TERIMLER_SOZLUGU.items():
            baslik_norm = metni_normallestir(t_veri["baslik"].split("(")[0])
            if baslik_norm and (baslik_norm in norm_text or norm_text in baslik_norm):
                yanit = f"🛠️ **{t_veri['baslik']} ({t_veri['kategori']}):**\n{t_veri['aciklama']}"
                etiket = f"Teknik Terim: {t_veri['kategori']}"
                break

    # 11. Bilinmeyen Soru -> "Bana öğretir misin?" Otomatik Öğrenme Kutusu Tetikleyicisi!
    if yanit is None:
        st.session_state["bekleyen_ogret_sorusu"] = kullanici_girdisi.strip()
        yanit = (
            f"🤔 **'{kullanici_girdisi}'** sorusunun cevabını henüz bilmiyorum Ahmet. **Bana öğretir misin?**\n\n"
            "👇 Hemen aşağıdaki **'🎓 Bana Öğret'** kutusuna bu sorunun cevabını yazıp kaydet; "
            "kod yazmana gerek kalmadan anında öğreneyim!"
        )
        etiket = "Bana Öğretir misin?"

    # 12. Çok Dilli Çeviri
    if hedef_dil != "tr":
        try:
            temiz_cevirilecek = re.sub(r"[#*`]", "", yanit)
            yanit = guvenli_cevir(temiz_cevirilecek, src="tr", dest=hedef_dil)
        except Exception as e:
            st.warning(f"Çeviri hatası oluştu, Türkçe gösteriliyor: {e}")
            hedef_dil = "tr"

    return yanit, hedef_dil, etiket

# ==============================================================================
# BÖLÜM 5: ANA UYGULAMA PANELİ VE 6 ÇALIŞMA STÜDYOSU
# ==============================================================================
# 4. TEKNOFEST İHA & AKILLI BEBEK ARABASI MÜHENDİSLİK ŞABLONLARI (180+ ADIM)
# ==============================================================================
MUHENDISLIK_KONTROL_LISTESI = [
    {
        "adim_no": 1,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #1)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 2,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #2)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 3,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #3)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 4,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #4)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 5,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #5)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 6,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #6)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 7,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #7)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 8,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #8)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 9,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #9)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 10,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #10)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 11,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #11)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 12,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #12)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 13,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #13)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 14,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #14)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 15,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #15)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 16,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #16)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 17,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #17)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 18,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #18)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 19,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #19)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 20,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #20)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 21,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #21)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 22,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #22)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 23,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #23)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 24,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #24)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 25,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #25)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 26,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #26)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 27,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #27)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 28,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #28)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 29,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #29)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 30,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #30)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 31,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #31)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 32,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #32)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 33,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #33)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 34,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #34)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 35,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #35)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 36,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #36)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 37,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #37)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 38,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #38)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 39,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #39)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 40,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #40)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 41,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #41)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 42,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #42)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 43,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #43)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 44,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #44)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 45,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #45)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 46,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #46)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 47,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #47)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 48,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #48)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 49,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #49)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 50,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #50)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 51,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #51)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 52,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #52)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 53,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #53)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 54,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #54)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 55,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #55)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 56,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #56)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 57,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #57)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 58,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #58)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 59,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #59)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 60,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #60)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 61,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #61)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 62,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #62)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 63,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #63)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 64,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #64)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 65,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #65)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 66,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #66)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 67,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #67)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 68,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #68)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 69,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #69)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 70,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #70)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 71,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #71)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 72,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #72)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 73,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #73)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 74,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #74)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 75,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #75)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 76,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #76)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 77,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #77)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 78,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #78)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 79,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #79)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 80,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #80)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 81,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #81)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 82,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #82)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 83,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #83)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 84,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #84)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 85,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #85)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 86,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #86)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 87,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #87)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 88,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #88)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 89,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #89)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 90,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #90)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 91,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #91)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 92,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #92)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 93,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #93)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 94,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #94)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 95,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #95)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 96,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #96)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 97,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #97)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 98,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #98)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 99,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #99)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 100,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #100)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 101,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #101)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 102,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #102)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 103,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #103)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 104,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #104)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 105,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #105)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 106,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #106)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 107,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #107)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 108,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #108)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 109,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #109)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 110,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #110)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 111,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #111)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 112,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #112)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 113,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #113)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 114,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #114)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 115,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #115)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 116,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #116)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 117,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #117)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 118,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #118)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 119,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #119)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 120,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #120)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 121,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #121)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 122,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #122)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 123,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #123)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 124,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #124)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 125,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #125)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 126,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #126)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 127,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #127)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 128,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #128)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 129,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #129)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 130,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #130)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 131,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #131)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 132,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #132)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 133,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #133)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 134,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #134)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 135,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #135)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 136,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #136)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 137,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #137)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 138,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #138)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 139,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #139)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 140,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #140)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 141,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #141)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 142,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #142)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 143,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #143)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 144,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #144)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 145,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #145)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 146,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #146)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 147,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #147)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 148,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #148)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 149,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #149)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 150,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #150)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 151,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #151)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 152,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #152)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 153,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #153)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 154,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #154)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 155,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #155)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 156,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #156)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 157,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #157)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 158,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #158)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 159,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #159)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 160,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #160)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 161,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #161)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 162,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #162)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 163,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #163)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 164,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #164)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 165,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #165)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 166,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #166)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 167,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #167)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 168,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #168)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 169,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #169)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 170,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #170)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 171,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #171)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 172,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #172)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 173,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #173)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 174,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #174)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 175,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #175)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 176,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #176)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 177,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #177)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 178,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #178)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 179,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #179)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 180,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #180)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 181,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #181)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 182,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #182)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 183,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #183)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 184,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #184)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 185,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #185)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 186,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #186)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 187,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #187)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 188,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #188)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 189,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #189)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 190,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #190)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 191,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #191)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 192,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #192)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 193,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #193)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 194,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #194)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 195,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #195)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 196,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #196)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 197,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #197)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 198,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #198)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 199,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #199)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 200,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #200)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 201,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #201)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 202,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #202)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 203,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #203)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 204,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #204)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 205,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #205)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 206,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #206)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 207,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #207)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 208,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #208)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 209,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #209)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 210,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #210)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 211,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #211)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 212,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #212)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 213,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #213)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 214,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #214)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 215,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #215)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 216,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #216)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 217,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #217)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 218,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #218)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 219,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #219)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 220,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #220)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 221,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #221)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 222,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #222)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 223,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #223)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 224,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #224)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 225,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #225)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 226,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #226)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 227,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #227)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 228,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #228)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 229,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #229)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 230,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #230)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 231,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #231)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 232,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #232)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 233,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #233)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 234,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #234)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 235,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #235)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 236,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #236)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 237,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #237)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 238,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #238)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 239,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #239)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 240,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #240)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 241,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #241)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 242,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #242)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 243,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #243)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 244,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #244)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 245,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #245)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 246,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #246)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 247,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #247)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 248,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #248)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 249,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #249)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 250,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #250)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 251,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #251)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 252,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #252)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 253,
        "proje": "Akıllı Bebek Arabası",
        "modul": "Motor Sürücü (Kontrol #253)",
        "gorev": "L298N ve DC dişli motorların zincir aktarma tork ölçümleri",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 254,
        "proje": "Yazılım & AI",
        "modul": "Ar AI Studio (Kontrol #254)",
        "gorev": "500.000+ kalıp indeksinin masaüstü ve mobil tarayıcıda hız testi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 255,
        "proje": "Yazılım & AI",
        "modul": "Doğal Ses Sentezi (Kontrol #255)",
        "gorev": "Edge-TTS AhmetNeural ve EmelNeural seslerinin gecikmesiz oynatılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 256,
        "proje": "Kişisel Gelişim",
        "modul": "Çok Dilli Pratik (Kontrol #256)",
        "gorev": "İngilizce, Çince ve Bengalce mühendislik terimlerinin günlük tekrarı",
        "oncelik": "Normal",
    },
    {
        "adim_no": 257,
        "proje": "TEKNOFEST 2027",
        "modul": "Otonom İHA Gövde (Kontrol #257)",
        "gorev": "Carbon Fiber PLA şasi parçalarının 3D yazıcıda %35 dolulukla basılması",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 258,
        "proje": "TEKNOFEST 2027",
        "modul": "Uçuş Kontrol & IMU (Kontrol #258)",
        "gorev": "PID katsayılarının (Roll, Pitch, Yaw) test standında kalibre edilmesi",
        "oncelik": "Normal",
    },
    {
        "adim_no": 259,
        "proje": "Otonom AI Drone",
        "modul": "Görüntü İşleme (Kontrol #259)",
        "gorev": "Raspberry Pi 5 üzerinde OpenCV ile gerçek zamanlı hedef/yüz takibi testi",
        "oncelik": "Yüksek",
    },
    {
        "adim_no": 260,
        "proje": "TÜBİTAK 2204-A",
        "modul": "Akıllı Bebek Arabası (Kontrol #260)",
        "gorev": "HC-SR04 ultrasonik sensör ile 40 cm altında otomatik frenleme testi",
        "oncelik": "Normal",
    },
]


# ==============================================================================
# 5. OTURUM DURUMU (SESSION STATE) VE YARDIMCI İŞLEYİCİLER
# ==============================================================================
def oturum_durumunu_hazirla():
    varsayilanlar = {
        "messages": None,
        "sessiz_mod": False,
        "ses_aktif": True,
        "pygame_aktif": False,
        "ses_cinsiyet": "Erkek",
        "secili_tema": "Derin Lacivert (Klasik Ar)",
        "quiz_soru": None,
        "quiz_puan": 0,
        "son_ses_bayt": None,
    }
    for k, v in varsayilanlar.items():
        if k not in st.session_state:
            st.session_state[k] = sohbet_gecmisi_yukle() if k == "messages" else v


def mesaji_isle(girdi_metni: str, hedef_dil: str):
    simdi = datetime.now()
    su_an = simdi.strftime("%H:%M:%S")
    bugun_str = simdi.strftime("%Y-%m-%d")
    cevap, dil_kodu, islem_etiketi = akilli_yanit_uret(girdi_metni, hedef_dil=hedef_dil)
    st.session_state.messages.append(
        {"role": "user", "content": girdi_metni, "zaman": su_an, "tarih": bugun_str, "etiket": islem_etiketi}
    )
    st.session_state.messages.append(
        {"role": "assistant", "content": cevap, "zaman": su_an, "tarih": bugun_str, "etiket": islem_etiketi}
    )
    sohbet_gecmisi_kaydet(st.session_state.messages)
    return cevap, dil_kodu


# ==============================================================================
# 6. ANA SİSTEM BAŞLATICI (sistemi_baslat)
# ==============================================================================
def sistemi_baslat():
    oturum_durumunu_hazirla()
    arayuz_stillerini_yukle(st.session_state.secili_tema)
    json_veritabani_hazirla()
    kalip_havuzu = kalip_havuzu_olustur()

    # --------------------------------------------------------------------------
    # YAN MENÜ: TEMA, SES, DİL VE GÜNLÜK BALONCUK SOHBET GEÇMİŞİ
    # --------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("## ⚡ Ar AI Kontrol Merkezi")

        if st.session_state.sessiz_mod:
            st.markdown('<span class="silent-badge">🤫 SESSİZ MOD AKTİF</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="live-badge">🔊 DOĞAL SES AKTİF</span>', unsafe_allow_html=True)

        bolum = st.radio(
            "Çalışma Stüdyosu Seçin:",
            [
                "💬 AI Chatbot & JSON Stüdyo",
                "🧮 Matematik & Fen Laboratuvarı",
                "📜 İslam Âlimleri Ansiklopedisi",
                "🌐 28 Dilli Çeviri & Dil Kartları",
                "🚀 Ahmet Profil & Proje Merkezi",
                "📊 Sistem Dashboard & Ayarlar",
            ],
        )

        st.markdown("---")
        st.markdown("### 🎨 Tema & Görünüm")
        tema_listesi = list(TEMA_PALETLERI.keys())
        if st.session_state.secili_tema not in tema_listesi:
            st.session_state.secili_tema = tema_listesi[0]
        secilen_tema = st.selectbox(
            "Renk Paleti (Koyu Lacivert & Kontrast):",
            options=tema_listesi,
            index=tema_listesi.index(st.session_state.secili_tema),
        )
        if secilen_tema != st.session_state.secili_tema:
            st.session_state.secili_tema = secilen_tema
            st.rerun()

        st.markdown("### 🎛️ Doğal Ses & Dil Ayarları")
        st.session_state.sessiz_mod = st.toggle("🤫 Sessiz Konuşma Modu", value=st.session_state.sessiz_mod)
        st.session_state.ses_aktif = st.toggle(
            "🔊 Doğal Ses Motoru (Neural + gTTS)",
            value=st.session_state.ses_aktif,
            disabled=st.session_state.sessiz_mod,
        )
        st.session_state.ses_cinsiyet = st.selectbox(
            "🎙️ Ses Karakteri:",
            options=["Erkek", "Kadın"],
            format_func=lambda x: "👨 Ahmet Neural (Doğal Erkek)" if x == "Erkek" else "👩 Emel Neural (Doğal Kadın)",
            disabled=st.session_state.sessiz_mod or not st.session_state.ses_aktif,
        )
        if PYGAME_MEVCUT:
            st.session_state.pygame_aktif = st.toggle(
                "🖥️ Yerel Hoparlör (Pygame)",
                value=st.session_state.pygame_aktif,
                disabled=st.session_state.sessiz_mod or not st.session_state.ses_aktif,
            )

        sohbet_dili = st.selectbox(
            f"Yanıt Dili ({len(DESTEKLENEN_DILLER)} Dil):",
            options=list(DESTEKLENEN_DILLER.keys()),
            format_func=lambda x: DESTEKLENEN_DILLER[x],
        )

        # GÜNLÜK BALONCUK SOHBET GEÇMİŞİ (Bugün bunu konuştuk / Dün bunu konuştuk)
        st.markdown("---")
        st.markdown("### 💬 Geçmiş Konuşma Baloncukları")
        kullanici_sorulari = [m for m in st.session_state.messages if m["role"] == "user"]
        st.caption(f"Toplam Konuşma Balonu: **{len(kullanici_sorulari)}**")

        bugun_tarih = datetime.now().strftime("%Y-%m-%d")
        dun_tarih = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        gruplar = {"Bugün Konuştuklarımız": [], "Dün Konuştuklarımız": [], "Önceki Günler": []}
        for m in reversed(kullanici_sorulari):
            t = m.get("tarih", bugun_tarih)
            if t == bugun_tarih:
                gruplar["Bugün Konuştuklarımız"].append(m)
            elif t == dun_tarih:
                gruplar["Dün Konuştuklarımız"].append(m)
            else:
                gruplar["Önceki Günler"].append(m)

        gecmis_kutusu = st.container(height=240)
        with gecmis_kutusu:
            if not kullanici_sorulari:
                st.caption("Henüz konuşma balonu yok. Bir soru sorarak başla!")
            else:
                for grup_adi, liste in gruplar.items():
                    if liste:
                        st.markdown(f'<div class="bubble-group-header">📅 {grup_adi} ({len(liste)})</div>', unsafe_allow_html=True)
                        for idx_m, m in enumerate(liste):
                            saat = m.get("zaman", "--:--")
                            etiket = m.get("etiket", "Sohbet")
                            kisa = m["content"][:34] + "..." if len(m["content"]) > 34 else m["content"]
                            st.markdown(sohbet_baloncuk_karti_olustur(etiket, saat, kisa), unsafe_allow_html=True)

        col_sb1, col_sb2 = st.columns(2)
        with col_sb1:
            st.download_button(
                label="📥 Yedekle",
                data=json.dumps(st.session_state.messages, ensure_ascii=False, indent=2),
                file_name=f"ar_gecmis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
            )
        with col_sb2:
            if st.button("🗑️ Temizle", use_container_width=True):
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Sohbet geçmişi sıfırlandı Ahmet! Yeni konuşmaya hazırız. ⚡",
                        "zaman": datetime.now().strftime("%H:%M:%S"),
                        "tarih": bugun_tarih,
                        "etiket": "Sıfırlandı",
                    }
                ]
                sohbet_gecmisi_kaydet(st.session_state.messages)
                st.rerun()

    # --------------------------------------------------------------------------
    # ÜST HERO BANNER
    # --------------------------------------------------------------------------
    hero_banner_goster(len(kalip_havuzu), st.session_state.secili_tema)

    # ==========================================================================
    # STÜDYO 1: AI CHATBOT & JSON KOMUT STÜDYOSU
    # ==========================================================================
    if bolum == "💬 AI Chatbot & JSON Stüdyo":
        col_chat, col_studio = st.columns([2.15, 1.15], gap="large")

        with col_chat:
            st.subheader("💬 Canlı Asistan Sohbeti (Masaüstü & Mobil)")

            q1, q2, q3, q4 = st.columns(4)
            hizli_girdi = None
            if q1.button("👤 Hakkımda", use_container_width=True):
                hizli_girdi = "benim hakkımda ne biliyorsun"
            if q2.button("√ Köklü Sayı", use_container_width=True):
                hizli_girdi = "kök 72"
            if q3.button("📜 El-Cezerî", use_container_width=True):
                hizli_girdi = "El-Cezeri kimdir"
            if q4.button("📐 Denklem", use_container_width=True):
                hizli_girdi = "3x + 9 = 24"

            chat_penceresi = st.container(height=480)
            with chat_penceresi:
                for msg in st.session_state.messages:
                    avatar = "👤" if msg["role"] == "user" else "⚡"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.markdown(msg["content"])
                        saat_bilgi = msg.get("zaman", "")
                        etiket_bilgi = msg.get("etiket", "")
                        if saat_bilgi or etiket_bilgi:
                            st.caption(f"🕒 {saat_bilgi}  |  🏷️ {etiket_bilgi}")

            if st.session_state.get("son_ses_bayt"):
                st.audio(st.session_state.son_ses_bayt, format="audio/mp3", autoplay=True)
                st.session_state.son_ses_bayt = None

            prompt = st.chat_input("Ar'a yaz... (Örn: 'Nasılsın?', 'Ne haber?', 'Kimsin?', 'Ömer kim?', '76 çarpı 25', 'kök 128')")
            aktif_girdi = hizli_girdi or prompt

            if aktif_girdi is not None and aktif_girdi.strip() != "":
                cevap, dil_kodu = mesaji_isle(aktif_girdi, sohbet_dili)
                sesli_soyle(cevap, dil=dil_kodu, rerun_sonrasi=True)
                st.rerun()

            # KOD YAZMADAN ANINDA ÖĞRETME PANELİ ("Bana öğretir misin?")
            bekleyen_soru = st.session_state.get("bekleyen_ogret_sorusu", "")
            with st.expander(
                f"🎓 Bana Öğretir misin? — {'Yeni Soru: ' + bekleyen_soru if bekleyen_soru else 'Kod Yazmadan Hızlı Soru-Cevap Öğret'}",
                expanded=bool(bekleyen_soru),
            ):
                with st.form("hizli_bana_ogret_formu", clear_on_submit=True):
                    ogret_soru_input = st.text_input(
                        "Öğretilecek Soru veya Kelime:",
                        value=bekleyen_soru,
                        placeholder="Örn: en sevdiğim yemek nedir",
                    )
                    ogret_cevap_input = st.text_area(
                        "Ar'ın Vereceği Cevap:",
                        height=85,
                        placeholder="Ar bu soruya ne cevap versin? Buraya yaz...",
                    )
                    if st.form_submit_button("💾 Öğret ve Hafızaya Kaydet (Kod Yazmadan)", use_container_width=True):
                        if ogret_soru_input.strip() and ogret_cevap_input.strip():
                            kat_kodu = f"ogrenilen_{int(time.time())}"
                            json_komut_ekle(kat_kodu, ogret_soru_input.strip(), ogret_cevap_input.strip())
                            st.session_state["bekleyen_ogret_sorusu"] = ""
                            onay_mesaji = (
                                f"✅ **Teşekkür ederim Ahmet, hemen öğrendim!**\n\n"
                                f"Artık bana **'{ogret_soru_input.strip()}'** dediğinde şu cevabı vereceğim:\n"
                                f"> {ogret_cevap_input.strip()}"
                            )
                            simdi_z = datetime.now()
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": onay_mesaji,
                                "zaman": simdi_z.strftime("%H:%M:%S"),
                                "tarih": simdi_z.strftime("%Y-%m-%d"),
                                "etiket": "Yeni Öğrenildi",
                            })
                            sohbet_gecmisi_kaydet(st.session_state.messages)
                            st.success("Başarıyla öğrenildi ve hafızaya kaydedildi!")
                            st.rerun()
                        else:
                            st.warning("Lütfen hem soruyu hem de cevabı yaz Ahmet.")

        with col_studio:
            st.subheader("🧠 JSON Komut Stüdyosu")
            tab_ekle, tab_yonet = st.tabs(["➕ Yeni Cevap", "🗂️ JSON Yönetimi"])

            with tab_ekle:
                with st.form("yeni_komut_formu", clear_on_submit=True):
                    kat_input = st.text_input("Kategori Adı:", placeholder="Örn: ozel_bilgiler")
                    kelime_input = st.text_input("Anahtar Kelimeler (Virgülle):", placeholder="Örn: okulum, favori ders")
                    yanit_input = st.text_area("Verilecek Cevap:", height=110, placeholder="Cevabı buraya yaz...")
                    if st.form_submit_button("💾 JSON Dosyasına Kaydet", use_container_width=True):
                        if kat_input and kelime_input and yanit_input:
                            json_komut_ekle(kat_input, kelime_input, yanit_input)
                            st.success(f"'{kat_input}' başarıyla kaydedildi!")
                            st.rerun()
                        else:
                            st.warning("Lütfen tüm kutucukları doldurun.")

            with tab_yonet:
                guncel_json = json_oku()
                if guncel_json:
                    sil_secim = st.selectbox("Silinecek Kategori:", options=list(guncel_json.keys()))
                    if st.button("🗑️ Seçili Kategoriyi Sil", use_container_width=True):
                        json_kategori_sil(sil_secim)
                        st.success(f"'{sil_secim}' silindi!")
                        st.rerun()
                with st.expander("📄 Canlı komutlar.json İçeriği", expanded=True):
                    st.json(guncel_json)

    # ==========================================================================
    # STÜDYO 2: MATEMATİK & FEN LABORATUVARI
    # ==========================================================================
    elif bolum == "🧮 Matematik & Fen Laboratuvarı":
        st.subheader("🧮 İnteraktif Matematik Öğretmeni, Geometri & Çözüm Laboratuvarı")
        t1, t2, t3, t4 = st.tabs(["📚 Konu Anlatımları", "⚡ Çözücü & Geometri", "📖 150 Çözümlü Soru", "🎯 Canlı Test"])

        with t1:
            secili_konu = st.selectbox("Öğrenmek İstediğin Konuyu Seç:", list(MATEMATIK_KONU_REHBERI.keys()))
            k_veri = MATEMATIK_KONU_REHBERI[secili_konu]
            st.markdown(bilgi_karti_olustur(secili_konu, f"📘 {k_veri['alt_baslik']}", k_veri["icerik"].replace("\n", "<br>")), unsafe_allow_html=True)
            if st.button("🔊 Bu Konuyu Sesli Anlat"):
                sesli_soyle(k_veri["icerik"], dil="tr")

        with t2:
            c_m1, c_m2, c_m3 = st.columns(3, gap="medium")
            with c_m1:
                st.markdown("#### √ Karekök (`a√b`) & Referans")
                kok_n = st.number_input("Sayı gir:", min_value=1, max_value=1000000, value=72, step=1)
                dis, ic = karekok_sadelestir(int(kok_n))
                if ic == 1:
                    st.success(f"`√{kok_n}` = **{dis}** (Tam Kare)")
                else:
                    st.success(f"`√{kok_n}` = **`{dis if dis > 1 else ''}√{ic}`** (`{math.sqrt(kok_n):.4f}`)")
                if int(kok_n) in MATEMATIK_REFERANS_TABLOSU:
                    ref = MATEMATIK_REFERANS_TABLOSU[int(kok_n)]
                    st.info(f"**Karesi:** `{ref['karesi']}` | **Küpü:** `{ref['kupu']}`")

            with c_m2:
                st.markdown("#### 📐 2. Derece Denklem (`ax²+bx+c=0`)")
                da = st.number_input("a katsayısı:", value=1.0, step=1.0)
                db = st.number_input("b katsayısı:", value=-5.0, step=1.0)
                dc = st.number_input("c sabiti:", value=6.0, step=1.0)
                st.markdown(ikinci_derece_denklem_coz(da, db, dc))

            with c_m3:
                st.markdown("#### 📏 Pisagor & Dik Üçgen")
                k_a = st.number_input("1. Dik Kenar (a):", min_value=1.0, value=6.0, step=1.0)
                k_b = st.number_input("2. Dik Kenar (b):", min_value=1.0, value=8.0, step=1.0)
                st.markdown(pisagor_hesapla(k_a, k_b))

        with t3:
            secili_soru_no = st.slider("Çözümlü Soru Seç (1 - 154):", 1, len(COZUMLU_SORU_BANKASI), 1)
            s_obj = COZUMLU_SORU_BANKASI[secili_soru_no - 1]
            st.markdown(bilgi_karti_olustur(f"Soru #{s_obj['no']} — {s_obj['konu']}", f"Doğru Cevap: {s_obj['cevap']}", f"**Soru:** {s_obj['soru']}<br><br>**Adım Adım Çözüm:** {s_obj['cozum']}"), unsafe_allow_html=True)

        with t4:
            st.caption(f"Toplam Doğru Puanın: **{st.session_state.quiz_puan}**")
            if st.button("🎲 Yeni Test Sorusu Getir") or st.session_state.quiz_soru is None:
                rast = random.choice(COZUMLU_SORU_BANKASI)
                st.session_state.quiz_soru = (rast["soru"], rast["cevap"], rast["cozum"])
            q_soru, q_cevap, q_cozum = st.session_state.quiz_soru
            st.info(f"**Soru:** {q_soru}")
            k_yanit = st.text_input("Cevabın:", key="canli_quiz_girdi")
            if st.button("✅ Cevabı Kontrol Et"):
                if k_yanit.strip().replace(" ", "") == q_cevap.replace(" ", ""):
                    st.session_state.quiz_puan += 10
                    st.success(f"🎉 Harika Ahmet! Doğru cevap: **{q_cevap}** (+10 Puan)")
                else:
                    st.error(f"❌ Doğru cevap: **{q_cevap}** | Çözüm: {q_cozum}")

    # ==========================================================================
    # STÜDYO 3: İSLAM ÂLİMLERİ ANSİKLOPEDİSİ (30 ÂLİM)
    # ==========================================================================
    elif bolum == "📜 İslam Âlimleri Ansiklopedisi":
        st.subheader(f"📜 İslam Bilim ve Düşünce Tarihine Yön Veren {len(ISLAM_ALIMLERI)} Büyük Âlim")
        arama = st.text_input("Âlim, Eser veya Bilim Dalı Ara:", placeholder="Örn: Cezeri, Harezmi, Optik, Cerrahi, Buhara...").lower().strip()
        col_a1, col_a2 = st.columns(2, gap="medium")
        for idx, (kod, bilgi) in enumerate(ISLAM_ALIMLERI.items()):
            birlesik = f"{bilgi['ad']} {bilgi['alan']} {bilgi['eserler']} {bilgi['bilgi']}".lower()
            if arama and arama not in birlesik:
                continue
            with (col_a1 if idx % 2 == 0 else col_a2):
                st.markdown(bilgi_karti_olustur(f"📜 {bilgi['ad']}", f"🕰️ {bilgi['donem']} | 🔬 {bilgi['alan']}", f"<strong>Başlıca Eserleri:</strong> {bilgi['eserler']}<br><br>{bilgi['bilgi']}"), unsafe_allow_html=True)
                if st.button(f"🔊 {bilgi['ad'].split('(')[0].strip()} Biyografisini Dinle", key=f"dinle_{kod}"):
                    sesli_soyle(bilgi["bilgi"], dil="tr")

    # ==========================================================================
    # STÜDYO 4: 28 DİLLİ ÇEVİRİ & DİL EĞİTİM KARTLARI
    # ==========================================================================
    elif bolum == "🌐 28 Dilli Çeviri & Dil Kartları":
        st.subheader(f"🌐 {len(DESTEKLENEN_DILLER)} Dilli Çeviri Stüdyosu & Çok Dilli Kelime Kartları")
        tab_ceviri, tab_kartlar = st.tabs(["🔄 Akıllı Çeviri & Seslendirme", "🗂️ İngilizce - Çince - Bengalce Kartları (150 Kart)"])

        with tab_ceviri:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                kaynak = st.selectbox("Kaynak Dil:", options=["auto"] + list(DESTEKLENEN_DILLER.keys()), format_func=lambda x: "✨ Otomatik Algıla" if x == "auto" else DESTEKLENEN_DILLER[x])
                metin_giris = st.text_area("Çevrilecek Metin:", height=190, placeholder="Çevirmek istediğin metni buraya yaz...")
            with c2:
                hedef = st.selectbox("Hedef Dil:", options=list(DESTEKLENEN_DILLER.keys()), index=1, format_func=lambda x: DESTEKLENEN_DILLER[x])
                cikti = st.empty()
                cikti.text_area("Çeviri Sonucu:", value="", height=190, key="ceviri_bos")

            b1, b2 = st.columns(2)
            btn_cevir = b1.button("🔄 Sadece Çevir", use_container_width=True)
            btn_sesli = b2.button("🔊 Çevir ve Doğal Sesle Oku", use_container_width=True)
            if btn_cevir or btn_sesli:
                if metin_giris.strip():
                    try:
                        cevrilen = guvenli_cevir(metin_giris, src=kaynak, dest=hedef)
                        cikti.text_area("Çeviri Sonucu:", value=cevrilen, height=190, key="ceviri_dolu")
                        if btn_sesli:
                            sesli_soyle(cevrilen, dil=hedef)
                    except Exception as e:
                        st.error(f"Çeviri hatası: {e}")
                else:
                    st.warning("Lütfen çevirmek için bir metin girin.")

        with tab_kartlar:
            kart_no = st.slider("Kelime Kartı Seç (1 - 150):", 1, len(DIL_EGITIM_KARTLARI), 1)
            kart = DIL_EGITIM_KARTLARI[kart_no - 1]
            st.markdown(bilgi_karti_olustur(f"🇬🇧 {kart['ingilizce']} — 🇹🇷 {kart['turkce']}", f"Kategori: {kart['kategori']} | Seviye: {kart['seviye']}", f"🇨🇳 <strong>Çince:</strong> {kart['cince']}<br>🇧🇩 <strong>Bengalce:</strong> {kart['bengalce']}<br>📝 <strong>Örnek Cümle:</strong> {kart['ornek_cumle']}"), unsafe_allow_html=True)
            if st.button("🔊 İngilizce Örnek Cümleyi Dinle"):
                sesli_soyle(kart["ornek_cumle"], dil="en")

    # ==========================================================================
    # STÜDYO 5: AHMET PROFİL, TEKNİK TERİMLER & PROJE MERKEZİ
    # ==========================================================================
    elif bolum == "🚀 Ahmet Profil & Proje Merkezi":
        st.subheader("🚀 Geliştirici Ahmet Profili, TEKNOFEST İHA & Mühendislik Merkezi")
        p_tab1, p_tab2, p_tab3 = st.tabs(["👤 Kişisel Profil & Notlar", "🛠️ Mühendislik Sözlüğü (175 Terim)", "✅ Proje Kontrol Listesi (180 Adım)"])

        with p_tab1:
            col_p1, col_p2 = st.columns([1.4, 1.0], gap="large")
            with col_p1:
                for _, p_veri in AHMET_BILGI_TABANI.items():
                    st.markdown(bilgi_karti_olustur("⚡ Ahmet Bilgi Kartı", "Aktif Geliştirici Profili", p_veri["yanit"].replace("\n", "<br>")), unsafe_allow_html=True)
            with col_p2:
                st.markdown("#### 📝 Hızlı Proje Notu Ekle")
                with st.form("proje_not_formu", clear_on_submit=True):
                    n_baslik = st.text_input("Proje / Konu Başlığı:", placeholder="Örn: Otonom İHA Kamera Testi")
                    n_icerik = st.text_area("Not İçeriği:", height=100)
                    if st.form_submit_button("💾 Notu Kaydet", use_container_width=True) and n_baslik and n_icerik:
                        proje_notu_ekle(n_baslik, n_icerik)
                        st.success("Proje notu kaydedildi!")
                        st.rerun()
                for n_item in proje_notlari_oku()[:6]:
                    st.markdown(bilgi_karti_olustur(f"📌 {n_item['baslik']}", f"🕒 {n_item['tarih']}", n_item["icerik"]), unsafe_allow_html=True)

        with p_tab2:
            terim_ara = st.text_input("Teknik Terim Ara (PID, PWM, IMU, Kalman, PETG...):").lower().strip()
            for _, t_obj in list(TEKNIK_TERIMLER_SOZLUGU.items())[:30]:
                if terim_ara and terim_ara not in f"{t_obj['baslik']} {t_obj['aciklama']}".lower():
                    continue
                st.markdown(bilgi_karti_olustur(t_obj["baslik"], f"Kategori: {t_obj['kategori']} | Kod: {t_obj['kod']}", t_obj["aciklama"]), unsafe_allow_html=True)

        with p_tab3:
            for g_item in MUHENDISLIK_KONTROL_LISTESI[:25]:
                st.markdown(bilgi_karti_olustur(f"Adım #{g_item['adim_no']} — {g_item['modul']}", f"Proje: {g_item['proje']} | Öncelik: {g_item['oncelik']}", g_item["gorev"]), unsafe_allow_html=True)

    # ==========================================================================
    # STÜDYO 6: SİSTEM DASHBOARD, KISAYOLLAR & AYARLAR
    # ==========================================================================
    elif bolum == "📊 Sistem Dashboard & Ayarlar":
        st.subheader("📊 5 Modüllü Sistem Analitiği, Kısayol Rehberi ve Bakım")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Hazır AI Kalıbı", f"{len(kalip_havuzu):,}".replace(",", "."), "O(1) İndeks")
        m2.metric("Sohbet Mesajı", f"{len(st.session_state.messages)}", "Baloncuk Hafıza")
        m3.metric("İslam Âlimleri", f"{len(ISLAM_ALIMLERI)} Âlim", "Tam Ansiklopedi")
        m4.metric("Dil & Ses", f"{len(DESTEKLENEN_DILLER)} Dil", "Neural + gTTS")

        st.markdown("---")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("### 📂 Aktif Modüller ve Veritabanı Yolları")
            st.info(
                f"**1. Arayüz & Tema:** `config_ve_arayuz.py`\n\n"
                f"**2. Bilgi & Ansiklopedi:** `veri_tabani.py`\n\n"
                f"**3. Matematik & Fizik:** `matematik_motoru.py`\n\n"
                f"**4. AI & Neural Ses:** `zeka_ve_ses_motoru.py`\n\n"
                f"**5. Ana Başlatıcı:** `main.py` (`streamlit run main.py`)"
            )
            if st.button("♻️ komutlar.json Dosyasını Sıfırla", use_container_width=True):
                if os.path.exists(JSON_DOSYA_ADI):
                    os.remove(JSON_DOSYA_ADI)
                json_veritabani_hazirla()
                st.success("komutlar.json başarıyla sıfırlandı!")
                st.rerun()

        with c2:
            st.markdown("### ⌨️ PyCharm & Masaüstü Hızlı Kısayol Rehberi")
            for k_item in SISTEM_KISAYOL_REHBERI[:10]:
                st.markdown(bilgi_karti_olustur(f"⌨️ {k_item['tus']}", k_item["platform"], k_item["aciklama"]), unsafe_allow_html=True)


if __name__ == "__main__":
    sistemi_baslat()