"""
CryptoRadar | Telegram Yayın & Dağıtım Motoru
Haberleri ve Full HD piyasa kartlarını Telegram kanalına / grubuna otomatik gönderir.
"""
import os
import requests
import html
import re

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_TARGET_CHAT = os.getenv("TELEGRAM_TARGET_CHAT", "@Kripto_FinansR")


def format_telegram_caption(title: str, summary: str, market_data: dict, channel_handle: str = "@Kripto_FinansR") -> str:
    """Telegram için şık ve emoji zenginliğinde haber bülteni metni."""
    c_title = html.unescape(title).strip()
    c_summary = html.unescape(summary)
    c_summary = re.sub(r'<[^>]+>', '', c_summary)
    c_summary = re.sub(r'https?://\S+', '', c_summary).strip()
    
    # 2-3 cümle
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', c_summary) if len(s.strip()) > 20]
    body = " ".join(sents[:2]) if sents else c_title

    btc_info = market_data.get("coins", {}).get("BTC", {})
    btc_p = btc_info.get("price", "78,000")
    btc_chg = btc_info.get("change", 0.0)
    chg_sign = "+" if btc_chg >= 0 else ""
    fng_val = market_data.get("fng_value", "50")
    fng_sent = market_data.get("fng_sentiment", "Nötr")

    caption = (
        f"🚨 <b>KRİPTO SON DAKİKA!</b>\n\n"
        f"📌 <b>{c_title}</b>\n\n"
        f"{body}\n\n"
        f"📊 <b>Anlık Piyasa Verileri:</b>\n"
        f"• <b>Bitcoin (BTC):</b> ${btc_p} ({chg_sign}{btc_chg}%)\n"
        f"• <b>Korku Endeksi:</b> {fng_val}/100 ({fng_sent})\n\n"
        f"⚡ <b>Kripto Radar</b> | {channel_handle}"
    )
    return caption[:1020]


def send_crypto_post_to_telegram(photo_path: str, caption: str, target_chat: str = None) -> bool:
    """Telegram kanalına veya sohbetine fotoğraflı bülten gönderir."""
    chat_id = target_chat or TELEGRAM_TARGET_CHAT
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    try:
        with open(photo_path, "rb") as f:
            resp = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "caption": caption,
                    "parse_mode": "HTML"
                },
                files={"photo": f},
                timeout=25
            )
            data = resp.json()
            if data.get("ok"):
                return True
            else:
                print(f"⚠️ Telegram Gönderim Hatası: {data.get('description')}")
                return False
    except Exception as e:
        print(f"⚠️ Telegram İstisnası: {e}")
        return False
