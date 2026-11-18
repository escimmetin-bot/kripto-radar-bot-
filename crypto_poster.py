"""
CryptoRadar | X (Twitter) Paylaşım Motoru
Playwright ile çerez tabanlı, Mavi Tik uzun format desteği ve görsel kart yükleme.
"""
import os
import sys
import time
import json
import re
from typing import Tuple, Optional
from playwright.sync_api import sync_playwright

import config
from crypto_market import get_live_market_data

HISTORY_FILE = os.path.join(config.BASE_DIR, "crypto_posted_history.json")


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(history: list):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-150:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Geçmiş kaydedilemedi: {e}")


def can_post_now(force: bool = False) -> Tuple[bool, str]:
    if force:
        return True, "Zorunlu mod aktif."

    hist = load_history()
    posted = [h for h in hist if isinstance(h, dict) and h.get("status") in ("posted", "posted_telegram") and h.get("ts")]
    if not posted:
        return True, "İlk paylaşım."

    last_ts = float(posted[-1]["ts"])
    now_ts = time.time()
    elapsed = (now_ts - last_ts) / 60.0

    # 3 Bot Ortak Senkron Saat Sistemi (Türkiye Saati UTC+3 ile 120 dakikalık sabit dilimler)
    # Ortak Dilimler: 00:00, 02:00, 04:00, 06:00, 08:00, 10:00, 12:00, 14:00, 16:00, 18:00, 20:00, 22:00
    slot_seconds = 7200  # 120 dakika (2 saat)
    current_slot = int((now_ts + 10800) // slot_seconds)
    last_slot = int((last_ts + 10800) // slot_seconds)

    if current_slot <= last_slot:
        next_slot_ts = (current_slot + 1) * slot_seconds - 10800
        rem = max(1.0, round((next_slot_ts - now_ts) / 60.0, 1))
        return False, f"Senkron 120 dk kilidi: Bu 2 saatlik dilimde paylaşıldı (Yeni ortak dilime {rem} dk kaldı)."

    if elapsed < 85.0:
        rem = round(85.0 - elapsed, 1)
        return False, f"Senkron koruma kilidi: Son paylaşımdan {round(elapsed, 1)} dk geçti ({rem} dk kaldı)."

    return True, f"Senkron ortak dilim aktif ({round(elapsed, 1)} dk geçti)."


def format_crypto_tweet(title: str, summary: str, market_data: dict) -> str:
    """X'in 280 karakter limitine mükemmel oturan, açıklamalı ve veri dolu kripto tweeti."""
    import html
    clean_title = html.unescape(title).strip()
    clean_summary = html.unescape(summary)
    clean_summary = re.sub(r'<[^>]+>', '', clean_summary)
    clean_summary = re.sub(r'https?://\S+', '', clean_summary).strip()

    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_summary) if len(s.strip()) > 15]
    desc = sents[0] if sents else ""

    btc_info = market_data.get("coins", {}).get("BTC", {})
    btc_p = btc_info.get("price", "78,000")
    btc_chg = btc_info.get("change", 0.0)
    chg_sign = "+" if btc_chg >= 0 else ""
    fng_val = market_data.get("fng_value", "50")

    header = "🚨 #KRİPTO SON DAKİKA"
    market_line = f"📊 BTC: ${btc_p} ({chg_sign}{btc_chg}%) • F&G: {fng_val}/100"
    tags = "#Bitcoin #Kripto #BTC #Altcoin"

    fixed_len = len(header) + len(market_line) + len(tags) + 8
    avail_for_content = 270 - fixed_len

    if len(clean_title) + len(desc) + 4 <= avail_for_content:
        content = f"📌 {clean_title}\n\n{desc}"
    elif len(clean_title) <= avail_for_content:
        rem = avail_for_content - len(clean_title) - 6
        if rem > 25 and desc:
            short_desc = desc[:rem].rsplit(' ', 1)[0] + "..."
            content = f"📌 {clean_title}\n\n{short_desc}"
        else:
            content = f"📌 {clean_title}"
    else:
        content = f"📌 {clean_title[:avail_for_content - 3]}..."

    tweet = f"{header}\n\n{content}\n\n{market_line}\n\n{tags}"
    return tweet.strip()


