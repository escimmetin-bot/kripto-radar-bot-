"""
CryptoRadar | Kripto & Finans Haber Motoru
Uzmancoin, CoinTurk ve CoinDesk gibi dev kaynaklardan haberleri çeker ve virallik puanına göre sıralar.
"""
import re
import html
import urllib.parse
import urllib.request
import json
import feedparser
import requests
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def ensure_turkish(text: str) -> str:
    """Metin yabancı dildeyse anında akıcı Türkçeye çevirir."""
    if not text:
        return ""
    # Türkçe karakterler veya yaygın Türkçe kelimeler içeriyorsa çeviriye gerek yok
    tr_markers = [" ve ", " bir ", " için ", " ile ", " da ", " de ", "nin ", "nin\n", "nın ", "den ", "dan "]
    if any(c in text for c in "çğıöşüÇĞİÖŞÜ") or any(m in f" {text.lower()} " for m in tr_markers):
        return text

    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=tr&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode("utf-8"))
            translated_parts = [p[0] for p in res[0] if p and p[0]]
            return "".join(translated_parts).strip()
    except Exception:
        return text

CRYPTO_VIRAL_KEYWORDS = {
    # Kurumsal & Regülasyon (En yüksek etki)
    "binance": 55, "sec": 55, "fed": 50, "faiz": 50, "etf": 50, "blackrock": 45,
    "powell": 45, "tether": 40, "usdt": 40, "coinbase": 40,

    # Büyük Coinler
    "bitcoin": 45, "btc": 45, "ethereum": 40, "eth": 40, "solana": 40, "sol": 40, "xrp": 40,

    # Piyasa Hareketi (Duygu patlamaları)
    "rekor": 45, "ath": 45, "fırladı": 45, "ralli": 45, "boğa": 40,
    "çöküş": 45, "düştü": 40, "tasfiye": 45, "likidasyon": 45, "ayı": 40,
    "balina": 40, "listeleme": 40, "milyar dolar": 40, "milyon dolar": 35
}

JUNK_KEYWORDS = [
    "kimdir", "nereli", "sponsorlu", "tanıtım bülteni", "indirim kodu",
    "burç", "astroloji", "kaç yaşında", "can yeleği"
]


def calculate_crypto_virality(title: str, summary: str) -> int:
    score = 100
    text = f"{title} {summary}".lower()

    for kw, pt in CRYPTO_VIRAL_KEYWORDS.items():
        if re.search(rf"\b{re.escape(kw)}\b", text):
            score += pt

    # Çöp kontrolü
    for jk in JUNK_KEYWORDS:
        if jk in text:
            score -= 100

    return score


def fetch_crypto_articles(feed_urls: List[str]) -> List[Dict]:
    articles = []
    seen_titles = set()

    for url in feed_urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:12]:
                title = entry.get("title", "").strip()
                if not title or title.lower() in seen_titles or len(title) < 20:
                    continue

                seen_titles.add(title.lower())
                summary = entry.get("summary", "") or entry.get("description", "")
                
                # HTML tag temizliği
                clean_summary = re.sub(r'<[^>]+>', '', summary).strip()
                clean_title = re.sub(r'<[^>]+>', '', title).strip()

                # %100 TÜRKÇE GARANTİSİ (Yabancı kaynaktan gelirse Türkçeleştir)
                clean_title = ensure_turkish(clean_title)
                clean_summary = ensure_turkish(clean_summary)

                # Olayın / Haberin Gerçek Görselini Yakala (4 Kademeli Tarama)
                img_url = None
                if hasattr(entry, "enclosures") and entry.enclosures:
                    img_url = entry.enclosures[0].href
                elif hasattr(entry, "media_content") and entry.media_content:
                    img_url = entry.media_content[0].get("url")
                elif hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    img_url = entry.media_thumbnail[0].get("url")

                # HTML içindeki gerçek görsel etiketi
                if not img_url:
                    raw_html = summary or ""
                    found_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', raw_html)
                    if found_imgs:
                        img_url = found_imgs[0]

                # Web sayfasından og:image (Gerçek Orijinal Manşet Fotoğrafı)
                article_link = entry.get("link", "")
                if not img_url and article_link:
                    try:
                        r_page = requests.get(article_link, headers=HEADERS, timeout=4)
                        if r_page.status_code == 200:
                            og_match = re.search(r'<meta[^>]+property=[\'"]og:image[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', r_page.text, re.I)
                            if not og_match:
                                og_match = re.search(r'<meta[^>]+content=[\'"]([^\'"]+)[\'"][^>]+property=[\'"]og:image[\'"]', r_page.text, re.I)
                            if og_match:
                                img_url = og_match.group(1)
                    except Exception:
                        pass

                score = calculate_crypto_virality(clean_title, clean_summary)
                if score < 50:
                    continue

                slug = re.sub(r'[^a-zA-Z0-9]+', '-', clean_title.lower()).strip('-')[:50]
                articles.append({
                    "title": clean_title,
                    "summary": clean_summary,
                    "link": entry.get("link", ""),
                    "image_url": img_url,
                    "virality_score": score,
                    "slug": slug
                })
        except Exception as e:
            print(f"⚠️ RSS Okuma Hatası ({url}): {e}")
            continue

    # En yüksek virallik puanına göre sırala
    articles.sort(key=lambda x: x["virality_score"], reverse=True)
    return articles


if __name__ == "__main__":
    from config import CRYPTO_RSS_FEEDS
    items = fetch_crypto_articles(CRYPTO_RSS_FEEDS)
    print(f"Toplanan Kripto Haber Sayısı: {len(items)}")
    for it in items[:3]:
        print(f"[{it['virality_score']} Puan] {it['title']}")
