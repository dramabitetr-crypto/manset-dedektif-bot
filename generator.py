import json
import os
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont

# 1. State (Kaldığımız yer) dosyasını oku
if os.path.exists('state.json'):
    with open('state.json', 'r', encoding='utf-8') as f:
        state = json.load(f)
else:
    state = {"last_index": 0}

currentIndex = state.get("last_index", 0)

# 2. Vakalar.json dosyasını oku
with open('vakalar.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# Sıradaki vakayı seç (100 biterse baştan başla)
current_case = cases[currentIndex % len(cases)]
print(f"İşlenen Vaka: {current_case['title']}")

# 3. Dikey Video için Arka Plan Görseli Oluştur (9:16 - 1080x1920)
img = Image.new('RGB', (1080, 1920), color='#090d16')
d = ImageDraw.Draw(img)

# Türkçe karakterleri destekleyen sistem fontunu yükleyelim (Linux sunucularda bulunur)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    title_font = ImageFont.truetype(font_path, 55)
    content_font = ImageFont.truetype(font_regular, 38)
    alert_font = ImageFont.truetype(font_path, 50)
    footer_font = ImageFont.truetype(font_regular, 36)
except:
    # Yedek olarak varsayılan fontu kullan
    title_font = ImageFont.load_default()
    content_font = ImageFont.load_default()
    alert_font = ImageFont.load_default()
    footer_font = ImageFont.load_default()

title_text = current_case['title']
clean_content = current_case['content'].replace('<b>', '').replace('</b>', '').replace('<br>', '\n')

# Metinleri ve Başlığı Yerleştirme
d.text((80, 200), "🚨 GİZLİ DOSYA / MANŞET DEDEKTİF", fill="#38bdf8", font=footer_font)
d.text((80, 280), title_text, fill="#fbbf24", font=title_font)

# İçeriği ekrana ortalama tarzında çizdirme
d.text((80, 450), clean_content, fill="#f8fafc", font=content_font)

# Dikkat çekici uyarı ve sayaç vurgusu
d.text((80, 1250), "⏳ ÇÖZÜM İÇİN SON 20 SANİYE!", fill="#ef4444", font=alert_font)
d.text((80, 1400), "Kimin işlediğini bulabilecek misin?\nCevap ve Oyunu Çözmek İçin:\nTelegram Mini App'e Tıkla! 👇\nt.me/manset_dedektif_bot/dedektif", fill="#38bdf8", font=footer_font)

# Geçici görsel olarak kaydet
image_path = "temp_frame.png"
img.save(image_path)

# 4. FFmpeg kullanarak görseli 15 saniyelik dikey MP4 videoya dönüştür (Okunabilir süre)
video_path = "gunun_vakasi.mp4"
ffmpeg_command = [
    "ffmpeg", "-y",
    "-loop", "1",
    "-i", image_path,
    "-t", "15",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-vf", "scale=1080:1920",
    video_path
]

print("Video oluşturuluyor (15 saniye & Türkçe font desteği)...")
subprocess.run(ffmpeg_command, check=True)
print("Video başarıyla üretildi!")

# 5. Telegram Kanalına Videoyu Gönder
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🎬 GÜNÜN DEDEKTİFİK VAKASI!\n\n{title_text}\n\n🕵️ Oyuna katılmak ve çözmek için Mini App'e tıkla!"
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 6. Endeks numarasını bir artır ve state.json'a kaydet
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("Vaka başarıyla işlendi ve kanala gönderildi!")
