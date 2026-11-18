"""
CryptoRadar | Ana Çalıştırıcı Motor
Kullanım:
  python main.py          (Normal döngü)
  python main.py --dry    (Simülasyon / Test modu)
"""
import os
import sys
import time

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import config
from crypto_market import get_live_market_data, detect_relevant_coin
from crypto_news import fetch_crypto_articles
from crypto_card import generate_crypto_card
from crypto_poster import can_post_now, format_crypto_tweet, post_to_x, load_history, save_history
from crypto_telegram import format_telegram_caption, send_crypto_post_to_telegram


def run_cycle(dry_run: bool = False):
    print("=" * 60)
    print("⚡ CRYPTORADAR | OTONOM KRİPTO & FINANS MOTORU")
    print("=" * 60)

    # 1. Zaman Kilidi Kontrolü
    if not dry_run:
        allowed, reason = can_post_now()
        if not allowed:
            print(f"⏳ [Zaman Kilidi] {reason}")
            return

    # 2. Canlı Piyasa Verileri
    print("📊 Canlı piyasa verileri çekiliyor (Binance & FNG)...")
    market = get_live_market_data()
    print(f"  • BTC: ${market['btc_price']} ({market['btc_change']}%)")
    print(f"  • Piyasa Duygusu: {market['fng_value']}/100 ({market['fng_sentiment']})")

    # 3. Kripto Haber Havuzu
    print("📡 Kripto haber akışları taranıyor...")
    articles = fetch_crypto_articles(config.CRYPTO_RSS_FEEDS)
    print(f"  • {len(articles)} adet sıcak gelişme tespit edildi.")

    if not articles:
        print("ℹ️ Şu an paylaşılacak yeni içerik bulunamadı.")
        return

    history = load_history()
    posted_slugs = {h.get("slug") for h in history if isinstance(h, dict)}

    candidate = None
    for art in articles:
        if art["slug"] not in posted_slugs:
            candidate = art
            break

    if not candidate:
        print("ℹ️ Havuzdaki tüm haberler daha önce paylaşılmış.")
        return

    # İlgili Coini Tespit Et (SOL, ETH, XRP, BTC)
    rel_coin = detect_relevant_coin(candidate["title"], candidate.get("summary", ""), market)
    print(f"🎯 [Seçilen Haber - {candidate['virality_score']} Puan]: {candidate['title']} (Coin: {rel_coin.get('symbol')})")

    # 4. Editoryal Lüks Kart Tasarımı
    out_dir = os.path.join(config.BASE_DIR, "output")
    os.makedirs(out_dir, exist_ok=True)
    card_path = os.path.join(out_dir, f"crypto_{candidate['slug'][:25]}.jpg")

    generate_crypto_card(
        title=candidate["title"],
        output_path=card_path,
        market_data=market,
        relevant_coin=rel_coin,
        image_url=candidate.get("image_url"),
        brand_name=config.BRAND_NAME,
        handle=config.X_HANDLE,
        accent_hex=config.BRAND_ACCENT_COLOR
    )
    print(f"🎨 Editoryal Kripto Kartı Oluşturuldu: {card_path}")

    # 5. Tweet & Telegram Formatlama
    tweet_text = format_crypto_tweet(candidate["title"], candidate.get("summary", ""), market)
    tg_caption = format_telegram_caption(candidate["title"], candidate.get("summary", ""), market, channel_handle=config.TELEGRAM_TARGET_CHAT)
    print("-" * 40)
    print(tweet_text)
    print("-" * 40)

    # 6. Telegram Yayını
    print("✈️ Telegram yayını yapılıyor...")
    tg_ok = send_crypto_post_to_telegram(card_path, tg_caption)
    if tg_ok:
        print("✅ [Telegram] Kripto bülteni başarıyla gönderildi!")
    else:
        print("⚠️ [Telegram] Gönderim başarısız oldu.")

    # 7. X (Twitter) Yayını
    if not config.TWITTER_AUTH_TOKEN:
        print("ℹ️ X çerezleri tanımlanmamış, sadece Telegram yayını yapıldı.")
        history.append({
            "slug": candidate["slug"],
            "title": candidate["title"],
            "status": "posted_telegram",
            "ts": time.time()
        })
        save_history(history)
        return

    print("🚀 X'e gönderiliyor...")
    res = post_to_x(tweet_text, card_path)
    if res.get("status") == "success":
        history.append({
            "slug": candidate["slug"],
            "title": candidate["title"],
            "status": "posted",
            "ts": time.time()
        })
        save_history(history)
        print("🎉 [CryptoRadar] X'e başarıyla paylaşıldı!")
    else:
        print(f"⚠️ Paylaşım Hatası: {res.get('message')}")


if __name__ == "__main__":
    dry = "--dry" in sys.argv or "--test" in sys.argv
    run_cycle(dry_run=dry)