def post_to_x(text: str, image_path: str = None) -> dict:
    """Playwright çerezleriyle X'e tweet atar (Ultra stabil & Çift Hedef Korumalı)."""
    if not config.TWITTER_AUTH_TOKEN or not config.TWITTER_CT0:
        return {"status": "error", "message": "TWITTER_AUTH_TOKEN veya TWITTER_CT0 eksik."}

    try:
        with sync_playwright() as p:
            launch_args = [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
            browser = None
            try:
                browser = p.chromium.launch(channel="chrome", headless=True, args=launch_args)
            except Exception:
                browser = p.chromium.launch(headless=True, args=launch_args)

            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            ctx.add_cookies([
                {"name": "auth_token", "value": config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/", "secure": True, "httpOnly": True},
                {"name": "ct0", "value": config.TWITTER_CT0, "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False}
            ])

            page = ctx.new_page()
            
            # 1. Önce doğrudan /compose/post dene
            page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
            
            editor = None
            try:
                page.wait_for_selector('div[role="textbox"]', timeout=8000)
                editor = page.locator('div[role="textbox"][data-testid="tweetTextarea_0"]')
                if not editor.count():
                    editor = page.locator('div[role="textbox"]')
            except Exception:
                pass

            # 2. Bulunamadıysa ana akışa (/home) dön ve oradaki editörü kullan
            if not editor or not editor.count():
                print("🔄 /compose/post açılmadı, /home sayfasına geçiliyor...")
                page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_selector('div[role="textbox"]', timeout=12000)
                    editor = page.locator('div[role="textbox"][data-testid="tweetTextarea_0"]')
                    if not editor.count():
                        editor = page.locator('div[role="textbox"]')
                except Exception:
                    pass

            if not editor or not editor.count():
                browser.close()
                return {"status": "error", "message": "Tweet metin kutusu bulunamadı"}

            editor.first.click()
            editor.first.fill(text)
            page.wait_for_timeout(500)
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

            # Tweet Gönder Butonu
            post_btn = page.locator('button[data-testid="tweetButton"]').last
            if not post_btn.count():
                post_btn = page.locator('button[data-testid="tweetButtonInline"]').first

            # Görsel Ekle
            if image_path and os.path.exists(image_path):
                file_input = page.locator('input[data-testid="fileInput"]').first
                if file_input.count():
                    file_input.set_input_files(image_path)
                    print("⏳ Görsel X'e aktarılıyor...")
                    for sec in range(1, 15):
                        page.wait_for_timeout(1000)
                        attachments = page.locator('div[data-testid="attachments"]').count()
                        aria_dis = post_btn.get_attribute("aria-disabled") if post_btn.count() else "true"
                        if attachments > 0 and aria_dis != "true":
                            print(f"✅ Görsel başarıyla yüklendi ({sec}. saniye).")
                            break

            # Buton aktifliğini bekle
            for _ in range(10):
                aria_dis = post_btn.get_attribute("aria-disabled") if post_btn.count() else "true"
                if aria_dis != "true":
                    break
                page.wait_for_timeout(1000)

            # Gönderim
            page.keyboard.press("Escape")
            time.sleep(1)

            try:
                editor.first.focus()
                page.keyboard.press("Control+Enter")
            except Exception:
                pass

            page.wait_for_timeout(3000)
            if post_btn.count() and post_btn.is_visible():
                try:
                    post_btn.dispatch_event("click")
                except Exception:
                    pass

            page.wait_for_timeout(4000)
            browser.close()
            return {"status": "success", "message": "Tweet başarıyla paylaşıldı."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
