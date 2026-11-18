"""
CryptoRadar | Konfigürasyon Dosyası
Kripto & Finans Radarı - 7/24 Otonom Piyasa ve Bülten Motoru
"""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

# -------------------------------------------------------------
# 🏷️ MARKA & HESAP AYARLARI
# -------------------------------------------------------------
BRAND_NAME = os.getenv("BRAND_NAME", "KRİPTO & FİNANS RADARI")
X_HANDLE = os.getenv("X_HANDLE", "@kriptofinansa")
BRAND_ACCENT_COLOR = os.getenv("BRAND_ACCENT_COLOR", "#F59E0B")  # Altın / Bitcoin Turuncusu
SECONDARY_ACCENT_COLOR = os.getenv("SECONDARY_ACCENT_COLOR", "#10B981")  # Yükseliş Yeşili

# -------------------------------------------------------------
# ⏱️ PAYLAŞIM VE GECİKME AYARLARI (3-5 Kasım: 2 Saatte 1)
# -------------------------------------------------------------
# 3-5 Kasım hızlandırma dönemi: 2 saatte bir (120 dk hedef, 30 dk cron payı ile 105 dk)
POST_COOLDOWN_MINUTES = 105.0

# -------------------------------------------------------------
# 🔑 X (TWITTER) ÇEREZLERİ
# -------------------------------------------------------------
TWITTER_AUTH_TOKEN = os.getenv("TWITTER_AUTH_TOKEN", "").strip()
TWITTER_CT0 = os.getenv("TWITTER_CT0", "").strip()

# -------------------------------------------------------------
# ✈️ TELEGRAM AYARLARI
# -------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_TARGET_CHAT = os.getenv("TELEGRAM_TARGET_CHAT", "@Kripto_FinansR")

# -------------------------------------------------------------
# 📡 KRİPTO & FİNANS HABER KAYNAKLARI (RSS)
# -------------------------------------------------------------
CRYPTO_RSS_FEEDS = [
    "https://tr.cointelegraph.com/rss",
    "https://koinbulteni.com/feed",
    "https://www.coinkolik.com/feed/",
    "https://uzmancoin.com/feed/",
    "https://tr.investing.com/rss/news_301.rss",
    "https://tr.investing.com/rss/news_25.rss"
]
