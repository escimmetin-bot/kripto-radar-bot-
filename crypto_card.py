"""
CryptoRadar | Gündem Analizi Tarzı 1080x1080 Tam Boyut Editoryal Kart Motoru
- Tam boyut (full bleed) arka plan görseli
- Aşağı doğru koyulaşan şık karartma katmanı (gradient)
- Üstte sol ve sağ rozetler
- Altta büyük ve net 54px Arial Bold başlık
- Alt bilgi çubuğu: Kaynak, tarih ve altın sarısı marka etiketi
"""
import os
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

CARD_W = 1080
CARD_H = 1080

FONT_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "arialbd.ttf"),
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "arialbd.ttf"
]


def get_font(size: int):
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) > max_width:
            current_line.pop()
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def create_gradient(width: int, height: int, start_alpha: int = 50, end_alpha: int = 245) -> Image.Image:
    gradient = Image.new("RGBA", (width, height), color=0)
    draw = ImageDraw.Draw(gradient)
    for y in range(height):
        ratio = y / height
        alpha = int(start_alpha + (end_alpha - start_alpha) * (ratio ** 1.6))
        draw.line([(0, y), (width, y)], fill=(12, 16, 26, alpha))
    return gradient


def generate_crypto_card(
    title: str,
    output_path: str,
    market_data: dict,
    relevant_coin: dict = None,
    image_url: str = None,
    brand_name: str = "KRİPTO & FİNANS RADARI",
    handle: str = "@kriptofinansa",
    accent_hex: str = "#00FFA3"
) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    c_info = relevant_coin or market_data.get("coins", {}).get("BTC", {"price": "78,000", "change": 0.5, "symbol": "BTC"})
    c_sym = c_info.get("symbol", "BTC")
    c_p = c_info.get("price", "78,000")
    c_chg = c_info.get("change", 0.0)

    base_image = None
    if image_url:
        try:
            r = requests.get(image_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.content) > 3000:
                raw_img = Image.open(BytesIO(r.content)).convert("RGBA")
                img_ratio = raw_img.width / raw_img.height
                target_ratio = CARD_W / CARD_H
                if img_ratio > target_ratio:
                    new_width = int(CARD_H * img_ratio)
                    raw_img = raw_img.resize((new_width, CARD_H), Image.Resampling.LANCZOS)
                    crop_x = (new_width - CARD_W) // 2
                    base_image = raw_img.crop((crop_x, 0, crop_x + CARD_W, CARD_H))
                else:
                    new_height = int(CARD_W / img_ratio)
                    raw_img = raw_img.resize((CARD_W, new_height), Image.Resampling.LANCZOS)
                    crop_y = (new_height - CARD_H) // 2
                    base_image = raw_img.crop((0, crop_y, CARD_W, crop_y + CARD_H))
        except Exception as e:
            print(f"⚠️ Görsel indirilemedi: {e}")

    if base_image is None:
        base_image = Image.new("RGBA", (CARD_W, CARD_H), (15, 20, 32, 255))
        bg_draw = ImageDraw.Draw(base_image)
        for y in range(CARD_H):
            r = int(15 + 20 * (y / CARD_H))
            g = int(20 + 35 * (y / CARD_H))
            b = int(35 + 50 * (y / CARD_H))
            bg_draw.line([(0, y), (CARD_W, y)], fill=(r, g, b, 255))

    # Gündem Analizi Karartma Katmanı
    gradient = create_gradient(CARD_W, CARD_H, start_alpha=50, end_alpha=245)
    composed = Image.alpha_composite(base_image, gradient)
    draw = ImageDraw.Draw(composed)

    # 1. Üst Sol Rozet (Badge: ● FLAŞ HABER | BTC)
    font_badge = get_font(28)
    badge_text = f"●  FLAŞ HABER | {c_sym}"
    b_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = (b_bbox[2] - b_bbox[0]) + 44
    bh = (b_bbox[3] - b_bbox[1]) + 24
    draw.rounded_rectangle([(60, 60), (60 + bw, 60 + bh)], radius=10, fill=(220, 38, 38, 240))
    draw.text((82, 70), badge_text, fill=(255, 255, 255), font=font_badge)

    # 2. Üst Sağ Ticker Rozeti (Fiyat & Değişim)
    chg_sign = "+" if c_chg >= 0 else ""
    ticker_text = f"{c_sym}: ${c_p} ({chg_sign}{c_chg}%)"
    t_bbox = draw.textbbox((0, 0), ticker_text, font=font_badge)
    tw = (t_bbox[2] - t_bbox[0]) + 40
    th = (t_bbox[3] - t_bbox[1]) + 24
    tx = CARD_W - 60 - tw
    ticker_bg = (16, 185, 129, 230) if c_chg >= 0 else (239, 68, 68, 230)
    draw.rounded_rectangle([(tx, 60), (tx + tw, 60 + th)], radius=10, fill=ticker_bg)
    draw.text((tx + 20, 70), ticker_text, fill=(255, 255, 255), font=font_badge)

    # 3. Ana Başlık Metni (Alt kısımda dev 54px Arial Bold)
    font_title = get_font(54)
    max_text_width = CARD_W - 120
    lines = wrap_text(title, font_title, max_text_width, draw)[:4]

    line_height = 70
    total_text_h = len(lines) * line_height
    text_start_y = CARD_H - total_text_h - 150

    for i, line in enumerate(lines):
        y = text_start_y + (i * line_height)
        # Metin gölgesi
        draw.text((63, y + 3), line, fill=(0, 0, 0, 220), font=font_title)
        # Asıl başlık (Beyaz)
        draw.text((60, y), line, fill=(255, 255, 255), font=font_title)

    # 4. Alt Bilgi Çubuğu (Kaynak ve Tarih)
    font_meta = get_font(24)
    current_date = datetime.now().strftime("%d.%m.%Y • %H:%M")
    footer_text = f"Kaynak: {brand_name}   |   {current_date}"
    draw.text((60, CARD_H - 75), footer_text, fill=(200, 205, 215), font=font_meta)

    # Sağ alt köşe marka etiketi (Altın Sarısı)
    brand_text = handle
    b_bbox = draw.textbbox((0, 0), brand_text, font=font_meta)
    draw.text((CARD_W - 60 - (b_bbox[2] - b_bbox[0]), CARD_H - 75), brand_text, fill=(255, 215, 0), font=font_meta)

    composed.convert("RGB").save(output_path, "JPEG", quality=95)
    return output_path
