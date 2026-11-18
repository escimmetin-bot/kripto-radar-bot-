"""
CryptoRadar | Marka Görselleri Üretici
- Profil Fotoğrafı (Avatar): 1080x1080 (Twitter & Telegram dairesel uyumlu)
- Twitter Kapak Fotoğrafı (Banner): 1500x500 (Tam Twitter standardı)
"""
import os
import sys
import math

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "brand_assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def generate_avatar():
    size = 1080
    img = Image.new("RGBA", (size, size), (11, 14, 20, 255))
    draw = ImageDraw.Draw(img)

    # 1. Siber Radar Halkaları (Dairesel kırpmaya tam oturacak neon halkalar)
    center = size // 2
    accent_green = (0, 255, 163, 255)
    accent_cyan = (0, 240, 255, 255)
    dark_border = (25, 35, 52, 255)

    # Dış çevre halkaları
    for r in range(480, 510, 4):
        draw.ellipse([(center - r, center - r), (center + r, center + r)], outline=(0, 255, 163, 80), width=2)
    
    draw.ellipse([(center - 460, center - 460), (center + 460, center + 460)], outline=accent_green, width=6)
    draw.ellipse([(center - 380, center - 380), (center + 380, center + 380)], outline=(0, 240, 255, 120), width=3)
    draw.ellipse([(center - 280, center - 280), (center + 280, center + 280)], outline=(35, 50, 75, 255), width=2)

    # Radar Tarama Çizgileri
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        x_end = center + int(460 * math.cos(rad))
        y_end = center + int(460 * math.sin(rad))
        draw.line([(center, center), (x_end, y_end)], fill=(20, 30, 48, 160), width=2)

    # 2. Merkez Parlama / Glow
    for glow_r in range(220, 260, 2):
        alpha = int(40 * (1.0 - (glow_r - 220) / 40.0))
        draw.ellipse([(center - glow_r, center - glow_r), (center + glow_r, center + glow_r)], fill=(0, 255, 163, alpha))

    # Merkez Daire
    draw.ellipse([(center - 220, center - 220), (center + 220, center + 220)], fill=(16, 22, 32, 255), outline=accent_cyan, width=5)

    # 3. Yazı Tipleri
    try:
        f_hero = ImageFont.truetype("arialbd.ttf", 160)
        f_sub = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        f_hero = ImageFont.load_default()
        f_sub = ImageFont.load_default()

    # "KR" Monogram Logosu
    draw.text((center - 128, center - 138), "KR", font=f_hero, fill=(0, 0, 0, 200))
    draw.text((center - 130, center - 140), "KR", font=f_hero, fill=(255, 255, 255, 255))

    # Altına "RADAR" etiketi
    tag_bg_w, tag_bg_h = 240, 56
    tag_x = center - tag_bg_w // 2
    tag_y = center + 55
    draw.rounded_rectangle([(tag_x, tag_y), (tag_x + tag_bg_w, tag_y + tag_bg_h)], radius=12, fill=accent_green)
    draw.text((center - 75, tag_y + 8), "RADAR", font=f_sub, fill=(10, 14, 20))

    avatar_path = os.path.join(ASSETS_DIR, "kripto_radar_avatar.png")
    img.save(avatar_path, "PNG")
    print(f"✅ Profil Avatarı Hazırlandı: {avatar_path}")
    return avatar_path


def generate_twitter_banner():
    bw, bh = 1500, 500
    img = Image.new("RGBA", (bw, bh), (8, 11, 16, 255))
    draw = ImageDraw.Draw(img)

    # Arka plan siber ızgara
    for x in range(0, bw, 60):
        draw.line([(x, 0), (x, bh)], fill=(15, 22, 34, 255), width=1)
    for y in range(0, bh, 60):
        draw.line([(0, y), (bw, y)], fill=(15, 22, 34, 255), width=1)

    # Neon Yeşil & Mavi dalgalanma çizgileri (Grafik simülasyonu)
    points_green = [
        (0, 380), (200, 350), (450, 390), (700, 310), (950, 330), (1200, 240), (1350, 260), (1500, 190)
    ]
    draw.line(points_green, fill=(0, 255, 163, 220), width=4)

    # Başlık ve Metinler
    try:
        f_title = ImageFont.truetype("arialbd.ttf", 68)
        f_tag = ImageFont.truetype("arialbd.ttf", 26)
        f_sub = ImageFont.truetype("arial.ttf", 34)
    except Exception:
        f_title = ImageFont.load_default()
        f_tag = ImageFont.load_default()
        f_sub = ImageFont.load_default()

    # Rozet
    draw.rounded_rectangle([(100, 90), (420, 138)], radius=8, fill=(0, 255, 163, 255))
    draw.text((120, 98), "7/24 CANLI PİYASA & ANALİZ", font=f_tag, fill=(10, 14, 20))

    # Ana İsim
    draw.text((102, 162), "KRİPTO & FİNANS RADARI", font=f_title, fill=(0, 0, 0))
    draw.text((100, 160), "KRİPTO & FİNANS RADARI", font=f_title, fill=(255, 255, 255))

    # Alt Açıklama
    draw.text((100, 260), "Doğru Haber • Anlık Veriler • Bitcoin, Altcoin ve Finans Analizleri", font=f_sub, fill=(160, 175, 195))

    # Sağ Taraf: Metrik Rozetleri
    box_x = 1080
    draw.rounded_rectangle([(box_x, 90), (box_x + 340, 210)], radius=16, fill=(16, 24, 36), outline=(0, 240, 255, 160), width=2)
    draw.text((box_x + 25, 110), "⚡ PİYASA TAKİBİ", font=f_tag, fill=(0, 240, 255))
    draw.text((box_x + 25, 150), "@Kripto_FinansR", font=f_sub, fill=(255, 255, 255))

    draw.rounded_rectangle([(box_x, 230), (box_x + 340, 350)], radius=16, fill=(16, 24, 36), outline=(0, 255, 163, 160), width=2)
    draw.text((box_x + 25, 250), "🟢 CANLI VERİ AKIŞI", font=f_tag, fill=(0, 255, 163))
    draw.text((box_x + 25, 290), "7/24 Kesintisiz Radar", font=f_sub, fill=(240, 240, 240))

    banner_path = os.path.join(ASSETS_DIR, "kripto_radar_banner.png")
    img.save(banner_path, "PNG")
    print(f"✅ Twitter Kapak Banner Hazırlandı: {banner_path}")
    return banner_path


if __name__ == "__main__":
    generate_avatar()
    generate_twitter_banner()
